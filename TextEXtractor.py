# TextEXtractor.py
import os
import json
import sys

# Encoding aman
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

# --- Konfigurasi filter konten ---
# Set None untuk mematikan whitelist dan mengambil semua file teks (deteksi binary tetap berlaku).
WHITELIST_EXT = {
    ".py",".js",".ts",".tsx",".jsx",".json",".md",".txt",".html",".css",
    ".yml",".yaml",".toml",".ini",".cfg",".sql",".sh",".bat",".ps1",
    ".c",".cpp",".h",".hpp",".java",".kt",".go",".rs",".vue",".xml"
}
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MB

def log(*a, **k):
    print(*a, file=sys.stderr, **k)

def looks_binary(sample: bytes) -> bool:
    if not sample:
        return False
    if b'\x00' in sample:
        return True
    non_text = sum(1 for b in sample if b < 9 or (13 < b < 32) or b > 126)
    return non_text > len(sample) * 0.30

def read_exclude_file(file_path):
    if not os.path.exists(file_path):
        return []
    out = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith('#'):
                out.append(s)
    return out

def is_excluded(root, filename, exclude_set):
    """
    Exclude jika:
      - basename folder atau file ada di exclude_set, ATAU
      - path relatif mengandung salah satu token exclude (semi-substring match sederhana).
    """
    base = os.path.basename(root)
    if base in exclude_set or filename in exclude_set:
        return True
    # cek substring pada path relatif
    rel_root = root.replace("\\", "/")
    for token in exclude_set:
        if token in rel_root or token in filename:
            return True
    return False

def combine_files_in_folder_recursive(folder_path, output_file_name='Output.txt', exclude_file=None, formatted_output=True):
    if os.path.exists(output_file_name):
        try:
            os.remove(output_file_name)
        except:
            log(f"❌ Error: Gagal menghapus file output '{output_file_name}'. Tutup file jika sedang dibuka.")
            return

    if not os.path.isdir(folder_path):
        log(f"❌ Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return

    excluded_found, included_found = [], []

    exclude_names = read_exclude_file(exclude_file) if exclude_file else []
    exclude_set = set(exclude_names)

    log("Daftar nama yang akan dikecualikan:")
    if exclude_set:
        for name in sorted(exclude_set):
            log(f"- {name}")
    else:
        log("Tidak ada nama yang dikecualikan.")
    log("\n" + "="*50 + "\n")

    header_note = "BA denotes the top border and WA denotes the bottom border used to separate files.\n"

    with open(output_file_name, 'w', encoding='utf-8', errors='ignore') as out:
        if formatted_output:
            out.write(header_note)

        for root, dirs, files in os.walk(folder_path):
            # Prune folder yang di-exclude (berdasarkan nama / token)
            pruned_dirs = []
            for d in list(dirs):
                if is_excluded(os.path.join(root, d), d, exclude_set):
                    log(f"⚠️ Melewatkan folder '{os.path.join(root, d)}' (exclude).")
                    excluded_found.append(d)
                else:
                    pruned_dirs.append(d)
            dirs[:] = pruned_dirs  # efektif memangkas traversal

            for filename in files:
                if is_excluded(root, filename, exclude_set):
                    log(f"⚠️ Melewatkan file '{os.path.join(root, filename)}' (exclude).")
                    excluded_found.append(filename)
                    continue

                ext = os.path.splitext(filename)[1].lower()
                if WHITELIST_EXT is not None:
                    if ext and ext not in WHITELIST_EXT:
                        # Lewati tipe yang tidak di-whitelist
                        continue

                fp = os.path.join(root, filename)

                try:
                    size = os.path.getsize(fp)
                except Exception as e:
                    log(f"⚠️ Melewatkan '{fp}' (gagal getsize: {e})")
                    continue

                if size > MAX_FILE_BYTES:
                    log(f"⚠️ Melewatkan '{fp}' (> {MAX_FILE_BYTES} bytes)")
                    continue

                try:
                    with open(fp, 'rb') as fb:
                        sample = fb.read(4096)
                        if looks_binary(sample):
                            log(f"⚠️ Melewatkan '{fp}' (binary-like)")
                            continue

                    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if formatted_output:
                        out.write("BA\n")
                        out.write(f"'{fp}'\n")
                        out.write(content)
                        out.write("\nWA\n")
                    else:
                        out.write(f"----- {fp} -----\n")
                        out.write(content)
                        out.write("\n\n")

                    included_found.append(filename)

                except Exception as e:
                    log(f"⚠️ Melewatkan file '{fp}' karena kesalahan: {e}")

    log(f"\n✅ Berhasil! Semua konten digabungkan ke '{output_file_name}'.")
    if excluded_found:
        log("\nBerikut adalah file/folder yang dikecualikan:")
        for item in sorted(set(excluded_found)):
            log(f"- {item}")

    if included_found:
        log("\nBerikut adalah file/folder yang digabungkan:")
        for item in sorted(set(included_found)):
            log(f"- {item}")
    else:
        log("Tidak ada file atau folder yang digabungkan.")

folder = os.environ.get("VT_FOLDER") or config_data["TARGET_FOLDER"]
# Panggilan fungsi dengan parameter dari config
combine_files_in_folder_recursive(
    folder_path=folder,
    output_file_name=config_data["OUTPUT_FILE"],
    exclude_file=config_data["EXCLUDE_FILE_PATH"],
    formatted_output=True
)
