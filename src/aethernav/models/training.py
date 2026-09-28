"""Optional, reproducible temporal-model training utilities."""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np

from .temporal import TemporalDeadReckoner, physics_informed_loss, require_torch, uncertainty_nll


def make_windows(frame, reference_enu, window=20, use_magnetometer=False):
    """Create IMU windows and local ENU motion-increment targets."""
    features = [
        "accelerometer_x", "accelerometer_y", "accelerometer_z",
        "gyroscope_x", "gyroscope_y", "gyroscope_z",
    ]
    if use_magnetometer:
        features += ["magnetometer_x", "magnetometer_y", "magnetometer_z"]
    available = [name for name in features if name in frame]
    if len(available) < 6:
        raise ValueError("at least six IMU features are required")
    values = np.nan_to_num(frame[available].to_numpy(float), nan=0.0)
    targets = np.diff(reference_enu[:, :2], axis=0, prepend=reference_enu[:1, :2])
    yaw = np.zeros((len(frame), 1))
    if "heading_deg" in frame:
        yaw[:, 0] = np.radians(np.unwrap(np.radians(frame.heading_deg.fillna(0).to_numpy(float))))
    target = np.concatenate((targets, yaw), axis=1)
    xs, ys = [], []
    for end in range(window, len(frame)):
        xs.append(values[end - window:end])
        ys.append(target[end])
    return np.asarray(xs, dtype=np.float32), np.asarray(ys, dtype=np.float32)


def train_model(x, y, output, epochs=10, physics=False, seed=2026, use_magnetometer=False):
    """Train and checkpoint the temporal model. Requires PyTorch at runtime."""
    require_torch()
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    model = TemporalDeadReckoner(feature_dim=x.shape[-1])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    xt, yt = torch.from_numpy(x), torch.from_numpy(y)
    history = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        prediction = model(xt)
        loss = physics_informed_loss(
            prediction, yt,
            physics_weight=0.1 if physics else 0.0,
            nonholonomic_weight=0.1 if physics else 0.0,
        )
        loss = loss + 0.1 * uncertainty_nll(prediction, yt)
        loss.backward()
        optimizer.step()
        history.append({"epoch": epoch + 1, "loss": float(loss.detach())})
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model_state": model.state_dict(),
        "feature_dim": x.shape[-1],
        "use_magnetometer": use_magnetometer,
        "physics_loss": physics,
        "seed": seed,
        "history": history,
    }, output)
    return history
