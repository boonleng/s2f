#!/bin/bash

if [ "${HOSTNAME}" == "tiffany" ]; then
	python3 -m notebook --no-browser --port=8081
elif [ "${HOSTNAME}" == "bumblebee.arrc.ou.edu" ]; then
	python -m notebook --no-browser --port=8080
elif [[ "${HOSTNAME}" == "schooner"* ]]; then
	module load Python/3.8.0-GCCcore-8.2.0
	module load jupyterlab/1.2.5-foss-2019a-Python-3.8.0
	module load TensorFlow/2.0.0-foss-2019a-Python-3.8.0
	python -m notebook --no-browser --port=8080
else
	python -m notebook
fi
