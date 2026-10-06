#!/usr/bin/env python3
"""Keep existing terminal-profile PostScript names without changing font outlines."""
import sys
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont


def charstrings(font):
    if 'CFF ' not in font:
        return None
    cff = font['CFF '].cff
    result = {}
    for name in cff.topDictIndex[0].CharStrings.keys():
        string = cff.topDictIndex[0].CharStrings[name]
        string.compile()
        result[name] = string.bytecode
    return result


def preserve(path):
    style = path.stem.removeprefix('MonofokiNerdFont-')
    if style not in ('Regular', 'Italic', 'Bold', 'BoldItalic'):
        raise ValueError(f'Unexpected Nerd Font style: {path}')
    postscript = f'MonofokiNF-{style}'
    with TTFont(path, lazy=True, recalcBBoxes=False, recalcTimestamp=False) as font:
        if font['name'].getDebugName(6) == postscript:
            return
        untouched = {tag: font.reader[tag] for tag in font.reader.keys() if tag not in ('name', 'head', 'CFF ')}
        outlines = charstrings(font)
        head = font.reader['head']
        for record in font['name'].names:
            if record.nameID == 6:
                record.string = postscript.encode(record.getEncoding())
        if 'CFF ' in font:
            font['CFF '].cff.fontNames = [postscript]
        with tempfile.TemporaryDirectory(dir=path.parent) as directory:
            temporary = Path(directory) / path.name
            font.save(temporary)
            with TTFont(temporary, lazy=True, recalcBBoxes=False, recalcTimestamp=False) as checked:
                assert checked['name'].getDebugName(6) == postscript
                assert all(checked.reader[tag] == data for tag, data in untouched.items()), 'non-name table changed'
                assert charstrings(checked) == outlines, 'CFF glyph bytes changed'
                updated_head = checked.reader['head']
                assert head[:8] + head[12:] == updated_head[:8] + updated_head[12:], 'head fields changed'
            temporary.replace(path)
    print(f'{path.name}: preserved {postscript}; outline, hint and metric data unchanged')


if __name__ == '__main__':
    for path in map(Path, sys.argv[1:]):
        preserve(path)
