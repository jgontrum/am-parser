#!/bin/bash

mkdir -p external_data
cp download.sh external_data/
cd external_data && ./download.sh && rm ./download.sh && cd /app

if [ -d /app/external_data/bert ]; then
  rm -rf /root/.pytorch_pretrained_bert/ 2>/dev/null
  ln -s /app/external_data/bert /root/.pytorch_pretrained_bert
fi
