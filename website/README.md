# Monofoki specimen site

This adapts the paired specimens and explanations of the [original Mononoki site](https://madmalik.github.io/mononoki/) for this fork. The default dark palette comes from Crush's [Charmtone theme](https://github.com/charmbracelet/crush/blob/main/internal/ui/styles/themes.go); the light palette uses darker versions of the same accent hues for legibility.

The `site` job in `.github/workflows/build-fonts.yml` downloads the regular and Nerd Font artifacts from its own workflow run. `script_helper/build_site.py` stages five WOFF2 files, licenses, HTML, and the demo under ignored `_site/`. Generated font and video files are never committed. Only the separate `deploy` job can publish to GitHub Pages, and it runs on `master` outside pull requests.

Asset URLs include content hashes (or the recording's source revision) so a browser cannot keep an older font, video, or poster after a new site build.

To preview locally, download the two artifacts from a successful font-build run, then run:

```sh
python3 script_helper/build_site.py \
  --regular /path/to/regular-artifact \
  --nerd /path/to/nerd-artifact \
  --revision COMMIT_SHA \
  --build-url https://github.com/nodoubleg/monofoki/actions/runs/RUN_ID
python3 -m http.server --directory _site 8000
```

The site and terminal demo get all three art pieces from `art_pieces()` in `script_helper/terminal_demo.py`. Print them with:

```sh
python3 script_helper/terminal_demo.py --art
```

For the recording, install [VHS](https://github.com/charmbracelet/vhs), `ttyd`, and `ffmpeg`, install the built Monofoki Nerd Font OTFs, and run this from the repository root after staging the site:

```sh
vhs website/demo.tape
```

The tape produces `_site/media/monofoki.mp4`. CI extracts a PNG poster from its final held artwork frame with FFmpeg. It uses deterministic specimen scenes rather than live app sessions. The video has playback controls, a poster, and a text alternative; it does not autoplay. The Nerd Fonts and Unicode versions, font-build revision and per-file SHA-256 values are recorded in `_site/build.json`.
