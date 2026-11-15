import json,sys
d=json.load(open(sys.argv[1])); lim=int(sys.argv[2]) if len(sys.argv)>2 else 120
seen=set(); out=[]
keys=['fontFamily','fontSize','fontWeight','lineHeight','color','backgroundColor','borderTop','borderBottom','borderRadius','paddingTop','paddingRight','boxShadow','letterSpacing','textTransform','textDecorationLine']
def walk(n,dep=0):
    t=(n.get('x','') or n.get('ph',''))
    s=n['s']
    if t or n['t'] in('input','button','textarea') or ('backgroundColor' in s):
        sig=(t[:25],n['t'],s.get('fontSize'),s.get('backgroundColor'))
        if sig not in seen:
            seen.add(sig)
            st={k:s[k].replace('Rubik-Regular, ','') for k in keys if k in s}
            out.append(f"{n['t']} {(n.get('c') or '')[:22]} {n['r']} {t[:40]!r} {st}")
    for k in n.get('k',[]): walk(k,dep+1)
walk(d['tree'] if 'tree' in d else d)
print('\n'.join(out[:lim]))
