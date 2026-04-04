import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from evokb.config import CHECK_INTERVAL, RAW_DIR, WIKI_DIR, PROGRAM_MD
from evokb.utils import ensure_dir, read_file
from evokb.core.retriever import compile_to_wiki, run_autoresearch_iteration
from evokb.evaluator import score_change, apply_change, revert_change


class RawHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith((".md", ".pdf", ".txt")):
            return
        print(f"📥 New raw file: {event.src_path}")
        compile_to_wiki(Path(event.src_path))


def parse_proposed_action(output: str) -> dict:
    """Parse the LLM output to extract action details"""
    result = {"action": None, "target": None, "content": None, "reasoning": None}

    sections = ["REASONING:", "PROPOSED_ACTION:", "TARGET_FILE:", "NEW_CONTENT:"]
    current_section = None

    for line in output.split("\n"):
        line = line.strip()
        if line in sections:
            current_section = line.lower().replace(":", "")
            result[current_section] = ""
        elif current_section and line:
            result[current_section] += line + "\n"

    for key in result:
        if result[key]:
            result[key] = result[key].strip()

    return result


def run_safe_iteration():
    """Propose → Evaluate → Apply → Revert loop"""
    output = run_autoresearch_iteration()
    if not output:
        return

    parsed = parse_proposed_action(output)

    if not parsed.get("action") or not parsed.get("target"):
        print("No valid action parsed")
        return

    target_file = WIKI_DIR / parsed["target"] if parsed["target"] != "new" else None

    if target_file and target_file.exists():
        old_content = read_file(target_file)
        new_content = parsed.get("content", "")

        if new_content:
            print(f"\n📋 Evaluating change to {parsed['target']}...")
            eval_result = score_change(
                new_content, ["clarity", "grounding", "coverage", "backlinks"]
            )

            print(f"   Scores: {eval_result.get('scores', {})}")
            print(f"   Overall: {eval_result.get('overall', 0)}/10")
            print(f"   Passed: {eval_result.get('passed', False)}")

            if eval_result.get("passed", False):
                if apply_change(target_file, new_content):
                    print(f"✅ Applied change to {parsed['target']}")
                else:
                    print("❌ Failed to apply change")
            else:
                print("❌ Change did not pass evaluation threshold")
    elif parsed["target"] == "new" and parsed.get("content"):
        new_path = WIKI_DIR / "new_page.md"
        if apply_change(new_path, parsed["content"]):
            print(f"✅ Created new page")


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

## Self-Improvement Loop
Follow the closed-loop pipeline:

1. **Failure Mining** — Actively identify issues (inconsistent formatting, broken backlinks, weak summaries, duplicate content)
2. **Evaluation Candidates** — Group similar issues into improvement categories
3. **Optimization Loop** — Propose → Evaluate → Apply → Revert if needed (require ≥80% pass rate)
4. **Regression Suite** — Track resolved issues as guardrails

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
        run_safe_iteration()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
