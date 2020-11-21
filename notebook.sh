#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="/Users/boonleng/Downloads/bitcoin-analytics-00278a2332d3.json"

if [ "${HOSTNAME}" == "tiffany" ]; then
	python3 -m notebook --no-browser --port=8081
else
	python -m notebook
fi
