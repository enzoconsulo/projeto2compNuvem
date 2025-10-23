#!/bin/bash
# delete_env.sh
# Uso: delete_env.sh <nome>

NAME=$1
CGROUP_PATH="/sys/fs/cgroup/$NAME"
LOG_PATH="/home/vagrant/projeto2/logs/${NAME}.log"
PID_FILE="/tmp/${NAME}.pid"

echo "===== Removendo ambiente $NAME ====="

# 1. Remove os cgroups (necessário para limpeza total dos recursos)
if [ -d "$CGROUP_PATH" ]; then
    echo "[+] Removendo cgroup: $CGROUP_PATH"
    sudo rmdir "$CGROUP_PATH" || sudo rm -rf "$CGROUP_PATH"
fi

# 2. Remove o arquivo de PID (se existir)
if [ -f "$PID_FILE" ]; then
    echo "[+] Removendo arquivo PID: $PID_FILE"
    rm -f "$PID_FILE"
fi

# 3. Remove o arquivo de log
if [ -f "$LOG_PATH" ]; then
    echo "[+] Removendo arquivo de Log: $LOG_PATH"
    rm -f "$LOG_PATH"
fi

echo "[+] Ambiente $NAME limpo do sistema."
