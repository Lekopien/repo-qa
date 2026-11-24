"""Clone a repo, split files into line-numbered chunks, store in SQLite FTS5 (BM25)."""
import re
import sqlite3
import subprocess
import tempfile
from pathlib import Path

DB_PATH = "repoqa.db"
CHUNK_LINES = 40
OVERLAP = 8
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "__pycache__", ".next"}
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".c", ".h",
            ".cpp", ".cs", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".html", ".css", ".sh"}


def connect(path: str = DB_PATH) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path, start_line UNINDEXED, end_line UNINDEXED, body)")
    return db


def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in TEXT_EXT and not (set(p.parts) & SKIP_DIRS) and p.stat().st_size < 200_000:
            yield p


def index_repo(url: str, db_path: str = DB_PATH) -> int:
    db = connect(db_path)
    db.execute("DELETE FROM chunks")
    count = 0
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "--depth", "1", url, tmp], check=True, capture_output=True)
        root = Path(tmp)
        for f in iter_files(root):
            lines = f.read_text(errors="ignore").splitlines()
            step = CHUNK_LINES - OVERLAP
            for i in range(0, max(len(lines), 1), step):
                chunk = lines[i : i + CHUNK_LINES]
                if not chunk:
                    break
                db.execute(
                    "INSERT INTO chunks VALUES (?,?,?,?)",
                    (str(f.relative_to(root)), i + 1, i + len(chunk), "\n".join(chunk)),
                )
                count += 1
    db.commit()
    return count


def search(query: str, k: int = 8, db_path: str = DB_PATH):
    db = connect(db_path)
    terms = " OR ".join(w for w in re.findall(r"\w+", query) if len(w) > 2)
    if not terms:
        return []
    return db.execute(
        "SELECT path, start_line, end_line, body FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks) LIMIT ?",
        (terms, k),
    ).fetchall()
