"""Exponential moving average of model weights (architecture spec 11 / 13).

Identical EMA policy for both the baseline and hybrid models. The EMA shadow
weights are used for validation, checkpoint selection and the saved checkpoint;
raw weights continue training.

Run inside the `ai` conda environment.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
from torch import Tensor


class EMA:
    """Maintains decayed copies of all trainable model parameters.

    ``apply_shadow`` / ``restore`` let the trainer evaluate the EMA weights on
    the validation set without losing the in-progress raw optimizer state.
    """

    def __init__(self, model: nn.Module, decay: float = 0.999) -> None:
        self.decay = decay
        self.shadow: dict[str, Tensor] = {}
        self.backup: dict[str, Tensor] = {}
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.detach().clone()

    @torch.no_grad()
    def update(self, model: nn.Module) -> None:
        for name, param in model.named_parameters():
            shadow = self.shadow.get(name)
            if shadow is not None:
                shadow.mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    @torch.no_grad()
    def apply_shadow(self, model: nn.Module) -> None:
        self.backup.clear()
        for name, param in model.named_parameters():
            shadow = self.shadow.get(name)
            if shadow is not None:
                self.backup[name] = param.detach().clone()
                param.data.copy_(shadow)

    @torch.no_grad()
    def restore(self, model: nn.Module) -> None:
        for name, param in model.named_parameters():
            original = self.backup.pop(name, None)
            if original is not None:
                param.data.copy_(original)

    def state_dict(self) -> dict[str, Any]:
        return {"decay": self.decay, "shadow": {k: v.cpu() for k, v in self.shadow.items()}}

    def load_state_dict(self, state: dict[str, Any]) -> None:
        self.decay = float(state["decay"])
        self.shadow = {k: v.clone() for k, v in state["shadow"].items()}
