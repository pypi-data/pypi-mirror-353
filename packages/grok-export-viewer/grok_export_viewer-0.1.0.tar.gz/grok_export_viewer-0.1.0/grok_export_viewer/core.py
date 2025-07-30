import json
import re
import csv
import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any
import markdown as md_lib
from pygments.formatters import HtmlFormatter

def clean(name: str) -> str:
    """Sanitize string for use in filenames."""
    cleaned = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned[:100]

def sessions(json_file: Path) -> List[Dict[str, Any]]:
    """Load and parse Grok JSON export file."""
    try:
        with json_file.open(encoding="utf-8") as f:
            return json.load(f).get("conversations", [])
    except (json.JSONDecodeError, IOError) as e:
        raise ValueError(f"Failed to load JSON file: {e}")

def rows(item: Dict[str, Any], idx: int) -> Tuple[str, List[Dict[str, str]]]:
    """Extract title and messages from a conversation item."""
    title = item.get("conversation", {}).get("title", f"Untitled_{idx}")
    msgs = []
    for r in item.get("responses", []):
        resp = r.get("response", {})
        txt = (resp.get("message") or "").strip()
        if txt:
            msgs.append({"sender": resp.get("sender", "").lower(), "text": txt})
    return title, msgs

def export_markdown(conv: List[Dict[str, Any]]) -> Path:
    """Export conversations to Markdown files."""
    out = Path("data/markdown")
    out.mkdir(exist_ok=True, parents=True)
    [f.unlink() for f in out.glob("*.md")]
    for i, itm in enumerate(conv):
        title, msgs = rows(itm, i)
        if not msgs:
            continue
        fp = out / f"{i+1:03}_{clean(title)}.md"
        fp.write_text(
            "# " + title + "\n\n" + "\n\n---\n\n".join(
                f"**{m['sender'].upper()}**:\n{m['text']}" for m in msgs
            ),
            encoding="utf-8"
        )
    print("✅ Markdown ->", out.resolve())
    return out

def export_html(conv: List[Dict[str, Any]]) -> None:
    """Export conversations to HTML with a searchable index."""
    md_dir = export_markdown(conv)
    html_dir = Path("data/html")
    html_dir.mkdir(exist_ok=True, parents=True)
    css = HtmlFormatter().get_style_defs(".codehilite")
    links, search_index = [], []

    for md_f in md_dir.glob("*.md"):
        title = md_f.stem
        html_f = html_dir / (title + ".html")
        body = md_lib.markdown(
            md_f.read_text(),
            extensions=["fenced_code", "codehilite", "tables"]
        )
        html_f.write_text(
            f"""<!doctype html><html><head><meta charset='utf-8'>
<title>{title}</title><style>{css}</style></head><body>{body}</body></html>""",
            encoding="utf-8"
        )
        links.append(f"<li><a href='{html_f.name}'>{title}</a></li>")
        search_index.append({
            "title": title,
            "file": html_f.name,
            "content": re.sub(r"<[^>]+>", "", body).lower()
        })

    (html_dir / "index.html").write_text(
        f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Grok Chats</title>
<style>body{{font-family:sans-serif;padding:2rem}}
input{{padding:.5rem;width:60%;font-size:1rem;margin-bottom:1rem}}
ul{{list-style:none;padding-left:0}}li{{margin:.4rem 0}}</style></head>
<body><h2>📚 Grok Chats</h2>
<input id='s' placeholder='Search...'>
<ul id='list'>{''.join(links)}</ul>
<script>
const data = {json.dumps(search_index)};
const list = document.getElementById('list');
document.getElementById('s').oninput = e => {{
  const v=e.target.value.toLowerCase();
  list.innerHTML = data.filter(d=>d.title.toLowerCase().includes(v)||d.content.includes(v))
                       .map(d=>`<li><a href='${{d.file}}'>${{d.title}}</a></li>`).join('');
}};
</script></body></html>""",
        encoding="utf-8"
    )
    print("✅ HTML ->", html_dir.resolve())

def export_csv(conv: List[Dict[str, Any]]) -> None:
    """Export conversations to CSV files."""
    out = Path("data/csv")
    out.mkdir(exist_ok=True, parents=True)
    [f.unlink() for f in out.glob("*.csv")]
    for i, itm in enumerate(conv):
        title, msgs = rows(itm, i)
        if msgs:
            fp = out / f"{i+1:03}_{clean(title)}.csv"
            with fp.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["sender", "message"])
                w.writerows([[m["sender"], m["text"]] for m in msgs])
    print("✅ CSV ->", out.resolve())

def export_json(conv: List[Dict[str, Any]]) -> None:
    """Export conversations to JSON files."""
    out = Path("data/json")
    out.mkdir(exist_ok=True, parents=True)
    [f.unlink() for f in out.glob("*.json")]
    for i, itm in enumerate(conv):
        title, msgs = rows(itm, i)
        if msgs:
            (out / f"{i+1:03}_{clean(title)}.json").write_text(
                json.dumps(msgs, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
    print("✅ JSON ->", out.resolve())

def export_sqlite(conv: List[Dict[str, Any]]) -> None:
    """Export conversations to SQLite database."""
    db = Path("data/sqlite/grokchat.db")
    db.parent.mkdir(exist_ok=True, parents=True)
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("CREATE TABLE chat(id INTEGER PRIMARY KEY, session, sender, message)")
    for i, itm in enumerate(conv):
        _, msgs = rows(itm, i)
        cur.executemany(
            "INSERT INTO chat(session, sender, message) VALUES (?, ?, ?)",
            [(i + 1, m["sender"], m["text"]) for m in msgs]
        )
    con.commit()
    con.close()
    print("✅ SQLite ->", db.resolve())