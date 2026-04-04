import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import CHECK_INTERVAL, RAW_DIR, WIKI_DIR, PROGRAM_MD
from .utils import ensure_dir
from .retriever import compile_to_wiki, run_autoresearch_iteration


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

You are the EvoKB Librarian — an expert research assistant that maintains a high-quality, interlinked Markdown knowledge base.

## Goals
- Turn raw documents into clean, structured wiki pages with frontmatter, summaries, key claims, and backlinks.
- Improve existing wiki pages when new information arrives.
- Create and evolve Knowledge Clusters for fast, reusable answers.
- Keep everything human-auditable and editable in Obsidian/VS Code.

## Rules
- Never hallucinate facts — always ground in raw or existing wiki content.
- Use clear Markdown: headings, lists, tables, [[backlinks]].
- When proposing changes, output a diff or full new version + reasoning.
- Evaluate your own changes: does it improve clarity, reduce duplication, add useful connections?
""")

    print("🚀 EvoKB Autoresearch Librarian started")
    print("Drop files into raw/ folder.\n")

    event_handler = RawHandler()
    observer = Observer()
    observer.schedule(event_handler, str(RAW_DIR), recursive=True)
    observer.start()

    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        run_autoresearch_iteration()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
