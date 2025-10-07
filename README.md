# 🧭 CodeDevour – Project Viewer & Extractor

**CodeDevour** is a lightweight web-based tool that helps developers and students **visualize project structures**, **extract file contents**, and **manage excluded files** in one simple interface.  
It’s ideal for preparing **project documentation**, **source analysis**, or **academic reports**.

---

## ✨ Key Features

- 🗂️ **NamesExtractor** – Recursively lists all files and folders in your project, with optional file size display.  
- 🧾 **TextExtractor** – Merges the content of all readable text/code files into a single file (`Output.txt`) for easy documentation or archiving.  
- 🚫 **Exclude Manager** – Define ignored files/folders (e.g. `.venv`, `__pycache__`, `node_modules`, `.git`) via a simple text editor in the web UI.  
- 🖥️ **Web Interface** – Built with **Flask + TailwindCSS**, offering a clean and responsive UI accessible in your browser.  
- ⚙️ **Auto Browser Launch** – Automatically opens your default browser when the app starts.

---

## 🧰 Tech Stack

| Component | Technology |
|----------|------------|
| Backend  | Python 3.x, Flask |
| Frontend | HTML, JavaScript, TailwindCSS |
| Config   | JSON (`config.json`) |
| Output   | Combined text via `TextExtractor` |

---

## 🪄 Installation Guide

### 🔹 Prerequisites
- **Python 3.8+** installed
- Works on **Windows**, **Linux**, and **macOS**

### 🔹 1) Clone the Repository
```bash
git clone https://github.com/Anwitch/codedevour.git
cd codedevour
````

### 🔹 2) Create & Activate a Virtual Environment (venv)

#### 🪟 Windows (PowerShell/CMD)

```bash
python -m venv venv
venv\Scripts\activate
```

#### 🐧 Linux / macOS (bash/zsh)

```bash
python3 -m venv venv
source venv/bin/activate
```

> You should see the `(venv)` prefix in your terminal, indicating the environment is active.
> To leave the venv later, run: `deactivate`

### 🔹 3) Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔹 4) Run the Application

```bash
python app.py
```

The server will start and (typically) open a browser window at:

```
http://127.0.0.1:5000
```

If it doesn’t open automatically, paste the URL into your browser.

---

## 🧑‍💻 How to Use

### 1) Set Project Path

* Click **“Choose Folder…”** to pick your project directory, **or**
* Manually type the path in **Project Path** and click **Set Path**.

### 2) View Project Structure (NamesExtractor)

* Select:

  * ✅ **Include Files**
  * ✅ **Include Sizes** (optional)
* Click **“Run NamesExtractor.py”** to generate the folder tree (left panel).

### 3) Extract All Text Content (TextExtractor)

* Switch to the **TextExtractor** tab.
* Click **“Run TextEXtractor.py”**.
* The merged content will display on the right and be saved to `Output.txt`.

### 4) Manage Excluded Files/Folders

* Open the **Exclude Me** tab.
* Enter one file/folder name per line (e.g. `.git`, `node_modules`, `.venv`).
* Click **Save** to update `exclude_me.txt`.

---

## 📁 Default Project Structure

```
codedevour/
├── app.py                # Flask main app
├── NamesExtractor.py     # Folder & file lister
├── TextEXtractor.py      # Merges all readable files
├── config.json           # Paths & output configuration
├── exclude_me.txt        # Excluded files/folders
├── templates/
│   └── Tree.html         # Web interface (HTML)
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License
└── README.md             # This documentation
```

---

## ⚙️ Configuration Reference (`config.json`)

```json
{
  "TARGET_FOLDER": "C:/Users/YourName/YourProject",
  "NAME_OUTPUT_FILE": "OutputAllNames.txt",
  "OUTPUT_FILE": "Output.txt",
  "EXCLUDE_FILE_PATH": "exclude_me.txt"
}
```

You can edit this file manually or update it from the web UI.

---

## 💡 Notes

* Works seamlessly on **Windows** and **Linux**.
* The extractor automatically skips binary files, very large files (> 2 MB), and items in the exclusion list.
* Folder size calculation is done lazily for performance.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push and open a Pull Request 🎉

---

## 📜 License

Licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

**Developed with ❤️ by [Anwitch](https://github.com/Anwitch)**
*© 2025 – CodeDevour*