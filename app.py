import os
import subprocess
from flask import Flask, render_template, jsonify, request
import json
import config

app = Flask(__name__)

# Tentukan path ke skrip dan file konfigurasi
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_EXTRACTOR_SCRIPT = os.path.join(PROJECT_DIR, 'TextEXtractor.py')
LISTER_SCRIPT = os.path.join(PROJECT_DIR, 'NamesExtractor.py')
NAME_OUTPUT_FILE = os.path.join(PROJECT_DIR, 'OutputAllNames.txt')
OUTPUT_FILE = os.path.join(PROJECT_DIR, 'output.txt')
EXCLUDE_FILE_PATH = os.path.join(PROJECT_DIR, 'exclude_me.txt')

# Route utama untuk menampilkan halaman HTML
@app.route('/')
def index():
    return render_template('Tree.html')

# Route baru untuk mengatur path project
@app.route('/set_path', methods=['POST'])
def set_project_path():
    data = request.json
    new_path = data.get('path')
    if new_path and os.path.isdir(new_path):
        config.TARGET_FOLDER = new_path
        return jsonify({'success': True, 'message': f'Path berhasil diatur ke {new_path}'})
    return jsonify({'success': False, 'error': 'Path tidak valid atau tidak ditemukan.'}), 400

# Route untuk menjalankan skrip NamesExtractor.py
@app.route('/run_nameextractor', methods=['POST'])
def run_nameextractor():
    try:
        data = request.json
        include_files = data.get('include_files', True)
        include_size = data.get('include_size', False)
        
        # Jalankan skrip NamesExtractor.py dengan argumen
        process = subprocess.run(
            ['python', LISTER_SCRIPT, 
             '--include-files', str(include_files), 
             '--include-size', str(include_size)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        
        # Baca output.txt setelah skrip dijalankan
        with open(NAME_OUTPUT_FILE, 'r', encoding='utf-8') as f:
            output_content = f.read()

        return jsonify({'success': True, 'output': output_content})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except FileNotFoundError:
        return jsonify({'success': False, 'error': f"Skrip '{LISTER_SCRIPT}' tidak ditemukan."}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route untuk menjalankan skrip TextEXtractor.py
@app.route('/run_textextractor', methods=['POST'])
def run_extractor():
    try:
        # Jalankan skrip TextEXtractor.py
        process = subprocess.run(
            ['python', TEXT_EXTRACTOR_SCRIPT], 
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        
        # Baca output.txt setelah skrip dijalankan
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            output_content = f.read()

        return jsonify({'success': True, 'output': output_content})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except FileNotFoundError:
        return jsonify({'success': False, 'error': f"Skrip '{TEXT_EXTRACTOR_SCRIPT}' tidak ditemukan."}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route untuk mengelola file pengecualian
@app.route('/manage_exclude_file', methods=['GET', 'POST'])
def manage_exclude_file():
    if request.method == 'GET':
        # Baca konten file exclude_me.txt dan kirimkan
        try:
            with open(EXCLUDE_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'content': content})
        except FileNotFoundError:
            return jsonify({'success': False, 'error': 'File exclude_me.txt tidak ditemukan.'}), 500
    
    elif request.method == 'POST':
        # Simpan konten baru ke file exclude_me.txt
        data = request.json
        new_content = data.get('content')
        if new_content is not None:
            try:
                with open(EXCLUDE_FILE_PATH, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return jsonify({'success': True, 'message': 'File pengecualian berhasil disimpan.'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Konten tidak valid'}), 400

if __name__ == '__main__':
    app.run(debug=True)