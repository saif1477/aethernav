"""Optional PyTorch temporal dead-reckoning model and physics losses."""
from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    torch = None
    nn = None


def require_torch():
    if torch is None:
        raise RuntimeError("PyTorch is optional and is not installed; install a compatible CPU wheel to train the neural model")


if nn is not None:
    class TemporalDeadReckoner(nn.Module):
        """GRU predicts local-frame delta east, delta north, and yaw correction plus log variance."""
        def __init__(self, feature_dim: int = 6, hidden_dim: int = 32):
            super().__init__(); self.gru = nn.GRU(feature_dim, hidden_dim, batch_first=True); self.head = nn.Linear(hidden_dim, 6)

        def forward(self, features):
            encoded, _ = self.gru(features); return self.head(encoded[:, -1, :])
else:
    class TemporalDeadReckoner:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs): require_torch()


def physics_informed_loss(prediction, target, lateral_velocity=None, physics_weight=0.1, nonholonomic_weight=0.1):
    """Loss = robust motion loss + dynamics residual + lateral-motion penalty.

    Prediction columns are delta-east, delta-north, delta-yaw, and log variances.
    """
    require_torch(); motion = prediction[..., :3]; target = target[..., :3]
    base = torch.nn.functional.smooth_l1_loss(motion, target)
    physics = torch.mean((motion[..., 2:] - target[..., 2:]) ** 2)
    nonholonomic = torch.mean(lateral_velocity ** 2) if lateral_velocity is not None else prediction.new_tensor(0.0)
    return base + physics_weight * physics + nonholonomic_weight * nonholonomic


def uncertainty_nll(prediction, target):
    require_torch(); mean = prediction[..., :3]; log_var = prediction[..., 3:].clamp(-8, 8)
    return torch.mean(0.5 * (torch.exp(-log_var) * (mean - target[..., :3]) ** 2 + log_var))
