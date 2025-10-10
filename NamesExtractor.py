# NamesExtractor.py
import os
import sys
import json
import argparse

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

# Pastikan encoding aman (Windows-friendly)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass  # older Python fallback

# --- GLOBAL logger switch ---
is_json_out = False
def log(*a, **k):
    """Kirim log ke stderr saat output mode JSON, agar stdout tetap 'bersih' untuk JSON."""
    if is_json_out:
        print(*a, file=sys.stderr, **k)
    else:
        print(*a, **k)

def format_file_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    x = float(size_bytes)
    while x >= 1024 and i < len(size_names) - 1:
        x /= 1024.0
        i += 1
    return f"{x:.1f} {size_names[i]}"

def get_folder_size(folder_path):
    total_size = 0
    try:
        # os.scandir sedikit lebih cepat dari os.walk untuk size sum
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                fp = os.path.join(root, filename)
                try:
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
                except (OSError, IOError):
                    pass
    except (OSError, IOError):
        pass
    return total_size

def get_item_size(item_path):
    try:
        if os.path.isfile(item_path):
            size_bytes = os.path.getsize(item_path)
        elif os.path.isdir(item_path):
            size_bytes = get_folder_size(item_path)
        else:
            return 0, "0 B"
        return size_bytes, format_file_size(size_bytes)
    except (OSError, IOError):
        return 0, "0 B"

def read_exclude_file(file_path):
    if not os.path.exists(file_path):
        return []
    excluded_items = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith('#'):
                excluded_items.append(s)
    return excluded_items

def add_files_to_list(all_items, files, root, exclude_names_set, include_size):
    for filename in files:
        if filename in exclude_names_set:
            continue
        file_path = os.path.join(root, filename)
        if include_size:
            size_bytes, formatted_size = get_item_size(file_path)
            all_items.append({
                'path': file_path,
                'type': 'FILE',
                'size_bytes': size_bytes,
                'formatted_size': formatted_size
            })
        else:
            all_items.append({
                'path': file_path,
                'type': 'FILE'
            })

def list_all_names(folder_path, include_files=True, include_size=False, exclude_file=None):
    if not os.path.isdir(folder_path):
        log(f"❌ Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return []

    all_items = []
    exclude_names = read_exclude_file(exclude_file) if exclude_file else []
    exclude_names_set = set(exclude_names)

    log(f"✅ Memulai penelusuran dari direktori: {folder_path}")

    for root, dirs, files in os.walk(folder_path):
        if os.path.basename(root) in exclude_names_set:
            del dirs[:]
            continue

        if include_size:
            size_bytes, formatted_size = get_item_size(root)
            all_items.append({
                'path': root,
                'type': 'FOLDER',
                'size_bytes': size_bytes,
                'formatted_size': formatted_size
            })
        else:
            all_items.append({'path': root, 'type': 'FOLDER'})

        # prune dirs
        dirs[:] = [d for d in dirs if d not in exclude_names_set]

        if include_files:
            add_files_to_list(all_items, files, root, exclude_names_set, include_size)
    return all_items

def main():
    global is_json_out

    parser = argparse.ArgumentParser(description="List files and folders recursively.")
    parser.add_argument('--include-files', type=lambda x: x.lower() == 'true', default=True)
    parser.add_argument('--include-size', type=lambda x: x.lower() == 'true', default=False)
    parser.add_argument('--format', choices=['json','text'], default='json')
    args = parser.parse_args()

    is_json_out = (args.format == 'json')

    folder = os.environ.get("VT_FOLDER") or config_data["TARGET_FOLDER"]

    items = list_all_names(
        folder_path=folder,
        include_files=args.include_files,
        include_size=args.include_size,
        exclude_file=config_data["EXCLUDE_FILE_PATH"]
    )

    if args.format == 'json':
        # stdout HANYA JSON
        sys.stdout.write(json.dumps(items, ensure_ascii=False))
        try:
            sys.stdout.flush()
        except Exception:
            pass
    else:
        # kompatibel lama: tulis file teks
        output_file_name = config_data["NAME_OUTPUT_FILE"]
        try:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                for item in items:
                    if args.include_size and 'size_bytes' in item:
                        f.write(f"{item['path']}; [{item['type']}]; {item['size_bytes']}; {item['formatted_size']}\n")
                    else:
                        f.write(f"{item['path']}; [{item['type']}]\n")
            log(f"\n✅ Berhasil! Daftar semua file/folder disimpan ke '{output_file_name}'.")
        except Exception as e:
            log(f"\n❌ Gagal menulis file output: {e}")

if __name__ == '__main__':
    main()