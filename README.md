# Postgres Migration & Lock Safety Auditor

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PostgreSQL](https://img.shields.io/badge/Postgres-14%2B-blue)](https://www.postgresql.org/)
[![Gumroad Product](https://img.shields.io/badge/Full%20Agent%20Skill-%249%20USD-green)](https://neoninnovationlab.gumroad.com/l/postgres-migration-auditor)

A lightweight CLI auditor that scans PostgreSQL migration files (SQL, Prisma, Drizzle, Alembic, Django, Flyway) for hazardous table locks, full table rewrites, and zero-downtime deployment violations.

---

## The Problem

In high-concurrency PostgreSQL databases, running innocent-looking DDL migrations like `CREATE INDEX` or `ALTER TABLE ... ADD COLUMN` can acquire an `ACCESS EXCLUSIVE` table lock.

This queues up all incoming `SELECT`, `INSERT`, `UPDATE`, and `DELETE` queries, causing pool exhaustion, cascade timeouts, and downtime in production.

This auditor scans your migration scripts before they reach production.

---

## Detected Locking Hazards

1. **Blocking Index Creation**: Detects `CREATE INDEX` without `CONCURRENTLY`.
2. **Volatile Defaults**: Detects `ADD COLUMN ... DEFAULT now()` causing table rewrites.
3. **Column Type Changes**: Detects `ALTER COLUMN TYPE` requiring `ACCESS EXCLUSIVE`.
4. **Primary Key Locks**: Detects blocking primary key constraint additions.
5. **Rename Disruptions**: Detects column and table renames that break blue/green rollouts.

---

## Quick Start

### Installation

No dependencies needed. Pure Python 3.8+:

```bash
git clone https://github.com/Ansarii/postgres-migration-lock-auditor.git
cd postgres-migration-lock-auditor
chmod +x auditor.py
```

### Usage

Scan a single SQL migration file:
```bash
./auditor.py ./migrations/001_create_users.sql
```

Scan an entire directory (Prisma, Drizzle, Alembic):
```bash
./auditor.py ./prisma/migrations
```

Add to GitHub Actions CI/CD:
```yaml
name: Migration Safety Check
on: [pull_request]
jobs:
  audit-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Postgres Lock Auditor
        run: python3 auditor.py ./migrations
```

---

## Upgrade to Full AI Agent Skill Pack

Looking to automate migration reviews directly in **Cursor**, **Claude Code**, or **Copilot**?

The **Postgres Migration & Lock Safety Auditor AI Skill** equips your AI coding assistant with:
- 15+ advanced PostgreSQL lock matrices
- Automated zero-downtime dual-write triggers
- Safe backfill batched migration generators
- Native `.cursorrules` and Claude Code `CLAUDE.md` skills

👉 **[Download the Full AI Agent Skill ($9 on Gumroad)](https://neoninnovationlab.gumroad.com/l/postgres-migration-auditor)**

---

## Commercial Enterprise Bundle

Get the complete **Enterprise AI Agent Skills Bundle** (Postgres Lock Auditor + AWS/GCP Cloud Cost Optimizer + OWASP Top 10 Security Reviewer) for \$19:
👉 **[Download Complete Bundle ($19 on Gumroad)](https://neoninnovationlab.gumroad.com/l/devops-ai-skills)**

---

## License

MIT License. Authored by [Neon Innovation Lab](https://neoninnovationlab.com). Support: `hello@neoninnovationlab.com`.
