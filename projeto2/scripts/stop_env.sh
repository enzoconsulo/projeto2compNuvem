#!/bin/bash
# stop_env.sh
# Uso: stop_env.sh <nome>

NAME=$1
CGROUP_PATH="/sys/fs/cgroup/$NAME"
PID_FILE="/tmp/${NAME}.pid"
LOG_PATH="/home/vagrant/projeto2/logs/${NAME}.log"

echo "===== Encerrando ambiente $NAME =====" | tee -a $LOG_PATH

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "[+] Encerrando processo principal PID=$PID e toda a árvore" | tee -a "$LOG_PATH"

    # Mata toda a árvore de processos recursivamente
    PIDS=$(pstree -p $PID | grep -o '([0-9]\+)' | tr -d '()')
    if [ -n "$PIDS" ]; then
        echo "[+] Matando PIDs: $PIDS" | tee -a "$LOG_PATH"
        sudo kill -9 $PIDS 2>/dev/null
    else
        sudo kill -9 $PID 2>/dev/null
    fi

    rm -f "$PID_FILE"
else
    echo "[!] Nenhum arquivo de PID encontrado." | tee -a "$LOG_PATH"
fi

# Mata processos residuais
sudo pkill -f "$NAME" 2>/dev/null
sudo pkill -f "stress" 2>/dev/null
sudo pkill -f "unshare" 2>/dev/null

# Remove cgroup se existir
if [ -d "$CGROUP_PATH" ]; then
    echo "[+] Removendo cgroup $CGROUP_PATH" | tee -a "$LOG_PATH"
    sudo rmdir "$CGROUP_PATH" 2>/dev/null
else
    echo "[!] Nenhum cgroup encontrado para $NAME" | tee -a "$LOG_PATH"
fi

echo "[✓] Ambiente $NAME encerrado com sucesso." | tee -a "$LOG_PATH"
echo "=====================================" | tee -a "$LOG_PATH"
