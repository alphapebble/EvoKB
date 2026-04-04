import random
import time
from pathlib import Path
from datetime import datetime
from litellm import completion

from evokb.cluster import KnowledgeCluster, ClusterStore
from evokb.utils import read_file, list_files, ensure_dir
from evokb.config import MODEL, RAW_DIR, WIKI_DIR, PROGRAM_MD

MAX_SAMPLES = 8
MAX_ROUNDS = 3


def extract_keywords(query: str) -> list:
    prompt = f"Extract 8-15 important keywords and phrases from this query (comma separated):\n{query}"
    resp = completion(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return [k.strip() for k in resp.choices[0].message.content.split(",")]


def simple_keyword_search(keywords: list, wiki_dir: Path, max_files=20):
    candidates = []
    for file in wiki_dir.rglob("*.md"):
        try:
            text = file.read_text(encoding="utf-8").lower()
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                candidates.append((score, str(file), text[:500]))
        except:
            pass
    candidates.sort(reverse=True)
    return candidates[:max_files]


def monte_carlo_sample(file_path: Path, keywords: list, max_samples=8, max_rounds=3):
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except:
        return []

    lines = text.splitlines()
    n = len(lines)
    if n < 10:
        return [{"file": str(file_path), "snippet": text, "score": 8.0}]

    evidences = []
    seeds = []

    for round_num in range(max_rounds):
        new_samples = []
        if round_num == 0 or not seeds:
            for _ in range(max_samples):
                start = random.randint(0, max(0, n - 40))
                window = "\n".join(lines[start : start + 40])
                new_samples.append((start, window))
        else:
            for seed in seeds[:3]:
                for _ in range(max_samples // 3):
                    offset = int(random.gauss(0, 20 * (1 - round_num * 0.3)))
                    start = max(0, min(n - 40, seed.get("start", 0) + offset))
                    window = "\n".join(lines[start : start + 40])
                    new_samples.append((start, window))

        for start, window in new_samples:
            prompt = f"Rate relevance 0-10 to keywords '{', '.join(keywords)}'. Reply ONLY with number then brief reason.\nSnippet:\n{window}"
            try:
                resp = completion(
                    model=MODEL, messages=[{"role": "user", "content": prompt}]
                )
                score_str = resp.choices[0].message.content.strip()[:10]
                score = float("".join(c for c in score_str if c.isdigit() or c == "."))
            except:
                score = 5.0

            if score > 4.0:
                evidences.append(
                    {
                        "file": str(file_path),
                        "snippet": window,
                        "score": score,
                        "start": start,
                    }
                )

        seeds = sorted(evidences, key=lambda x: x["score"], reverse=True)[:5]
        if seeds and seeds[0]["score"] > 8.5:
            break

    return sorted(evidences, key=lambda x: x["score"], reverse=True)[:8]


def run_autoresearch_iteration():
    """Autoresearch-style iteration: propose → evaluate → apply"""
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

Propose the next improvement to the knowledge base.

Output exactly in this format:

REASONING:
[Your thinking about what needs to be done]

PROPOSED_ACTION:
[compile new page | improve existing | create cluster | fix links | etc.]

TARGET_FILE:
[filename.md or "new"]

NEW_CONTENT:
[Full Markdown for new/updated file]

EVALUATION_CRITERIA:
[How we will know if this is better]
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
            f"\n=== Autoresearch Iteration @ {datetime.now().strftime('%H:%M:%S')} ===\n"
        )
        print(output)
        return output
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def compile_to_wiki(raw_path: Path, wiki_dir: Path = None) -> str:
    content = read_file(raw_path)
    if wiki_dir is None:
        wiki_dir = WIKI_DIR

    wiki_dir = Path(wiki_dir)
    wiki_dir.mkdir(exist_ok=True)

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
    wiki_content = response.choices[0].message.content

    # Save to wiki
    output_file = wiki_dir / raw_path.name
    output_file.write_text(wiki_content)
    print(f"Saved wiki page: {output_file}")

    return wiki_content


def query_evo_kb(query: str, wiki_dir: Path = None):
    if wiki_dir is None:
        wiki_dir = WIKI_DIR

    store = ClusterStore()

    similar = store.find_similar(query)
    if similar:
        cluster = similar[0][1]
        cluster.use_count += 1
        cluster.last_used = datetime.now().isoformat()
        cluster.history.append(query)
        store.save(cluster)
        return cluster.summary, cluster

    keywords = extract_keywords(query)
    candidates = simple_keyword_search(keywords, wiki_dir)

    all_evidences = []
    for _, file_path_str, _ in candidates:
        file_path = Path(file_path_str)
        samples = monte_carlo_sample(file_path, keywords)
        all_evidences.extend(samples)

    evidence_text = "\n\n".join([e["snippet"] for e in all_evidences[:6]])
    synth_prompt = f"""Query: {query}

Relevant evidence:
{evidence_text}

Synthesize a clear, evidence-backed answer in Markdown. Include confidence (0-100) and list sources."""

    resp = completion(model=MODEL, messages=[{"role": "user", "content": synth_prompt}])
    answer = resp.choices[0].message.content

    cluster = KnowledgeCluster(query, all_evidences, answer, confidence=80)
    store.save(cluster)

    return answer, cluster


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

    print("🚀 EvoKB Autoresearch Librarian starting...")
    print("Drop files into raw/ folder.\n")

    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        run_autoresearch_iteration()
        time.sleep(8)


if __name__ == "__main__":
    main()
