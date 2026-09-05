#!/usr/bin/env python3
from pathlib import Path
for p in Path('.').rglob('*'):
    if p.is_symlink(): raise SystemExit(f'symlink: {p}')
print('publication disclosure checks passed')
