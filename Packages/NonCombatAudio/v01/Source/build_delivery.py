"""Package current non-combat audio and full requirements, preserving audio paths."""
from pathlib import Path, PurePosixPath
import hashlib, json, posixpath, re, zipfile

PROJECT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
PREFIX='WuxiaDemo_NonCombatAudio_Requirements_v01'

def digest(data): return hashlib.sha256(data).hexdigest()

def main():
    files={}
    audio=PROJECT/'Audio/SFX/v02'
    for p in sorted(audio.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            files[p.relative_to(PROJECT).as_posix()]=p.read_bytes()
    # Keep the previous resource-only ZIP referenced by the full requirement.
    for name in ['WuxiaDemo_NonCombat_SFX_v02.zip','WuxiaDemo_NonCombat_SFX_v02.zip.sha256']:
        p=PROJECT/'Audio/SFX'/name
        files[p.relative_to(PROJECT).as_posix()]=p.read_bytes()
    req='Requirements/Audio/v01/非战斗音效完整接入需求.md'
    original=(PROJECT/req).read_bytes()
    files[req]=original
    omitted=[]
    def replace_link(match):
        label,target=match.group(1),match.group(2)
        resolved=posixpath.normpath(posixpath.join(posixpath.dirname(req),target))
        if resolved in files: return match.group(0)
        omitted.append(resolved)
        return f'{label}（项目参考：`{resolved}`，未随本音频包附带）'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',replace_link,original.decode('utf-8'))
    text=text.replace('# 新手村 Demo 非战斗音效完整接入需求\n',
        '# 新手村 Demo 非战斗音效完整接入需求\n\n> 合并交付副本：正文要求保持一致；项目内其他业务文档的链接改为来源路径说明。音频、适配、试听与校验链接均在包内可用。\n',1)
    files[req]=text.encode('utf-8')
    readme='''# 新手村 Demo · 非战斗音频与完整需求

日期：2026-11-06。解压整个文件夹后使用，目录结构请保持不变。

- [完整接入需求](Requirements/Audio/v01/非战斗音效完整接入需求.md)：范围、25枚资源、36条适配、触发规则、去重并发、实施与验收。
- [逐项试听](Audio/SFX/v02/试听.html)：原生播放器，使用相对音频路径。
- [适配表](Audio/SFX/v02/适配表.md) · [CSV](Audio/SFX/v02/适配表.csv) · [manifest](Audio/SFX/v02/manifest.json)。
- [资源说明与复现](Audio/SFX/v02/README.md) · [数值检查](Audio/SFX/v02/QA/validation.json)。

WAV在Audio/SFX/v02/WAV；生成、验证和资源包脚本在Audio/SFX/v02/Source。附带旧版资源专用ZIP，方便沿用原需求中的下载链接；它与展开目录中的音频相同，不必重复导入。

全部素材为程序合成试听／占位资源；已完成文件与数值检查，未实际试听、接入Unity或验收游戏混音。排除战斗音、BGM和配音。

为便于独立交付，本包完整需求中的外围业务文档引用以项目原始路径说明，未附带无关美术与其他模块交付包。需求原文件SHA-256及该处理范围见delivery-manifest.json。音频资源原文件未修改。

checksums.sha256覆盖包内全部文件（自身除外）；ZIP旁SHA文件用于核对整个压缩包。
'''
    files['README.md']=readme.encode('utf-8')
    files['Source/build_delivery.py']=Path(__file__).read_bytes()
    info=dict(date='2026-11-06',audioVersion='v02',requirementVersion='v01',wavCount=25,mappingCount=36,
              originalRequirement=req,originalRequirementSHA256=digest(original),packagedRequirementSHA256=digest(files[req]),
              change='only added delivery note and replaced unbundled reference hyperlinks with project path descriptions',
              unbundledProjectReferences=sorted(set(omitted)),engineIntegrated=False,listenedByAgent=False)
    files['delivery-manifest.json']=(json.dumps(info,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    manifest=json.loads(files['Audio/SFX/v02/manifest.json'])
    assert len(manifest['sounds'])==25 and len(manifest['mappings'])==36
    for s in manifest['sounds']:
        assert digest(files['Audio/SFX/v02/'+s['file']])==s['sha256']
    checked=0
    for name,data in list(files.items()):
        if name.endswith('.md'):
            refs=re.findall(r'\]\(([^)]+)\)',data.decode('utf-8'))
        elif name.endswith('.html'):
            refs=re.findall(r'(?:src|href)="([^"]+)"',data.decode('utf-8'))
        else: continue
        for ref in refs:
            if '://' in ref or ref.startswith('#'): continue
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),ref))
            assert resolved in files,(name,ref)
            checked+=1
    files['checksums.sha256']=(''.join(f'{digest(data)}  {name}\n' for name,data in sorted(files.items()))).encode('utf-8')
    dest=OUT/(PREFIX+'.zip')
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            zi=zipfile.ZipInfo(PREFIX+'/'+name,(2026,11,6,0,0,0))
            zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,data)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)
        for name,data in files.items(): assert z.read(PREFIX+'/'+name)==data
    sha=digest(dest.read_bytes())
    dest.with_suffix('.zip.sha256').write_text(sha+'  '+dest.name+'\n',encoding='utf-8')
    report=dict(status='pass',zip=str(dest),bytes=dest.stat().st_size,files=len(files),wavCount=25,mappings=36,
                localLinksChecked=checked,zipCRC='pass',payloadComparison='pass',sha256=sha)
    (OUT/'package-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__': main()
