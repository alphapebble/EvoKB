"""
EvoKB Hermes - Supervisor/Review Agent

Reviews wiki articles before they go live.
Scores accuracy, quality, and decides what persists.

This is the "review gate" between drafts and live knowledge.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import re

DRAFTS_DIR = Path("wiki_drafts")
LIVE_DIR = Path("wiki")
SCORES_FILE = Path("evokb_article_scores.json")


class Hermes:
    """
    Review gate for wiki articles.

    Scores articles before they enter the permanent brain.
    Clean outputs get promoted, bad ones die in drafts.
    """

    def __init__(self, drafts_dir: Path = DRAFTS_DIR, live_dir: Path = LIVE_DIR):
        self.drafts_dir = drafts_dir
        self.live_dir = live_dir
        self.scores = self._load_scores()

        # Create dirs if needed
        self.drafts_dir.mkdir(exist_ok=True)

    def _load_scores(self) -> Dict:
        if SCORES_FILE.exists():
            return json.loads(SCORES_FILE.read_text())
        return {"articles": {}, "history": []}

    def _save_scores(self):
        SCORES_FILE.write_text(json.dumps(self.scores, indent=2))

    def score_article(self, content: str) -> Dict[str, float]:
        """Score an article on multiple dimensions."""
        scores = {}

        # 1. Length check (too short = likely incomplete)
        word_count = len(content.split())
        scores["length"] = min(1.0, word_count / 200) if word_count < 500 else 1.0

        # 2. Structure (has headers, sections)
        has_headers = bool(re.search(r"^#{1,3}\s+", content, re.MULTILINE))
        scores["structure"] = 1.0 if has_headers else 0.3

        # 3. Factual density (contains specific info, not just fluff)
        has_numbers = bool(re.search(r"\d+", content))
        has_technical = bool(
            re.search(r"(API|function|class|method|system)", content, re.I)
        )
        scores["content_quality"] = (
            0.5 + (0.25 if has_numbers else 0) + (0.25 if has_technical else 0)
        )

        # 4. No obvious hallucinations (check for suspicious claims)
        hallucination_flags = [
            "100% accurate",
            "always works",
            "guaranteed",
            "proven to be",
        ]
        has_suspicious = any(flag in content.lower() for flag in hallucination_flags)
        scores["credibility"] = 0.5 if has_suspicious else 1.0

        # 5. Source attribution
        has_source = bool(
            re.search(r"(source:|from:|reference:|based on)", content, re.I)
        )
        scores["attribution"] = 1.0 if has_source else 0.6

        # Calculate overall score
        scores["total"] = sum(scores.values()) / len(scores)

        return scores

    def review_article(self, article_name: str, content: str) -> Dict:
        """Review a single article and decide if it goes live."""
        scores = self.score_article(content)

        # Decision thresholds
        threshold_promote = 0.7
        threshold_review = 0.5

        decision = "reject"
        reason = "Below review threshold"

        if scores["total"] >= threshold_promote:
            decision = "promote"
            reason = "High quality - ready for permanent brain"
        elif scores["total"] >= threshold_review:
            decision = "needs_review"
            reason = "Medium quality - needs manual review"

        result = {
            "article": article_name,
            "scores": scores,
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

        # Store score
        self.scores["articles"][article_name] = result
        self.scores["history"].append(result)
        self.scores["history"] = self.scores["history"][-100:]  # Keep last 100
        self._save_scores()

        return result

    def review_all_drafts(self) -> List[Dict]:
        """Review all draft articles."""
        if not self.drafts_dir.exists():
            return []

        results = []
        for draft in self.drafts_dir.glob("*.md"):
            content = draft.read_text()
            result = self.review_article(draft.name, content)
            results.append(result)

            # Auto-promote high-quality articles
            if result["decision"] == "promote":
                self._promote_article(draft)

        return results

    def _promote_article(self, draft_path: Path):
        """Move article from drafts to live."""
        live_path = self.live_dir / draft_path.name

        content = draft_path.read_text()
        # Add review metadata
        reviewed_content = f"""---
reviewed_by: hermes
reviewed_at: {datetime.now().isoformat()}
---

{content}
"""
        live_path.write_text(reviewed_content)

        print(f"✓ Promoted: {draft_path.name}")

    def get_article_score(self, article_name: str) -> Optional[Dict]:
        """Get score for a specific article."""
        return self.scores["articles"].get(article_name)

    def get_stats(self) -> Dict:
        """Get Hermes statistics."""
        articles = self.scores["articles"]

        return {
            "total_reviewed": len(articles),
            "promoted": sum(1 for a in articles.values() if a["decision"] == "promote"),
            "needs_review": sum(
                1 for a in articles.values() if a["decision"] == "needs_review"
            ),
            "rejected": sum(1 for a in articles.values() if a["decision"] == "reject"),
            "avg_score": sum(a["scores"]["total"] for a in articles.values())
            / max(1, len(articles)),
        }


def run_hermes():
    """Run Hermes review on all drafts."""
    print("[INFO] Running Hermes review...")

    hermes = Hermes()
    results = hermes.review_all_drafts()

    if not results:
        print("No drafts to review")
        return

    print(f"\nReviewed {len(results)} articles:")
    for r in results:
        status = (
            "✓"
            if r["decision"] == "promote"
            else "○"
            if r["decision"] == "needs_review"
            else "✗"
        )
        print(f"  {status} {r['article']}: {r['scores']['total']:.2f} - {r['reason']}")

    stats = hermes.get_stats()
    print(
        f"\n📊 Stats: {stats['promoted']} promoted, {stats['rejected']} rejected, avg: {stats['avg_score']:.2f}"
    )


if __name__ == "__main__":
    run_hermes()
