"""Validate the portable card-upgrade art package using only Python standard library."""
from pathlib import Path
import hashlib, json, re, struct

root=Path(__file__).resolve().parents[1]
checks=json.loads((root/'checksums.json').read_text(encoding='utf-8'))
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='checksums.json'}
assert actual==set(checks), 'File inventory mismatch'
for name,expected in checks.items():
    p=(root/name).resolve()
    assert p.is_relative_to(root), name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected, name
art=root/'Assets/WuxiaCardUpgradeUI'
manifest=json.loads((art/'manifest.json').read_text(encoding='utf-8'))
assert len({a['id'] for a in manifest['assets']})==len(manifest['assets'])
for asset in manifest['assets']:
    data=(art/asset['file']).read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n', asset['file']
    assert struct.unpack('>II',data[16:24])==(asset['width'],asset['height']), asset['file']
    assert hashlib.sha256(data).hexdigest()==asset['sha256'], asset['file']
for doc in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
        if not link.startswith(('http:','https:','#')):
            assert (doc.parent/link.split('#')[0]).exists(), f'{doc}: {link}'
print(f'PASS: {len(checks)} files, {len(manifest["assets"])} PNG assets, hashes/dimensions/local links valid. Unity not tested.')
