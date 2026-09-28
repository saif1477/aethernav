# Dataset guide

## Local availability

No IO-VNBD files were present in the workspace during Phase 0 inspection. The repository therefore uses only `data/sample/demo.csv`, which is synthetic and clearly labeled. No IO-VNBD columns, results, or benchmarks have been invented.

## Add IO-VNBD later

After obtaining the dataset from its official source and accepting its license/attribution terms, place a supported file under `data/raw/` without committing it:

```bash
cp /path/to/official/io-vnbd-file.csv data/raw/
python scripts/inspect_dataset.py data/raw/io-vnbd-file.csv
```

The adapter also supports JSON, JSONL, and Parquet. For a directory of files:

```bash
python scripts/inspect_dataset.py data/raw/
```

The inspector normalizes only documented aliases such as `time` to `timestamp`, `lat` to `latitude`, and `lon` to `longitude`. Unknown columns are preserved. Missing measurements are reported, not fabricated.
