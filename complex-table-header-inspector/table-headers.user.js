// ==UserScript==
// @name         Complex Table Header Inspector
// @namespace    https://novasia.estate/
// @version      1.0.0
// @description  Inspect explicit and scoped HTML table header associations, spans and structural problems locally, on demand.
// @author       NovAsia Estate
// @homepageURL  https://novasia.estate/
// @supportURL   https://github.com/novasia-estate/open-property-lab/issues
// @license      MIT
// @match        http://*/*
// @match        https://*/*
// @grant        GM_registerMenuCommand
// @run-at       document-idle
// @noframes
// ==/UserScript==

(function () {
  'use strict';
  function inspect(table) {
    const rows = Array.from(table.rows);
    if (rows.length > 200) throw new Error('Table exceeds the 200-row review limit.');
    const grid = [], cells = [], issues = [], byElement = new Map(), ids = new Map();
    const colgroups = []; let column = 0;
    for (const group of Array.from(table.children).filter(e => e.tagName === 'COLGROUP')) {
      const cols = Array.from(group.children).filter(e => e.tagName === 'COL');
      const span = cols.length ? cols.reduce((n, c) => n + c.span, 0) : group.span;
      if (column + span > 80) throw new Error('Column groups exceed the 80-column review limit.');
      for (let i = 0; i < span; i++) colgroups[column++] = group;
    }
    rows.forEach((row, r) => {
      grid[r] ||= []; let c = 0;
      for (const el of Array.from(row.cells)) {
        while (grid[r][c]) c++;
        let groupEnd = r;
        while (groupEnd + 1 < rows.length && rows[groupEnd + 1].parentElement === row.parentElement) groupEnd++;
        const declared = el.rowSpan, height = declared === 0 ? groupEnd - r + 1 : declared;
        const width = el.colSpan;
        if (c + width > 80 || cells.length >= 4000) throw new Error('Table exceeds the 80-column / 4000-cell review limit.');
        if (r + height - 1 > groupEnd) issues.push(`Row ${r + 1}, column ${c + 1}: rowspan crosses its row group; clipped for review.`);
        const cell = {el, row:r, col:c, height:Math.min(height, groupEnd-r+1), width, group:row.parentElement,
          header:el.tagName === 'TH', scope:(el.getAttribute('scope') || '').toLowerCase(), id:el.id};
        cells.push(cell); byElement.set(el, cell);
        if (el.id) { const entries = ids.get(el.id) || []; entries.push(cell); ids.set(el.id, entries); }
        for (let y=r;y<r+cell.height;y++) {
          grid[y] ||= [];
          for (let x=c;x<c+width;x++) {
            if (grid[y][x]) issues.push(`Overlapping spans at row ${y+1}, column ${x+1}.`);
            else grid[y][x] = cell;
          }
        }
        if (cell.header && !['row','col','rowgroup','colgroup'].includes(cell.scope))
          issues.push(`Header at row ${r+1}, column ${c+1}: ${cell.scope ? 'invalid scope' : 'no explicit scope'}; automatic header inference is outside this tool.`);
        c += width;
      }
    });
    for (const [id, entries] of ids) if (entries.length>1) issues.push(`Duplicate cell ID: ${id}.`);
    const width = Math.max(0,...grid.map(r=>r.length));
    grid.forEach((row,r)=>{ for(let c=0;c<width;c++) if(!row[c]) issues.push(`Unoccupied slot at row ${r+1}, column ${c+1}.`); });
    function headersFor(cell) {
      const found = [], warnings = [];
      const attr = cell.el.getAttribute('headers');
      if (attr !== null) {
        for (const id of [...new Set(attr.trim().split(/\s+/).filter(Boolean))]) {
          const matches = ids.get(id) || [];
          if(matches.length!==1 || !matches[0].header || matches[0]===cell) warnings.push(`Unresolved, ambiguous or non-header reference: ${id}.`);
          else found.push(matches[0]);
        }
        return {headers:found, warnings, mode:'explicit headers attribute'};
      }
      for(const h of cells.filter(c=>c.header && c!==cell)) {
        const rowOverlap = h.row < cell.row+cell.height && cell.row < h.row+h.height;
        const colOverlap = h.col < cell.col+cell.width && cell.col < h.col+h.width;
        let match = h.scope==='row' && rowOverlap || h.scope==='col' && colOverlap || h.scope==='rowgroup' && h.group===cell.group;
        if(h.scope==='colgroup') {
          const groups = colgroups.slice(h.col,h.col+h.width).filter(Boolean);
          if(!groups.length) warnings.push(`Column-group header at row ${h.row+1}, column ${h.col+1} has no declared colgroup.`);
          match = colgroups.slice(cell.col,cell.col+cell.width).some(g=>g && groups.includes(g));
        }
        if(match) found.push(h);
      }
      if(!found.length) warnings.push('No explicit or supported scoped headers found. Check the browser accessibility tree manually.');
      return {headers:found,warnings,mode:'declared scope review'};
    }
    return {cells, grid, issues:[...new Set(issues)], headersFor};
  }
  if(typeof module!=='undefined' && module.exports) { module.exports={inspect}; return; }
  let panel;
  function open() {
    if(panel) { panel.remove(); panel=null; }
    const tables=Array.from(document.querySelectorAll('table')).slice(0,101);
    panel=document.createElement('div'); const shadow=panel.attachShadow({mode:'open'});
    const style=document.createElement('style'); style.textContent=':host{all:initial;position:fixed;inset:20px 20px auto auto;z-index:2147483647;width:min(540px,90vw)}section{font:15px/1.5 system-ui;background:#fff;color:#172033;border:2px solid #265eaa;box-shadow:0 8px 40px #0005;padding:18px;max-height:85vh;overflow:auto}h2{margin:0 0 10px;font-size:20px}label{display:block;margin-top:10px}select,button{font:inherit;max-width:100%;padding:5px}p{margin:8px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 monospace}'; shadow.append(style);
    const section=document.createElement('section'); section.setAttribute('role','dialog'); section.setAttribute('aria-label','Complex Table Header Inspector');
    const h=document.createElement('h2');h.textContent='Complex Table Header Inspector'; section.append(h);
    const close=document.createElement('button');close.textContent='Close';close.onclick=()=>{panel.remove();panel=null;};section.append(close);
    const p=document.createElement('p');p.textContent='Local review only. No page data is uploaded or stored. This reviews explicit headers and declared scopes, not the full browser inference algorithm or a WCAG conformance verdict.';section.append(p);
    function select(label) {const l=document.createElement('label');l.append(document.createTextNode(label+' '));const s=document.createElement('select');l.append(s);section.append(l);return s;}
    const tableSelect=select('Table'),cellSelect=select('Cell');const report=document.createElement('pre');report.setAttribute('aria-live','polite');section.append(report);
    function option(s,value,text){const o=document.createElement('option');o.value=String(value);o.textContent=text;s.append(o);}
    function label(c){return `r${c.row+1} c${c.col+1} ${c.header?'TH':'TD'}: ${c.el.textContent.trim().replace(/\s+/g,' ').slice(0,100)}`;}
    tables.slice(0,100).forEach((t,i)=>option(tableSelect,i,`Table ${i+1}: ${(t.caption?.textContent || t.getAttribute('aria-label') || 'unnamed').trim().slice(0,80)}`));
    let model;
    function showCell(){if(!model)return;const c=model.cells[Number(cellSelect.value)];if(!c)return;const result=model.headersFor(c);report.textContent=[label(c),`Mode: ${result.mode}`,`Headers (${result.headers.length}):`,...result.headers.map(label),'',...result.warnings,'',`Structural findings (${model.issues.length}):`,...model.issues.slice(0,100),model.issues.length>100?'Further findings omitted.':''].join('\n');}
    function showTable(){cellSelect.replaceChildren();model=null;try{model=inspect(tables[Number(tableSelect.value)]);model.cells.forEach((c,i)=>option(cellSelect,i,label(c)));if(!model.cells.length)report.textContent='Empty table.';else showCell();}catch(e){report.textContent=e.message;}}
    tableSelect.onchange=showTable;cellSelect.onchange=showCell;shadow.append(section);document.documentElement.append(panel);
    if(tables.length)showTable();else report.textContent='No HTML tables in this document. Shadow DOM and cross-origin frames are not scanned.';
    if(tables.length>100)p.textContent+=' First 100 tables only.';
    close.focus();section.addEventListener('keydown',e=>{if(e.key==='Escape')close.click();});
  }
  GM_registerMenuCommand('Inspect complex table headers',open);
})();
