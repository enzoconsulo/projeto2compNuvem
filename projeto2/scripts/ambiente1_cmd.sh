#!/bin/bash
set -e
#!/bin/bash
# test_logger.sh — imprime timestamps, simula atividade e erro
set -euo pipefail

NAME="${1:-testlogger}"
echo "=== Iniciando test_logger for $NAME ==="
for i in $(seq 1 60); do
  echo "$(date +'%Y-%m-%d %H:%M:%S') [INFO] contador=$i"
  # a cada 10 iterações escreve uma linha de erro
  if (( i % 10 == 0 )); then
    echo "$(date +'%Y-%m-%d %H:%M:%S') [ERROR] erro simulado contador=$i" >&2
  fi
  sleep 1
done

echo "=== Finalizando test_logger for $NAME ==="
exit 0
