import os, sqlite3, datetime, traceback, zipfile, unicodedata, re, subprocess
from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

BASE_DIR = "/home/vagrant/projeto2"
DB_PATH  = os.path.join(BASE_DIR, "database.db")
LOG_DIR  = os.path.join(BASE_DIR, "logs")
SCRIPT_DIR = os.path.join(BASE_DIR, "scripts")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCRIPT_DIR, exist_ok=True)

def safe_filename(name):
    nfkd = unicodedata.normalize("NFKD", name)
    safe = "".join([c for c in nfkd if not unicodedata.combining(c)])
    safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", safe)
    return safe

def db_init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS envs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE,
      cpu TEXT,
      mem TEXT,
      status TEXT,
      created_at TEXT,
      log_path TEXT,
      command TEXT
    )
    """)
    conn.commit()
    conn.close()

def db_execute(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(sql, params)
    conn.commit()
    conn.close()

db_init()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create():
    try:
        name = request.form["name"].strip()
        cpu  = request.form["cpu"].strip()
        mem  = request.form["mem"].strip()
        log_path = f"{LOG_DIR}/{name}.log"

        script_file = request.files.get("script_file")

        if script_file and script_file.filename:
            filename = safe_filename(script_file.filename)
            name_s = safe_filename(name)
            script_path = os.path.join(SCRIPT_DIR, f"{name_s}_{filename}")
            script_file.save(script_path)

            if filename.lower().endswith(".zip"):
                extract_dir = os.path.join(SCRIPT_DIR, f"{name_s}_site")
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(script_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
                port = "9005"
                command = f"python3 -m http.server {port} --directory {extract_dir}"
            else:
                os.chmod(script_path, 0o755)
                command = f"bash {script_path}"

        else:
            command_raw = request.form.get("command", "").strip()
            command_raw = command_raw.replace("\r", "")

            script_path = os.path.join(SCRIPT_DIR, f"{safe_filename(name)}_cmd.sh")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("#!/bin/bash\nset -e\n")
                f.write(command_raw + "\n")
            os.chmod(script_path, 0o755)
            command = f"bash {script_path}"
            
        r = requests.post("http://127.0.0.1:9001/create_env", data={
            "name": name, "cpu": cpu, "mem": mem, "cmd": command, "log": log_path
        })
        if r.status_code != 200:
            raise Exception(f"Erro do daemon: {r.text}")

        db_execute("""
            INSERT OR REPLACE INTO envs (name, cpu, mem, status, created_at, log_path, command)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, cpu, mem, "executando",
              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              log_path, command))

        return redirect(url_for("list_envs"))

    except Exception:
        return f"<h3>Erro ao criar ambiente:</h3><pre>{traceback.format_exc()}</pre>"

@app.route("/list")
def list_envs():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT * FROM envs ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("list.html", envs=rows)

@app.route("/log/<env_name>")
def view_log(env_name):
    log_path = f"{LOG_DIR}/{env_name}.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            return f"<pre>{f.read()}</pre>"
    return "Log não encontrado."

@app.route('/top')
def get_top():
    try:
        import html
        out = subprocess.check_output(
            ["ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"],
            text=True, encoding="utf-8", errors="replace"
        )
        linhas = out.strip().split("\n")
        header = linhas[0]
        body = "\n".join(linhas[1:80])
        safe_body = html.escape(f"{header}\n{body}")
        html_output = f"""
        <div style="max-height:420px;overflow-y:auto;
                    background:#111;color:#00ff99;
                    font-family:monospace;border-radius:8px;
                    padding:10px;border:1px solid #333;">
            <pre>{safe_body}</pre>
        </div>
        """
        return html_output
    except subprocess.CalledProcessError as e:
        return f"<pre>Erro ao executar ps: {e}</pre>", 500
    except Exception as e:
        return f"<pre>Erro inesperado: {str(e)}</pre>", 500

@app.route("/stop/<env_name>")
def stop_env(env_name):
    try:
        requests.post("http://127.0.0.1:9001/stop_env", data={"name": env_name})
        db_execute("UPDATE envs SET status=? WHERE name=?", ("finalizado", env_name))
        return redirect(url_for("list_envs"))
    except Exception:
        return f"<h3>Erro ao encerrar:</h3><pre>{traceback.format_exc()}</pre>"

@app.route("/restart/<env_name>")
def restart_env(env_name):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT name,cpu,mem,command,log_path FROM envs WHERE name=?", (env_name,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return f"Ambiente {env_name} não encontrado."

    name, cpu, mem, command, log_path = row
    r = requests.post("http://127.0.0.1:9001/create_env", data={
        "name": name, "cpu": cpu, "mem": mem, "cmd": command, "log": log_path
    })
    if r.status_code != 200:
        return f"Erro do daemon: {r.text}"

    db_execute("UPDATE envs SET status=? WHERE name=?", ("reiniciado", env_name))
    return redirect(url_for("list_envs"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
