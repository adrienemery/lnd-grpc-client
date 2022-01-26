#!/bin/bash

[[ -z "$1" ]] && { echo "Must enter version to upload as a parameter!!!" ; exit 1; }

app_name=lnd_grpc_client
echo "Uploading wheel version: $1"

twine upload --repository-url https://upload.pypi.org/legacy/ dist/$app_name-$1-py3-none-any.whl
