# Attachment Portability Audit

A read-only ZIP inventory for teams exchanging floor plans, brochures and photo deliveries across Windows, macOS and Linux. It reports path traversal, absolute/drive paths, backslashes, case and Unicode-normalisation collisions, Windows reserved names, streams, trailing spaces/dots, symlinks and file/directory conflicts.

```sh
python -B audit.py delivery.zip --out review.json
python -B -m unittest -q
```

Python3.10+, standard library only. It inspects the central directory, never extracts or executes members, never follows symlinks and does not modify the input. Exit0 means no configured path flags,1 means review required,2 means invalid archive or inspection limit. The declared member-size total and number of entries are bounded; limits fail closed rather than reporting a partial pass.

This is not an antivirus, ZIP-bomb decompressor, integrity/CRC check or permission to redistribute files. Archive content and symlink targets are not validated. Unicode/case collisions can matter differently on different filesystems. Keep reports private if member names are private.

Maintained by [NovAsia Estate](https://novasia.estate/). [Source and issues](https://github.com/novasia-estate/open-property-lab/tree/main/attachment-portability-audit). MIT. Tests create tiny synthetic ZIPs, including adversarial paths; none is extracted.
