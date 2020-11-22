#!/bin/bash

auth_file="${HOME}/Downloads/bitcoin-analytics-00278a2332d3.json"
if [ -f ${auth_file} ]; then
	export GOOGLE_APPLICATION_CREDENTIALS=${auth_file}
fi

if [ "${HOSTNAME}" == "tiffany" ]; then
	python3 -m notebook --no-browser --port=8081
else
	python -m notebook
fi
