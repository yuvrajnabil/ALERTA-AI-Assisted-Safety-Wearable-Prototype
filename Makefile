PYTHON ?= python3

.PHONY: data train test model-smoke all

all: data train test model-smoke

data:
	$(PYTHON) ml/generate_synthetic_data.py --rows 6000 --subjects 80 --seed 42 --output data/alerta_synthetic_v1.csv

train:
	$(PYTHON) ml/train_models.py --data data/alerta_synthetic_v1.csv --outdir artifacts --header include/generated_models.h --seed 42

test:
	$(PYTHON) -m unittest discover -s ml/tests -v

model-smoke:
	g++ -std=c++17 -Wall -Wextra -Werror -Iinclude ml/tests/generated_header_smoke.cpp -o /tmp/alerta-model-smoke
	/tmp/alerta-model-smoke

