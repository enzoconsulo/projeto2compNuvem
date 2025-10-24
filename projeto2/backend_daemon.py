from flask import Flask, request
import subprocess, os

app = Flask(__name__)
BASE_DIR   = "/home/vagrant/projeto2"
SCRIPTS_DIR= os.path.join(BASE_DIR, "scripts")

@app.route("/create_env", methods=["POST"])
def create_env():
    name = request.form["name"]
    cpu  = request.form["cpu"]
    mem  = request.form["mem"]
    cmd  = request.form["cmd"]
    log  = request.form["log"]

    subprocess.Popen(
        ["bash", f"{SCRIPTS_DIR}/create_env.sh", name, cpu, mem, cmd, log],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return "OK", 200

@app.route("/stop_env", methods=["POST"])
def stop_env():
    name = request.form["name"]
    subprocess.Popen(
        ["bash", f"{SCRIPTS_DIR}/stop_env.sh", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return "OK", 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9001)
