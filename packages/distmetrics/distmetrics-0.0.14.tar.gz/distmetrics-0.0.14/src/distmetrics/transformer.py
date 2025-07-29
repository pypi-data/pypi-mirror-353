import json
import math
import os
import platform
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Union

import einops
import numpy as np
import torch
import torch.mps
import torch.nn as nn
import torch.nn.functional as F
from einops._torch_specific import allow_ops_in_compiled_graph
from pydantic import BaseModel, ConfigDict, model_validator
from scipy.special import logit
from tqdm.auto import tqdm

from distmetrics.mahalanobis import _transform_pre_arrs
from distmetrics.model_data.transformer_config import transformer_config, transformer_latest_config


MODEL_DATA = Path(__file__).parent.resolve() / 'model_data'
TRANSFORMER_WEIGHTS_PATH_LATEST = MODEL_DATA / 'transformer_latest.pth'
TRANSFORMER_WEIGHTS_PATH_ORIGINAL = MODEL_DATA / 'transformer.pth'

# Dtype selection
_DTYPE_MAP = {
    'float32': torch.float32,
    'float': torch.float32,
    'bfloat16': torch.bfloat16,
}
DEV_DTYPE = _DTYPE_MAP.get(os.environ.get('DEV_DTYPE', 'float32').lower(), torch.float32)

_MODEL = None


def unfolding_stream(
    image_st: torch.Tensor, kernel_size: int, stride: int, batch_size: int
) -> Generator[torch.Tensor, None, None]:
    _, _, H, W = image_st.shape

    patches = []
    slices = []

    n_patches_y = int(np.floor((H - kernel_size) / stride) + 1)
    n_patches_x = int(np.floor((W - kernel_size) / stride) + 1)

    for i in range(0, n_patches_y):
        for j in range(0, n_patches_x):
            if i == (n_patches_y - 1):
                s_y = slice(H - kernel_size, H)
            else:
                s_y = slice(i * stride, i * stride + kernel_size)

            if j == (n_patches_x - 1):
                s_x = slice(W - kernel_size, W)
            else:
                s_x = slice(j * stride, j * stride + kernel_size)

            patch = image_st[..., s_y, s_x]
            patches.append(patch)
            slices.append((s_y, s_x))

            # Yield patches in batches
            if len(patches) == batch_size:
                yield torch.stack(patches, dim=0), slices
                patches = []
                slices = []

    if patches:
        yield torch.stack(patches, dim=0), slices


class DiagMahalanobisDistance2d(BaseModel):
    dist: Union[np.ndarray, list]  # noqa: UP007
    mean: np.ndarray
    std: np.ndarray

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode='after')
    def check_shapes(cls, values: dict) -> dict:
        """Check the covariance matrix is of the form 2 x 2 x H x W."""
        d = values.dist
        mu = values.mean
        sigma = values.std

        if mu.shape != sigma.shape:
            raise ValueError('mean and std must have the same shape')
        if d.shape != sigma.shape[1:]:
            raise ValueError('The mean/std must have same spatial dimensions as dist')


class SpatioTemporalTransformer(nn.Module):
    def __init__(self, model_config: dict) -> None:
        super().__init__()

        self.d_model = model_config['d_model']
        self.nhead = model_config['nhead']
        self.num_encoder_layers = model_config['num_encoder_layers']
        self.dim_feedforward = model_config['dim_feedforward']
        self.max_seq_len = model_config['max_seq_len']
        self.dropout = model_config['dropout']
        self.activation = model_config['activation']

        self.num_patches = model_config['num_patches']
        self.patch_size = model_config['patch_size']
        self.data_dim = model_config['data_dim']

        self.embedding = nn.Linear(self.data_dim, self.d_model)

        self.spatial_pos_embed = nn.Parameter(torch.zeros(1, 1, self.num_patches, self.d_model))
        self.temporal_pos_embed = nn.Parameter(torch.zeros(1, self.max_seq_len, 1, self.d_model))

        encoder_layer = nn.TransformerEncoderLayer(
            self.d_model,
            self.nhead,
            self.dim_feedforward,
            dropout=self.dropout,
            activation=self.activation,
            batch_first=True,
        )

        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, self.num_encoder_layers)

        self.mean_out = nn.Sequential(
            nn.Linear(self.d_model, self.dim_feedforward),  # reuse dim feedforward here
            nn.ReLU(),
            nn.Linear(self.dim_feedforward, self.data_dim),
        )

        self.logvar_out = nn.Sequential(
            nn.Linear(self.d_model, self.dim_feedforward),  # reuse dim feedforward here
            nn.ReLU(),
            nn.Linear(self.dim_feedforward, self.data_dim),
        )

    def num_parameters(self) -> float:
        """Count the number of trainable parameters in the model."""
        if not hasattr(self, '_num_parameters'):
            self._num_parameters = 0
            for p in self.parameters():
                count = 1
                for s in p.size():
                    count *= s
                self._num_parameters += count

        return self._num_parameters

    def forward(self, img_baseline: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, seq_len, channels, height, width = img_baseline.shape

        assert self.num_patches == (height * width) / (self.patch_size**2)

        img_baseline = einops.rearrange(
            img_baseline, 'b t c (h ph) (w pw) -> b t (h w) (c ph pw)', ph=self.patch_size, pw=self.patch_size
        )  # batch, seq_len, num_patches, data_dim

        img_baseline = (
            self.embedding(img_baseline)
            + self.spatial_pos_embed
            # changed self.temporal_pos_embed[:, :seq_len, :, :]
            # to self.temporal_pos_embed[:, (self.max_seq_len-seq_len):, :, :] to ensure last pre-image always has
            # correct index
            + self.temporal_pos_embed[:, (self.max_seq_len - seq_len) :, :, :]
        )  # batch, seq_len, num_patches, d_model

        img_baseline = img_baseline.view(
            batch_size, seq_len * self.num_patches, self.d_model
        )  # transformer expects (batch_size, sequence, dmodel)

        output = self.transformer_encoder(img_baseline)

        mean = self.mean_out(output)  # batchsize, seq_len*num_patches, data_dim
        logvar = self.logvar_out(output)  # batchsize, seq_len*num_patches, 2*data_dim

        mean = mean.view(batch_size, seq_len, self.num_patches, self.data_dim)  # undo previous operation
        logvar = logvar.view(batch_size, seq_len, self.num_patches, self.data_dim)

        # reshape to be the same shape as input batch_size, seq len, channels, height, width
        mean = einops.rearrange(
            mean,
            'b t (h w) (c ph pw) -> b t c (h ph) (w pw)',
            ph=self.patch_size,
            pw=self.patch_size,
            c=channels,
            h=height // self.patch_size,
            w=width // self.patch_size,
        )

        # reshape so for each pixel we output 4 numbers (ie each entry of cov matrix)
        logvar = einops.rearrange(
            logvar,
            'b t (h w) (c ph pw) -> b t c (h ph) (w pw)',
            ph=self.patch_size,
            pw=self.patch_size,
            c=channels,
            h=height // self.patch_size,
            w=width // self.patch_size,
        )

        return mean[:, -1, ...], logvar[:, -1, ...]


def get_device() -> str:
    if torch.cuda.is_available():
        device = 'cuda'
    elif platform.system() == 'Darwin' and torch.backends.mps.is_available():
        device = 'mps'
    else:
        device = 'cpu'
    return device


def control_flow_for_device(device: str | None = None) -> str:
    if device is None:
        device = get_device()
    elif isinstance(device, str):
        if device not in ['cpu', 'cuda', 'mps']:
            raise ValueError('device must be one of cpu, cuda, mps')
    return device


def load_transformer_model(
    model_token: str = 'latest',
    model_cfg_path: Path | None = None,
    model_wts_path: Path | None = None,
    device: str | None = None,
    optimize: bool = False,
    batch_size: int = 32,
) -> SpatioTemporalTransformer:
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    if model_token not in ['latest', 'original', 'external']:
        raise ValueError('model_token must be one of latest, original, or external')

    if model_token == 'latest':
        config = transformer_latest_config
        weights_path = TRANSFORMER_WEIGHTS_PATH_LATEST
    elif model_token == 'original':
        config = transformer_config
        weights_path = TRANSFORMER_WEIGHTS_PATH_ORIGINAL
    else:
        with Path.open(model_cfg_path) as cfg:
            config = json.load(cfg)
        weights_path = model_wts_path

    device = control_flow_for_device(device)
    weights = torch.load(weights_path, map_location=device, weights_only=True)
    transformer = SpatioTemporalTransformer(config).to(device)
    transformer.load_state_dict(weights)
    transformer = transformer.eval()

    if optimize:
        allow_ops_in_compiled_graph()

        if device == 'cuda':
            import torch_tensorrt

            # Get dimensions
            total_pixels = transformer.num_patches * (transformer.patch_size**2)
            wh = math.isqrt(total_pixels)
            channels = transformer.data_dim // (transformer.patch_size**2)
            expected_dims = (batch_size, transformer.max_seq_len, channels, wh, wh)

            transformer = torch_tensorrt.compile(
                transformer,
                inputs=[
                    torch_tensorrt.Input(
                        min_shape=(1,) + expected_dims[1:],
                        opt_shape=expected_dims,
                        max_shape=expected_dims,
                        dtype=DEV_DTYPE,
                    )
                ],
                enabled_precisions={DEV_DTYPE},  # e.g., {torch.float}, {torch.float16}
                truncate_long_and_double=True,  # Optional: helps prevent type issues
            )

        else:
            transformer = torch.compile(transformer, mode='max-autotune-no-cudagraphs', dynamic=False)

    _MODEL = transformer

    return transformer


@torch.inference_mode()
def _estimate_logit_params_via_streamed_patches(
    model: torch.nn.Module,
    imgs_copol: list[np.ndarray],
    imgs_crosspol: list[np.ndarray],
    stride: int = 2,
    batch_size: int = 32,
    max_nodata_ratio: float = 0.1,
    tqdm_enabled: bool = True,
    device: str | None = None,
) -> tuple[np.ndarray]:
    """Estimate the mean and sigma of the normal distribution of logit input images using low-memory strategy.

    This streams the data in chunks *on the CPU* and requires less GPU memory, but is slower due to data transfer.

    Parameters
    ----------
    model : torch.nn.Module
        transformer with chip (or patch size) 16
    pre_imgs_vv : list[np.ndarray]
    pre_imgs_vh : list[np.ndarray]
        _description_
    stride : int, optional
        Should be between 1 and 16, by default 2.
    batch_size : int, optional
        How to batch chips.

    Returns
    -------
    tuple[np.ndarray]
        pred_mean, pred_sigma (as logits)

    Notes
    -----
    - Applied model to images where mask values are assigned 1e-7
    """
    P = 16
    assert stride <= P
    assert stride > 0

    device = control_flow_for_device(device)

    # stack to T x 2 x H x W
    pre_imgs_stack = _transform_pre_arrs(imgs_copol, imgs_crosspol)
    pre_imgs_stack = pre_imgs_stack.astype('float32')

    # Mask
    mask_stack = np.isnan(pre_imgs_stack)
    # Remove T x 2 dims
    mask_spatial = torch.from_numpy(np.any(mask_stack, axis=(0, 1))).to(device)
    assert len(mask_spatial.shape) == 2, 'spatial mask should be 2d'

    # Logit transformation
    pre_imgs_stack[mask_stack] = 1e-7
    pre_imgs_logit = logit(pre_imgs_stack)
    pre_imgs_stack_t = torch.from_numpy(pre_imgs_logit).to(device, dtype=DEV_DTYPE)

    # C x H x W
    C, H, W = pre_imgs_logit.shape[-3:]

    # Sliding window
    n_patches_y = int(np.floor((H - P) / stride) + 1)
    n_patches_x = int(np.floor((W - P) / stride) + 1)
    n_patches = n_patches_y * n_patches_x

    n_batches = math.ceil(n_patches / batch_size)

    target_shape = (C, H, W)
    count = torch.zeros(*target_shape).to(device, dtype=DEV_DTYPE)
    pred_means = torch.zeros(*target_shape).to(device, dtype=DEV_DTYPE)
    pred_logvars = torch.zeros(*target_shape).to(device, dtype=DEV_DTYPE)

    unfold_gen = unfolding_stream(pre_imgs_stack_t, P, stride, batch_size)

    for patch_batch, slices in tqdm(
        unfold_gen,
        total=n_batches,
        desc='Chips Traversed',
        mininterval=2,
        disable=(not tqdm_enabled),
        dynamic_ncols=True,
    ):
        patch_batch = patch_batch.to(device, dtype=DEV_DTYPE)
        chip_mean, chip_logvar = model(patch_batch)
        for k, (sy, sx) in enumerate(slices):
            chip_mask = mask_spatial[sy, sx]
            if (chip_mask).sum().item() / chip_mask.nelement() <= max_nodata_ratio:
                pred_means[:, sy, sx] += chip_mean[k, ...]
                pred_logvars[:, sy, sx] += chip_logvar[k, ...]
                count[:, sy, sx] += 1
    pred_means /= count
    pred_logvars /= count

    M_3d = mask_spatial.unsqueeze(dim=0).expand(pred_means.shape)
    pred_means[M_3d] = torch.nan
    pred_logvars[M_3d] = torch.nan

    pred_means = pred_means.cpu().numpy().squeeze()
    pred_logvars = pred_logvars.cpu().numpy().squeeze()
    pred_sigmas = np.sqrt(np.exp(pred_logvars))
    return pred_means, pred_sigmas


@torch.inference_mode()
def _estimate_logit_params_via_folding(
    model: torch.nn.Module,
    imgs_copol: list[np.ndarray],
    imgs_crosspol: list[np.ndarray],
    stride: int = 2,
    batch_size: int = 32,
    device: str | None = None,
    tqdm_enabled: bool = True,
) -> tuple[np.ndarray]:
    """Estimate the mean and sigma of the normal distribution of logit input images using high-memory strategy.

    This uses folding/unfolding which stores pixels reduntly in memory, but is very fast on the GPU.

    Parameters
    ----------
    model : torch.nn.Module
        transformer with chip (or patch size) 16, make sure your model is in evaluation mode
    pre_imgs_vv : list[np.ndarray]
    pre_imgs_vh : list[np.ndarray]
        _description_
    stride : int, optional
        Should be between 1 and 16, by default 2.
    stride : int, optional
        How to batch chips.
    device : str | None, optional
        Device to run the model on. If None, will use the best device available.
        Acceptable values are 'cpu', 'cuda', 'mps'. Defaults to None.

    Returns
    -------
    tuple[np.ndarray]
        pred_mean, pred_sigma (as logits)

    Notes
    -----
    - May apply model to chips of slightly smaller size around boundary
    - Applied model to images where mask values are assigned 1e-7
    """
    P = 16
    assert stride <= P
    assert stride > 0

    device = control_flow_for_device(device)

    # stack to T x 2 x H x W
    pre_imgs_stack = _transform_pre_arrs(imgs_copol, imgs_crosspol)
    pre_imgs_stack = pre_imgs_stack.astype('float32')

    # Mask
    mask_stack = np.isnan(pre_imgs_stack)
    # Remove T x 2 dims
    mask_spatial = torch.from_numpy(np.any(mask_stack, axis=(0, 1))).to(device)
    assert len(mask_spatial.shape) == 2, 'spatial mask should be 2d'

    # Logit transformation
    pre_imgs_stack[mask_stack] = 1e-7
    pre_imgs_logit = logit(pre_imgs_stack)

    # H x W
    H, W = pre_imgs_logit.shape[-2:]
    T = pre_imgs_logit.shape[0]
    C = pre_imgs_logit.shape[1]

    # Sliding window
    n_patches_y = int(np.floor((H - P) / stride) + 1)
    n_patches_x = int(np.floor((W - P) / stride) + 1)
    n_patches = n_patches_y * n_patches_x

    # Shape (T x 2 x H x W)
    pre_imgs_stack_t = torch.from_numpy(pre_imgs_logit).to(device, dtype=DEV_DTYPE)
    # T x (2 * P**2) x n_patches
    patches = F.unfold(pre_imgs_stack_t, kernel_size=P, stride=stride)
    # n_patches x T x (C * P**2)
    patches = patches.permute(2, 0, 1).to(device, dtype=DEV_DTYPE)
    # n_patches x T x C x P**2
    patches = patches.view(n_patches, T, C, P**2)

    n_batches = math.ceil(n_patches / batch_size)

    target_chip_shape = (n_patches, C, P, P)
    pred_means_p = torch.zeros(*target_chip_shape).to(device, dtype=DEV_DTYPE)
    pred_logvars_p = torch.zeros(*target_chip_shape).to(device, dtype=DEV_DTYPE)

    for i in tqdm(
        range(n_batches),
        desc='Chips Traversed',
        mininterval=2,
        disable=(not tqdm_enabled),
        dynamic_ncols=True,
    ):
        # change last dimension from P**2 to P, P; use -1 because won't always have batch_size as 0th dimension
        batch_s = slice(batch_size * i, batch_size * (i + 1))
        patch_batch = patches[batch_s, ...].view(-1, T, C, P, P)
        chip_mean, chip_logvar = model(patch_batch)
        pred_means_p[batch_s, ...] += chip_mean
        pred_logvars_p[batch_s, ...] += chip_logvar
    del patches
    torch.cuda.empty_cache()

    # n_patches x C x P x P -->  (C * P**2) x n_patches
    pred_logvars_p_reshaped = pred_logvars_p.view(n_patches, C * P**2).permute(1, 0)
    pred_logvars = F.fold(pred_logvars_p_reshaped, output_size=(H, W), kernel_size=P, stride=stride)
    del pred_logvars_p

    pred_means_p_reshaped = pred_means_p.view(n_patches, C * P**2).permute(1, 0)
    pred_means = F.fold(pred_means_p_reshaped, output_size=(H, W), kernel_size=P, stride=stride)
    del pred_means_p_reshaped

    input_ones = torch.ones(1, H, W).to(device, dtype=DEV_DTYPE)
    count_patches = F.unfold(input_ones, kernel_size=P, stride=stride)
    count = F.fold(count_patches, output_size=(H, W), kernel_size=P, stride=stride)
    del count_patches
    torch.cuda.empty_cache()

    pred_means /= count
    pred_logvars /= count

    mask_3d = mask_spatial.unsqueeze(dim=0).expand(pred_means.shape)
    pred_means[mask_3d] = torch.nan
    pred_logvars[mask_3d] = torch.nan

    pred_means = pred_means.cpu().numpy().squeeze()
    pred_logvars = pred_logvars.cpu().numpy().squeeze()
    pred_sigmas = np.sqrt(np.exp(pred_logvars))
    return pred_means, pred_sigmas


def estimate_normal_params_of_logits(
    model: torch.nn.Module,
    imgs_copol: list[np.ndarray],
    imgs_crosspol: list[np.ndarray],
    stride: int = 2,
    batch_size: int = 32,
    tqdm_enabled: bool = True,
    memory_strategy: str = 'high',
    device: str | None = None,
) -> tuple[np.ndarray]:
    if memory_strategy not in ['high', 'low']:
        raise ValueError('memory strategy must be high or low')

    estimate_logits = (
        _estimate_logit_params_via_folding if memory_strategy == 'high' else _estimate_logit_params_via_streamed_patches
    )

    mu, sigma = estimate_logits(
        model, imgs_copol, imgs_crosspol, stride=stride, batch_size=batch_size, tqdm_enabled=tqdm_enabled, device=device
    )
    return mu, sigma


def compute_transformer_zscore(
    model: torch.nn.Module,
    pre_imgs_copol: list[np.ndarray],
    pre_imgs_crosspol: list[np.ndarray],
    post_arr_copol: np.ndarray,
    post_arr_crosspol: np.ndarray,
    stride: int = 4,
    batch_size: int = 32,
    tqdm_enabled: bool = True,
    agg: str | Callable = 'max',
    memory_strategy: str = 'high',
    device: str | None = None,
) -> DiagMahalanobisDistance2d:
    """
    Compute the transformer z-score.

    Assumes that VV and VH are independent so returns mean, std for each polarizaiton separately (as learned by
    model). The mean and std are returned as 2 x H x W matrices. The two zscores are aggregated by the callable agg.
    Agg defaults to maximum z-score of each polarization.

    Warning: mean and std are in logits! That is logit(gamma_naught)!
    """
    if isinstance(agg, str):
        if agg not in ['max', 'min']:
            raise NotImplementedError('We expect max/min as strings')
        elif agg == 'min':
            agg = np.min
        else:
            agg = np.max

    mu, sigma = estimate_normal_params_of_logits(
        model,
        pre_imgs_copol,
        pre_imgs_crosspol,
        stride=stride,
        batch_size=batch_size,
        tqdm_enabled=tqdm_enabled,
        memory_strategy=memory_strategy,
        device=device,
    )

    post_arr_logit_s = logit(np.stack([post_arr_copol, post_arr_crosspol], axis=0))
    z_score_dual = np.abs(post_arr_logit_s - mu) / sigma
    z_score = agg(z_score_dual, axis=0)
    m_dist = DiagMahalanobisDistance2d(dist=z_score, mean=mu, std=sigma)
    return m_dist
