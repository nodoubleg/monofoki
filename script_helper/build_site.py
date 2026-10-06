#!/usr/bin/env python3
"""Stage the specimen site using fonts from GitHub Actions (no generated files in Git)."""
import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path

from terminal_demo import CHARACTER_SAMPLE, art_pieces

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regular', type=Path, required=True, help='downloaded regular font artifact directory')
    parser.add_argument('--nerd', type=Path, required=True, help='downloaded Nerd Font artifact directory')
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    parser.add_argument('--revision', required=True, help='source commit SHA of the font build')
    parser.add_argument('--build-url', required=True, help='GitHub Actions run producing these fonts')
    args = parser.parse_args()
    output = args.output.resolve()
    # Do not permit an output path that could overwrite project source.
    protected = (ROOT / name for name in ('website', 'src', 'script_helper', '.git', '.agents', '.codex'))
    if output == ROOT or ROOT.is_relative_to(output) or any(output.is_relative_to(path) for path in protected):
        parser.error('output must be a separate generated directory')
    output.mkdir(parents=True, exist_ok=True)
    for directory in ('fonts', 'licenses', 'media'):
        (output / directory).mkdir(exist_ok=True)
    for name in ('style.css', 'specimen.js'):
        shutil.copy2(ROOT / 'website' / name, output / name)
    hashes = {}
    for family, directory, styles in (
        ('Monofoki', args.regular, ('Regular', 'Italic', 'Bold', 'Bold-Italic')),
        ('MonofokiNerdFont', args.nerd, ('Regular',)),
    ):
        for style in styles:
            name = f'{family}-{style}.woff2'
            source = directory / name
            if not source.is_file() or source.stat().st_size == 0:
                parser.error(f'missing CI font: {source}')
            shutil.copy2(source, output / 'fonts' / name)
            hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    for name, directory in (('LICENSE-Monofoki', args.regular), ('LICENSE-nerd-font', args.nerd), ('license-audit-nerd-font.md', args.nerd)):
        shutil.copy2(directory / name, output / 'licenses' / name)
    gallery = []
    for key, title, description, text in art_pieces():
        gallery.append(f'<figure id="art-{key}"><pre aria-hidden="true">{html.escape(text)}</pre>'
                       f'<figcaption>{html.escape(title)}<small>{html.escape(description)}</small></figcaption></figure>')
    document = (ROOT / 'website' / 'index.html').read_text()
    replacements = {'@@ART_GALLERY@@': '\n'.join(gallery), '@@CHARACTER_SAMPLE@@': html.escape(CHARACTER_SAMPLE),
                    '@@BUILD_URL@@': html.escape(args.build_url, quote=True), '@@BUILD_REVISION@@': html.escape(args.revision[:7])}
    for marker, value in replacements.items():
        assert marker in document, marker
        document = document.replace(marker, value)
    (output / 'index.html').write_text(document)
    shutil.copy2(ROOT / 'script_helper' / 'terminal_demo.py', output / 'terminal_demo.py')
    text_demo = '\n\n'.join(f'{title}\n\n{text}' for _, title, _, text in art_pieces())
    (output / 'demo.txt').write_text(f'Monofoki terminal specimen\n\n{CHARACTER_SAMPLE}\n\n{text_demo}\n')
    (output / 'build.json').write_text(json.dumps({'revision': args.revision, 'build_url': args.build_url,
                                                'font_sha256': hashes, 'vhs_version': '0.12.1'}, indent=2) + '\n')
    (output / '.nojekyll').touch()
    print(f'Staged {len(hashes)} CI webfonts and {len(gallery)} shared art pieces in {output}')


if __name__ == '__main__':
    main()
