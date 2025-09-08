import os
import sys
import config
import argparse

sys.stdout.reconfigure(encoding='utf-8')


def format_file_size(size_bytes):
    """
    Mengkonversi ukuran dalam bytes ke format yang lebih mudah dibaca.
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


def get_folder_size(folder_path):
    """
    Menghitung total ukuran folder beserta semua subdirektori dan file di dalamnya.
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    if not os.path.islink(file_path):
                        total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
    except (OSError, IOError):
        pass
    return total_size


def get_item_size(item_path):
    """
    Mendapatkan ukuran file atau folder.
    """
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
    """
    Membaca daftar nama file atau folder yang akan dikecualikan dari sebuah file.
    """
    if not os.path.exists(file_path):
        return []
    
    excluded_items = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith('#'):
                excluded_items.append(stripped_line)
    return excluded_items


def add_files_to_list(all_items, files, root, exclude_names_set):
    """
    Menambahkan nama file yang tidak dikecualikan ke dalam daftar beserta ukurannya.
    """
    for filename in files:
        if filename in exclude_names_set:
            print(f"⚠️ Melewatkan file '{filename}' karena ada di daftar pengecualian.")
            continue
        
        file_path = os.path.join(root, filename)
        size_bytes, formatted_size = get_item_size(file_path)
        all_items.append({
            'path': file_path,
            'type': 'FILE',
            'size_bytes': size_bytes,
            'formatted_size': formatted_size
        })


def list_all_names_to_file(folder_path, output_file_name, include_files=True, include_size=True, exclude_file=None):
    """
    Menelusuri semua file dan folder secara rekursif dari path yang diberikan
    dan mencatat nama-nama tersebut ke dalam file teks baru.
    """
    if not os.path.isdir(folder_path):
        print(f"❌ Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return

    all_items = []
    exclude_names = read_exclude_file(exclude_file) if exclude_file else []
    exclude_names_set = set(exclude_names)

    print("Daftar nama yang akan dikecualikan:")
    if exclude_names_set:
        for name in exclude_names_set:
            print(f"- {name}")
    else:
        print("Tidak ada nama yang dikecualikan.")
    print("\n" + "="*50 + "\n")
    
    print(f"✅ Memulai penelusuran dari direktori: {folder_path}")
    
    for root, dirs, files in os.walk(folder_path):
        if os.path.basename(root) in exclude_names_set:
            print(f"⚠️ Melewatkan folder '{root}' dan isinya karena ada di daftar pengecualian.")
            del dirs[:]
            continue
        
        size_bytes, formatted_size = get_item_size(root)
        all_items.append({
            'path': root,
            'type': 'FOLDER',
            'size_bytes': size_bytes,
            'formatted_size': formatted_size
        })
        
        dirs[:] = [d for d in dirs if d not in exclude_names_set]

        if include_files:
            add_files_to_list(all_items, files, root, exclude_names_set)

    try:
        with open(output_file_name, 'w', encoding='utf-8') as f:
            for item in all_items:
                if include_size:
                    f.write(f"{item['path']}; [{item['type']}]; {item['size_bytes']}; {item['formatted_size']}\n")
                else:
                    f.write(f"{item['path']}; [{item['type']}]\n")

        total_size_bytes = sum(item['size_bytes'] for item in all_items)
        total_formatted_size = format_file_size(total_size_bytes)
        
        print(f"\n✅ Berhasil! Daftar semua file dan folder telah disimpan ke '{output_file_name}'.")
        print(f"📊 Total {len(all_items)} item ditemukan.")
        if include_size:
            print(f"💾 Total ukuran keseluruhan: {total_formatted_size} ({total_size_bytes:,} bytes)")

    except Exception as e:
        print(f"\n❌ Terjadi kesalahan saat menulis file output: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="List files and folders recursively.")
    parser.add_argument('--include-files', type=lambda x: x.lower() == 'true', default=True, help='Include files in the list.')
    parser.add_argument('--include-size', type=lambda x: x.lower() == 'true', default=False, help='Include size information.')
    args = parser.parse_args()

    list_all_names_to_file(
        folder_path=config.TARGET_FOLDER,
        output_file_name=config.LISTER_OUTPUT_FILE_NAME,
        include_files=args.include_files,
        include_size=args.include_size,
        exclude_file=config.EXCLUDE_FILE_PATH
    )