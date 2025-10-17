#!/bin/bash
# create_env.sh
# Uso: create_env.sh <nome> <cpu_limit> <mem_limit_MB> <comando> <log_path>

NAME=$1
CPU=$2
MEM=$3
CMD=$4
LOG_PATH=$5

LOG_DIR=$(dirname "$LOG_PATH")
PID_FILE="/tmp/${NAME}.pid"

mkdir -p "$LOG_DIR"

echo "===== Criando ambiente $NAME =====" | tee -a "$LOG_PATH"
echo "[+] CPU=$CPU MEM=${MEM}MB CMD=$CMD" | tee -a "$LOG_PATH"

# Caminho do cgroup
CGROUP_PATH="/sys/fs/cgroup/$NAME"
sudo mkdir -p "$CGROUP_PATH"

# Define limites de CPU e memória
# cpu.max → período=1s (1.000.000 µs), quota=CPU em microssegundos
sudo bash -c "echo '$CPU 1000000' > $CGROUP_PATH/cpu.max"
sudo bash -c "echo $(($MEM * 1024 * 1024)) > $CGROUP_PATH/memory.max"

# Executa o processo dentro do cgroup e namespace
sudo nohup unshare -p -m -n --fork --mount-proc bash -c "
    echo \$\$ | sudo tee $CGROUP_PATH/cgroup.procs
    exec $CMD
" >> "$LOG_PATH" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

echo "[+] Ambiente $NAME criado com PID $PID" | tee -a "$LOG_PATH"
echo "[+] Log: $LOG_PATH" | tee -a "$LOG_PATH"
