"""Proposed hybrid segmentation model (architecture spec v3, Section 4/5/18).

`HybridSegmentation` is the proposed architecture: an ImageNet-pretrained
ResNet34 encoder (same as the baseline), a lightweight Transformer applied
only at the 16x16 CNN bottleneck, projected element-wise fusion of the CNN
bottleneck with the Transformer output, and the *same* U-Net-style decoder
(with deep supervision) used by `ResNet34UNet`.

Locked transformer configuration (Section 3):

    blocks        = 4
    attention     = 4 heads
    model dim     = 256
    FFN dim       = 1024
    activation    = GELU
    normalization = Pre-LayerNorm
    dropout       = 0.10 (attention and FFN)
    position      = learned 2-D embedding over the 16x16 token grid

Fusion (Section 5.3) is projected element-wise addition of the CNN C5 1x1
projection and the Transformer output at the bottleneck:

    fused = project(c5) + transformer(c5)

Run inside the `ai` conda environment.
"""

from __future__ import annotations

from typing import cast

import torch
import torch.nn as nn
from torch import Tensor

from ml.models.resnet34_unet import (
    BOTTLENECK_DIM,
    NUM_CLASSES,
    ResNet34Encoder,
    UnetDecoder,
)

BOTTLENECK_TOKENS = 256  # 16 x 16 token grid
TRANSFORMER_BLOCKS = 4
TRANSFORMER_HEADS = 4
TRANSFORMER_FFN_DIM = 1024
TRANSFORMER_DROPOUT = 0.10


class BottleneckTransformer(nn.Module):
    """Attention applied only to the 16x16 bottleneck features.

    Input  : C5 tensor [B, 512, 16, 16]
    Project: 1x1 conv 512 -> 256, flatten to 256 tokens -> [B, 256, 256]
    Output : reshaped [B, 256, 16, 16] global-context representation
    """

    def __init__(
        self,
        in_channels: int = 512,
        d_model: int = BOTTLENECK_DIM,
        num_blocks: int = TRANSFORMER_BLOCKS,
        num_heads: int = TRANSFORMER_HEADS,
        ffn_dim: int = TRANSFORMER_FFN_DIM,
        dropout: float = TRANSFORMER_DROPOUT,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.project = nn.Conv2d(in_channels, d_model, kernel_size=1)
        self.pos_embed = nn.Parameter(torch.zeros(1, BOTTLENECK_TOKENS, d_model))
        nn.init.normal_(self.pos_embed, 0.0, 0.02)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=num_heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            activation="gelu",
            norm_first=True,
            batch_first=True,
        )
        self.blocks = nn.TransformerEncoder(layer, num_layers=num_blocks)

    def forward(self, c5: Tensor) -> Tensor:
        x = self.project(c5)
        batch, channels, height, width = x.shape
        tokens = x.flatten(2).transpose(1, 2)
        tokens = tokens + self.pos_embed
        tokens = self.blocks(tokens)
        out = tokens.transpose(1, 2).reshape(batch, channels, height, width)
        return cast(Tensor, out)


class HybridSegmentation(nn.Module):
    """ResNet34 + bottleneck Transformer + additive fusion + U-Net decoder."""

    def __init__(
        self,
        num_classes: int = NUM_CLASSES,
        pretrained: bool = True,
        weights_path: str | None = None,
    ) -> None:
        super().__init__()
        self.num_classes = num_classes
        self.encoder = ResNet34Encoder(pretrained=pretrained, weights_path=weights_path)
        self.project = nn.Conv2d(512, BOTTLENECK_DIM, kernel_size=1)
        self.transformer = BottleneckTransformer()
        self.decoder = UnetDecoder(num_classes=num_classes)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        skips = self.encoder(x)
        c5 = skips["c5"]
        fused = self.project(c5) + self.transformer(c5)
        return cast(tuple[Tensor, Tensor, Tensor], self.decoder(fused, skips))
