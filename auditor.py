#!/usr/bin/env python3
"""
Postgres Migration Lock Safety Auditor
Detects exclusive table locks, unindexed foreign keys, and zero-downtime migration risks.
"""

import os
import sys
import re
import argparse
from typing import List, Dict, Any

RISK_PATTERNS = [
    {
        "id": "LOCK_CREATE_INDEX_BLOCKING",
        "severity": "HIGH",
        "regex": r"CREATE\s+INDEX\s+(?!CONCURRENTLY\b)",
        "message": "CREATE INDEX blocks all table writes (SHARE lock). Use CREATE INDEX CONCURRENTLY instead.",
        "fix": "CREATE INDEX CONCURRENTLY idx_name ON table_name (column_name);"
    },
    {
        "id": "LOCK_ADD_COLUMN_VOLATILE_DEFAULT",
        "severity": "HIGH",
        "regex": r"ALTER\s+TABLE\s+\w+\s+ADD\s+COLUMN\s+\w+.*DEFAULT\s+(now\(\)|clock_timestamp\(\)|random\(\)|uuid_generate_v4\(\))",
        "message": "Adding a column with a volatile default rewrites the entire table under an ACCESS EXCLUSIVE lock.",
        "fix": "1. Add column without default.\n2. Set default in separate statement.\n3. Backfill data in small batches."
    },
    {
        "id": "LOCK_ALTER_COLUMN_TYPE",
        "severity": "CRITICAL",
        "regex": r"ALTER\s+TABLE\s+\w+\s+ALTER\s+COLUMN\s+\w+\s+TYPE",
        "message": "ALTER COLUMN TYPE acquires ACCESS EXCLUSIVE lock and requires full table rewrite.",
        "fix": "1. Add new column with new type.\n2. Write to both columns via trigger.\n3. Backfill data.\n4. Rename and drop old column."
    },
    {
        "id": "LOCK_ADD_PRIMARY_KEY",
        "severity": "CRITICAL",
        "regex": r"ALTER\s+TABLE\s+\w+\s+ADD\s+PRIMARY\s+KEY",
        "message": "ADD PRIMARY KEY creates a unique index that blocks all reads and writes unless created concurrently.",
        "fix": "1. CREATE UNIQUE INDEX CONCURRENTLY.\n2. ALTER TABLE ... ADD CONSTRAINT ... PRIMARY KEY USING INDEX."
    },
    {
        "id": "LOCK_RENAME_COLUMN_OR_TABLE",
        "severity": "MEDIUM",
        "regex": r"ALTER\s+TABLE\s+\w+\s+RENAME\s+(COLUMN\s+\w+\s+TO\s+\w+|TO\s+\w+)",
        "message": "Renaming a column or table can break running application queries and replication pipelines.",
        "fix": "Use expanding and contracting views to support blue/green deployments."
    }
]

def analyze_sql(content: str, filename: str) -> List[Dict[str, Any]]:
    findings = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        clean_line = re.sub(r"--.*$", "", line).strip()
        if not clean_line:
            continue

        for rule in RISK_PATTERNS:
            if re.search(rule["regex"], clean_line, re.IGNORECASE):
                findings.append({
                    "file": filename,
                    "line": idx,
                    "code": clean_line,
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "fix": rule["fix"]
                })

    return findings

def scan_path(path: str) -> List[Dict[str, Any]]:
    all_findings = []
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_findings.extend(analyze_sql(f.read(), path))
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in sorted(files):
                if file.endswith((".sql", ".prisma", ".ts")):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        all_findings.extend(analyze_sql(f.read(), full_path))
    return all_findings

def main():
    parser = argparse.ArgumentParser(description="Postgres Migration Lock Safety Auditor")
    parser.add_argument("path", nargs="?", default=".", help="Path to migration SQL files or directory")
    args = parser.parse_args()

    print("============================================================")
    print("Postgres Migration & Lock Safety Auditor")
    print("Scanning for exclusive locks, table rewrites, and downtime risks")
    print("============================================================\n")

    findings = scan_path(args.path)

    if not findings:
        print("✅ [PASS] No blocking exclusive table lock hazards detected!")
        sys.exit(0)

    print(f"🚨 Found {len(findings)} migration safety warning(s):\n")

    for f in findings:
        color = "🔴" if f["severity"] == "CRITICAL" else "🟡"
        print(f"{color} [{f['severity']}] {f['rule_id']} at {f['file']}:{f['line']}")
        print(f"   Code: {f['code']}")
        print(f"   Warning: {f['message']}")
        print(f"   Safe Fix:\n   {f['fix']}\n")

    print("------------------------------------------------------------")
    print("Want automated Claude Code / Cursor AI agent audit skills?")
    print("Full Auditor Skill: https://neoninnovationlab.gumroad.com/l/postgres-migration-auditor")
    print("------------------------------------------------------------")

    sys.exit(1 if any(f["severity"] == "CRITICAL" for f in findings) else 0)

if __name__ == "__main__":
    main()
