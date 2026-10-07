#!/usr/bin/env python3
"""Export actual font repertoires and scoped fallback targets for the site."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def make_catalog(regular, nerd, glyphnames):
    data = ROOT / 'script_helper/unicode/18.0.0'
    names, categories = {}, {}
    for line in (data / 'UnicodeData.txt').read_text().splitlines():
        fields = line.split(';')
        cp = int(fields[0], 16)
        names[cp], categories[cp] = fields[1:3]
    scripts = []
    for line in (data / 'Scripts.txt').read_text().splitlines():
        value = line.split('#')[0].strip()
        if not value:
            continue
        interval, script = map(str.strip, value.split(';'))
        ends = interval.split('..')
        scripts.append((int(ends[0], 16), int(ends[-1], 16), script))
    def allowed(cp):
        script = next((script for first, last, script in scripts if first <= cp <= last), 'Unknown')
        return script in ('Latin', 'Common', 'Inherited') or categories.get(cp, '').startswith('S') or categories.get(cp) == 'Co'
    with TTFont(regular) as font:
        regular_map = font.getBestCmap()
    with TTFont(nerd) as font:
        nerd_map = font.getBestCmap()
    original = json.loads((ROOT / 'script_helper/mononoki_repertoire.json').read_text())
    metadata = json.loads(glyphnames.read_text())
    assert metadata['METADATA']['version'] == '3.5.1'
    aliases = defaultdict(list)
    for name, item in metadata.items():
        if name != 'METADATA':
            aliases[int(item['code'], 16)].append(name)
    def entry(cp):
        return {'codepoint': f'{cp:04X}', 'name': names.get(cp, regular_map.get(cp, nerd_map.get(cp, 'PRIVATE USE'))),
                'category': categories.get(cp, 'Co'), 'regular': cp in regular_map, 'nerd': cp in nerd_map}
    baseline = [entry(cp) for cp in original['codepoints'] if allowed(cp)]
    icons = []
    for cp in sorted(nerd_map):
        private = 0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD or 0x100000 <= cp <= 0x10FFFD
        if private or (cp not in regular_map and allowed(cp)):
            item = entry(cp)
            item['aliases'] = sorted(aliases.get(cp, [nerd_map[cp]]))
            item['group'] = item['aliases'][0].split('-')[0] if private else 'unicode'
            icons.append(item)
    scope = json.loads((ROOT / 'script_helper/terminal_ranges.json').read_text())
    targets = {cp for _, _, first, last in scope['blocks'] for cp in range(first, last + 1)
               if cp in names and categories[cp] not in ('Cc', 'Cf', 'Cs') and allowed(cp)}
    assert len(targets) == 2113
    targets.update(int(item['codepoint'], 16) for item in baseline)
    fallback = [entry(cp) for cp in sorted(targets) if cp not in regular_map or cp not in nerd_map]
    return {'schema_version': 1, 'unicode_version': '18.0.0', 'nerd_fonts_version': '3.5.1',
            'filter': 'Latin, Common, Inherited, symbols and private-use characters; other writing-system alphabets omitted',
            'original_source': original['source'], 'original_source_sha256': original['source_sha256'],
            'font_sha256': {'regular': hashlib.sha256(regular.read_bytes()).hexdigest(),
                            'nerd': hashlib.sha256(nerd.read_bytes()).hexdigest()},
            'baseline': baseline, 'icons': icons, 'fallback': fallback}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regular', type=Path, required=True)
    parser.add_argument('--nerd', type=Path, required=True)
    parser.add_argument('--glyphnames', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalog = make_catalog(args.regular, args.nerd, args.glyphnames)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    print(f'Catalogue: {len(catalog["baseline"])} original characters, {len(catalog["icons"])} Nerd glyphs, {len(catalog["fallback"])} fallback targets')
