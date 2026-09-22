from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS iterations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project TEXT NOT NULL,
  round INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  trigger TEXT NOT NULL,
  strengths TEXT NOT NULL,
  defects TEXT NOT NULL,
  changes TEXT NOT NULL,
  evidence TEXT NOT NULL,
  metrics TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'recorded'
);
CREATE INDEX IF NOT EXISTS idx_iterations_project_round ON iterations(project, round);
"""

def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    return db

def payload(value: str) -> str:
    return json.dumps([x.strip() for x in value.split("|") if x.strip()], ensure_ascii=False)

def main() -> int:
    p = argparse.ArgumentParser(description="记录并检索文档迭代经验")
    p.add_argument("db", type=Path)
    sub = p.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("--project", required=True)
    add.add_argument("--round", type=int, required=True)
    add.add_argument("--trigger", required=True)
    add.add_argument("--strengths", default="")
    add.add_argument("--defects", default="")
    add.add_argument("--changes", default="")
    add.add_argument("--evidence", default="")
    add.add_argument("--metrics", default="")
    show = sub.add_parser("show")
    show.add_argument("--project", required=True)
    show.add_argument("--limit", type=int, default=10)
    args = p.parse_args()
    db = connect(args.db)
    if args.command == "add":
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        db.execute("INSERT INTO iterations(project,round,created_at,trigger,strengths,defects,changes,evidence,metrics) VALUES(?,?,?,?,?,?,?,?,?)", (args.project,args.round,now,args.trigger,payload(args.strengths),payload(args.defects),payload(args.changes),payload(args.evidence),args.metrics))
        db.commit()
        print(json.dumps({"status":"recorded","project":args.project,"round":args.round}, ensure_ascii=False))
    else:
        rows=db.execute("SELECT round,created_at,trigger,strengths,defects,changes,metrics FROM iterations WHERE project=? ORDER BY round DESC LIMIT ?",(args.project,args.limit)).fetchall()
        print(json.dumps([{"round":r[0],"created_at":r[1],"trigger":r[2],"strengths":json.loads(r[3]),"defects":json.loads(r[4]),"changes":json.loads(r[5]),"metrics":r[6]} for r in rows],ensure_ascii=False,indent=2))
    db.close()
    return 0
if __name__ == "__main__": raise SystemExit(main())
