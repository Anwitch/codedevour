# 🧭 CodeDevour – Intelligent Codebase Bundler & Explorer

**CodeDevour** is a powerful web-based tool for **exploring project structure**, **bundling code files**, and **managing file exclusions** through an intuitive interface. Transform any codebase into a single, well-organized document perfect for documentation, code review, AI analysis, or academic purposes.

---

## ✨ Key Features

### 🌍 Multi-Language Code Visualizer
- **13+ Languages Supported**: Full support for Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, PHP, and more.
- **Smart Parsing**: AST-based for Python, JS/TS for high accuracy; regex for others.
- **Dependency Analysis**: Extracts `import`/`export` and `require` statements to map module dependencies.
- **Dynamic Alias Resolution**: Automatically detects and resolves path aliases from `tsconfig.json` or `jsconfig.json`.
- **Interactive Visualization**: Explore code structure and dependencies with an interactive graph.

### 📂 Interactive Project Explorer
- **Visual File Tree**: Lazy-loading folder sizes for fast performance.
- **Drag-and-Drop Filtering**: Easily exclude files or folders by dragging them to the exclusion list.

### 📝 Smart Text Bundler
- **Automatic File Merging**: Bundles code into a single text file, supporting 30+ extensions.
- **Advanced Filtering**: Whitelist/blacklist files and sync with `.gitignore`.
- **Real-Time Metrics**: Live token, word, and line counts.

---

## 🧰 Technology Stack

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, JavaScript, D3.js
- **Parsing**: Esprima (JavaScript), AST (Python), Tiktoken (OpenAI)

---

## 🔧 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Anwitch/codedevour.git
   cd codedevour
   ```
2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   # Windows
   scripts\run_app.bat
   
   # Linux/macOS
   python server/app.py
   ```
   The application will open automatically at `http://127.0.0.1:5000`.

---

## 🎯 How to Use

1. **Launch the application** and open it in your browser.
2. **Set Project Path**: Enter the path to your project and click "Set Path".
3. **Explore**: Use the **NamesExtractor** to view the file tree or the **Code Explorer** to visualize dependencies.
4. **Bundle**: Use the **TextExtractor** to merge code into a single file.
5. **Filter**: Manage exclusions and inclusions in the **Exclude Me** and **Just Me** tabs.

---

## ⚙️ Configuration

The application is designed to be portable and works out of the box. For advanced configurations, such as path aliases in JavaScript/TypeScript projects, ensure a `tsconfig.json` or `jsconfig.json` is present in your project root.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and open a pull request.

---

## 📜 License

MIT License – See the `LICENSE` file for details.