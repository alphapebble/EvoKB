import json
from datetime import datetime
from pathlib import Path
import duckdb
import hashlib


class KnowledgeCluster:
    def __init__(self, query: str, evidences: list, summary: str, confidence: float):
        self.id = hashlib.md5((query + summary).encode()).hexdigest()[:16]
        self.query = query
        self.evidences = evidences
        self.summary = summary
        self.confidence = confidence
        self.created_at = datetime.now().isoformat()
        self.last_used = self.created_at
        self.use_count = 1
        self.history = [query]

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        cluster = cls.__new__(cls)
        cluster.__dict__.update(data)
        return cluster


class ClusterStore:
    def __init__(self, path="clusters/evokb.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS clusters (
                id TEXT PRIMARY KEY,
                data JSON
            )
        """)

    def save(self, cluster: KnowledgeCluster):
        self.conn.execute(
            "INSERT OR REPLACE INTO clusters VALUES (?, ?)",
            [cluster.id, json.dumps(cluster.to_dict())],
        )

    def find_similar(self, query: str, threshold: float = 0.5):
        rows = self.conn.execute("SELECT data FROM clusters").fetchall()
        query_words = set(query.lower().split())
        results = []

        for row in rows:
            data = json.loads(row[0])
            cluster = KnowledgeCluster.from_dict(data)
            cluster_words = set(cluster.query.lower().split())
            overlap = len(query_words & cluster_words) / max(len(query_words), 1)
            if overlap >= threshold:
                results.append((overlap, cluster))

        results.sort(reverse=True)
        return results

    def get(self, cluster_id: str):
        row = self.conn.execute(
            "SELECT data FROM clusters WHERE id = ?", [cluster_id]
        ).fetchone()
        if row:
            return KnowledgeCluster.from_dict(json.loads(row[0]))
        return None

    def all(self):
        rows = self.conn.execute("SELECT data FROM clusters").fetchall()
        return [KnowledgeCluster.from_dict(json.loads(row[0])) for row in rows]
