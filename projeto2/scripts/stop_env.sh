#!/bin/bash
# stop_env.sh — encerra ambiente isolado e garante liberação da porta
# Uso: stop_env.sh <nome>

set -euo pipefail

NAME=$1
CGROUP_PATH="/sys/fs/cgroup/$NAME"
PID_FILE="/tmp/${NAME}.pid"
LOG_PATH="/home/vagrant/projeto2/logs/${NAME}.log"

{
  echo "===== Encerrando ambiente $NAME ====="
  echo "[i] Iniciado em $(date '+%Y-%m-%d %H:%M:%S')"

  if [[ -f "$PID_FILE" ]]; then
    ROOT_PID=$(cat "$PID_FILE")
    echo "[+] PID wrapper salvo: $ROOT_PID"
  else
    echo "[!] Nenhum arquivo PID encontrado."
  fi

  if [[ -d "$CGROUP_PATH" ]]; then
    echo "[i] Matando todos os processos do cgroup $CGROUP_PATH"

    # Lê todos os PIDs dentro do cgroup e mata de forma forçada
    while read -r pid; do
      if [[ -n "$pid" && -d "/proc/$pid" ]]; then
        PROC=$(basename "$(readlink /proc/$pid/exe 2>/dev/null || echo '?')")
        CMDLINE=$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null || true)
        echo "  → Matando PID $pid ($PROC $CMDLINE)"
        sudo kill -TERM "$pid" 2>/dev/null || true
        sleep 0.2
        sudo kill -KILL "$pid" 2>/dev/null || true
      fi
    done < "$CGROUP_PATH/cgroup.procs"

    sleep 0.5

    # Verifica novamente se sobrou algo
    REMAIN=$(cat "$CGROUP_PATH/cgroup.procs" 2>/dev/null | wc -l)
    if [[ "$REMAIN" -eq 0 ]]; then
      echo "[✓] Nenhum processo restante no cgroup."
    else
      echo "[!] $REMAIN processos ainda ativos — forçando remoção direta."
      while read -r pid; do
        sudo kill -9 "$pid" 2>/dev/null || true
      done < "$CGROUP_PATH/cgroup.procs"
    fi

    sudo rmdir "$CGROUP_PATH" 2>/dev/null || echo "[i] cgroup ocupado, será limpo depois."
  else
    echo "[!] Nenhum cgroup encontrado para $NAME"
  fi

  # Mata o wrapper se ainda estiver ativo
  if [[ -n "${ROOT_PID:-}" && -d "/proc/$ROOT_PID" ]]; then
    echo "[i] Matando wrapper $ROOT_PID (fora do namespace)"
    sudo kill -9 "$ROOT_PID" 2>/dev/null || true
  fi

  rm -f "$PID_FILE" 2>/dev/null || true

  echo "[✓] Ambiente $NAME completamente encerrado e porta liberada."
  echo "==============================================="
} | tee -a "$LOG_PATH"
