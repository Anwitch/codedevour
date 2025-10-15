# ai_digest.py
import os, re, json, math, zipfile, datetime, tempfile, hashlib
from typing import List, Dict, Tuple, Optional

# =========================
# Tokenizer & Utilities
# =========================
def _get_encoder_for_model(model_target: str):
    """
    Pilih encoder tiktoken berdasarkan model_target.
    Fallback aman: cl100k_base.
    """
    try:
        import tiktoken
    except Exception:
        return None

    model = (model_target or "").lower()
    # mapping ringan & aman
    # - o200k_base untuk model konteks sangat besar (mis. GPT-4.1/4o long context)
    # - cl100k_base untuk mayoritas (4/4o/mini)
    try:
        if any(k in model for k in ["o200k", "128k", "200k", "4.1"]):
            return tiktoken.get_encoding("o200k_base")
        # default
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None

def _safe_len_tokens(enc, text: str) -> int:
    if enc:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    return math.ceil(len(text) / 4)

def _lang_by_ext(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    mapping = {
        ".py":"python",".js":"javascript",".ts":"typescript",".tsx":"tsx",".jsx":"jsx",".json":"json",".md":"markdown",
        ".txt":"text",".html":"html",".css":"css",".yml":"yaml",".yaml":"yaml",".toml":"toml",".ini":"ini",".cfg":"ini",
        ".sql":"sql",".sh":"bash",".bat":"bat",".ps1":"powershell",".c":"c",".cpp":"cpp",".h":"c",".hpp":"cpp",
        ".java":"java",".kt":"kotlin",".go":"go",".rs":"rust",".vue":"vue",".xml":"xml",".prisma":"prisma",".env":"env"
    }
    return mapping.get(ext, (ext[1:] if ext.startswith(".") else "text") or "text")

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()

# =========================
# Parsing BA/WA
# =========================
def parse_ba_wa(output_text: str) -> List[Dict]:
    """
    Format:
      BA
      'path/to/file'
      <contents>
      WA
    """
    lines = output_text.splitlines()
    items = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "BA" and i + 1 < len(lines):
            m = re.match(r"^'(.*)'$", lines[i+1].strip())
            if m:
                path = m.group(1)
                j = i + 2
                buf = []
                while j < len(lines) and lines[j].strip() != "WA":
                    buf.append(lines[j])
                    j += 1
                content = "\n".join(buf).rstrip("\n")
                items.append({
                    "path": path,
                    "lang": _lang_by_ext(path),
                    "content": content
                })
                i = j + 1
                continue
        i += 1
    return items

# =========================
# Summaries & API Map
# =========================
def one_line_summary(path: str, content: str) -> str:
    """
    Ringkasan 1 kalimat heuristik:
      - Ambil baris docstring/comment/heading pertama yang non-empty
      - Jika tak ada, kembalikan nama file
    """
    # coba docstring python
    m = re.search(r'("""|\'\'\')\s*(.+?)\s*\1', content, re.S)
    if m:
        s = m.group(2).strip().splitlines()[0].strip()
        if s:
            return s[:160]

    # komentar umum // # <!-- -->
    for line in content.splitlines():
        L = line.strip()
        if not L:
            continue
        if L.startswith(("#","//","<!--")):
            L = re.sub(r"^(\#|\s*//\s*|<!--\s*|\s*-->\s*)", "", L).strip()
            if L:
                return L[:160]
        # heading markdown
        if L.startswith("#"):
            return L.lstrip("#").strip()[:160]
    # fallback: nama file
    return os.path.basename(path)

def collect_api_map(items: List[Dict]) -> List[str]:
    """
    Kumpulkan endpoint sederhana:
      - Flask: @app.route('/x', methods=['GET'])
      - Express: app.get('/x'), router.post('/y')
      - FastAPI: @app.get('/x')
    Output: list string "METHOD PATH (file)"
    """
    rows = []
    rx = [
        # Flask/FastAPI decorators
        (r"@app\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", 1, 2),
        (r"@(?:router|api)\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", 1, 2),
        # Flask route with route()
        (r"@app\.route\(\s*['\"]([^'\"]+)['\"]\s*(?:,.*methods\s*=\s*\[([^\]]+)\])?", None, 1),
        # Express
        (r"\b(app|router)\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", 2, 3),
    ]
    for it in items:
        p = it["path"]
        c = it["content"]
        for pat, group_method, group_path in rx:
            for m in re.finditer(pat, c):
                if group_method is None:
                    # Flask route() tanpa method -> treat as GET
                    method = "GET"
                    path = m.group(group_path)
                else:
                    method = m.group(group_method).upper()
                    path = m.group(group_path)
                rows.append(f"{method:6s} {path}    ({os.path.basename(p)})")
    # dedup
    rows = list(dict.fromkeys(rows))
    return rows[:300]  # batasi

# =========================
# Truncation
# =========================
def smart_truncate(enc, text: str, max_token: int,
                   head_lines: int = 200, tail_lines: int = 120) -> Tuple[str, bool]:
    toks = _safe_len_tokens(enc, text)
    if toks <= max_token:
        return text, False
    ls = text.splitlines()
    # adaptif jika file sangat besar
    if toks > max_token * 2:
        head_lines = max(80, head_lines // 2)
        tail_lines = max(60, tail_lines // 2)
    head = ls[:head_lines]
    tail = ls[-tail_lines:] if len(ls) > tail_lines else []
    truncated = "\n".join(head + ["", "// … truncated …", ""] + tail)
    if _safe_len_tokens(enc, truncated) > max_token:
        target_chars = max_token * 4
        truncated = truncated[:target_chars] + "\n// … truncated …\n"
    return truncated, True

# =========================
# Build Digest (STREAMING ZIP)
# =========================
def build_digest_to_zipfile(items: List[Dict], model: str, max_tokens_per_chunk: int) -> str:
    """
    Streaming ZIP langsung ke disk (tempfile). Return absolute zip_path.
    - Menambahkan chunk 0000-overview (hard split)
    - INDEX.md kaya (Chunk + Summary + Top 20 by tokens)
    """
    enc = _get_encoder_for_model(model)

    # 1) Klasifikasi overview vs non-overview
    def is_overview_path(p: str) -> bool:
        l = p.replace("\\","/").lower()
        base = os.path.basename(l)
        if base in ("readme", "readme.md", "readme.txt"): return True
        if "readme" in base: return True
        if base in (".env.example","env.example"): return True
        if base.endswith(".prisma") or base.endswith(".sql"): return True
        if base == "dockerfile" or base.endswith("/dockerfile"): return True
        if "architecture" in l or "arsitektur" in l: return True
        return False

    overview_files = []
    others = []
    for it in items:
        (overview_files if is_overview_path(it["path"]) else others).append(it)

    # Urutan lainnya: backend → frontend → lain (heuristik ringan)
    def prio(x):
        p = x["path"].replace("\\","/").lower()
        if any(k in p for k in ["/app.py","/main.py","/server.","/manage.py","/routes","/controllers","/router"]):
            return (1, p)
        if any(k in p for k in ["/pages/","/components/","next.config","vite.config",".tsx",".jsx"]):
            return (2, p)
        return (3, p)

    others_sorted = sorted(others, key=prio)
    items_sorted = overview_files + others_sorted  # hanya untuk penomoran ringkas

    # 2) Siapkan ZIP path
    tmpf = tempfile.NamedTemporaryFile(prefix="ai-digest-", suffix=".zip", delete=False)
    tmpf.close()
    zip_path = tmpf.name

    index_rows = []   # utk tabel INDEX.md
    file2chunk = {}   # peta file → no chunk
    file_meta = []    # simpan (path, lang, loc, tokens, summary, sha)

    # Helper tulis chunk
    def write_chunk(zf: zipfile.ZipFile, idx: int, content: str) -> str:
        name = f"chunks/chunk-{idx:04d}.txt"
        zf.writestr(name, content)
        return name

    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 3) CHUNK 0000 - OVERVIEW (hard split)
        api_lines = collect_api_map(items)
        overview_blocks = []
        # Persiapkan konten API lines
        api_content = api_lines if api_lines else ["(no routes detected)"]
        
        overview_intro = [
            "### OVERVIEW",
            "",
            "- This chunk aggregates README/docs, env example, schema (Prisma/SQL), Dockerfile, and a quick API map.",
            "- Start here to understand the project at a glance.",
            "",
            "#### API MAP (quick scan)",
            "```"
        ] + api_content + [
            "```",
            ""
        ]
        overview_blocks.append("\n".join(overview_intro))

        # masukkan file overview
        for it in overview_files:
            path, lang, content = it["path"], it["lang"], it["content"]
            loc = content.count("\n") + (0 if content.endswith("\n") else 1)
            toks = _safe_len_tokens(enc, content)
            summ = one_line_summary(path, content)
            sha = _sha256(content)

            meta = [
                "BA",
                f"'{path}'",
                "# META:",
                f"# lang: {lang}",
                f"# loc: {loc}",
                f"# tokens: {toks}",
                f"# summary: {summ}"
            ]
            overview_blocks.append("\n".join(meta) + "\n" + content + "\nWA\n")

            file_meta.append((path, lang, loc, toks, summ, sha))

        # tulis chunk 0000
        chunk0_content = "\n".join(overview_blocks).rstrip("\n")
        chunk_index = 0
        chunk_paths = [write_chunk(zf, chunk_index, chunk0_content)]

        # tandai overview file berada di chunk 0
        for it in overview_files:
            file2chunk[it["path"]] = 0

        # 4) Chunking sisanya (token-aware + truncation cerdas)
        cur_buf = []
        cur_tok = 0
        chunk_no = 1  # setelah 0000
        half = max_tokens_per_chunk // 2

        def flush():
            nonlocal cur_buf, cur_tok, chunk_no
            if not cur_buf:
                return
            chunk_paths.append(write_chunk(zf, chunk_no, "\n".join(cur_buf).rstrip("\n")))
            chunk_no += 1
            cur_buf = []
            cur_tok = 0

        for it in others_sorted:
            path, lang, content = it["path"], it["lang"], it["content"]
            loc = content.count("\n") + (0 if content.endswith("\n") else 1)
            toks = _safe_len_tokens(enc, content)
            summ = one_line_summary(path, content)
            sha = _sha256(content)

            # truncate file besar agar tetap masuk chunk
            body, did_trunc = smart_truncate(enc, content, half)
            meta = [
                "BA",
                f"'{path}'",
                "# META:",
                f"# lang: {lang}",
                f"# loc: {loc}",
                f"# tokens: {toks}",
                f"# summary: {summ}",
            ]
            if did_trunc:
                meta.append("# note: truncated")

            block = "\n".join(meta) + "\n" + body + "\nWA\n"
            block_tok = _safe_len_tokens(enc, block)

            if cur_tok + block_tok > max_tokens_per_chunk and cur_buf:
                flush()

            # Jika masih lebih besar dari ukuran chunk, potong lagi kasar
            if block_tok > max_tokens_per_chunk:
                block, _ = smart_truncate(enc, block, max_tokens_per_chunk - 512)
                block_tok = _safe_len_tokens(enc, block)

            if not cur_buf:
                # file pertama di chunk baru → tandai mapping chunk
                file2chunk[path] = chunk_no
            else:
                # kalau file menempati chunk yang sama
                file2chunk[path] = chunk_no

            cur_buf.append(block)
            cur_tok += block_tok

            file_meta.append((path, lang, loc, toks, summ, sha))

        flush()

        # 5) manifest.json
        manifest = {
            "version": "1.1",
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "model_target": model,
            "chunks": [{"name": cp} for cp in chunk_paths],
            "files_total": len(items_sorted),
            "notes": [
                "0000-overview is guaranteed and should be read first.",
                "BA/WA delimit file blocks; META header gives quick facts per file."
            ]
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

        # 6) INDEX.md kaya: File | Lang | LOC | Tokens | Chunk | Summary
        index_lines = [
            "# AI Digest Index",
            "",
            "| File | Lang | LOC | Tokens | Chunk | Summary |",
            "| ---- | ---- | --- | ------ | ----- | ------- |",
        ]
        # siapkan Top 20 by tokens
        top20 = sorted(file_meta, key=lambda x: x[3], reverse=True)[:20]

        for (path, lang, loc, toks, summ, sha) in file_meta:
            ch = file2chunk.get(path, "-")
            index_lines.append(f"| `{path}` | {lang} | {loc} | {toks} | {ch} | {summ.replace('|','/')} |")

        index_lines += [
            "",
            "## Top 20 Files by Tokens",
            "",
            "| Rank | File | Tokens | Lang | Chunk |",
            "| ---- | ---- | ------ | ---- | ----- |",
        ]
        for i, (path, lang, loc, toks, summ, sha) in enumerate(top20, start=1):
            ch = file2chunk.get(path, "-")
            index_lines.append(f"| {i} | `{path}` | {toks} | {lang} | {ch} |")

        zf.writestr("INDEX.md", "\n".join(index_lines))

        # 7) HOW_TO_USE.md
        how = """# How to Use

1) Start with `manifest.json` then open `chunks/chunk-0000.txt` (overview).
2) Do **not** read all chunks at once. Open only the chunk relevant to your task.
3) Each file block is wrapped by BA/WA with a META header: lang, LOC, tokens, and summary.
"""
        zf.writestr("HOW_TO_USE.md", how)

    return zip_path