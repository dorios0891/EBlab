#!/usr/bin/env python3
# Convierte farmacos_actualizado.xlsx -> farmacos.json (datos del Motor farmacológico EBIME)
import openpyxl, json, re, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)) or ".")
from _std_rules import standardize as _S

def clean_pump(s):
    if not s: return s
    out=re.sub(r'[^.;]*\b(?:canal|l[ií]nea)\s+(?:a\s*y\s*b|a/b|a|b)\b[^.;]*[.;]?',' ',s,flags=re.I)
    out=re.sub(r'\s{2,}',' ',out).strip(' ,;.')
    if out and not out.endswith('.'): out+='.'
    return out


SRC = sys.argv[1] if len(sys.argv)>1 else 'farmacos_actualizado.xlsx'
OUT = sys.argv[2] if len(sys.argv)>2 else 'farmacos.json'

SHEET_LABEL = {
 'Cardio':'Cardiovascular / Vasoactivo','Antibioticos':'Antibióticos / Antifúngicos',
 'Electrolitos':'Electrolitos / Fluidos','Sedoanalgesia':'Sedoanalgesia',
 'Hoja 5':'Varios','Antineoplásicos':'Antineoplásicos','Antiepilépticos':'Antiepilépticos',
 'Otros':'Otros','Glucocorticoides':'Glucocorticoides','Inmunosupresores':'Inmunosupresores',
 'Anticoagulantes':'Anticoagulantes',
}
SKIP_SHEETS = {'Notas y Fuentes'}
DESCRIPTORS = {'nombre genérico','nombre generico',''}

def clean(v):
    if v is None: return ''
    s=str(v).replace('\\n',' ').replace('\n',' ').replace('\r',' ')
    s=re.sub(r'\s+',' ',s).strip()
    return s

def find(headers, *names):
    for i,hh in enumerate(headers):
        h=clean(hh).lower()
        for n in names:
            if h==n: return i
    # contains
    for i,hh in enumerate(headers):
        h=clean(hh).lower()
        for n in names:
            if n in h: return i
    return -1

def classify(text):
    t=text.lower()
    if 'vesicante' in t: return 'Vesicante'
    if 'irritante' in t: return 'Irritante'
    if 'neutro' in t: return 'Neutro'
    return ''

def risk(text):
    t=text.lower()
    if 'alto riesgo' in t or t.strip()=='alto' or 'medicamento de alto riesgo' in t: return 'Alto'
    if t.strip()=='medio': return 'Medio'
    if t.strip()=='bajo': return 'Bajo'
    return ''

def parse_osmo(s):
    s=(s or '').lower(); vals=[]
    for m in re.findall(r'(\d[\d.,]*)\s*mosm', s):
        n=m.replace('.','').replace(',','')
        if n.isdigit(): vals.append(int(n))
    if not vals:
        for n in re.findall(r'\b(\d{3,5})\b', s):
            vals.append(int(n))
    return max(vals) if vals else None

def route(osmo, ph, clasif, blob):
    t=(blob or '').lower(); ot=(osmo or '').lower()
    o=parse_osmo(osmo); lo,hi=ph_bounds(ph)
    if any(k in t for k in ['vía central','via central','exclusiv','por cvc','catéter central','acceso central','vena central','solo central']): return 'Central'
    if clasif=='Vesicante': return 'Central'
    if ('hipertón' in ot) or (o is not None and o>=900): return 'Central'
    if (lo is not None and lo<5) or (hi is not None and hi>9): return 'Central/Periférica'
    if clasif=='Irritante': return 'Central/Periférica'
    if (o is not None and o>=600): return 'Central/Periférica'
    if ('isotón' in ot) or ('hipotón' in ot) or (o is not None and o<600): return 'Periférica'
    if 'perif' in t: return 'Periférica'
    return 'Periférica'

def ph_bounds(ph):
    nums=re.findall(r'\d+[.,]?\d*', ph)
    nums=[float(n.replace(',','.')) for n in nums]
    nums=[n for n in nums if 0<=n<=14]
    if not nums: return None,None
    return min(nums),max(nums)

def get(row,i):
    return clean(row[i]) if 0<=i<len(row) else ''

drugs=[]
wb=openpyxl.load_workbook(SRC, data_only=True, read_only=True)
for ws in wb.worksheets:
    if ws.title in SKIP_SHEETS: continue
    label=SHEET_LABEL.get(ws.title, ws.title)
    rows=[[c for c in r] for r in ws.iter_rows(values_only=True)]
    if not rows: continue
    headers=rows[0]
    hjoin=' '.join(clean(x).lower() for x in headers)
    simple = ('grupo' in hjoin and 'clasificación' in hjoin) or ('nivel de riesgo' in hjoin)
    ci={
      'name': find(headers,'medicamento y presentación','medicamento'),
      'via':  find(headers,'vía y forma de administración','vía y forma de administración'),
      'dil':  find(headers,'forma de realizar la dilución','dilución y administración','vehículo de dilución'),
      'dosis':find(headers,'dosis de seguridad','dosis'),
      'incomp':find(headers,'incompatibilidad en "y"','compatibilidad / incompatibilidad','compatibilidad / incompatibilidad'),
      'tiempo':find(headers,'tiempo de infusión o administración','tiempo de admnistracion','tiempo de administración'),
      'recom':find(headers,'recomendaciones de administración'),
      'ph':   find(headers,'ph'),
      'osmo': find(headers,'osmolaridad','osmolaridad (mosm/l)'),
      'cuid': find(headers,'cuidados de enfermería específicos','acciones de enfermería'),
      'grupo':find(headers,'grupo'),
      'clasif':find(headers,'clasificación'),
      'riesgo':find(headers,'nivel de riesgo'),
      'conc': find(headers,'concentración de dilución por ml','concentración de dilución por ml'),
    }
    for r in rows[1:]:
        name=get(r,ci['name'])
        if clean(name).lower() in DESCRIPTORS: continue
        if not name: continue
        ph=get(r,ci['ph']); osmo=get(r,ci['osmo']); cuid=get(r,ci['cuid'])
        if not (ph or osmo or cuid): continue   # fila vacía
        clasif = get(r,ci['clasif']) if simple else ''
        clasif = classify(clasif) if clasif else classify(cuid+' '+name)
        rk = risk(get(r,ci['riesgo'])) if simple else risk(cuid)
        blob=' '.join([get(r,ci['via']),get(r,ci['dil']),get(r,ci['recom']),cuid,osmo])
        via = route(osmo, ph, clasif, blob)
        lo,hi=ph_bounds(ph)
        rec={
          'grupo':label,
          'nombre':_S(name),
          'ph':ph,'phLo':lo,'phHi':hi,
          'osmolaridad':_S(osmo),
          'tipo':clasif,'riesgo':rk,'via':via,
          'dilucion':_S(get(r,ci['dil'])),
          'dosis':_S(get(r,ci['dosis'])),
          'tiempo':_S(get(r,ci['tiempo'])),
          'incompatibilidades':_S(get(r,ci['incomp'])),
          'recomendaciones':clean_pump(_S(get(r,ci['recom']))),
          'cuidados':clean_pump(_S(cuid)),
          'concentracion':_S(get(r,ci['conc'])),
        }
        drugs.append(rec)

# dedup por (nombre+grupo+dilucion)
seen=set(); uniq=[]
for d in drugs:
    k=(d['nombre'],d['grupo'],d['dilucion'][:30])
    if k in seen: continue
    seen.add(k); uniq.append(d)

data={'version':1,'fuente':os.path.basename(SRC),'total':len(uniq),'grupos':sorted(set(d['grupo'] for d in uniq)),'farmacos':uniq}
json.dump(data, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
print('Total fármacos:',len(uniq))
from collections import Counter
print('Por grupo:',dict(Counter(d['grupo'] for d in uniq)))
print('Tipo:',dict(Counter(d['tipo'] or '—' for d in uniq)))
print('Vía:',dict(Counter(d['via'] or '—' for d in uniq)))
print('bytes:',os.path.getsize(OUT))
