import hashlib,io,json
import streamlit as st
import pandas as pd
from recovery import recover_pdf,edited_table,csv_bytes,bundle,MAX_BYTES

st.set_page_config(page_title='Brochure Table Recovery Workbench',page_icon='▦',layout='wide')
st.title('Brochure Table Recovery Workbench')
st.write('Recover a ruled table from a digital PDF, inspect page and bounding-box provenance, correct cell text, then export a reviewable table.')
st.caption('Open-source workbench by [NovAsia Estate](https://novasia.estate/) · [Source and limitations](https://github.com/novasia-estate/open-property-lab/tree/main/brochure-table-recovery)')
st.info('Public hosted app: uploaded PDF bytes are sent to the hosting server for this session. Use public brochures or synthetic files. Do not upload contracts, IDs, tenant details or confidential documents. The application does not intentionally write uploads to disk or external services; hosting logs and infrastructure are controlled by Streamlit.')
with st.expander('What this tool can and cannot recover'):
 st.write('Up to10MiB and30pages. It detects ruled-line tables, not every visual layout. Scanned PDFs need OCR elsewhere. It does not authenticate documents, infer current availability, fix prices or automatically guess missing columns. Always compare the exported text with the source page. Extraction uses a bounded report, but PDF parser work is not a hardened security sandbox.')
uploaded=st.file_uploader('Public digital PDF brochure',type=['pdf'])
if uploaded:
 data=uploaded.getvalue()
 if len(data)>MAX_BYTES:st.error('File is larger than10MiB.');st.stop()
 key=hashlib.sha256(data).hexdigest()
 if st.session_state.get('source_key')!=key:
  st.session_state.clear();st.session_state.source_key=key
 if st.button('Inspect PDF tables',type='primary'):
  try:st.session_state.report=recover_pdf(data)
  except Exception as e:st.error(f'Could not inspect PDF: {type(e).__name__}: {e}')
 report=st.session_state.get('report')
 if report:
  st.code('Source SHA-256: '+report['source_sha256'],language=None)
  if not report['tables']:
   st.warning('No ruled tables found. '+('The inspected pages contain no extractable digital characters. ' if report['digital_text_absent'] else '')+'No OCR or automatic reconstruction was attempted.')
  else:
   selected=st.selectbox('Recovered table',[t['table_id'] for t in report['tables']]);table=next(t for t in report['tables'] if t['table_id']==selected)
   st.write(f"Source page: {table['page']} · Bounding box (PDF points): {table['bbox']}")
   if table['flags']:st.warning('Review flags: '+', '.join(table['flags']))
   padded=[r+[None]*(table['column_count']-len(r)) for r in table['rows']]
   frame=pd.DataFrame(padded,columns=[f'column_{i+1}' for i in range(table['column_count'])])
   st.subheader('Review and correct text')
   st.caption('Column labels above are neutral positions, not invented field meanings. The first recovered row is retained as data. JSON keeps the original extracted rows alongside edits.')
   edited=st.data_editor(frame,num_rows='dynamic',key='edit_'+selected,hide_index=True)
   current=edited_table(table,[[None if pd.isna(c) else str(c) for c in row] for row in edited.values.tolist()])
   a,b,c=st.columns(3)
   a.download_button('Download spreadsheet-safe CSV',csv_bytes(current),'recovered-table.csv','text/csv')
   b.download_button('Download JSON with original cells',json.dumps({**report,'selected_table':current},ensure_ascii=False,indent=2),'recovery-provenance.json','application/json')
   c.download_button('Download CSV + provenance bundle',bundle(report,current),'table-review.zip','application/zip')
 if st.button('Clear this session'):
  st.session_state.clear();st.rerun()
else:st.write('Start with a public PDF containing a visibly ruled table. No example market prices or private documents are preloaded.')
