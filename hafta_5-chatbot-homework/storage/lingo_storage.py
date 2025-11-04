# storage/lingo_storage.py
from pathlib import Path
import json
from typing import Optional, Dict, Any, List
import pandas as pd
import datetime

class LingoStorage:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.words_file = self.data_dir / "words.json"
        # Ensure files exist
        for f in (self.users_file, self.words_file):
            if not f.exists():
                f.write_text("[]", encoding="utf-8")

    # ---------- Users ----------
    def load_users(self) -> List[Dict[str, Any]]:
        return self._read(self.users_file)

    def save_users(self, users: List[Dict[str, Any]]):
        self._write(self.users_file, users)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        users = self.load_users()
        for u in users:
            if u.get("id") == user_id:
                return u
        return None

    def upsert_user(self, user: Dict[str, Any]):
        users = self.load_users()
        found = False
        for i,u in enumerate(users):
            if u.get("id") == user.get("id"):
                users[i] = user
                found = True
                break
        if not found:
            users.append(user)
        self.save_users(users)

    # ---------- Words / Journal ----------
    def load_words(self) -> List[Dict[str, Any]]:
        return self._read(self.words_file)

    def save_words(self, arr: List[Dict[str, Any]]):
        self._write(self.words_file, arr)

    def append_word_entry(self, entry: Dict[str, Any]):
        arr = self.load_words()
        arr.append(entry)
        self.save_words(arr)

    def get_user_words(self, user_id: str) -> List[Dict[str, Any]]:
        arr = self.load_words()
        return [x for x in arr if x.get("user_id") == user_id]

    def clear_user_words(self, user_id: str):
        arr = [x for x in self.load_words() if x.get("user_id") != user_id]
        self.save_words(arr)

    # ---------- Helpers ----------
    def _read(self, path: Path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write(self, path: Path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_user_words_csv(self, user_id: str, out_path: Path):
        rows = self.get_user_words(user_id)
        if not rows:
            return None
        df = pd.DataFrame(rows)
        df.to_csv(out_path, index=False)
        return out_path

    def weekly_summary(self, user_id: str):
        rows = self.get_user_words(user_id)
        if not rows:
            return {"count":0, "hardest": None}
        # filter last 7 days
        now = datetime.datetime.utcnow()
        last7 = []
        for r in rows:
            ts = r.get("timestamp")
            try:
                t = datetime.datetime.fromisoformat(ts)
                if (now - t).days < 7:
                    last7.append(r)
            except Exception:
                pass
        count = len(last7)
        # find word with most failures (field 'failures' tracked)
        hardest = None
        if last7:
            freq = {}
            for r in last7:
                w = r.get("word")
                freq[w] = freq.get(w,0) + (r.get("failures",0) or 0)
            if freq:
                hardest = max(freq.items(), key=lambda x: x[1])[0]
        return {"count": count, "hardest": hardest}
