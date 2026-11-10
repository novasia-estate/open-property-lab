'use strict';
let parser;
async function inspect(source) {
  if(typeof source!=='string'||Buffer.byteLength(source,'utf8')>2*1024*1024) throw new Error('Require HTML text of at most2MiB.');
  parser??=await import('parse5');
  const full=/<!doctype\s+html|<html(?:\s|>)/i.test(source);
  const doc=full?parser.parse(source,{sourceCodeLocationInfo:true}):parser.parseFragment(source,{sourceCodeLocationInfo:true});
  const nodes=[];function visit(n,parent){n.reviewParent=parent;nodes.push(n);for(const c of n.childNodes||[])visit(c,n);if(n.content)visit(n.content,n);}
  visit(doc,null);
  const attr=(n,k)=>n.attrs?.find(a=>a.name===k)?.value;
  const ids=new Map();for(const n of nodes){const id=attr(n,'id');if(id){if(!ids.has(id))ids.set(id,[]);ids.get(id).push(n);}}
  const hidden=n=>{for(let p=n;p;p=p.reviewParent)if(attr(p,'aria-hidden')==='true'||attr(p,'hidden')!==undefined||p.tagName==='template')return true;return false;};
  const text=n=>{
    if(hidden(n)||['script','style','template'].includes(n.tagName))return '';
    if(n.nodeName==='#text')return n.value||'';
    if(n.tagName==='img')return attr(n,'alt')||'';
    return (n.childNodes||[]).map(text).join(' ').trim();
  };
  const accessibleName=n=>{
    if(attr(n,'aria-labelledby')!==undefined)return attr(n,'aria-labelledby').split(/\s+/).filter(Boolean).map(id=>ids.get(id)?.length===1?text(ids.get(id)[0]):'').join(' ').trim();
    if(attr(n,'aria-label')!==undefined)return attr(n,'aria-label').trim();
    if(['button','a'].includes(n.tagName))return text(n);
    const id=attr(n,'id');
    const labels=nodes.filter(x=>x.tagName==='label'&&id&&attr(x,'for')===id).map(text);
    for(let p=n.reviewParent;p;p=p.reviewParent)if(p.tagName==='label'){labels.push(text(p));break;}
    return labels.join(' ').trim();
  };
  const issues=[];
  function flag(n,rule,message){const l=n.sourceCodeLocation;if(!l)return;issues.push({rule,message,start:l.startOffset,end:l.startTag?.endOffset||l.endOffset||l.startOffset+1,line:l.startLine,column:l.startCol});}
  for(const [id,items] of ids)if(items.length>1)for(const n of items)flag(n,'duplicate-id',`Duplicate ID "${id}" can break label references.`);
  for(const n of nodes){
    if(!n.tagName||hidden(n))continue;
    if(n.tagName==='html'&&full&&!attr(n,'lang')?.trim())flag(n,'document-language','Declare the document language; fragments are not required to include an html element.');
    if(n.tagName==='img'&&attr(n,'alt')===undefined&&attr(n,'role')!=='presentation'&&attr(n,'role')!=='none')flag(n,'image-alternative','Image has no alt attribute. Supply meaningful alternative text or explicitly document that the image is decorative.');
    if((n.tagName==='button'||(n.tagName==='a'&&attr(n,'href')!==undefined))&&!accessibleName(n))flag(n,'empty-action-name','Action has no name found by the supported text/ARIA/label checks.');
    if(['input','select','textarea'].includes(n.tagName)){
      const type=(attr(n,'type')||'text').toLowerCase();
      if(['hidden','button','submit','reset','image'].includes(type)){
        if(type==='image'&&!attr(n,'alt')?.trim()&&!accessibleName(n))flag(n,'image-input-name','Image input needs an accessible name.');
      }else if(!accessibleName(n))flag(n,'input-label','Control has no explicit label found. A placeholder is not a persistent label.');
    }
    const refs=attr(n,'aria-labelledby');
    if(refs!==undefined)for(const id of refs.split(/\s+/).filter(Boolean))if(ids.get(id)?.length!==1)flag(n,'label-reference',`aria-labelledby reference "${id}" is missing or ambiguous.`);
  }
  return issues;
}
module.exports={inspect};
