#!/bin/bash
# delete_env.sh
# Uso: delete_env.sh <nome>

NAME=$1
CGROUP_PATH="/sys/fs/cgroup/$NAME"
LOG_PATH="/home/vagrant/projeto2/logs/${NAME}.log"
PID_FILE="/tmp/${NAME}.pid"

echo "===== Removendo ambiente $NAME ====="

# 1. Finaliza processo associado
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    [ -n "$PID" ] && kill -9 $PID 2>/dev/null
    rm -f "$PID_FILE"
fi

# 2. Remove cgroup
[ -d "$CGROUP_PATH" ] && rmdir "$CGROUP_PATH" 2>/dev/null || rm -rf "$CGROUP_PATH" 2>/dev/null

# 3. Remove log
[ -f "$LOG_PATH" ] && rm -f "$LOG_PATH" 2>/dev/null

echo "[+] Ambiente $NAME limpo."
echo "===== Removido ====="
