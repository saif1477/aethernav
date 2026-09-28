"""Evaluation plots."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def save_trajectory_plot(path, reference, estimate, timestamps, outage_mask=None):
    fig, ax = plt.subplots(figsize=(9, 6)); ax.plot(reference[:, 0], reference[:, 1], label="reference", lw=2)
    ax.plot(estimate[:, 0], estimate[:, 1], label="naive inertial", lw=1.5)
    if outage_mask is not None and np.any(outage_mask):
        ax.scatter(reference[outage_mask, 0], reference[outage_mask, 1], s=8, label="GNSS outage", color="tab:red")
    ax.set(xlabel="East (m)", ylabel="North (m)", title="AetherNav trajectory evaluation"); ax.axis("equal"); ax.grid(alpha=.25); ax.legend()
    Path(path).parent.mkdir(parents=True, exist_ok=True); fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def save_error_plot(path, errors, timestamps, outage_mask=None):
    fig, ax = plt.subplots(figsize=(9, 4)); ax.plot(timestamps, errors, label="horizontal error", color="tab:orange")
    if outage_mask is not None and np.any(outage_mask):
        ax.fill_between(timestamps, 0, errors.max(), where=outage_mask, alpha=.15, color="tab:red", label="GNSS outage")
    ax.set(xlabel="Time (s)", ylabel="Error (m)", title="Position error over time"); ax.grid(alpha=.25); ax.legend()
    Path(path).parent.mkdir(parents=True, exist_ok=True); fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
