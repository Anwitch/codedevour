# 🚀 Tips untuk Project Besar (9 Juta Kata)

## ✅ Yang Sudah Diperbaiki:

### 1. **Timeout Diperpanjang**
- **Sebelum:** 30 menit (1800 detik)
- **Sekarang:** 2 jam (7200 detik)
- Cukup untuk process jutaan kata

### 2. **Chunk Size Diperbesar**
- **Sebelum:** 16 KB per chunk
- **Sekarang:** 128 KB per chunk
- **8x lebih cepat** untuk I/O operations

### 3. **Max File Size Dinaikkan**
- **Sebelum:** 2 MB per file
- **Sekarang:** 10 MB per file
- Bisa customize di config.json: `"MAX_FILE_SIZE_MB": 20`

### 4. **Progress Logging Added**
- Log setiap 100 files diproses
- Tampilkan total MB yang sudah di-scan
- User tahu process masih jalan (tidak hang)

---

## 📋 Checklist untuk Project Besar:

### ✅ 1. **Pastikan Exclude Node_modules**
File: `lists/exclude_me.txt`
```
node_modules
.git
dist
build
.next
.nuxt
vendor
__pycache__
.pytest_cache
.venv
venv
```

### ✅ 2. **Set Target yang Spesifik (Gunakan Just_Me)**
File: `lists/just_me.txt`

**Contoh - Hanya ambil source code:**
```
src/
app/
components/
lib/
utils/
*.py
*.js
*.ts
```

### ✅ 3. **Increase Timeout Jika Perlu**
Jika project **sangat besar** (>10 juta kata), bisa set `timeout=None`:

Edit: `server/routes/text.py` line 90:
```python
timeout=None,  # No limit (was 7200)
```

### ✅ 4. **Gunakan SSD untuk Output**
- Output file ke SSD, bukan HDD
- **10x lebih cepat** untuk write operations

### ✅ 5. **Tutup Aplikasi Lain**
- Close Chrome tabs yang tidak perlu
- Free up RAM untuk Python process
- Monitor Task Manager

---

## 🔍 Monitoring Progress:

### Di Browser:
1. Klik "Jalankan TextEXtractor.py"
2. **Jangan tutup tab/window**
3. Lihat Network tab di DevTools (F12)
   - Request akan "pending" (normal)
   - Bukan error, tapi sedang proses

### Di Terminal (Alternatif):
```bash
# Jalankan manual untuk lihat progress
cd C:\Users\Andri\Project\CodeDevour
python server/extractors/TextEXtractor.py
```

**Output yang akan muncul:**
```
[*] Memulai scanning folder: C:/path/to/project
[+] Diproses: 100 files (5.2 MB)
[+] Diproses: 200 files (12.8 MB)
[+] Diproses: 300 files (22.1 MB)
...
-> Berhasil! 1250 files digabungkan (156.3 MB)
-> Skipped: 45 files (binary/too large/errors)
```

---

## ⏱️ Estimasi Waktu:

| Project Size | Files | Estimated Time |
|--------------|-------|----------------|
| Small | < 100 | 10-30 seconds |
| Medium | 100-1000 | 1-5 minutes |
| Large | 1000-5000 | 5-20 minutes |
| Very Large | 5000-10000 | 20-60 minutes |
| Huge | 10000+ | 1-2 hours |

**9 juta kata** ≈ **~5000 files** ≈ **15-30 menit**

---

## 🐛 Troubleshooting:

### "Chrome Not Responding"
**Penyebab:** Browser nunggu HTTP response yang sangat lama

**Solusi:**
1. **Jangan panic!** Process masih jalan di background
2. Check Task Manager → Python process masih running?
3. Tunggu sampai selesai (lihat estimasi waktu di atas)
4. **Alternatif:** Jalankan via terminal (lebih stabil)

### "Out of Memory"
**Penyebab:** File terlalu besar, RAM habis

**Solusi:**
1. Lower `MAX_FILE_SIZE_MB` di config:
   ```json
   {
     "MAX_FILE_SIZE_MB": 5
   }
   ```
2. Tambah virtual memory (pagefile) di Windows
3. Close aplikasi lain
4. Process secara bertahap (per folder)

### "Process Terlalu Lama"
**Penyebab:** Terlalu banyak file

**Solusi:**
1. **Gunakan just_me.txt** untuk filter folder spesifik
2. Process per module/folder:
   ```
   just_me.txt:
   src/frontend/
   ```
   Run, save output → Clear just_me.txt → Next folder:
   ```
   just_me.txt:
   src/backend/
   ```

### "Output File Kosong"
**Penyebab:** Semua file di-exclude atau binary

**Solusi:**
1. Check `exclude_me.txt` - jangan terlalu ketat
2. Check file extensions - pastikan ada di WHITELIST_EXT
3. Jalankan via terminal untuk lihat log errors

---

## 💡 Pro Tips:

### 1. **Split Large Projects**
Daripada 1x process 9 juta kata, split jadi 3-4 batch:
- Batch 1: Frontend code
- Batch 2: Backend code  
- Batch 3: Config/docs
- Combine manual nanti

### 2. **Use just_me.txt Wisely**
Contoh untuk React project:
```
src/
public/index.html
package.json
tsconfig.json
```

Exclude tests:
```
# Di exclude_me.txt
__tests__
*.test.js
*.spec.ts
```

### 3. **Monitor di Task Manager**
- Python.exe process
- Watch RAM usage
- Watch Disk I/O
- Jika freeze >10 min → ada masalah

### 4. **Test Small First**
Sebelum process full project:
```
# Set just_me.txt ke 1 folder kecil
src/components/Button/
```
Test dulu → works? → Expand ke full src/

---

## 🎯 Recommended Workflow:

1. **Setup Filters**
   - Exclude: node_modules, .git, dist, build
   - Just_me: src/, app/, lib/ (source code saja)

2. **Test Small**
   - Process 1 folder dulu
   - Verify output correct

3. **Run Full Scan**
   - Via browser atau terminal
   - Monitor progress logs
   - **Patience!** Bisa 15-30 menit

4. **Verify Output**
   - Check Output.txt size
   - Check word/token count di UI
   - Spot check beberapa files

5. **Optimize if Needed**
   - Terlalu lambat? Kurangi scope
   - Too big? Split jadi batches
   - Errors? Check logs

---

## 📊 Success Metrics:

Setelah optimization, target:
- ✅ Process 1000 files dalam 5-10 menit
- ✅ Chrome tidak freeze/hang
- ✅ Progress visible (logs muncul)
- ✅ Output file complete & correct
- ✅ No out-of-memory errors

---

**Selamat mencoba! Kalau masih ada issue, kirim error message lengkapnya.** 🚀
