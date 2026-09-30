.PHONY: sample test inspect plot evaluate install-ml validate-onnx export parity docker-build docker-eval docker-test docker-api
sample:
	python scripts/create_sample_dataset.py --output data/sample/demo.csv
test:
	python -m pytest -q
inspect:
	python scripts/inspect_dataset.py data/sample/demo.csv
plot:
	python scripts/plot_sample.py --input data/sample/demo.csv --output artifacts/sample_trajectory.png
evaluate:
	python scripts/evaluate.py --config configs/demo.yaml
install-ml:
	python -m pip install -e '.[ml]'
validate-onnx:
	python scripts/validate_model_contract.py --model artifacts/aethernav_integration_test.onnx
export:
	python scripts/export_integration_test_model.py && python scripts/create_model_manifest.py
parity:
	python scripts/onnx_parity.py
docker-build:
	docker build -t aethernav:latest .
docker-eval:
	docker compose run --rm eval
docker-test:
	docker compose run --rm test
docker-api:
	docker compose up api

