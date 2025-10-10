import os
import sys
import subprocess
from threading import Timer
import webbrowser
from flask import Flask, render_template, jsonify, request, Response
import json

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(PROJECT_DIR, 'config.json')

def load_config():
    # default aman untuk repo baru
    default_cfg = {
        "TARGET_FOLDER": "",
        "NAME_OUTPUT_FILE": "OutputAllNames.txt",
        "OUTPUT_FILE": "",                 # kosong = belum diset
        "EXCLUDE_FILE_PATH": "exclude_me.txt"
    }
    if not os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_cfg, f, indent=4)
        return default_cfg
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    for k, v in default_cfg.items():
        cfg.setdefault(k, v)
    return cfg


def save_config(data):
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def _needs_output_destination(cfg, override_dir=None, override_name=None):
    """Return (needs_pick: bool, reason: str, suggested_name: str)."""
    if override_dir or override_name:
        return (False, "", "")
    out_file = (cfg.get("OUTPUT_FILE") or "").strip()
    if not out_file:
        return (True, "OUTPUT_FILE kosong", "Output.txt")
    out_dir = os.path.dirname(out_file) or PROJECT_DIR
    if not os.path.isdir(out_dir):
        return (True, f"Folder output belum ada: {out_dir}", os.path.basename(out_file) or "Output.txt")
    try:
        test_path = os.path.join(out_dir, ".cd_probe_write")
        with open(test_path, "w", encoding="utf-8") as _f: _f.write("ok")
        os.remove(test_path)
    except Exception:
        return (True, f"Folder output tidak dapat ditulis: {out_dir}", os.path.basename(out_file) or "Output.txt")
    return (False, "", "")

def _remove_blank_lines_inplace(file_path: str):
    """Hapus baris kosong/whitespace-only dari file, in-place."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        # buang baris yang kosong (setelah strip)
        cleaned = [ln for ln in lines if ln.strip()]
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.writelines(cleaned)
        return True, len(lines) - len(cleaned)
    except Exception as e:
        return False, str(e)
# app.py

# ... (setelah save_config) ...

def get_config_value(key, default=None):
    return config_data.get(key, default)

def sync_gitignore_to_exclude(target_folder, exclude_file_path):
    """Membaca .gitignore di TARGET_FOLDER dan menggabungkannya ke exclude_me.txt."""
    gitignore_path = os.path.join(target_folder, '.gitignore')
    
    if not os.path.exists(gitignore_path):
        return False # Tidak ada .gitignore
        
    try:
        # 1. Baca pola dari .gitignore
        with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
            gitignore_lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

        # 2. Baca pola dari exclude_me.txt yang sudah ada
        existing_exclude_lines = []
        if os.path.exists(exclude_file_path):
            with open(exclude_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                existing_exclude_lines = [line.strip() for line in f if line.strip()]

        # 3. Gabungkan dan hapus duplikat (menggunakan set)
        combined_set = set(existing_exclude_lines)
        
        # Tambahkan pola dari .gitignore sebagai komentar di exclude_me.txt agar mudah dibedakan
        # Kita tambahkan semua polanya langsung, tapi di .gitignore_lines kita tambahkan header/separator agar jelas
        
        # Pisahkan pola yang sudah ada di exclude_me.txt agar tidak terduplikasi
        new_gitignore_patterns = [p for p in gitignore_lines if p not in combined_set]

        if not new_gitignore_patterns:
            return True # Tidak ada pola baru yang perlu digabungkan

        # Tambahkan ke set untuk penyimpanan
        for p in new_gitignore_patterns:
            combined_set.add(p)

        # 4. Simpan kembali ke exclude_file_path
        # Format: Pola yang sudah ada + separator + Pola baru dari .gitignore
        
        header = "\n\n# === POLA DARI .gitignore ===\n# Pola di bawah ini otomatis disinkronkan saat Set Path.\n"
        
        # Baca konten exclude_me.txt yang lama (jika ada)
        old_content = ""
        if os.path.exists(exclude_file_path):
             with open(exclude_file_path, 'r', encoding='utf-8') as f:
                old_content = f.read().strip()
                
        # Pola yang baru ditambahkan
        new_content = "\n".join(new_gitignore_patterns)

        # Cek apakah bagian .gitignore sudah ada sebelumnya
        if "# === POLA DARI .gitignore ===" in old_content:
             # Jika sudah ada, cari dan timpa hanya bagian gitignore-nya (agar manual exclude tidak hilang)
             import re
             # Pola regex untuk mencari dan mengganti konten di antara dua separator
             pattern = r'(# === POLA DARI \.gitignore ===[\s\S]*?)(?=\n\n|\Z)'
             
             # Coba cari dan ganti, jika tidak ketemu, append
             if re.search(pattern, old_content):
                final_content = re.sub(pattern, header + new_content, old_content).strip() + "\n"
             else:
                final_content = old_content + header + new_content + "\n"

        else:
             # Jika belum ada, langsung append di akhir
             final_content = old_content + header + new_content + "\n"
        
        # Simpan final content
        os.makedirs(os.path.dirname(exclude_file_path), exist_ok=True) if os.path.dirname(exclude_file_path) else None
        with open(exclude_file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        return True

    except Exception as e:
        print(f"Error saat sinkronisasi .gitignore: {e}", file=sys.stderr)
        return False # Gagal sinkronisasi

config_data = load_config()

TEXT_EXTRACTOR_SCRIPT = os.path.join(PROJECT_DIR, 'TextEXtractor.py')
LISTER_SCRIPT = os.path.join(PROJECT_DIR, 'NamesExtractor.py')

# --- Helper: safe int/env
def env_bool(name, default=False):
    v = os.environ.get(name)
    if v is None: return default
    return v.strip().lower() in ("1","true","yes","y")

# --- (Opsional) Restrict base path (isi ALLOWED_ROOTS kalau mau batasi)
ALLOWED_ROOTS = []  # contoh: [os.path.expanduser("~"), "D:/Repos"]

def is_allowed_path(p):
    if not ALLOWED_ROOTS:
        return True
    p = os.path.abspath(p)
    for root in ALLOWED_ROOTS:
        root_abs = os.path.abspath(root)
        if os.path.commonpath([p, root_abs]) == root_abs:
            return True
    return False

def clean_path(p: str) -> str:
    if not p:
        return p
    p = p.strip()

    # Lepas kutip berlapis (termasuk smart quotes)
    while (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
        p = p[1:-1].strip()
    for ql, qr in [('“', '”'), ('‘', '’')]:
        if p.startswith(ql) and p.endswith(qr):
            p = p[1:-1].strip()

    # Normalisasi slash -> forward slash
    p = p.replace('\\', '/')

    # Pertahankan UNC prefix //, rapikan duplikasi slash hanya di bagian setelahnya
    if p.startswith('//'):
        head, rest = '//', p[2:]
        while '//' in rest:
            rest = rest.replace('//', '/')
        return head + rest

    # Untuk path dengan drive (C:/...), rapikan duplikasi slash setelah drive
    if len(p) >= 3 and p[1:3] == ':/':
        drv, rest = p[:3], p[3:]
        while '//' in rest:
            rest = rest.replace('//', '/')
        return drv + rest

    # Selain itu, rapikan duplikasi slash biasa
    while '//' in p:
        p = p.replace('//', '/')
    return p

# --- Routes

@app.route('/')
def index():
    return render_template('Tree.html')

@app.route('/set_path', methods=['POST'])
def set_project_path():
    try:
        data = request.json or {}
        new_path = clean_path(data.get('path', '')).strip()
        if not new_path or not os.path.isdir(new_path):
            return jsonify({'success': False, 'error': 'Path tidak valid atau tidak ditemukan.'}), 400
        if not is_allowed_path(new_path):
            return jsonify({'success': False, 'error': 'Path tersebut tidak diizinkan.'}), 403

        config_data["TARGET_FOLDER"] = new_path
        save_config(config_data)
        exclude_path = config_data.get("EXCLUDE_FILE_PATH")
        if sync_gitignore_to_exclude(new_path, exclude_path):
             msg = 'Path berhasil diatur dan pola .gitignore digabungkan.'
        else:
             msg = 'Path berhasil diatur dan disimpan ke config.json.'
        
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pick_folder', methods=['GET'])
def pick_folder():
    try:
        # Buka dialog folder di mesin lokal (server == komputer kamu)
        import tkinter as tk
        from tkinter import filedialog, TclError

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        initial = config_data.get("TARGET_FOLDER") or os.path.expanduser("~")
        chosen = filedialog.askdirectory(initialdir=initial, title="Pilih folder proyek")
        chosen = clean_path(chosen)

        root.destroy()

        if not chosen:
            return jsonify({'success': False, 'error': 'Pemilihan dibatalkan.'}), 400

        if not is_allowed_path(chosen):
            return jsonify({'success': False, 'error': 'Path tersebut tidak diizinkan.'}), 403

        # Simpan ke config + balas ke UI
        config_data["TARGET_FOLDER"] = clean_path(chosen)
        save_config(config_data)
        exclude_path = config_data.get("EXCLUDE_FILE_PATH")
        if sync_gitignore_to_exclude(chosen, exclude_path):
            msg = 'Path diperbarui dari dialog dan pola .gitignore digabungkan.'
        else:
            msg = 'Path diperbarui dari dialog.'
            
        return jsonify({'success': True, 'path': config_data["TARGET_FOLDER"], 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except TclError as e:
        return jsonify({'success': False, 'error': f'Tidak bisa membuka dialog folder (no display?): {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pick_output_folder', methods=['GET'])
def pick_output_folder():
    try:
        import tkinter as tk
        from tkinter import filedialog, TclError

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        initial = os.path.dirname(config_data.get("OUTPUT_FILE") or "") or (config_data.get("TARGET_FOLDER") or os.path.expanduser("~"))
        chosen = filedialog.askdirectory(initialdir=initial, title="Pilih folder output TextExtractor")
        chosen = clean_path(chosen)
        root.destroy()

        if not chosen:
            return jsonify({'success': False, 'error': 'Pemilihan dibatalkan.'}), 400
        if not os.path.isdir(chosen):
            return jsonify({'success': False, 'error': 'Folder tidak valid.'}), 400

        return jsonify({'success': True, 'path': chosen})
    except TclError as e:
        return jsonify({'success': False, 'error': f'Tidak bisa membuka dialog folder (no display?): {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/manage_exclude_file', methods=['GET', 'POST'])
def manage_exclude_file():
    try:
        exclude_path = config_data.get("EXCLUDE_FILE_PATH")
        if not exclude_path:
            return jsonify({'success': False, 'error': 'EXCLUDE_FILE_PATH tidak diset di config.json'}), 500

        if request.method == 'GET':
            # Muat isi file exclude
            if not os.path.exists(exclude_path):
                # Buat file kosong agar UI tetap bisa tampil
                open(exclude_path, 'a', encoding='utf-8').close()
            with open(exclude_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return jsonify({'success': True, 'content': content})

        # POST => simpan konten
        data = request.get_json(silent=True) or {}
        new_content = data.get('content', '')

        # Guard ukuran biar ga kebablasan
        if len(new_content) > 200_000:  # ~200 KB
            return jsonify({'success': False, 'error': 'Konten terlalu besar.'}), 400

        # Normalisasi newline dan hapus trailing spaces
        norm = "\n".join(line.rstrip() for line in new_content.splitlines())
        # Pastikan file di-create jika belum ada
        os.makedirs(os.path.dirname(exclude_path), exist_ok=True) if os.path.dirname(exclude_path) else None
        with open(exclude_path, 'w', encoding='utf-8') as f:
            f.write(norm + ("\n" if not norm.endswith("\n") else ""))

        return jsonify({'success': True, 'message': 'Daftar pengecualian berhasil disimpan.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# --- Legacy (tetap ada): jalankan NameExtractor yang menulis file teks
@app.route('/run_nameextractor', methods=['POST'])
def run_nameextractor_legacy():
    try:
        data = request.json or {}
        include_files = data.get('include_files', True)
        include_size = data.get('include_size', False)

        process = subprocess.run(
            [sys.executable, LISTER_SCRIPT,
             '--include-files', str(include_files),
             '--include-size', str(include_size),
             '--format', 'text'],
            capture_output=True, text=True, encoding='utf-8', check=True
        )
        out_path = os.path.join(PROJECT_DIR, config_data["NAME_OUTPUT_FILE"])
        with open(out_path, 'r', encoding='utf-8') as f:
            output_content = f.read()
        return jsonify({'success': True, 'output': output_content})
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Baru: langsung JSON (tanpa file antar)
@app.route('/run_nameextractor_json', methods=['POST'])
def run_nameextractor_json():
    try:
        data = request.json or {}
        include_files = data.get('include_files', True)
        include_size = data.get('include_size', False)
        override_path = data.get('path')

        env = os.environ.copy()
        if override_path:
            env['VT_FOLDER'] = clean_path(override_path) 

        process = subprocess.run(
            [sys.executable, LISTER_SCRIPT,
             '--include-files', str(include_files),
             '--include-size', str(include_size),
             '--format', 'json'],
            capture_output=True, text=True, encoding='utf-8', check=True, timeout=600,
            env=env
        )
        items = json.loads(process.stdout or "[]")
        return jsonify({'success': True, 'items': items})
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Proses terlalu lama dan dihentikan.'}), 504
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Output JSON tidak valid dari NamesExtractor.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Lazy size: hitung ukuran saat diminta
def _human(n):
    units = ["B","KB","MB","GB","TB"]
    i=0
    x=float(n)
    while x>=1024 and i<len(units)-1:
        x/=1024.0; i+=1
    return f"{x:.1f} {units[i]}"

def _compute_size(path):
    if os.path.isfile(path):
        try: s = os.path.getsize(path)
        except: s = 0
        return s
    total = 0
    for root, dirs, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                if not os.path.islink(fp):
                    total += os.path.getsize(fp)
            except:
                pass
    return total

@app.route('/size')
def size_endpoint():
    p = clean_path(request.args.get('path', ''))
    if not p or not os.path.exists(p):
        return jsonify({'success': False, 'error':'Path tidak ditemukan.'}), 400
    if not is_allowed_path(p):
        return jsonify({'success': False, 'error':'Path tidak diizinkan.'}), 403
    bytes_ = _compute_size(p)
    return jsonify({'success': True, 'size_bytes': bytes_, 'formatted_size': _human(bytes_)})

# --- Text extractor (tetap kompatibel, plus opsi stream baca output)

@app.route('/run_textextractor', methods=['POST'])
# (di route /run_textextractor, ambil flag dari body)
@app.route('/run_textextractor', methods=['POST'])
def run_extractor():
    try:
        data = request.get_json(silent=True) or {}
        override_path = data.get('path')
        output_dir = data.get('output_dir')
        output_name = (data.get('output_name') or '').strip()
        remove_blank = bool(data.get('remove_blank_lines'))  # <-- NEW

        needs, reason, suggested = _needs_output_destination(config_data, output_dir, output_name)
        if needs:
            return jsonify({
                'success': False,
                'need_output_path': True,
                'reason': reason,
                'suggested_name': suggested
            }), 428

        env = os.environ.copy()
        if override_path:
            env['VT_FOLDER'] = clean_path(override_path)

        original_output_file = config_data.get("OUTPUT_FILE")
        if output_dir or output_name:
            base_name = output_name if output_name else (os.path.basename(original_output_file) if original_output_file else "Output.txt")
            base_dir = clean_path(output_dir) if output_dir else (
                clean_path(os.path.dirname(original_output_file)) if original_output_file else PROJECT_DIR
            )
            new_output_full = clean_path(os.path.join(base_dir, base_name))
            os.makedirs(os.path.dirname(new_output_full), exist_ok=True)
            config_data["OUTPUT_FILE"] = new_output_full
            save_config(config_data)

        process = subprocess.run(
            [sys.executable, TEXT_EXTRACTOR_SCRIPT],
            capture_output=True, text=True, encoding='utf-8', check=True, timeout=1800, env=env
        )

        out_path = config_data.get("OUTPUT_FILE") or os.path.join(PROJECT_DIR, "Output.txt")

        # === NEW: bersihkan baris kosong jika diminta ===
        header_notes = []
        if remove_blank:
            ok, info = _remove_blank_lines_inplace(out_path)
            if ok:
                removed = info  # jumlah baris yang dihapus
                header_notes.append(f"🧹 Blank-line cleaner: {removed} baris kosong dihapus.")
            else:
                header_notes.append(f"⚠️ Blank-line cleaner gagal: {info}")

        def generate():
            header = "\n".join(s for s in [process.stdout, process.stderr] if s).strip()
            if header or header_notes:
                yield (header + ("\n" if header else "") + "\n".join(header_notes)).strip() + "\n\n"
            with open(out_path, 'r', encoding='utf-8', errors='ignore') as f:
                for chunk in iter(lambda: f.read(8192), ''):
                    yield chunk

        return Response(generate(), mimetype='text/plain; charset=utf-8')

    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'TextEXtractor berjalan terlalu lama.'}), 504
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': e.stderr}), 500
    except FileNotFoundError:
        return jsonify({'success': False, 'error': "File output tidak ditemukan."}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/output_metrics', methods=['GET'])
def output_metrics():
    import re, math
    try:
        out_path = config_data.get("OUTPUT_FILE") or os.path.join(PROJECT_DIR, "Output.txt")
        if not os.path.exists(out_path):
            return jsonify({'success': True, 'exists': False, 'words': 0, 'tokens': 0, 'lines': 0, 'chars': 0, 'bytes': 0})
        with open(out_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        words = len(re.findall(r'\S+', text))
        lines = text.count('\n') + (1 if text and text[-1] != '\n' else 0)
        chars = len(text); bytes_len = len(text.encode('utf-8'))
        try:
            import tiktoken
            try:
                enc = tiktoken.encoding_for_model("gpt-4o-mini")
            except Exception:
                enc = tiktoken.get_encoding("cl100k_base")
            tokens = len(enc.encode(text))
        except Exception:
            tokens = math.ceil(chars / 4)  # fallback kasar
        return jsonify({'success': True, 'exists': True, 'words': words, 'tokens': tokens,
                        'lines': lines, 'chars': chars, 'bytes': bytes_len})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")

    # Auto-open sekali
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" and not getattr(app, "browser_opened", False):
        Timer(1, open_browser).start()
        app.browser_opened = True

    # DEBUG via env (default False di production)
    debug_mode = env_bool("FLASK_DEBUG", True)
    app.run(debug=debug_mode)