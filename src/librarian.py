import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from litellm import completion

from .utils import read_file, list_files, ensure_dir

PROGRAM_MD = Path("program.md")
RAW_DIR = Path("raw")
WIKI_DIR = Path("wiki")
MODEL = "ollama/llama3.2"
CHECK_INTERVAL = 8


def compile_to_wiki(raw_path: Path) -> str:
    with open(raw_path, "r", encoding="utf-8") as f:
        content = f.read()

    prompt = f"""You are an expert research librarian.
    Turn the following raw document into a clean, structured Markdown wiki page.
    - Add frontmatter with title, tags, summary, last_updated, related_pages
    - Use clear headings
    - Extract key claims and evidence
    - Suggest 3-5 backlinks to other potential wiki pages
    Raw content:
    {content[:15000]}
    """

    response = completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


def run_librarian_iteration():
    program = read_file(PROGRAM_MD)
    raw_files = [f.name for f in list_files(RAW_DIR)]
    wiki_preview = ""
    for f in list(list_files(WIKI_DIR, "*.md"))[:3]:
        content = read_file(f)
        wiki_preview += f"\n--- {f.name} ---\n{content[:700]}\n"

    prompt = f"""Current time: {datetime.now().isoformat()}

{program}

Recent raw files: {raw_files}
Current wiki preview:
{wiki_preview}

Propose the next useful action for the knowledge base.

Output exactly in this format:

REASONING:
[Your thinking]

PROPOSED_ACTION:
[compile new page | improve existing | create backlinks | etc.]

TARGET_FILE:
[filename.md or "new"]

NEW_CONTENT:
[Full Markdown if creating/updating]

WHY_THIS_IMPROVES:
[Brief reason]
"""

    try:
        response = completion(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        output = response.choices[0].message.content
        print(
            f"\n=== Librarian Iteration @ {datetime.now().strftime('%H:%M:%S')} ===\n"
        )
        print(output)
    except Exception as e:
        print(f"LLM Error: {e}")


class RawHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith((".md", ".pdf", ".txt")):
            return
        print(f"📥 New raw file: {event.src_path}")
        compile_to_wiki(Path(event.src_path))


def main():
    ensure_dir(RAW_DIR)
    ensure_dir(WIKI_DIR)

    if not PROGRAM_MD.exists():
        PROGRAM_MD.write_text("""# EvoKB Librarian Program

You are the EvoKB Librarian — a careful, precise research assistant that maintains a high-quality Markdown knowledge base.

## Core Goals
- Convert raw documents into clean, well-structured wiki pages with frontmatter, summaries, key claims, and [[backlinks]].
- Improve existing pages when new information arrives.
- Reduce duplication and create useful connections.
- Keep everything human-readable and auditable.

## Rules
- Ground every change in actual content from raw/ or wiki/.
- Never hallucinate facts.
- Prefer small, safe improvements.
- Use clear Markdown formatting.

Always check the current state of raw/ and wiki/ before proposing actions.
""")

    print("🚀 EvoKB Autoresearch Librarian started (Org: alphapebble)")
    print("Drop files into raw/ folder.\n")

    event_handler = RawHandler()
    observer = Observer()
    observer.schedule(event_handler, str(RAW_DIR), recursive=True)
    observer.start()

    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        run_librarian_iteration()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
