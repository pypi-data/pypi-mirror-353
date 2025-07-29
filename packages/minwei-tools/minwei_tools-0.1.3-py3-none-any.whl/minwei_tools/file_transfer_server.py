import os
import zipfile
import io
from flask import Flask, send_file, render_template_string, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.abspath(".")

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Transfer Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h2>📁 File Transfer Server</h2>
    <form id="downloadForm" method="POST" action="/download_zip">
        <ul class="list-group mt-3">
            {% for f in files %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {% if f['is_dir'] %}
                    <a href="/?path={{ current_path }}/{{ f['name'] }}">📂 {{ f['name'] }}</a>
                {% else %}
                    <span>📄 {{ f['name'] }}</span>
                    <div>
                        <a href="/download?path={{ current_path }}/{{ f['name'] }}" class="btn btn-sm btn-primary">Download</a>
                        <input type="checkbox" name="files" value="{{ current_path }}/{{ f['name'] }}">
                    </div>
                {% endif %}
            </li>
            {% endfor %}
        </ul>
        <button type="submit" class="btn btn-success mt-3">Download Selected</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    rel_path = request.args.get("path", "").strip("/")
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return "Path not found", 404

    items = []
    for entry in os.scandir(abs_path):
        items.append({"name": entry.name, "is_dir": entry.is_dir()})

    return render_template_string(TEMPLATE, files=items, current_path=rel_path)

@app.route("/download", methods=["GET"])
def download_file():
    rel_path = request.args.get("path", "").strip("/")
    abs_path = os.path.join(BASE_DIR, rel_path)

    if not os.path.isfile(abs_path):
        return "File not found", 404

    return send_file(abs_path, as_attachment=True)

@app.route("/download_zip", methods=["POST"])
def download_zip():
    file_paths = request.form.getlist("files")
    if not file_paths:
        return "No files selected", 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for rel_path in file_paths:
            abs_path = os.path.join(BASE_DIR, rel_path)
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                zipf.write(abs_path, arcname=os.path.basename(abs_path))

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="files.zip")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)