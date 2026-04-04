import subprocess
from pathlib import Path
from litellm import completion
from .config import MODEL
from .utils import read_file


def score_change(content: str, criteria: list) -> dict:
    criteria_text = ", ".join(criteria)
    prompt = f"""Evaluate this proposed change against these criteria: {criteria_text}

Proposed content:
{content[:3000]}

Reply with ONLY a JSON object like:
{{"clarity": 8, "grounding": 9, "coverage": 7, "backlinks": 6, "overall": 8}}
Scores should be 0-10, where 10 is perfect.
"""

    try:
        resp = completion(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        output = resp.choices[0].message.content

        import re

        json_match = re.search(r"\{[^}]+\}", output)
        if json_match:
            import json

            scores = json.loads(json_match.group())
            overall = scores.get("overall", sum(scores.values()) / len(scores))
            return {"scores": scores, "overall": overall, "passed": overall >= 8}

        return {
            "scores": {},
            "overall": 5,
            "passed": False,
            "error": "Could not parse scores",
        }
    except Exception as e:
        return {"scores": {}, "overall": 0, "passed": False, "error": str(e)}


def apply_change(target_path: Path, new_content: str, backup: bool = True) -> bool:
    if backup and target_path.exists():
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        backup_path.write_text(read_file(target_path))

    try:
        target_path.write_text(new_content)
        return True
    except Exception as e:
        print(f"Error applying change: {e}")
        return False


def revert_change(target_path: Path) -> bool:
    backup_path = target_path.with_suffix(target_path.suffix + ".bak")
    if backup_path.exists():
        try:
            content = read_file(backup_path)
            target_path.write_text(content)
            backup_path.unlink()
            return True
        except Exception as e:
            print(f"Error reverting: {e}")
            return False
    return False


def git_commit(message: str) -> bool:
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message], check=True, capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
