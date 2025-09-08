# VibeTeks: Project Viewer & Extractor
**VibeTeks** is a web-based tool designed for developers and IT students to easily browse and analyze the structure and content of their projects. It's ideal for analyzing a codebase, generating documentation, or preparing projects for a presentation.

## Key Features
- **Interactive Structure Viewer**: Displays the project's folder structure visually with the option to include file sizes.
- **Text Extractor**: Merges the content of all text files (e.g., code files) into a single, readable output file.
- **Exclusion Management**: Allows you to specify irrelevant files and folders to be ignored, such as `__pycache__` or `venv`, via an `exclude_me.txt` file.
- **Simple Web Interface**: Built with **Flask**, the tool provides an intuitive user interface accessible through a web browser.

---

## Technology
- **Backend**: Python 3.x, Flask 
- **Frontend**: HTML, JavaScript, Tailwind CSS 

---

## How to Install and Run

### Prerequisites
- **Python 3.x** installed on your system.

### Steps
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Anwitch/Vibe-Teks.git
    cd Vibe-Teks
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```

4.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

---

## Usage
### NamesExtractor
- Enter your project's folder path in the `Path Project` field.
- Check the **"Sertakan File"** (Include Files) and/or **"Sertakan Ukuran"** (Include Size) options as needed.  
  *(Note: UI labels are in Bahasa Indonesia)*
- Click the **"Jalankan NamesExtractor.py"** (Run NamesExtractor.py) button to display the project structure.

### TextExtractor
- Click the **"Jalankan TextEXtractor.py"** (Run TextEXtractor.py) button to merge all file contents. The output will be displayed in the right panel.

### Manage Exclusion List
- Switch to the **"Exclude Me"** tab.
- Add the names of files or folders you want to exclude (one name per line).
- Click **"Simpan"** (Save) to update the `exclude_me.txt` file.

---

## Contribution
Contributions are highly appreciated!  
If you'd like to improve this tool, please fork the repository and submit a pull request.

---

## License
This project is licensed under the **MIT License**.