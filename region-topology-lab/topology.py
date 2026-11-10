"""Exact grid audit of explicitly supplied simple orthogonal regions."""
from fractions import Fraction as F
import itertools
import json
import math
import re


def number(value):
    if type(value) is int:
        result = F(value)
    elif isinstance(value, str) and re.fullmatch(r'[+-]?\d+(?:\.\d+)?', value):
        result = F(value)
    else:
        raise ValueError('Coordinates must be integers or decimal strings')
    if abs(result) > 1_000_000:
        raise ValueError('Coordinate limit exceeded')
    return result


def ring(raw):
    if not isinstance(raw, list) or not 4 <= len(raw) <= 81:
        raise ValueError('A ring needs 4 to 80 vertices, plus optional closing vertex')
    pts = []
    for point in raw:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError('Each point needs x and y')
        pts.append(tuple(map(number, point)))
    if pts[0] == pts[-1]: pts.pop()
    if len(pts) < 4 or len(set(pts)) != len(pts):
        raise ValueError('Repeated or insufficient vertices')
    edges = list(zip(pts, pts[1:]+pts[:1]))
    for i, (a,b) in enumerate(edges):
        if (a[0] == b[0]) == (a[1] == b[1]):
            raise ValueError('Only nonzero axis-aligned edges are supported')
        c = pts[(i+2)%len(pts)]
        if (b[0]-a[0])*(c[1]-b[1]) == (b[1]-a[1])*(c[0]-b[0]):
            raise ValueError('Remove redundant or reversing collinear vertices')
    def touch(e,f):
        (a,b),(c,d)=e,f
        return (max(min(a[0],b[0]),min(c[0],d[0])) <= min(max(a[0],b[0]),max(c[0],d[0])) and
                max(min(a[1],b[1]),min(c[1],d[1])) <= min(max(a[1],b[1]),max(c[1],d[1])))
    for i,e in enumerate(edges):
        for j,f in enumerate(edges[i+1:],i+1):
            if j == i+1 or (i == 0 and j == len(edges)-1): continue
            if touch(e,f): raise ValueError('Self-intersecting or self-touching ring')
    return pts


def inside(point, pts):
    x,y=point;yes=False
    for (ax,ay),(bx,by) in zip(pts,pts[1:]+pts[:1]):
        if ax == bx and ((ay > y) != (by > y)) and x < ax: yes=not yes
    return yes


def analyse(document):
    envelope=ring(document['envelope'])
    rawrooms=document['regions']
    if not isinstance(rawrooms,list) or not 1 <= len(rawrooms) <= 20:
        raise ValueError('Supply 1 to 20 regions')
    rooms={}
    for room in rawrooms:
        key=room['id']
        if not isinstance(key,str) or not key or key in rooms:
            raise ValueError('Region identifiers must be unique nonempty strings')
        rooms[key]=ring(room['polygon'])
    allpoints=envelope+list(itertools.chain.from_iterable(rooms.values()))
    if len(allpoints)>256: raise ValueError('Vertex limit exceeded')
    xs=sorted({p[0] for p in allpoints});ys=sorted({p[1] for p in allpoints})
    if (len(xs)-1)*(len(ys)-1)>4096: raise ValueError('Grid limit exceeded')
    cells={};envelope_area=F(0);gap=F(0);overlap=F(0);covered=F(0)
    totals={k:F(0) for k in rooms};outside={k:F(0) for k in rooms}
    issues=[]
    for i,(left,right) in enumerate(zip(xs,xs[1:])):
        for j,(bottom,top) in enumerate(zip(ys,ys[1:])):
            point=((left+right)/2,(bottom+top)/2)
            owners=tuple(k for k,p in rooms.items() if inside(point,p))
            within=inside(point,envelope);area=(right-left)*(top-bottom)
            cells[i,j]=(within,owners)
            for key in owners:
                totals[key]+=area
                if not within: outside[key]+=area
            if not within: continue
            envelope_area+=area
            if not owners: gap+=area;kind='gap'
            elif len(owners)>1: overlap+=area;kind='overlap';covered+=area
            else: covered+=area;continue
            issues.append({'kind':kind,'bbox':list(map(str,(left,bottom,right,top))), 'regions':list(owners),'area':str(area)})
    interfaces={}
    for (i,j),(within,owners) in cells.items():
        if not within or len(owners)!=1: continue
        for neighbour,length in [((i+1,j),ys[j+1]-ys[j]),((i,j+1),xs[i+1]-xs[i])]:
            inside_other,others=cells.get(neighbour,(False,()))
            if inside_other and len(others)==1 and owners!=others:
                pair=tuple(sorted((owners[0],others[0])))
                interfaces[pair]=interfaces.get(pair,F(0))+length
    assert gap+covered==envelope_area
    return {'units':'caller-supplied drawing units; areas are squared units',
            'envelope_area':str(envelope_area),'covered_union_area':str(covered),
            'uncovered_area':str(gap),'multiply_covered_area':str(overlap),
            'region_area':{k:str(v) for k,v in totals.items()},
            'outside_envelope_area':{k:str(v) for k,v in outside.items()},
            'exclusive_interfaces':[{'regions':list(k),'length':str(v)} for k,v in sorted(interfaces.items())],
            'cells':issues,'grid_cells':len(cells)}


def svg(document):
    import html
    points=ring(document['envelope'])+list(itertools.chain.from_iterable(ring(r['polygon']) for r in document['regions']))
    lo=min(x for x,y in points);hi=max(x for x,y in points);bottom=min(y for x,y in points);top=max(y for x,y in points)
    width=float(hi-lo);height=float(top-bottom)
    def poly(raw,color):
        pts=ring(raw)
        coords=' '.join(f'{float(x-lo):.8g},{float(top-y):.8g}' for x,y in pts)
        return f'<polygon points="{coords}" fill="{color}" fill-opacity="0.3" stroke="#243c56" stroke-width="{max(width,height)/250}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Synthetic regions; consult the numeric report" viewBox="-0.3 -0.3 {width+.6} {height+.6}" style="width:100%;max-width:700px;height:280px">'+poly(document['envelope'],'#e2e8f0')+''.join(poly(r['polygon'],['#0ea5a4','#f59e0b','#8b5cf6','#ec4899'][i%4]) for i,r in enumerate(document['regions']))+'</svg>'


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input');args=parser.parse_args()
    with open(args.input,encoding='utf-8') as f: data=json.load(f)
    print(json.dumps(analyse(data),indent=2))
