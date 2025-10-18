# Panduan Penggunaan Exclude & Just Me

## Perubahan Penting

Fitur exclude dan just_me sekarang mendukung **path lengkap**, bukan hanya nama file. Ini memungkinkan Anda untuk:
- Mengecualikan file dengan nama yang sama tapi di lokasi berbeda
- Memilih file spesifik berdasarkan path lengkapnya

## Format yang Didukung

### 1. Nama File Saja (Backward Compatible)
```
page.html
app.py
```
**Efek**: Semua file dengan nama tersebut akan di-exclude/include, di mana pun lokasinya.

### 2. Path Relatif (BARU)
```
src/pages/home/page.html
components/header/page.html
backend/app.py
```
**Efek**: Hanya file di path tersebut yang di-exclude/include.

### 3. Substring Pattern
```
/node_modules/
.log
/test/
```
**Efek**: Semua file/folder yang mengandung substring tersebut di path-nya.

## Contoh Penggunaan

### exclude_me.txt

Mengecualikan file/folder tertentu:

```txt
# Exclude semua file .log
.log

# Exclude folder node_modules di mana pun
/node_modules/

# Exclude file page.html hanya di folder src/pages/
src/pages/page.html

# Exclude app.py hanya di folder backend/
backend/app.py

# Tapi TIDAK exclude app.py di folder frontend/
# (karena path-nya berbeda)
```

### just_me.txt

Memilih hanya file/folder tertentu:

```txt
# Hanya ambil file di folder src/
src/

# Atau lebih spesifik, hanya component tertentu
src/components/Button.tsx
src/components/Header.tsx

# Ambil app.py di backend tapi tidak di frontend
backend/app.py

# Ambil semua file config
config/

# Atau file config tertentu saja
config/database.json
config/api.json
```

## Prioritas Matching

Sistem akan mencari kecocokan dengan urutan:

1. **Exact match** dengan path relatif lengkap
   - Pattern: `src/pages/home/page.html`
   - Match: `/project/src/pages/home/page.html`

2. **Substring match** di path
   - Pattern: `/pages/`
   - Match: `/project/src/pages/home/page.html`

3. **Exact match** dengan nama file (backward compatibility)
   - Pattern: `page.html`
   - Match: file dengan nama `page.html` di mana pun

## Tips Penggunaan

### Mengecualikan File Duplikat
Jika ada file dengan nama sama di berbagai folder:

```txt
# exclude_me.txt
tests/page.html          # Hanya exclude yang di folder tests/
docs/page.html           # Hanya exclude yang di folder docs/
# src/pages/page.html tidak di-exclude
```

### Memilih Component Spesifik
Jika ingin pilih component tertentu saja:

```txt
# just_me.txt
src/components/Button/
src/components/Header/
src/utils/helpers.ts
config/app.json
```

### Kombinasi Exclude dan Just Me
- **just_me** = whitelist (hanya ambil ini)
- **exclude_me** = blacklist (jangan ambil ini)

Jika keduanya digunakan:
1. Sistem filter dengan **just_me** dulu (whitelist)
2. Lalu buang yang ada di **exclude_me** (blacklist)

```txt
# just_me.txt
src/

# exclude_me.txt  
src/tests/
src/__pycache__/
```

Hasil: Hanya ambil file di `src/` kecuali `tests/` dan `__pycache__/`

## Path Format

- Gunakan forward slash (`/`) atau backslash (`\`) - keduanya akan dinormalisasi
- Path relatif dari root folder yang di-scan
- Tidak perlu leading slash

**Contoh**:
```txt
✓ src/pages/page.html
✓ src\pages\page.html
✗ /src/pages/page.html  (leading slash tidak perlu)
```

## Testing

Untuk test apakah pattern Anda bekerja:
1. Jalankan Names Extractor dengan setting yang sama
2. Periksa output - file yang muncul adalah yang akan di-process
3. Sesuaikan pattern di `exclude_me.txt` atau `just_me.txt`
4. Ulangi sampai hasilnya sesuai

## Performa

- Pattern matching dilakukan dengan substring search (sangat cepat)
- Cache digunakan untuk operasi yang berulang
- Relative path dihitung sekali per file
