# Generic AM Operations v0.4.0 — Development Edition

A local-first manufacturing ERP/MES/QMS development prototype. **Not production-ready, certified, or validated for AS9100D or ISO 13485.** No real customer, personnel, powder, build, or regulated manufacturing data is bundled. Do not enter real data.

## Windows: one-click start
Extract the ZIP, then double-click **START_WINDOWS.bat**. The launcher creates a local virtual environment, installs dependencies, runs tests and the release guard, and opens the GUI at http://127.0.0.1:8000/ . Internet is required for the initial dependency installation.

## Features
- Familiar module-based GUI with Light, Dark, and Slate themes
- Local SQLite database, created on first run under `local_data/` (excluded from Git)
- RFQ, work order, build, parts, powder lots and append-only powder transaction entry
- Part → build → powder lot reverse lookup and related inspection/NCR/shipping records
- Personnel, training materials, training records, procedures, documents, NCR, CAPA, supplier and quality modules
- Context-sensitive page help and built-in manual
- Basic append-only record creation event log (not tamper-evident)

## Critical limitations
- No user authentication, roles, approval workflows, digital signatures, controlled document revisions, validation evidence, automatic qualification gating or compliant audit trail
- No validated powder mass balance or full recursive blending genealogy
- Record creation only; no edit/delete, so incorrect records require a clean test database
- Traceability is a functional demonstration, not evidence of regulatory compliance
- No proprietary source code or private data copied from the original manufacturing application

## Run tests
`python -m pytest -q`

## Data handling
The software creates an **empty local SQLite database** when first run. Use invented test entries only. Never commit `local_data/`, database files, secrets, or real records.
