"""Build package checksums and complete ZIP; verify ZIP CRC and every payload hash.
Run after build.py and verify.py; ZIP is a sibling of v02 (never inside itself).
"""
from pathlib import Path
import hashlib, zipfile, json
ROOT=Path(__file__).resolve().parents[1]

def main():
    qa=json.loads((ROOT/'QA/validation.json').read_text(encoding='utf-8'))
    assert qa['status']=='pass'
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    for s in manifest['sounds']:
        assert hashlib.sha256((ROOT/s['file']).read_bytes()).hexdigest()==s['sha256']
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='checksums.sha256' and '__pycache__' not in p.parts)
    lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix() for p in files]
    (ROOT/'checksums.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    files.append(ROOT/'checksums.sha256')
    dest=ROOT.parent/'WuxiaDemo_NonCombat_SFX_v02.zip'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            info=zipfile.ZipInfo('v02/'+p.relative_to(ROOT).as_posix(),date_time=(2026,11,6,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)
        for p in files:
            assert z.read('v02/'+p.relative_to(ROOT).as_posix())==p.read_bytes()
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    dest.with_suffix('.zip.sha256').write_text(digest+'  '+dest.name+'\n',encoding='utf-8')
    print(json.dumps(dict(zip=str(dest),bytes=dest.stat().st_size,entries=len(files),sha256=digest,crcAndPayloads='pass')))

if __name__=='__main__':main()
