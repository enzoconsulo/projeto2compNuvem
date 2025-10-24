#!/bin/bash
set -e
echo "Iniciando relógio digital..."
while true
do
  echo "🕒 $(date '+%H:%M:%S')"
  echo "Data: $(date '+%d/%m/%Y')"
  echo "----------------------------------"
  sleep 1
done
