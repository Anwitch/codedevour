# 🧭 CodeDevour – Intelligent Codebase Bundler & Explorer

**CodeDevour** is a powerful web-based tool for **exploring project structure**, **bundling code files**, and **managing file exclusions** through an intuitive interface. Transform any codebase into a single, well-organized document perfect for documentation, code review, AI analysis, or academic purposes.

---

## ✨ Key Features

### 📂 Interactive Project Explorer
* **Visual file tree** with lazy-loading folder sizes
* **Drag-and-drop exclusion** – drag files/folders directly into the exclusion list
* **Real-time activity log** tracking all operations
* **Native folder picker** for easy path selection

### 📝 Smart Text Bundler
* **Automatic file merging** with customizable whitelist (30+ file extensions supported)
* **Binary detection** to skip non-text files automatically
* **Configurable size limits** (default 10MB per file, adjustable via config)
* **Blank-line removal** option for cleaner output
* **Streaming output** for large projects without memory issues
* **Token counting** with `tiktoken` integration for AI model compatibility
* **Extracted files list** – automatically generates `OutputExtractedFiles.txt` with list of processed files

### 🎯 Advanced Filtering
* **Whitelist/Blacklist system** via `exclude_me.txt` and `just_me.txt`
* **Automatic `.gitignore` sync** – patterns are merged into exclusions
* **Path-based filtering** for precise control
* **Smart exclusion matching** by name or relative path
* **Just Me filtering** – extract only specific files or folders you need

### 📊 Real-Time Metrics
* **Word count** · **Token count** · **Line count** · **File size**
* **Lazy folder size calculation** for performance
* **Live output statistics** updating as files are processed

### 🎨 Modern UI Experience
* **Tab navigation** (NamesExtractor / TextExtractor / Exclusions / Just Me / Activity Log)
* **TailwindCSS design** with crimson theme
* **Responsive layout** for all screen sizes
* **Native system dialogs** for file operations
* **Quick folder access** to view extracted files

---

## 🧰 Technology Stack

| Component     | Technology                               |
| ------------: | :--------------------------------------- |
| **Backend**   | Python 3.8+, Flask                       |
| **Frontend**  | HTML5, JavaScript, TailwindCSS           |
| **Parsing**   | tiktoken (OpenAI tokenizer)              |
| **Config**    | JSON-based configuration                 |
| **Output**    | Plain text bundled files                 |

---

## 📦 Project Structure

```
codedevour/
├── server/
│   ├── routes/           # API endpoints (text, names, lists, config)
│   ├── services/         # Business logic (metrics, cleaners, gitignore sync)
│   ├── extractors/       # Core extraction logic
│   ├── templates/        # HTML templates
│   └── app.py           # Flask application entry point
├── static/              # CSS, JS, and assets
├── config.json          # Configuration file
├── exclude_me.txt       # File exclusion list
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

---

## 🔧 Installation & Setup

### Prerequisites

* **Python 3.8 or higher** (Windows, Linux, or macOS)
* **Git** (optional, for cloning)

### Step 1: Get the Code

```bash
# Clone the repository
git clone https://github.com/Anwitch/codedevour.git
cd codedevour
```

Or download the ZIP file from GitHub and extract it.

### Step 2: Create Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- tiktoken (token counting)
- Other necessary dependencies

### Step 4: Run the Application

```bash
# Double-click or run from terminal
scripts\run_app.bat
```

The application will automatically open in your default browser at `http://127.0.0.1:5000`

If it doesn't open automatically, manually navigate to that URL.

> **Note for Windows users:** The batch script automatically activates your virtual environment and runs the app.

---

## 🎯 How to Use

### Getting Started

1. **Launch the application** by running `scripts\run_app.bat`
2. **Open your browser** to `http://127.0.0.1:5000`
3. You'll see four main tabs: **NamesExtractor**, **TextExtractor**, **Exclude Me**, and **Activity Log**

### 1. Set Your Project Path

* **Enter the path** to your project in the "Project Path" field
* Click **"Pick Folder..."** to use a native folder picker (recommended)
* Or click **"Set Path"** after typing the path manually
* The system will automatically sync patterns from `.gitignore` into your exclusion list

### 2. Explore Project Structure (NamesExtractor)

**Purpose:** View your project's file tree with sizes and statistics

1. Navigate to the **NamesExtractor** tab
2. Choose options:
   - ☑️ **Include files** – Show individual files (not just folders)
   - ☑️ **Include sizes** – Display file/folder sizes (calculated lazily)
3. Click **"Run NamesExtractor.py"**
4. **Expand folders** to explore – sizes are calculated on-demand
5. **Drag items** from the tree into the "Exclude Me" tab to exclude them

**Tip:** Folder sizes appear when you expand them, keeping the initial load fast!

### 3. Bundle Your Code (TextExtractor)

**Purpose:** Merge all code files into a single text file

1. Navigate to the **TextExtractor** tab
2. Configure output:
   - **Output Folder** – Where to save the bundled file (will prompt if empty)
   - **File Name** – Name for the output file (default: `Output.txt`)
3. Options:
   - ☑️ **Remove empty lines** – Clean up blank lines in the output
4. Click **"Run TextEXtractor.py"**
5. Watch the **streaming output** in the right panel
6. See **real-time metrics** (words · tokens · lines · bytes) in the badge

**What gets bundled?**
- Text-based files with supported extensions
- Files under 2MB in size
- Files not in your exclusion list
- Non-binary files only

**Supported file types:**
`.py .js .ts .tsx .jsx .json .md .txt .html .css .yml .yaml .toml .ini .cfg .sql .sh .bat .ps1 .c .cpp .h .hpp .java .kt .go .rs .vue .xml`

### Output Files

When you run TextExtractor, **two files are generated**:

1. **`Output.txt`** (or your custom name)
   - Location: User-specified output folder (downloaded via browser)
   - Content: Combined text content of all extracted files
   - Format: Files separated by `BA` (top border) and `WA` (bottom border) markers
   - Use: Feed to AI models, documentation, code review

2. **`OutputExtractedFiles.txt`** ✨ **Auto-generated**
   - Location: `data/output/` in the CodeDevour project directory
   - Content: List of all files that were successfully extracted
   - Format: Same as `OutputAllNames.txt` – `path; [FILE]` per line
   - Use: Quick verification, tracking what was processed, debugging filters

**Why two files?**
- `Output.txt` is the actual bundled code (can be large, 100MB+)
- `OutputExtractedFiles.txt` is lightweight metadata for quick reference
- You can verify extraction results without opening the large output file

### 4. Manage Exclusions (Exclude Me)

**Purpose:** Control which files/folders to skip during bundling

* **View/Edit** the exclusion list in the **Exclude Me** tab
* **Add items** by:
  - Dragging from the file tree
  - Typing names or patterns (one per line)
* **Save** your changes
* **Automatic sync** from `.gitignore` when you set a new path

**How exclusions work:**
- Files/folders are excluded if their **name** or **path** contains any exclusion pattern
- `.gitignore` patterns are automatically imported under `# === PATTERNS FROM .gitignore ===`
- Manual patterns are preserved above the `.gitignore` section

### 5. Use Just Me Filter (Optional)

**Purpose:** Extract only specific files or folders instead of everything

* Navigate to the **Just Me** tab (right panel)
* **Add patterns** for files/folders you want to include:
  - Filenames: `app.py`, `config.json`, `UserController.js`
  - Folder paths: `src/`, `components/`, `backend/controllers/`
  - Patterns work with **nested files** – all subdirectories are scanned
* **Leave empty** to process all files (default behavior)
* **Combines with exclusions** – excluded items are still skipped even if in Just Me list

**Example scenarios:**
- **Focus on authentication code:** Add `auth` to extract all auth-related files
- **Extract only one file:** Add exact filename like `adminApplicationController.js`
- **Process specific module:** Add `src/services/` to bundle only service layer

**Tips:**
- Just Me is **inclusive** – only specified items are processed
- Use **folder paths** to extract entire directories
- Drag items from NamesExtractor tree into Just Me tab

### 6. Monitor Activity (Activity Log)

* View **real-time logs** of all operations
* See **timestamps** for each action
* Track **errors** and **success messages**
* Monitor **processing progress**

---

## ⚙️ Configuration

### config.json

```json
{
  "TARGET_FOLDER": "C:/Users/You/YourProject",
  "NAME_OUTPUT_FILE": "OutputAllNames.txt",
  "OUTPUT_FILE": "Output.txt",
  "EXCLUDE_FILE_PATH": "exclude_me.txt"
}
```

**Configuration Options:**

* `TARGET_FOLDER` – The project directory to analyze
* `OUTPUT_FILE` – Output file path (can be changed from UI)
* `NAME_OUTPUT_FILE` – File list output path
* `EXCLUDE_FILE_PATH` – Path to exclusion list file
* `JUST_ME_FILE_PATH` – Path to inclusion filter file
* `MAX_FILE_SIZE_MB` – Maximum file size in MB (default: 10)

> The `OUTPUT_FILE` can be changed on-the-fly from the UI and will be automatically persisted to `config.json`.

### File Processing Limits

* **Maximum file size:** 10 MB per file (configurable via `MAX_FILE_SIZE_MB` in config)
* **Binary detection:** Files with >30% non-text characters are automatically skipped
* **Sample size:** 4096 bytes for binary detection
* **Performance optimizations:** 128KB chunk size for efficient I/O, 2-hour timeout for large projects

### Exclusion Rules

* Items are excluded if their **name** or **relative path** contains any pattern from `exclude_me.txt`
* Matching is case-sensitive
* Patterns use substring matching (not regex)

### Just Me (Inclusion) Rules

The **Just Me** filter allows you to extract **only specific files or folders** instead of processing everything:

* Add filenames (e.g., `app.py`, `config.json`) to extract only those files
* Add folder names (e.g., `src/`, `components/`) to extract entire directories
* Supports **nested files** – if you specify a filename, all subdirectories are scanned
* Combines with exclusion rules – excluded items are still skipped
* Leave empty to process all files (subject to exclusions)

**Example use cases:**
* Extract only controller files: Add `*Controller.js` patterns
* Focus on specific module: Add `src/auth/` to process only auth-related code
* Single file extraction: Add exact filename like `UserModel.py`

---

## 🔌 API Endpoints

| Method | Path                      | Description                                                      |
| :----: | :------------------------ | :--------------------------------------------------------------- |
| `POST` | `/set_path`               | Set project path and sync `.gitignore` patterns                  |
|  `GET` | `/pick_folder`            | Open native folder picker for project path                       |
|  `GET` | `/pick_output_folder`     | Open native folder picker for output destination                 |
|  `GET` | `/config_summary`         | Get current configuration for UI                                 |
|  `GET` | `/size?path=...`          | Calculate file/folder size (lazy loading)                        |
| `POST` | `/run_nameextractor_json` | Generate file tree as JSON (fast, no intermediate file)          |
| `POST` | `/run_nameextractor`      | Legacy mode – writes to `OutputAllNames.txt`                     |
| `POST` | `/run_textextractor`      | Bundle files with streaming output                               |
|  `GET` | `/manage_exclude_file`    | Read `exclude_me.txt` content                                    |
| `POST` | `/manage_exclude_file`    | Save `exclude_me.txt` content                                    |
|  `GET` | `/manage_just_me`         | Read `just_me.txt` content (inclusion filter)                    |
| `POST` | `/manage_just_me`         | Save `just_me.txt` content                                       |
|  `GET` | `/output_metrics`         | Get output statistics (words, tokens, lines, chars, bytes)       |

---

## 🐞 Troubleshooting

### Common Issues

**"Path is invalid or not found"**
* Use the **"Pick Folder..."** button to avoid typos
* Ensure you have read permissions for the directory
* Check that the path exists and is accessible

**"Output folder required"**
* Specify an output directory in the TextExtractor tab
* Or let the UI prompt you when running TextExtractor
* Ensure you have write permissions for the output location

**Folder sizes not appearing in NamesExtractor**
* Folder sizes are calculated **on-demand** when you expand them
* Check browser's Network tab for any failed requests to `/size?path=...`
* Ensure the target folder is accessible

**Token count looks approximate**
* Without `tiktoken` installed, counts are estimated using `chars/4`
* Install tiktoken for accurate token counting: `pip install tiktoken`

**Windows: Output file appears locked**
* Close any text editor or application holding `Output.txt`
* Ensure no other process is accessing the file
* Try running TextExtractor again

**Large projects taking too long**
* Use the exclusion list to filter out unnecessary directories (e.g., `node_modules`, `.git`)
* Enable `.gitignore` sync to automatically exclude common patterns
* Consider processing subdirectories separately

---

## 💡 Use Cases

### For Developers
* **Code review** – Bundle entire features for review
* **Documentation** – Generate snapshots of codebase state
* **Backup** – Create portable text versions of projects
* **Refactoring** – Analyze project structure before major changes

### For AI/ML Engineers
* **Model training** – Prepare code datasets
* **Token counting** – Calculate context window requirements
* **Code analysis** – Feed codebases to LLMs for analysis

### For Students & Academics
* **Assignment submission** – Bundle projects in readable format
* **Project documentation** – Generate comprehensive project overviews
* **Code study** – Create study materials from open-source projects

### For Teams
* **Knowledge sharing** – Share project structure with new team members
* **Onboarding** – Provide comprehensive project overviews
* **Audit trails** – Snapshot codebases at specific points in time

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes:** `git commit -m "Add your feature"`
5. **Push to your fork:** `git push origin feature/your-feature`
6. **Open a Pull Request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/codedevour.git
cd codedevour

# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Run tests (if available)
python -m pytest

# Start development server
scripts\run_app.bat
```

---

## 📜 License

MIT License – See `LICENSE` file for details.

---

## 🙏 Acknowledgments

* Built with [Flask](https://flask.palletsprojects.com/)
* Styled with [TailwindCSS](https://tailwindcss.com/)
* Token counting powered by [tiktoken](https://github.com/openai/tiktoken)

---

## 📞 Support

* **Issues:** [GitHub Issues](https://github.com/Anwitch/codedevour/issues)
* **Discussions:** [GitHub Discussions](https://github.com/Anwitch/codedevour/discussions)
* **Author:** [@Anwitch](https://github.com/Anwitch)

---

Made with ❤️ by **Anwitch** · *CodeDevour*

**Star this repo if you find it useful!** ⭐