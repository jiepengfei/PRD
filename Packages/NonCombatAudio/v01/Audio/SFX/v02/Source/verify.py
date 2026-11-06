"""Decode delivered PCM independently of synthesis; validate resources and references."""
from pathlib import Path
import wave, struct, math, hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
def db(x): return round(20*math.log10(max(x,1e-12)),4)

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    sounds=manifest['sounds']; results=[]; ids=set(); failures=[]
    for s in sounds:
        assert s['id'] not in ids
        ids.add(s['id'])
        data=(ROOT/s['file']).read_bytes()
        with wave.open(str(ROOT/s['file']),'rb') as w:
            specs=(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())
            frames=w.getnframes(); raw=w.readframes(frames)
        a=struct.unpack('<'+'h'*(len(raw)//2),raw)
        peak=max(map(abs,a))/32768; rms=math.sqrt(sum(x*x for x in a)/len(a))/32768
        edge=round(.005*44100)
        edge_delta=max(max(abs(a[i+1]-a[i]) for i in range(edge-1)),max(abs(a[i+1]-a[i]) for i in range(len(a)-edge,len(a)-1)))/32768
        silence=sum(abs(x)<=32 for x in a)/len(a)
        dc=sum(a)/len(a)/32768
        checks=dict(pcmSpec=specs==(1,2,44100,'NONE'),framesAndLength=frames==s['frames'] and len(raw)==frames*2 and len(data)==44+frames*2,
                    durationMatches=abs(frames/44100-s['durationSeconds'])<1e-8,durationRange=.08<=frames/44100<=1.5,
                    peakTarget=abs(db(peak)-s['targetPeakDbFS'])<.03,headroom=peak<10**(-8.9/20),
                    noClipping=all(-32768<x<32767 for x in a),notSilent=rms>10**(-50/20),dcOffset=abs(dc)<.002,
                    silenceFraction=silence<.85,zeroEndpoints=a[0]==0 and a[-1]==0,
                    edgeDiscontinuity=edge_delta<.06,sha256=hashlib.sha256(data).hexdigest()==s['sha256'])
        r=dict(id=s['id'],file=s['file'],frames=frames,durationSeconds=frames/44100,sampleRate=specs[2],channels=specs[0],bits=specs[1]*8,
               peakDbFS=db(peak),rmsDbFS=db(rms),dc=round(dc,8),clippedSamples=sum(x<=-32768 or x>=32767 for x in a),
               silenceFractionBelowMinus60dB=round(silence,5),firstSample=a[0],lastSample=a[-1],edge5msMaxDelta=round(edge_delta,6),checks=checks)
        results.append(r)
        failures += [s['id']+':'+k for k,v in checks.items() if not v]
    for m in manifest['mappings']:
        assert all(i in ids for i in m['ids'])
        assert all((ROOT/p).is_file() for p in m['files'])
    page=(ROOT/'试听.html').read_text(encoding='utf-8')
    refs=re.findall(r'(?:src|href)="([^"]+)"',page)
    for ref in refs:
        # The validation report is this script's output, generated after these checks.
        if ref != 'QA/validation.json' and not (ROOT/ref).is_file(): failures.append('htmlReference:'+ref)
    actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'WAV').glob('*.wav')}
    if actual!={s['file'] for s in sounds}: failures.append('unlisted_or_missing_wav')
    report=dict(status='pass' if not failures else 'fail',decoder='Python standard-library wave + independent int16 unpack',
                thresholds=dict(peakCeilingDbFS=-8.9,rmsFloorDbFS=-50,absoluteDcMax=.002,silenceFractionMax=.85,edge5msDeltaMax=.06),
                count=len(results),mappingCount=len(manifest['mappings']),htmlLocalReferencesChecked=len(refs),
                listenedByAgent=False,browserPlaybackVerified=False,engineIntegrated=False,failures=failures,sounds=results)
    (ROOT/'QA').mkdir(exist_ok=True)
    (ROOT/'QA/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],wavCount=len(results),mappings=len(manifest['mappings']),failures=failures),ensure_ascii=False))
    if failures: raise SystemExit(1)

if __name__=='__main__': main()
