import os
import subprocess
from threading import Timer
import webbrowser
from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, 'config.json')

# Fungsi load & save config
def load_config():
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

config_data = load_config()

# Tentukan path ke skrip
TEXT_EXTRACTOR_SCRIPT = os.path.join(PROJECT_DIR, 'TextEXtractor.py')
LISTER_SCRIPT = os.path.join(PROJECT_DIR, 'NamesExtractor.py')

# Route utama
@app.route('/')
def index():
    return render_template('Tree.html')

# Route untuk set path baru
@app.route('/set_path', methods=['POST'])
def set_project_path():
    data = request.json
    new_path = data.get('path')
    print(f"Path yang diterima: '{new_path}'")
    if new_path and os.path.isdir(new_path):
        try:
            config_data["TARGET_FOLDER"] = new_path
            save_config(config_data)
            return jsonify({'success': True, 'message': 'Path berhasil diatur dan disimpan ke config.json.'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Gagal menulis ke config.json: {str(e)}'}), 500
    return jsonify({'success': False, 'error': 'Path tidak valid atau tidak ditemukan.'}), 400

# Jalankan NamesExtractor
@app.route('/run_nameextractor', methods=['POST'])
def run_nameextractor():
    try:
        data = request.json
        include_files = data.get('include_files', True)
        include_size = data.get('include_size', False)

        process = subprocess.run(
            ['python', LISTER_SCRIPT,
             '--include-files', str(include_files),
             '--include-size', str(include_size)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )

        with open(os.path.join(PROJECT_DIR, config_data["NAME_OUTPUT_FILE"]), 'r', encoding='utf-8') as f:
            output_content = f.read()

        return jsonify({'success': True, 'output': output_content})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except FileNotFoundError:
        return jsonify({'success': False, 'error': f"Skrip '{LISTER_SCRIPT}' tidak ditemukan."}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Jalankan TextEXtractor
@app.route('/run_textextractor', methods=['POST'])
def run_extractor():
    try:
        process = subprocess.run(
            ['python', TEXT_EXTRACTOR_SCRIPT],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )

        with open(os.path.join(PROJECT_DIR, config_data["OUTPUT_FILE"]), 'r', encoding='utf-8') as f:
            output_content = f.read()

        return jsonify({'success': True, 'output': output_content})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except FileNotFoundError:
        return jsonify({'success': False, 'error': f"Skrip '{TEXT_EXTRACTOR_SCRIPT}' tidak ditemukan."}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Kelola exclude_me.txt
@app.route('/manage_exclude_file', methods=['GET', 'POST'])
def manage_exclude_file():
    exclude_path = os.path.join(PROJECT_DIR, config_data["EXCLUDE_FILE_PATH"])

    if request.method == 'GET':
        try:
            with open(exclude_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'content': content})
        except FileNotFoundError:
            return jsonify({'success': False, 'error': 'File exclude_me.txt tidak ditemukan.'}), 500

    elif request.method == 'POST':
        data = request.json
        new_content = data.get('content')
        if new_content is not None:
            try:
                with open(exclude_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return jsonify({'success': True, 'message': 'File pengecualian berhasil disimpan.'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Konten tidak valid'}), 400

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" and not getattr(app, "browser_opened", False):
        Timer(1, open_browser).start()
        app.browser_opened = True

    app.run(debug=True)
