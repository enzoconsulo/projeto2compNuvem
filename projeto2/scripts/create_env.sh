set -euo pipefail

NAME="$1"
CPU="$2"
MEM="$3"
shift 3
LOG_PATH="${@: -1}"
CMD="${*:1:$(($#-1))}"

LOG_DIR=$(dirname "$LOG_PATH")
PID_FILE="/tmp/${NAME}.pid"
CGROUP_PATH="/sys/fs/cgroup/$NAME"

mkdir -p "$LOG_DIR"
sudo mkdir -p "$CGROUP_PATH"

echo "===== Criando ambiente $NAME =====" | tee -a "$LOG_PATH"
echo "[+] CPU=$CPU MEM=${MEM}MB CMD=$CMD" | tee -a "$LOG_PATH"
echo "[i] $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_PATH"

echo "$CPU 1000000" | sudo tee "$CGROUP_PATH/cpu.max" >/dev/null
echo $(($MEM * 1024 * 1024)) | sudo tee "$CGROUP_PATH/memory.max" >/dev/null

(
  bash -c "
    echo \$\$ > '$PID_FILE'
    echo \$\$ | sudo tee '$CGROUP_PATH/cgroup.procs' >/dev/null
    echo '[i] Executando comando dentro do namespace...' >> '$LOG_PATH'
    $CMD >> '$LOG_PATH' 2>&1
    echo '[✓] Comando finalizado.' >> '$LOG_PATH'
  "
) &

PID=$!
echo "[+] Ambiente $NAME iniciado com PID $PID" | tee -a "$LOG_PATH"
echo "[+] Log: $LOG_PATH" | tee -a "$LOG_PATH"
echo "============================================" | tee -a "$LOG_PATH"

exit 0
