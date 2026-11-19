"""Portable static delivery checks. Run from any machine with Python 3."""
from pathlib import Path
import hashlib
import json
import re
import struct

root = Path(__file__).resolve().parents[1]
checks = json.loads((root / 'checksums.json').read_text(encoding='utf-8'))
actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'checksums.json'}
assert actual == set(checks), 'File inventory mismatch'
for name, expected in checks.items():
    path = (root / name).resolve()
    assert path.is_relative_to(root), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name

asset_root = root / 'Assets/WuxiaBattleSettlementUI'
manifest = json.loads((asset_root / 'manifest.json').read_text(encoding='utf-8'))
assert len({a['id'] for a in manifest['assets']}) == len(manifest['assets'])
for asset in manifest['assets']:
    data = (asset_root / asset['file']).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', asset['file']
    assert struct.unpack('>II', data[16:24]) == (asset['width'], asset['height']), asset['file']
    assert hashlib.sha256(data).hexdigest() == asset['sha256'], asset['file']

for md in root.rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', md.read_text(encoding='utf-8')):
        if not target.startswith(('http:', 'https:', '#')):
            assert (md.parent / target.split('#')[0]).exists(), f'{md}: {target}'
print(f'PASS: {len(checks)} files, {len(manifest["assets"])} PNG assets, hashes/dimensions/local links valid. Unity runtime not tested.')
