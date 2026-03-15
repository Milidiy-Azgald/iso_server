from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory
import yaml, os, shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret"

DB_FILE = "database.yaml"
USERS_FILE = "users.yaml"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# обмеження на розмір файлу 20GB
app.config["MAX_CONTENT_LENGTH"] = 20*1024*1024*1024

def load_yaml(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return yaml.safe_load(f) or []

def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)

def detect_type(name):
    n = name.lower()
    if "ubuntu" in n or "debian" in n or "arch" in n:
        return "linux"
    if "windows" in n:
        return "windows"
    if "server" in n:
        return "server"
    return "pc"

def detect_arch(name):
    n = name.lower()
    return "arm" if "arm" in n else "x86"

def detect_bits(name):
    return "64" if "64" in name else "32"

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        user=request.form["user"]
        password=request.form["pass"]
        users=load_yaml(USERS_FILE)
        for u in users:
            if u["user"]==user and u["pass"]==password:
                session["user"]=user
                session["role"]=u.get("role","user")
                return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session.get("user"), role=session.get("role"))

@app.route("/file-manager")
def file_manager():
    if "user" not in session:
        return redirect("/login")
    return render_template("file_manager.html")

@app.route("/upload", methods=["POST"])
def upload():
    file=request.files.get("file")
    if not file or not file.filename.endswith(".iso"):
        return "Invalid file", 400
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)
    size=os.path.getsize(path)
    data=load_yaml(DB_FILE)
    data.append({
        "name": filename,
        "type": detect_type(filename),
        "arch": detect_arch(filename),
        "bits": detect_bits(filename),
        "size": size,
        "file": filename
    })
    save_yaml(DB_FILE, data)
    return "ok"

@app.route("/edit", methods=["POST"])
def edit():
    idx=int(request.form["index"])
    name=request.form["name"]
    data=load_yaml(DB_FILE)
    if idx>=0 and idx<len(data):
        data[idx]["name"]=name
        save_yaml(DB_FILE, data)
    return "ok"

@app.route("/delete", methods=["POST"])
def delete():
    idx=int(request.form["index"])
    data=load_yaml(DB_FILE)
    if idx>=0 and idx<len(data):
        file = data[idx]["file"]
        try:
            os.remove(os.path.join(UPLOAD_DIR, file))
        except:
            pass
        data.pop(idx)
        save_yaml(DB_FILE, data)
    return "ok"

@app.route("/list")
def list_iso():
    return jsonify(load_yaml(DB_FILE))

@app.route("/disk")
def disk():
    total, used, free = shutil.disk_usage("/")
    return jsonify({"total":total,"used":used,"free":free})

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)