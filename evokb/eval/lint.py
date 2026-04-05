"""Wiki health checks: contradictions, stale claims, orphans, source-grounding."""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

from evokb.core.utils import read_file, list_files
from evokb.core.config import WIKI_DIR


def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    fm_lines = parts[1].strip().split("\n")
    for line in fm_lines:
        if ":" in line:
            key, val = line.split(":", 1)
            frontmatter[key.strip()] = val.strip().strip('"').strip("'")

    return frontmatter, parts[2]


def extract_links(content: str) -> Set[str]:
    """Extract wiki links from markdown [[page]] format."""
    return set(re.findall(r"\[\[([^\]|]+)", content))


def extract_claims(content: str) -> List[str]:
    """Extract factual claims ( sentences with specific markers)."""
    claims = []
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("#") or line.startswith("```"):
            continue
        if len(line) > 50 and any(
            marker in line.lower()
            for marker in [
                "is a",
                "are",
                "was",
                "were",
                "defined as",
                "refers to",
                "means",
            ]
        ):
            claims.append(line)
    return claims


def check_orphans(wiki_dir: Path = None) -> Dict:
    """Find pages with no inbound links."""
    wiki_dir = wiki_dir or WIKI_DIR
    pages = {}
    inbound_links = defaultdict(set)

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        title = md_file.stem
        pages[title] = content

        links = extract_links(content)
        for link in links:
            inbound_links[link].add(title)

    orphans = [title for title in pages if title not in inbound_links]

    return {"orphans": orphans, "total_pages": len(pages), "orphan_count": len(orphans)}


def check_stale_claims(wiki_dir: Path = None, max_age_days: int = 30) -> Dict:
    """Find claims that may be outdated based on timestamps."""
    wiki_dir = wiki_dir or WIKI_DIR
    stale_claims = []

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        fm, body = extract_frontmatter(content)

        updated = fm.get("updated")
        if not updated:
            stale_claims.append(
                {
                    "file": md_file.name,
                    "issue": "no_updated_timestamp",
                    "severity": "medium",
                }
            )
        else:
            try:
                updated_date = datetime.fromisoformat(updated.replace("Z", ""))
                if datetime.now() - updated_date > timedelta(days=max_age_days):
                    stale_claims.append(
                        {
                            "file": md_file.name,
                            "issue": "not_updated_in_days",
                            "days_old": (datetime.now() - updated_date).days,
                            "severity": "low",
                        }
                    )
            except ValueError:
                stale_claims.append(
                    {
                        "file": md_file.name,
                        "issue": "invalid_timestamp_format",
                        "severity": "medium",
                    }
                )

    return {"stale_claims": stale_claims, "count": len(stale_claims)}


def check_source_grounding(wiki_dir: Path = None) -> Dict:
    """Check that claims are grounded in sources."""
    wiki_dir = wiki_dir or WIKI_DIR
    ungrounded = []

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        fm, body = extract_frontmatter(content)

        has_sources = bool(fm.get("sources") or fm.get("source"))
        has_source_tag = bool(fm.get("source"))

        claims = extract_claims(body)
        if claims and not has_sources and not has_source_tag:
            ungrounded.append(
                {
                    "file": md_file.name,
                    "claim_count": len(claims),
                    "issue": "no_source_attribution",
                }
            )

    return {"ungrounded_pages": ungrounded, "count": len(ungrounded)}


def check_contradictions(wiki_dir: Path = None) -> Dict:
    """Find potential contradictions between pages."""
    wiki_dir = wiki_dir or WIKI_DIR

    claim_index = defaultdict(list)
    files_by_keyword = defaultdict(list)

    keywords = {
        "ai": ["ai", "artificial intelligence", "llm", "gpt"],
        "knowledge": ["knowledge", "graph", "database"],
        "model": ["model", "training", "training data"],
    }

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        content_lower = content.lower()

        for topic, kw_list in keywords.items():
            if any(kw in content_lower for kw in kw_list):
                files_by_keyword[topic].append(md_file.stem)

    potential_conflicts = []

    contradiction_patterns = [
        (r"not\s+\w+", r"\w+\s+never"),
        (r"always", r"never"),
        (r"impossible", r"possible"),
        (r"all", r"none"),
        (r"every", r"no"),
    ]
    patterns = list(contradiction_patterns)

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        for pos_pattern, neg_pattern in patterns:
            if re.search(pos_pattern, content, re.I) and re.search(
                neg_pattern, content, re.I
            ):
                potential_conflicts.append(
                    {
                        "file": md_file.name,
                        "pattern": f"{pos_pattern} vs {neg_pattern}",
                        "issue": "self_contradiction",
                    }
                )
                break

    return {
        "potential_conflicts": potential_conflicts,
        "count": len(potential_conflicts),
    }


def run_lint(wiki_dir: Path = None) -> Dict:
    """Run all lint checks."""
    wiki_dir = wiki_dir or WIKI_DIR

    orphans = check_orphans(wiki_dir)
    stale = check_stale_claims(wiki_dir)
    grounding = check_source_grounding(wiki_dir)
    contradictions = check_contradictions(wiki_dir)

    issues = []
    issues.extend(
        [{**o, "type": "orphan"} for o in [{"file": f} for f in orphans["orphans"]]]
    )
    issues.extend([{**s, "type": "stale"} for s in stale["stale_claims"]])
    issues.extend([{**g, "type": "ungrounded"} for g in grounding["ungrounded_pages"]])
    issues.extend(
        [{**c, "type": "contradiction"} for c in contradictions["potential_conflicts"]]
    )

    return {
        "orphans": orphans,
        "stale_claims": stale,
        "source_grounding": grounding,
        "contradictions": contradictions,
        "total_issues": len(issues),
        "issues": issues,
        "health_score": max(0, 100 - len(issues) * 10),
    }


def print_lint_report(report: Dict):
    """Print a formatted lint report."""
    print("\n" + "=" * 60)
    print("WIKI HEALTH REPORT")
    print("=" * 60)

    print(f"\n[HEALTH] Score: {report['health_score']}/100")
    print(f"Total Issues: {report['total_issues']}")

    print("\n--- ORPHANS (no inbound links) ---")
    orphans = report["orphans"]["orphans"]
    if orphans:
        for o in orphans[:10]:
            print(f"  - {o}")
    else:
        print("  None")

    print("\n--- STALE (not recently updated) ---")
    stale = report["stale_claims"]["stale_claims"]
    if stale:
        for s in stale[:10]:
            print(f"  - {s['file']}: {s['issue']}")
    else:
        print("  None")

    print("\n--- UNGROUNDED (no source attribution) ---")
    ungrounded = report["source_grounding"]["ungrounded_pages"]
    if ungrounded:
        for u in ungrounded[:10]:
            print(f"  - {u['file']}: {u['claim_count']} claims without source")
    else:
        print("  All pages have source attribution")

    print("\n--- CONTRADICTIONS ---")
    conflicts = report["contradictions"]["potential_conflicts"]
    if conflicts:
        for c in conflicts[:10]:
            print(f"  - {c['file']}: {c['pattern']}")
    else:
        print("  None detected")

    print()


if __name__ == "__main__":
    report = run_lint()
    print_lint_report(report)
