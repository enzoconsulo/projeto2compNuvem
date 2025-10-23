from flask import Flask, render_template, request, redirect, url_for, abort
from markupsafe import escape
import subprocess, os, sqlite3, datetime, logging

app = Flask(__name__)

DB_PATH = "/home/vagrant/projeto2/database.db"
LOG_DIR = "/home/vagrant/projeto2/logs"
SCRIPT_DIR = "/home/vagrant/projeto2/scripts"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCRIPT_DIR, exist_ok=True)

# Inicializa banco
conn = sqlite3.connect(DB_PATH)
conn.execute('''CREATE TABLE IF NOT EXISTS envs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              cpu TEXT,
              mem TEXT,
              status TEXT,
              created_at TEXT,
              log_path TEXT)''')
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    cpu = request.form['cpu']
    mem = request.form['mem']
    command = request.form['command']
    log_path = f"{LOG_DIR}/{name}.log"

    # Chama script bash para criar ambiente
    subprocess.run(["bash", f"{SCRIPT_DIR}/create_env.sh", name, cpu, mem, command, log_path])

    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO envs (name, cpu, mem, status, created_at, log_path) VALUES (?, ?, ?, ?, ?, ?)",
                 (name, cpu, mem, 'executando', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), log_path))
    conn.commit()
    conn.close()
    return redirect(url_for('list_envs'))

@app.route('/list')
def list_envs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM envs")
    rows = cur.fetchall()
    conn.close()

    try:
        top_output = subprocess.check_output(["/usr/bin/ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"], text=True)

    except Exception as e:
        top_output = f"Erro ao executar ps: {e}"

    return render_template('list.html', envs=rows, top_output=top_output)


@app.route('/stop/<env_name>')
def stop_env(env_name):
    subprocess.run(["bash", f"{SCRIPT_DIR}/stop_env.sh", env_name])
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE envs SET status=? WHERE name=?", ("finalizado", env_name))
    conn.commit()
    conn.close()
    return redirect(url_for('list_envs'))

@app.route('/log/<env_name>')
def view_log(env_name):
    log_path = f"{LOG_DIR}/{env_name}.log"
    if os.path.exists(log_path):
        with open(log_path) as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    else:
        return "Log não encontrado."
    
@app.route('/restart/<env_name>')
def restart_env(env_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, cpu, mem, log_path FROM envs WHERE name=?", (env_name,))
    env = cur.fetchone()
    conn.close()

    if not env:
        return f"Ambiente {env_name} não encontrado."

    name, cpu, mem, log_path = env
    command = "stress --cpu 1"

    subprocess.run(["bash", f"{SCRIPT_DIR}/create_env.sh", name, cpu, mem, command, log_path])

    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE envs SET status=? WHERE name=?", ("reiniciado", env_name))
    conn.commit()
    conn.close()

    return redirect(url_for('list_envs'))

@app.route('/delete/<env_name>')
def delete_env(env_name):
    import sqlite3
    import os

    conn = sqlite3.connect('envs.db')
    cursor = conn.cursor()

    # Exclui o ambiente do banco
    cursor.execute("DELETE FROM envs WHERE name = ?", (env_name,))
    conn.commit()
    conn.close()

    # Remove possíveis logs associados
    log_path = f'logs/{env_name}.log'
    if os.path.exists(log_path):
        os.remove(log_path)

    return redirect(url_for('list_envs'))

@app.route('/top')
def get_top():
    try:
        out = subprocess.check_output(["/usr/bin/ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"], text=True)
        # só as 20 primeiras linhas (cabeçalho + top 19)
        out = "\n".join(out.splitlines()[:20])
    except Exception as e:
        out = f"Erro ao executar ps: {e}"
    return f"<pre>{out}</pre>"
