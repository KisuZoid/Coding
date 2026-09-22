"""Controlled CNN research baseline (architecture spec v3, Section 9.1).

`ResNet34UNet` is the corrected CNN/U-Net baseline: an ImageNet-pretrained
ResNet34 encoder feeding a shared U-Net-style decoder, with deep supervision
at 128x128 and 64x64. It is the *controlled comparator* for the hybrid model
(`ml/models/hybrid_segmentation.py`); the only difference between the two is
the bottleneck Transformer + additive fusion.

The shared pieces (``ResNet34Encoder``, ``UnetDecoder``) are also used by the
hybrid so the encoder and decoder are literally the same modules and the
Transformer stays the single architectural difference.

Run inside the `ai` conda environment.
"""

from __future__ import annotations

from typing import cast

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torchvision.models import (  # type: ignore[import-untyped]  # type: ignore[import-untyped]
    ResNet34_Weights,
    resnet34,
)

NUM_CLASSES = 7
BOTTLENECK_DIM = 256
ENCODER_SKIP_CHANNELS = {"s0": 64, "c2": 64, "c3": 128, "c4": 256}


class ResNet34Encoder(nn.Module):
    """ImageNet-pretrained ResNet34 feature extractor (locked in the spec).

    Exposes the locked feature hierarchy:

        s0 -> [B, 64, 256, 256]   (relu output, pre-maxpool)
        c2 -> [B, 64, 128, 128]
        c3 -> [B, 128, 64, 64]
        c4 -> [B, 256, 32, 32]
        c5 -> [B, 512, 16, 16]

    ``weights_path`` (a local resnet34 state dict) overrides automatic weight
    download when provided.
    """

    def __init__(self, pretrained: bool = True, weights_path: str | None = None) -> None:
        super().__init__()
        if weights_path is not None:
            base = resnet34(weights=None)
            state = torch.load(weights_path, map_location="cpu", weights_only=True)
            base.load_state_dict(cast(dict[str, Tensor], state))
        elif pretrained:
            base = resnet34(weights=ResNet34_Weights.IMAGENET1K_V1)
        else:
            base = resnet34(weights=None)
        self.backbone = base
        self.feature_channels = ENCODER_SKIP_CHANNELS

    def forward(self, x: Tensor) -> dict[str, Tensor]:
        h = self.backbone.conv1(x)
        h = self.backbone.bn1(h)
        h = self.backbone.relu(h)
        s0 = h
        h = self.backbone.maxpool(h)
        c2: Tensor = self.backbone.layer1(h)
        c3: Tensor = self.backbone.layer2(c2)
        c4: Tensor = self.backbone.layer3(c3)
        c5: Tensor = self.backbone.layer4(c4)
        return {"s0": s0, "c2": c2, "c3": c3, "c4": c4, "c5": c5}


class _ConvBlock(nn.Module):
    """(conv3x3 -> BN -> ReLU) x2 used as the decoder refinement block."""

    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: Tensor) -> Tensor:
        return cast(Tensor, self.block(x))


def _upsample2(x: Tensor) -> Tensor:
    """Bilinear 2x upsampling (locked decoder mechanism)."""
    return cast(Tensor, F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False))


class UnetDecoder(nn.Module):
    """U-Net-style decoder with bilinear upsampling and channel refinement.

    Channel progression (locked in the spec):

        16x16 -> 256
        32x32 -> 256
        64x64 -> 128
        128x128 -> 64
        256x256 -> 64
        512x512 -> 32
        head -> num_classes

    Returns ``(main_logits, aux1_logits, aux2_logits)`` where the auxiliary
    heads are attached at 128x128 and 64x64 (deep supervision, Section 8).
    """

    def __init__(self, num_classes: int = NUM_CLASSES) -> None:
        super().__init__()
        self.num_classes = num_classes
        self.conv1 = _ConvBlock(BOTTLENECK_DIM + ENCODER_SKIP_CHANNELS["c4"], BOTTLENECK_DIM)
        self.conv2 = _ConvBlock(BOTTLENECK_DIM + ENCODER_SKIP_CHANNELS["c3"], 128)
        self.conv3 = _ConvBlock(128 + ENCODER_SKIP_CHANNELS["c2"], 64)
        self.conv4 = _ConvBlock(64 + ENCODER_SKIP_CHANNELS["s0"], 64)
        self.conv5 = _ConvBlock(64, 32)
        self.head_main = nn.Conv2d(32, self.num_classes, kernel_size=1)
        self.head_aux1 = nn.Conv2d(64, self.num_classes, kernel_size=1)
        self.head_aux2 = nn.Conv2d(128, self.num_classes, kernel_size=1)

    def forward(self, fused: Tensor, skips: dict[str, Tensor]) -> tuple[Tensor, Tensor, Tensor]:
        x = _upsample2(fused)
        x = torch.cat([x, skips["c4"]], dim=1)
        x = cast(Tensor, self.conv1(x))

        x = _upsample2(x)
        x = torch.cat([x, skips["c3"]], dim=1)
        x = cast(Tensor, self.conv2(x))
        aux2_feat = x

        x = _upsample2(x)
        x = torch.cat([x, skips["c2"]], dim=1)
        x = cast(Tensor, self.conv3(x))
        aux1_feat = x

        x = _upsample2(x)
        x = torch.cat([x, skips["s0"]], dim=1)
        x = cast(Tensor, self.conv4(x))

        x = _upsample2(x)
        x = cast(Tensor, self.conv5(x))

        main_logits = self.head_main(x)
        aux1_logits = self.head_aux1(aux1_feat)
        aux2_logits = self.head_aux2(aux2_feat)
        return main_logits, aux1_logits, aux2_logits


class ResNet34UNet(nn.Module):
    """Controlled CNN baseline: ResNet34 encoder + shared U-Net decoder.

    Bottleneck is a plain 1x1 projection of C5 to 256 channels. Forward
    returns ``(main_logits, aux1_logits, aux2_logits)`` so the baseline and
    hybrid share the identical training/evaluation contract.
    """

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
        self.decoder = UnetDecoder(num_classes=num_classes)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        skips = self.encoder(x)
        fused = self.project(skips["c5"])
        return cast(tuple[Tensor, Tensor, Tensor], self.decoder(fused, skips))
