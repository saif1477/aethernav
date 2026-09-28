#!/usr/bin/env python
"""Run deterministic Phase 1-4 baseline evaluation and ablation bookkeeping."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aethernav.baselines.classical import (
    ekf_trajectory,
    gnss_only_trajectory,
    last_velocity_trajectory,
)
from aethernav.baselines.inertial import integrate_planar_inertial
from aethernav.coordinates.enu import wgs84_to_enu
from aethernav.datasets.io_vnbd import discover_and_load, load_file
from aethernav.datasets.validation import save_split_metadata, split_sequences, validate_frame
from aethernav.metrics.navigation import relative_pose_error, trajectory_metrics, transition_jump
from aethernav.outage.simulator import OutageConfig, simulate_gnss_outage
from aethernav.visualization.plots import save_error_plot, save_trajectory_plot

parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True); args = parser.parse_args()
root = Path(__file__).resolve().parents[1]; config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
input_path = root / config["input"]
frame = discover_and_load(input_path)[0] if input_path.is_dir() else load_file(input_path)
report = validate_frame(frame)
if report.warnings: raise ValueError(f"input validation warnings must be resolved before evaluation: {report.warnings}")
splits = split_sequences(frame, config["sequence_split"]["train_fraction"], config["sequence_split"]["validation_fraction"])
out_dir = root / config["output_dir"]; out_dir.mkdir(parents=True, exist_ok=True); save_split_metadata(splits, out_dir / "splits.json")
outage_cfg = OutageConfig(**config["outage"]); all_results = []

for sequence_id in splits["test"]:
    sequence = frame[frame.get("sequence_id", "default").astype(str) == sequence_id].copy()
    simulated = simulate_gnss_outage(sequence, outage_cfg)
    origin = (float(sequence.latitude.iloc[0]), float(sequence.longitude.iloc[0]), float(sequence.get("altitude_m", 0.0).iloc[0]))
    reference = wgs84_to_enu(sequence.latitude, sequence.longitude, sequence.get("altitude_m", 0.0), origin)
    baselines = {
        "gnss_only": gnss_only_trajectory(simulated, origin, wgs84_to_enu),
        "last_velocity": last_velocity_trajectory(simulated),
        "naive_imu": np.column_stack((integrate_planar_inertial(sequence)[:, :2], np.zeros(len(sequence)))),
        "ekf": ekf_trajectory(simulated, origin, wgs84_to_enu),
    }
    outage_mask = ~simulated.gnss_available.to_numpy(bool)
    for name, estimate in baselines.items():
        estimate = np.asarray(estimate); errors = np.linalg.norm(estimate[:, :2] - reference[:, :2], axis=1)
        state_speed = estimate[:, 2] if estimate.shape[1] > 2 else None
        metrics = trajectory_metrics(reference, estimate, sequence.timestamp.to_numpy(), sequence.speed_mps, state_speed, sequence.heading_deg, None, outage_mask)
        metrics["relative_pose_error_m"] = relative_pose_error(reference, estimate)
        metrics["outage_entry_jump_m"] = transition_jump(estimate, int(np.flatnonzero(outage_mask)[0]))
        recovery_indices = np.flatnonzero(simulated.gnss_degraded.to_numpy(bool)); metrics["recovery_entry_jump_m"] = transition_jump(estimate, int(recovery_indices[0])) if len(recovery_indices) else None
        metrics.update({"sequence_id": sequence_id, "model": name}); all_results.append(metrics)
        prefix = out_dir / f"{sequence_id}_{name}"; save_trajectory_plot(str(prefix) + "_trajectory.png", reference, estimate, sequence.timestamp.to_numpy(), outage_mask); save_error_plot(str(prefix) + "_error.png", errors, sequence.timestamp.to_numpy(), outage_mask)

if not all_results: raise ValueError("test split is empty; provide at least two sequences")
metric_keys = [k for k in all_results[0] if k not in {"sequence_id", "model"} and isinstance(all_results[0][k], (int, float))]
summary = {model: {key: float(np.mean([r[key] for r in all_results if r["model"] == model and r[key] is not None])) for key in metric_keys} for model in sorted({r["model"] for r in all_results})}
result = {"provider": "synthetic_sample" if "sample" in str(input_path) else "external_dataset", "reference_only": "sample" in str(input_path), "split": splits, "per_model_sequence": all_results, "mean_by_model": summary, "neural_ablations": {"imu_only": "not_run_torch_unavailable", "imu_magnetometer": "not_run_torch_unavailable", "physics_loss": "not_run_torch_unavailable", "no_physics_loss": "not_run_torch_unavailable"}}
(out_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
lines = ["# AetherNav baseline metrics", "", "Deterministic synthetic/reference evaluation; no neural performance is claimed.", "", "| Model | ATE RMSE (m) | Endpoint (m) | Outage ATE RMSE (m) | RPE (m) |", "|---|---:|---:|---:|---:|"]
for model, values in summary.items(): lines.append(f"| {model} | {values['ate_rmse_m']:.3f} | {values['endpoint_error_m']:.3f} | {values['outage_ate_rmse_m']:.3f} | {values['relative_pose_error_m']:.3f} |")
lines += ["", "## Sequence split", f"- Train: `{', '.join(splits['train'])}`", f"- Validation: `{', '.join(splits['validation'])}`", f"- Test: `{', '.join(splits['test'])}`", "", "## Neural ablations", "The temporal model and physics/no-physics ablations require the optional PyTorch dependency. They are recorded as not run when PyTorch is unavailable; no placeholder metrics are inserted."]
(out_dir / "metrics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2)); print(f"outputs written to {out_dir}")
