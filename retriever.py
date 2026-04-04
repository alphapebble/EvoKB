import random
from pathlib import Path
from litellm import completion

from cluster import KnowledgeCluster, ClusterStore
from utils import read_file, list_files

MODEL = "ollama/llama3.2"


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


def monte_carlo_sample(file_path: Path, keywords: list, max_samples=8):
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    n = len(lines)

    evidences = []

    for _ in range(max_samples):
        start = random.randint(0, max(0, n - 30))
        window = "\n".join(lines[start : start + 30])

        score_prompt = (
            f"Rate relevance (0-10) of this snippet to keywords {keywords}:\n{window}"
        )
        resp = completion(
            model=MODEL, messages=[{"role": "user", "content": score_prompt}]
        )
        try:
            score = float(resp.choices[0].message.content.strip()[:2])
        except:
            score = 5.0

        if score > 4:
            evidences.append(
                {"file": str(file_path), "snippet": window, "score": score}
            )

    return sorted(evidences, key=lambda x: x["score"], reverse=True)[:5]


def query_evo_kb(query: str, wiki_dir: Path = Path("wiki")):
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


from datetime import datetime
