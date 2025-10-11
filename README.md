# 🧭 CodeDevour – Project Viewer & Extractor

**CodeDevour** is a lightweight web tool to **inspect project structure**, **merge text/code files**, and **manage exclusions** in one UI. Perfect for documentation, source analysis, or bundling artifacts for academic and dev use.

---

## 🚀 What’s New (October 2025)

> Highlights of **new/changed** features and behavior. Backward‑compatible with previous flows.

* **Smart Output Destination**

  * TextExtractor now **remembers** and **validates** the output destination (`OUTPUT_FILE`).
  * If not set or unwritable, the UI will **prompt to pick a folder** and **suggest a file name** (e.g., `Output.txt`) before processing.
  * Related endpoint: `GET /pick_output_folder`; internal guard `_needs_output_destination(...)`.

* **Blank‑Line Cleanup (Post‑processing)**

  * New option **“Remove empty lines from Output”** to clean up `Output.txt` after merging.
  * Shows a note like `🧹 Blank-line cleaner: 123 empty lines removed.` at the stream header.

* **Output Metrics (Words · Tokens · Lines · Bytes)**

  * UI badges for **word** and **token** counts (uses `tiktoken` if available; otherwise approximate with `chars/4`).
  * Endpoint: `GET /output_metrics` → `{ words, tokens, lines, chars, bytes }`.

* **NamesExtractor – Fast JSON mode (no intermediate file)**

  * New `POST /run_nameextractor_json` returns an **array of items** `{ path, type, size_bytes?, formatted_size? }`.
  * The file tree is rendered client‑side and **folder sizes are computed lazily** when expanded (endpoint `GET /size?path=...`).

* **`.gitignore` → `exclude_me.txt` Sync**

  * On **Set Path**, patterns from the project’s `.gitignore` are **copied** into `exclude_me.txt` under the header `# === PATTERNS FROM .gitignore ===`.
  * Manual patterns remain safe; the `.gitignore` section is **overwritten** on subsequent syncs.

* **Path Normalization & Optional Safety Root**

  * User input paths are cleaned (quotes, duplicate slashes) via `clean_path(...)`.
  * Optional **ALLOWED_ROOTS** (empty = unrestricted) to limit where scanning can occur.

* **Quick Config Summary**

  * `GET /config_summary` exposes `target_folder`, `output_dir`, `output_name`, `output_file` for UI prefills.

* **A Nicer UI**

  * **Top navigation chips** (NamesExtractor / TextExtractor / Exclude Me / Activity Log).
  * **Drag & drop** items from the tree into the *Exclude Me* textarea.
  * **Activity Log** timeline, real‑time output metrics badge, **crimson** theme.

---

## 🧰 Stack & Layout

| Component | Tech                                             |
| --------: | :----------------------------------------------- |
|   Backend | Python 3.x, Flask                                |
|  Frontend | HTML, JavaScript, TailwindCSS                    |
|    Config | `config.json`                                    |
|    Output | Merged file `OUTPUT_FILE` (default `Output.txt`) |

**Directory Skeleton (short)**

```
codedevour/
├─ app.py                # Flask app & new REST endpoints
├─ NamesExtractor.py     # Lister (text & JSON modes)
├─ TextEXtractor.py      # Merger + whitelist & size limits
├─ templates/Tree.html   # UI (chips, tabs, DnD exclude, metrics badge)
├─ exclude_me.txt        # Exclusion list (+ .gitignore sync)
├─ config.json           # TARGET_FOLDER, OUTPUT_FILE, etc.
├─ requirements.txt      # Python deps
└─ README.md
```

---

## 🔧 Installation

### 1) Prereqs

* Python **3.8+** (Windows/Linux/macOS)

### 2) Environment Setup

```bash
# clone & enter folder
git clone https://github.com/Anwitch/codedevour.git
cd codedevour

# create & activate venv (Windows)
python -m venv venv
venv\Scripts\activate

# Linux/macOS
# python3 -m venv venv
# source venv/bin/activate

# install deps
pip install -r requirements.txt

# (optional) for accurate token counts
pip install tiktoken
```

### 3) Run

```bash
python app.py
# your browser should open to http://127.0.0.1:5000
```

---

## 🧑‍💻 Usage

### A. Set Project Path

1. Fill **Project Path** then click **Set Path** or **Pick Folder…**.
2. On Set Path, patterns from `.gitignore` are **merged** into `exclude_me.txt`.
3. Watch **Activity Log** for status and notifications.

### B. NamesExtractor

* Options: **Include files** and **Include sizes** (optional).
* Click **Run NamesExtractor.py**:

  * **JSON mode** (default in UI): renders tree directly in the browser.
  * **Folder sizes** are fetched when you expand a folder (lazy via request).

### C. TextExtractor

1. (Optional) specify **Output Folder** and **File Name**; if left empty you’ll be prompted at runtime.
2. Check **Remove empty lines** for post‑processing.
3. Click **Run TextEXtractor.py** to start.
4. The **Output** streams in the right panel; blank‑line removal stats (if enabled) appear in the header.
5. The **Output: (words · tokens)** badge refreshes via `GET /output_metrics`.

### D. Exclude Me

* Drag file/folder names from the left tree into this textarea, or edit manually (one item per line).
* Click **Save** to update `exclude_me.txt`.
* The section `# === PATTERNS FROM .gitignore ===` is managed automatically on **Set Path**.

---

## ⚙️ Configuration (`config.json`)

```json
{
  "TARGET_FOLDER": "C:/Users/You/YourProject",
  "NAME_OUTPUT_FILE": "OutputAllNames.txt",
  "OUTPUT_FILE": "Output.txt",
  "EXCLUDE_FILE_PATH": "exclude_me.txt"
}
```

> `OUTPUT_FILE` can be changed on‑the‑fly from the UI (Output Folder + File Name) and will be **persisted** to `config.json`.

**TextExtractor Whitelist & Size Limits** (in `TextEXtractor.py`):

* `WHITELIST_EXT`: `.py .js .ts .tsx .jsx .json .md .txt .html .css .yml .yaml .toml .ini .cfg .sql .sh .bat .ps1 .c .cpp .h .hpp .java .kt .go .rs .vue .xml`
* `MAX_FILE_BYTES`: `2 * 1024 * 1024` (2 MB)
* Binary detection: sample 4096 bytes / if non‑text chars > ~30% then skip.

**Exclusion Notes**

* An item is excluded if its **name** or **relative path** contains any token from `exclude_me.txt` (semi‑substring match).

---

## 🔌 Endpoint Cheatsheet

| Method | Path                      | Description                                                                                                       |
| :----: | :------------------------ | :---------------------------------------------------------------------------------------------------------------- |
| `POST` | `/set_path`               | Set `TARGET_FOLDER` (sync `.gitignore` → `exclude_me.txt`).                                                       |
|  `GET` | `/pick_folder`            | Native folder picker for the project path.                                                                        |
|  `GET` | `/pick_output_folder`     | Native folder picker for TextExtractor output.                                                                    |
|  `GET` | `/config_summary`         | Return active config for UI prefill.                                                                              |
|  `GET` | `/size?path=…`            | Compute file/folder size (lazy).                                                                                  |
| `POST` | `/run_nameextractor_json` | Run NamesExtractor → **JSON** array items.                                                                        |
| `POST` | `/run_nameextractor`      | Legacy mode → writes `OutputAllNames.txt`, returns JSON with `output`.                                            |
| `POST` | `/run_textextractor`      | Run TextExtractor; **streams** merged output. Auto‑prompts for output dir if needed. Option `remove_blank_lines`. |
|  `GET` | `/manage_exclude_file`    | (GET) read `exclude_me.txt` content.                                                                              |
| `POST` | `/manage_exclude_file`    | (POST) save `exclude_me.txt` content.                                                                             |
|  `GET` | `/output_metrics`         | Output stats: words, tokens, lines, chars, bytes.                                                                 |

---

## 🐞 Troubleshooting

* **“Path is invalid or not found.”**
  Use **Pick Folder…** to avoid typos and confirm permissions.

* **“Output folder required.”**
  Choose an output directory when prompted, or fill **Output Folder** & **File Name** in the TextExtractor tab.

* **No folder sizes in NamesExtractor**
  Folder sizes are fetched **on expand**. Check your browser’s Network tab for request errors.

* **Token count looks approximate**
  Without `tiktoken`, we approximate with `chars/4`. Install `tiktoken` for accurate counts.

* **Windows: output file appears locked**
  Close any editor/preview holding `Output.txt`, then rerun TextExtractor.

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit & push
4. Open a Pull Request 🎉

---

## 📜 License

MIT License. See `LICENSE`.

---

Made with ❤️ by **Anwitch** · *CodeDevour*