"""Inspect ZIP member paths without extracting or executing any archive contents."""
import argparse, collections, json, re, stat, unicodedata, zipfile
from pathlib import Path, PurePosixPath

RESERVED=re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)',re.I)

def audit(path,max_members=10000,max_total_bytes=2_000_000_000):
    findings=[];groups=collections.defaultdict(list)
    def issue(member,code,detail): findings.append({'member':member,'code':code,'detail':detail})
    with zipfile.ZipFile(path) as archive:
        members=archive.infolist()
        if len(members)>max_members: raise ValueError('Member count exceeds inspection limit; no partial clearance.')
        declared_total=sum(i.file_size for i in members)
        if declared_total>max_total_bytes:raise ValueError('Declared uncompressed size exceeds inspection limit.')
        for info in members:
            name=info.filename;normalized=name.replace('\\','/');parts=normalized.split('/')
            if normalized.startswith('/') or re.match(r'^[A-Za-z]:',normalized) or '..' in parts:
                issue(name,'unsafe_path','Absolute, drive-prefixed or parent-traversing path.')
            if '\\' in name:issue(name,'backslash_path','Backslash has different path meaning across extractors.')
            if any(ord(c)<32 or ord(c)==127 for c in name):issue(name,'control_character','Control character in member path.')
            if any(c in normalized for c in ':*?"<>|'):issue(name,'windows_invalid_character','Not a portable Windows path; colon may denote a stream.')
            for part in filter(None,parts):
                if RESERVED.match(part):issue(name,'windows_reserved_name',part)
                if part.endswith((' ','.')):issue(name,'trailing_dot_or_space',part)
            mode=(info.external_attr>>16)&0xFFFF
            if stat.S_ISLNK(mode):issue(name,'symlink','Symlink metadata; target is deliberately not followed or read.')
            if info.flag_bits&1:issue(name,'encrypted','Encrypted member; contents not verified.')
            if len(normalized)>240:issue(name,'long_path','More than240 path characters; host limits differ.')
            key=unicodedata.normalize('NFC',normalized).casefold().rstrip('/')
            groups[key].append(name)
        for key,names in groups.items():
            if len(names)>1:issue(names[0],'portable_name_collision',json.dumps(names,ensure_ascii=False))
        # A file named a and a child a/b cannot both be extracted as intended.
        files={unicodedata.normalize('NFC',i.filename.replace('\\','/')).casefold().rstrip('/') for i in members if not i.is_dir()}
        for info in members:
            parts=unicodedata.normalize('NFC',info.filename.replace('\\','/')).casefold().strip('/').split('/')
            if any('/'.join(parts[:n]) in files for n in range(1,len(parts))):issue(info.filename,'file_directory_conflict','A parent path is also an archive file.')
    return {'schema_version':1,'members_inspected':len(members),'declared_uncompressed_bytes':declared_total,'content_status':'not_decompressed_or_verified','findings':findings,'status':'review_required' if findings else 'no_path_flags'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    try:report=audit(a.archive)
    except (OSError,ValueError,zipfile.BadZipFile) as e:p.exit(2,str(e)+'\n')
    text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if a.out:a.out.write_text(text,encoding='utf-8')
    else:print(text,end='')
    return 1 if report['findings'] else 0
if __name__=='__main__':raise SystemExit(main())
