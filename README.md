# Salt & Ember — a throwaway test kitchen

30 hand-written recipes, 240+ web-sourced photos, 70+ verified YouTube videos,
custom collections, instant client-side search, GitHub-Issues comments, and one easter egg.

Built overnight by an AI sous-chef as a proof-of-work test. **Do not use for anything real.**
This repo exists to be deleted after testing. 🧍🏻‍♂️

## Live site
https://hakoradev.github.io/site-test-test-super-test/

## How it works
- `data/recipes/*.json` — the content database (30 recipe files, plain JSON)
- `assets/data/media.json` — image/video manifest with source credits
- `tools/build_site.py` — Python generator that writes the entire static site (no framework)
- `assets/` — hand-rolled warm-editorial theme (CSS + vanilla JS), images, search index
- Comments: one GitHub Issue per recipe, fetched client-side from the public API

## Rebuild
```bash
python3 tools/build_site.py
```
