import json,sys
d=json.load(open(sys.argv[1])); part=sys.argv[2]; lim=int(sys.argv[3]) if len(sys.argv)>3 else 100
root = d[part] if part in ('header','footer') else d['sections'][int(part)]
keys=['display','position','width','height','fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','textTransform','color','backgroundColor','backgroundImage','borderTop','borderBottom','borderRadius','paddingTop','paddingRight','paddingBottom','paddingLeft','marginTop','marginBottom','boxShadow','opacity','textAlign','top','left','right','bottom']
out=[]
def walk(n,dep=0):
    s=n['s']; t=n.get('x','') or n.get('ph','')
    show = t or n['t'] in ('img','input','button','a','iframe','h1','h2','h3','h4','hr') or 'backgroundColor' in s or 'backgroundImage' in s or 'borderTop' in s or 'borderBottom' in s
    if show:
        st={k:s[k][:90] for k in keys if k in s and not (k in('fontFamily','fontSize','fontWeight','lineHeight','color') and not t and n['t'] not in('a','button','input'))}
        extra=(' src='+n['src'][-60:]) if 'src' in n else ''
        extra+=(' href='+n['href'][:40]) if 'href' in n else ''
        out.append('  '*min(dep,12)+f"{n['t']}.{(n.get('c') or '')[:40]} {n['r']} {t[:60]!r}{extra} {st}")
    for k in n.get('k',[]): walk(k,dep+1)
walk(root)
print('\n'.join(out[:lim]))
