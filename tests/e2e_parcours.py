"""Parcours complet Bayān jusqu’au MP4, via l’API HTTP réelle du service vidéo.

Reproduit ce que fait le studio : envoi du média, import (arabe), puis export MP4
avec des sous-titres ASS, suivi de l’avancement et téléchargement du fichier.

Usage :
  BAYAN_URL=http://127.0.0.1:8080 BAYAN_TOKEN=... python3 tests/e2e_parcours.py video.mp4 sortie.mp4 [quality] [exports]

`exports` (défaut 3) relance l’export sur le même média, comme une régénération
après correction des sous-titres dans le studio.

Aucun service payant n’est appelé (costPolicy=free).
"""
import json, os, subprocess, sys, time, uuid, urllib.request, urllib.error
from pathlib import Path

BASE=os.environ.get('BAYAN_URL','http://127.0.0.1:8080').rstrip('/')
TOKEN=os.environ['BAYAN_TOKEN']
FIXTURE=Path(__file__).parent/'fixtures'/'captions.ass'

def call(method,path,body=None,headers=None,raw=False):
    req=urllib.request.Request(BASE+path,data=body,method=method,headers={'Authorization':'Bearer '+TOKEN,**(headers or {})})
    try:
        with urllib.request.urlopen(req,timeout=600) as r:return r.read() if raw else json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f'ÉCHEC {method} {path} → HTTP {e.code} : {e.read().decode(errors="replace")}')

def ts(s):return f'{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}'

def build_ass(duration):
    head=FIXTURE.read_text().split('[Events]')[0]
    rows=[f'Dialogue: 0,{ts(i+.2)},{ts(min(duration,i+2.8))},Default,,0,0,0,,العلم نور — المقطع {n+1}\\NLe savoir est une lumière — segment {n+1}' for n,i in enumerate(range(0,int(duration),3))]
    return head+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'+'\n'.join(rows)+'\n'

def wait(job,label):
    start=time.time();last=None
    while True:
        state=call('GET','/jobs/'+job['id'])
        line=(state['status'],state.get('stage'),state.get('progress'))
        if line!=last:print(f'  [{label} +{time.time()-start:5.0f}s] {state["status"]} — {state.get("stage")} — {state.get("progress")}');last=line
        if state['status'] in ('complete','failed','blocked'):return state
        time.sleep(3)

def main():
    source=Path(sys.argv[1]);target=Path(sys.argv[2]);quality=sys.argv[3] if len(sys.argv)>3 else 'original'
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(source)]))
    print(f'Source : {source} — {source.stat().st_size/1e6:.1f} Mo — {duration:.1f} s')
    print('1. /health');print('  ',call('GET','/health'))
    asset=str(uuid.uuid4());data=source.read_bytes()
    print('2. Envoi du média (PUT /assets)');print('  ',call('PUT','/assets/'+asset,data,{'Content-Type':'application/octet-stream'}))
    project={'id':'e2e-'+asset[:8],'title':'Parcours 3 min','segments':[]}
    print('3. Import arabe (POST /jobs kind=import)')
    state=wait(call('POST','/jobs',json.dumps({'kind':'import','costPolicy':'free','asset':asset,'project':project}).encode(),{'Content-Type':'application/json'}),'import')
    if state['status']=='blocked':print('   → attendu en mode manuel : le studio importe alors un SRT/VTT.',state['error'])
    elif state['status']!='complete':raise SystemExit('ÉCHEC import : '+state.get('error',''))
    payload={'kind':'export','costPolicy':'free','asset':asset,'quality':quality,'ass':build_ass(duration),'project':project}
    for n in range(1,(int(sys.argv[4]) if len(sys.argv)>4 else 3)+1):
        print(f'4.{n} Export MP4 (POST /jobs kind=export)')
        state=wait(call('POST','/jobs',json.dumps(payload,ensure_ascii=False).encode(),{'Content-Type':'application/json'}),f'export {n}')
        if state['status']!='complete':raise SystemExit(f'ÉCHEC export {n} : '+state.get('error',''))
        print('  ',state['result'])
    print('5. Téléchargement (GET /jobs/:id/file)')
    target.write_bytes(call('GET','/jobs/'+state['id']+'/file',raw=True))
    out=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(target)]))
    print(f'OK : {target} — {target.stat().st_size/1e6:.1f} Mo — {out:.1f} s')

if __name__=='__main__':main()
