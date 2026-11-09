"""Fail closed on common data files and sensitive terms. Manual review is still required."""
from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
forbidden_extensions = {'.db', '.sqlite', '.sqlite3', '.csv', '.xlsx', '.xls', '.parquet', '.jsonl', '.zip', '.pem', '.key'}
forbidden_names = {'.env', 'id_rsa', 'credentials.json'}
# Check only the independently written release; its security docs mention excluded concepts.
source_extensions = {'.py', '.js', '.html', '.css'}
patterns = [re.compile(x, re.I) for x in [r'watt[ _-]?melt', r'quiet[ _-]?dog', r'\bserial(?:ization|isation|ized|ised|_number)?\b']]
errors=[]
for p in root.rglob('*'):
    if not p.is_file() or any(part in p.parts for part in ('.git', '__pycache__', '.venv', 'venv', '.pytest_cache')): continue
    if p.suffix.lower() in forbidden_extensions or p.name.lower() in forbidden_names:
        errors.append(f'Forbidden file: {p.relative_to(root)}')
    if p.suffix.lower() in source_extensions and p.name != 'release_guard.py':
        s=p.read_text(encoding='utf-8',errors='replace')
        for pattern in patterns:
            if pattern.search(s): errors.append(f'Sensitive term in {p.relative_to(root)}: {pattern.pattern}')
if errors:
    print('\n'.join(errors));sys.exit(1)
print('PASS: baseline file and source-term guard (manual review still required)')
