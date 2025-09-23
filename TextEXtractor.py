import os
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

def read_exclude_file(file_path):
    """
    Membaca daftar nama file atau folder yang akan dikecualikan dari sebuah file.
    Mengabaikan baris kosong dan baris yang dimulai dengan '#'.
    
    Args:
        file_path (str): Path ke file pengecualian.

    Returns:
        list: Daftar nama file/folder yang akan dikecualikan.
    """
    if not os.path.exists(file_path):
        return []
    
    excluded_items = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()
            # Abaikan baris kosong dan komentar
            if stripped_line and not stripped_line.startswith('#'):
                excluded_items.append(stripped_line)
    return excluded_items


def combine_files_in_folder_recursive(folder_path, output_file_name='Output.txt', exclude_file=None, formatted_output=False):
    """
    Menggabungkan konten dari semua file di dalam sebuah folder dan subfoldernya
    ke dalam satu file teks baru, sambil mengabaikan file atau folder yang ditentukan
    melalui file pengecualian.

    Args:
        folder_path (str): Path ke folder yang berisi file dan subfolder.
        output_file_name (str): Nama file output.
        exclude_file (str): Path ke file teks yang berisi nama-nama yang akan dikecualikan.
    """
    # Pastikan folder_path yang diberikan adalah path yang valid

    if os.path.exists(output_file_name):
        try:
            os.remove(output_file_name)
        except:
            return print(f"❌ Error: Gagal menghapus file output '{output_file_name}'. Pastikan file tidak sedang dibuka di program lain.")

    if not os.path.isdir(folder_path):
        print(f"❌ Error: Folder '{folder_path}' tidak ditemukan atau bukan direktori.")
        return
    combined_content = ""
    batas = ""
    bawah = ""
    excluded_found = []  # Daftar untuk menyimpan item yang dikecualikan
    included_found = []  # Daftar untuk menyimpan item yang berhasil digabungkan
    
    # Baca nama-nama dari file pengecualian
    exclude_names = read_exclude_file(exclude_file) if exclude_file else []
    
    # Gunakan set untuk pencarian nama yang efisien
    exclude_names_set = set(exclude_names)

    print("Daftar nama yang akan dikecualikan:")
    if exclude_names_set:
        for name in exclude_names_set:
            print(f"- {name}")
    else:
        print("Tidak ada nama yang dikecualikan.")
        
    print("\n" + "="*50 + "\n")
    if formatted_output:
        combined_content = f"BA denotes the top border, and WA denotes the bottom border used to separate files.\n"
        batas = "BA\n"
        bawah = "WA\n"
    for root, dirs, files in os.walk(folder_path):
        # Cek apakah direktori saat ini harus dikecualikan berdasarkan nama
        if os.path.basename(root) in exclude_names_set:
            print(f"⚠️ Melewatkan folder '{root}' dan isinya karena ada di daftar pengecualian.")
            excluded_found.append(os.path.basename(root))
            # Hapus subdirektori dari daftar yang akan dijelajahi lebih lanjut
            del dirs[:]
            continue
        
        # Tambahkan nama direktori yang akan diproses
        included_found.append(os.path.basename(root))
        
        # Prune `dirs` list in-place to exclude folders by name before os.walk continues
        dirs[:] = [d for d in dirs if d not in exclude_names_set]

        print(f"✅ Menjelajahi direktori: {root}")
        
        # Loop melalui setiap file yang ditemukan di direktori saat ini
        for filename in files:
            # Cek apakah file saat ini harus dikecualikan berdasarkan nama
            if filename in exclude_names_set:
                print(f"⚠️ Melewatkan file '{filename}' karena ada di daftar pengecualian.")
                excluded_found.append(filename)
                continue
            
            # Tambahkan nama file yang akan digabungkan
            included_found.append(filename)

            file_path = os.path.join(root, filename)

            try:
                # Buka file dalam mode baca ('r') dengan encoding UTF-8
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Tambahkan konten ke string gabungan dengan format yang diminta
                    combined_content += f"{batas}'{file_path}'\n{content}\n{bawah}\n"
            except Exception as e:
                # Tangani kesalahan saat membaca file
                print(f"⚠️ Melewatkan file '{file_path}' karena kesalahan: {e}")

    # Tulis konten gabungan ke file baru di direktori yang sama dengan skrip
    try:
        with open(output_file_name, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        print(f"\n✅ Berhasil! Semua konten digabungkan ke '{output_file_name}'.")
        
        # Menampilkan daftar file dan folder yang dikecualikan
        if excluded_found:
            print("\nBerikut adalah file dan folder yang berhasil dikecualikan:")
            for item in sorted(list(set(excluded_found))):
                print(f"- {item}")
        
        # Menampilkan daftar file dan folder yang disertakan
        if included_found:
            print("\nBerikut adalah file dan folder yang berhasil digabungkan:")
            for item in sorted(list(set(included_found))):
                print(f"- {item}")
        else:
            print("Tidak ada file atau folder yang digabungkan selama proses.")

    except Exception as e:
        print(f"\n❌ Terjadi kesalahan saat menulis file output: {e}")


# Panggilan fungsi dengan semua parameter yang tersedia
combine_files_in_folder_recursive(
    folder_path=config_data["TARGET_FOLDER"],
    exclude_file=config_data["EXCLUDE_FILE_PATH"],
    formatted_output=True
)