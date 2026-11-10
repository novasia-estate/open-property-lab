"""Bounded digital-PDF table recovery. No OCR, network, disk staging or silent cell correction."""
import csv,hashlib,io,json,zipfile

MAX_BYTES=10*1024*1024
MAX_PAGES=30
MAX_TABLES=100
MAX_CELLS=25000

def recover_pdf(data,selected_pages=None):
    if not isinstance(data,bytes) or not data or len(data)>MAX_BYTES:raise ValueError('Require PDF bytes,1–10MiB.')
    if not data.lstrip().startswith(b'%PDF-'):raise ValueError('Input is not a PDF header.')
    import pdfplumber
    reports=[];cells=0
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        if len(pdf.pages)>MAX_PAGES:raise ValueError('At most30pages per document; split before uploading.')
        pages=list(range(1,len(pdf.pages)+1)) if selected_pages is None else list(selected_pages)
        if not pages or len(set(pages))!=len(pages) or any(type(p) is not int or p<1 or p>len(pdf.pages) for p in pages):raise ValueError('Select unique existing1-based page numbers.')
        for number in pages:
            page=pdf.pages[number-1]
            for local_index,table in enumerate(page.find_tables(),1):
                if len(reports)>=MAX_TABLES:raise ValueError('Too many tables; no partial export.')
                original=table.extract();cells+=sum(len(r) for r in original)
                if cells>MAX_CELLS:raise ValueError('Too many cells; no partial export.')
                matrix=[[None if c is None else str(c) for c in row] for row in original]
                width=max((len(r) for r in matrix),default=0)
                issues=[]
                if any(len(r)!=width for r in matrix):issues.append('ragged_rows')
                if any(c is None for row in matrix for c in row):issues.append('missing_or_merged_cell')
                if matrix and len(set(c for c in matrix[0] if c))!=len([c for c in matrix[0] if c]):issues.append('duplicate_header_text')
                reports.append({'table_id':f'p{number}-t{local_index}','page':number,'bbox':list(table.bbox),'rows':matrix,'column_count':width,'flags':issues})
        scanned=not any(pdf.pages[n-1].chars for n in pages)
    return {'schema_version':1,'source_sha256':hashlib.sha256(data).hexdigest(),'source_bytes':len(data),'pages_inspected':pages,'digital_text_absent':scanned,'tables':reports,'method':'pdfplumber ruled-line detection; no OCR','limits':{'max_bytes':MAX_BYTES,'max_pages':MAX_PAGES,'max_tables':MAX_TABLES,'max_cells':MAX_CELLS}}

def edited_table(original,rows):
    if not isinstance(rows,list) or not rows or len(rows)>5000:raise ValueError('Require1–5000 rows.')
    if any(not isinstance(r,list) or len(r)!=original['column_count'] or any(c is not None and not isinstance(c,str) for c in r) for r in rows):raise ValueError('Every edited row must preserve the declared column width and text/null types.')
    result={**original,'rows':rows,'original_rows':original['rows'],'user_edited':True}
    return result

def csv_bytes(table,spreadsheet_safe=True):
    output=io.StringIO(newline='');writer=csv.writer(output)
    for row in table['rows']:
        values=[]
        for cell in row:
            text='' if cell is None else cell
            if spreadsheet_safe and text.lstrip().startswith(('=','+','-','@','\t','\r')):text="'"+text
            values.append(text)
        writer.writerow(values)
    return output.getvalue().encode('utf-8-sig')

def bundle(report,table):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('table.csv',csv_bytes(table))
        archive.writestr('provenance.json',json.dumps({**report,'selected_table':table},ensure_ascii=False,indent=2))
        archive.writestr('README.txt','Table values are extracted text, not verified prices or availability. CSV prefixes formula-looking values for spreadsheet safety; JSON preserves original text and manual edits. Coordinates are PDF page points from pdfplumber. Source PDF is not included.')
    return buffer.getvalue()
