# ⚡ Node.js Project Optimization Guide

## 🚨 **CRITICAL: Always Exclude node_modules!**

### ❌ **Problem: Extracting with node_modules**

**Typical node_modules stats:**
```
Files:     50,000 - 200,000+ files
Size:      200MB - 2GB+
Time:      10-60+ minutes to extract
Result:    99% useless for LLM context
```

**Why it's slow:**
1. 🐌 **Thousands of tiny files** (average 2-5KB each)
2. 🗑️ **Binary/compiled files** (.node, .wasm, .so)
3. 🔄 **Nested duplicates** (same package in multiple locations)
4. 💾 **Memory pressure** from processing so many files
5. 🧠 **LLM can't use** most of this code anyway

---

## ✅ **Solution: Proper Exclusion**

### 1. **Update exclude_me.txt** (✅ Already Done!)

```plaintext
# Node.js - MUST EXCLUDE
node_modules
package-lock.json
yarn.lock
pnpm-lock.yaml
bun.lockb

# Build outputs
dist
build
.next
.nuxt
.output
.cache
.turbo
.parcel-cache

# Editor/IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini
```

### 2. **What TO Include for Node.js Projects**

**Essential files only:**
```
✅ package.json          - Dependencies list
✅ src/**/*.{js,ts,jsx,tsx}  - Source code
✅ *.config.js           - Config files
✅ README.md            - Documentation
✅ .env.example         - Environment template
```

**Use Just Me filter:**
```plaintext
# In lists/just_me.txt
src/
package.json
*.config.js
README.md
tsconfig.json
```

---

## 📊 **Performance Comparison**

### Before Optimization (WITH node_modules):
```
Project: React App
Files:   95,432 files
Size:    1.2GB
Time:    45 minutes ⏰
Output:  250MB text file
LLM:     Can't even load it! 💥
```

### After Optimization (WITHOUT node_modules):
```
Project: React App
Files:   327 files ✨
Size:    12MB
Time:    8 seconds ⚡
Output:  3MB text file
LLM:     Perfect! 🎯
```

**Speed improvement: 337x faster!**

---

## 🎯 **Quick Fix Commands**

### Check Current Task Status
```powershell
# Get all tasks
Invoke-WebRequest -Uri http://localhost:5000/tasks/all_tasks -Method GET | Select-Object -ExpandProperty Content

# Cancel running task if needed
Invoke-WebRequest -Uri http://localhost:5000/tasks/cancel_task/<task_id> -Method POST
```

### Restart Extraction (Optimized)
```powershell
# After updating exclude_me.txt
Invoke-WebRequest -Uri http://localhost:5000/tasks/start_extraction `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"folder_path": "./your-project", "output_file": "Output.txt"}' | 
  Select-Object -ExpandProperty Content
```

---

## 🔧 **Advanced: Project Type Templates**

### React/Next.js Project
**exclude_me.txt additions:**
```plaintext
node_modules
.next
dist
build
coverage
.turbo
*.tsbuildinfo
```

**just_me.txt (focused extraction):**
```plaintext
src/
app/
pages/
components/
package.json
next.config.js
tsconfig.json
```

### Vue/Nuxt Project
**exclude_me.txt:**
```plaintext
node_modules
.nuxt
.output
dist
.cache
```

**just_me.txt:**
```plaintext
src/
components/
composables/
pages/
nuxt.config.ts
package.json
```

### Express/Node API
**exclude_me.txt:**
```plaintext
node_modules
dist
build
coverage
```

**just_me.txt:**
```plaintext
src/
routes/
controllers/
models/
middleware/
server.js
package.json
```

---

## 🎓 **Best Practices**

### 1. **Always Check exclude_me.txt FIRST**
```powershell
# Before extracting any new project
cat .\lists\exclude_me.txt
```

### 2. **Use Just Me for Large Projects**
Focus on what matters:
```plaintext
# lists/just_me.txt
src/components/
src/utils/
package.json
README.md
```

### 3. **Progressive Extraction**
Start small, expand if needed:
```
Round 1: Just src/ folder
Round 2: Add configs if needed
Round 3: Add tests if needed
```

### 4. **Monitor Progress**
```powershell
# Check task status every 5 seconds
while ($true) {
    Invoke-WebRequest -Uri "http://localhost:5000/tasks/task_status/<task_id>" |
    Select-Object -ExpandProperty Content
    Start-Sleep -Seconds 5
}
```

---

## 📈 **Smart Filter Recommendations**

Smart filter akan auto-detect project size:

**Small (<100 files):**
- Sync processing OK
- Fast extraction

**Medium (100-1000 files):**
- Consider async
- Enable progress tracking

**Large (1000-10000 files):**
- ✅ Use async processing
- ✅ Exclude node_modules
- ✅ Use just_me filter
- ✅ Monitor memory

**XLarge (>10000 files):**
- 🚨 **MUST exclude node_modules**
- 🚨 Use just_me filter (required)
- 🚨 Async only
- 🚨 Split into multiple extractions

---

## 🆘 **Troubleshooting**

### Problem: "Extraction taking forever"
**Solution:**
1. Cancel current task
2. Add `node_modules` to exclude_me.txt
3. Restart extraction

### Problem: "Out of memory"
**Solution:**
1. Check exclude_me.txt has node_modules
2. Reduce MAX_FILE_SIZE_MB in config
3. Use just_me.txt to limit scope

### Problem: "Output file too large for LLM"
**Solution:**
1. Use just_me.txt to extract specific folders only
2. Extract in multiple passes (frontend, backend, etc.)
3. Exclude test files if not needed

---

## 📝 **Quick Reference**

### Must-Exclude for Performance
```
node_modules     ← CRITICAL
.git             ← Version history
dist/build       ← Build outputs
coverage         ← Test coverage
.next/.nuxt      ← Framework cache
.cache           ← General cache
```

### Safe to Include
```
src/             ← Source code ✅
package.json     ← Dependencies ✅
*.config.js      ← Configuration ✅
README.md        ← Documentation ✅
tsconfig.json    ← TS config ✅
```

### Maybe Include (case-by-case)
```
tests/           ← If analyzing test patterns
docs/            ← If need detailed docs
public/          ← Usually skip (assets)
scripts/         ← Utility scripts
```

---

## 💡 **Pro Tips**

1. **Package.json is enough** - LLM can understand dependencies from package.json, no need for actual node_modules

2. **Lock files are useless** - package-lock.json, yarn.lock contain hashes, not helpful for LLM

3. **Build outputs are redundant** - dist/build folders are generated from source, skip them

4. **Use .gitignore as guide** - Most things in .gitignore should be in exclude_me.txt

5. **When in doubt, exclude** - Start with more exclusions, add back if needed

---

## 🎯 **Your Current Setup**

✅ **Updated exclude_me.txt with:**
- node_modules
- package-lock.json
- yarn.lock
- pnpm-lock.yaml
- Build outputs (dist, build, .next, etc.)

**Next steps:**
1. Cancel current slow extraction (if still running)
2. Restart extraction - should be 100x faster now!
3. Consider using just_me.txt for even more focused extraction

---

**Remember:** For Node.js projects, **ALWAYS exclude node_modules** - it's not optional, it's essential for performance!
