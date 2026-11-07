# BUILDING — developer notes

Solo project. This file is for me: how to build, how to ship, what lives where.
Players only need `README.md`.

## Project layout

| Path | Purpose |
|---|---|
| `main.py` | the game: fixed hand-made level and all systems |
| `achievements.py` | leveled achievements, 9 languages |
| `backdrop.py` | distant mountain backdrop and summit plateau |
| `chatter.py` | idle chatter lines |
| `flavor.py` | one-time tutorials and fall taunts |
| `i18n.py` | 9-language strings and font selection |
| `paths.py` | asset and user-data path resolution |
| `profiles.py` | local player profiles (accounts): per-profile save/achievement folders |
| `textures/` | sprites and terrain tiles |
| `sounds/` | music and sound effects |
| `sounds/voice/` | unpacked voice clips (git-ignored, ship as `voice.zip`) |
| `icons/` | `slipery.ico`, `slipery.icns`, `slipery.png` |
| `packaging/` | Linux `.desktop` entry, `run.sh`, notes |
| `.github/workflows/build.yml` | CI: Windows, macOS, Linux, deb, rpm |

## Run from source

- Install pygame: `pip install pygame`
- Unpack the voice clips once (they ship as one archive to keep the repo small):
  `unzip voice.zip -d sounds` (Windows PowerShell:
  `Expand-Archive voice.zip -DestinationPath sounds`)
- Start the game: `python main.py`

Python 3.8+ and pygame 2.6.1 are required. The release builds are made
with Python 3.8 so the game still starts on older machines
(Python 3.9+ needs Windows 8.1 or newer; the 3.8 build targets the
older Windows / glibc generation). PyInstaller is pinned to 6.22.3.

## Build the Windows exe

Run `build.bat` in the project folder, or paste this one line:

```
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "A Slipery Climb" --icon icons/slipery.ico ^
  --version-file version_info.txt ^
  --add-data "textures;textures" --add-data "sounds;sounds" ^
  --add-data "fonts;fonts" --add-data "tutorial;tutorial" main.py
```

(The `^` is a PowerShell line continuation; drop it and keep it one line in cmd.)

`profiles.py` is a plain module next to `main.py`, so PyInstaller picks it up
automatically — no extra hidden-import flag is needed.

## Build macOS / Linux / deb / rpm

Push a tag, for example `v1.5.0`. `.github/workflows/build.yml` then builds every
platform and attaches the packages to that release automatically. Nothing is
built locally for those platforms.

## Release checklist

1. Bump the version in `version_info.txt` (`filevers`, `prodvers`, both strings).
2. Bump the macOS `CFBundleShortVersionString` / `CFBundleVersion` in
   `.github/workflows/build.yml`.
3. Update `release-notes.md` (English / 中文 / Русский sections).
4. Mirror `release-notes.md` into `store/github_release_notes.md`.
5. Mirror `README.md` into `store/github_readme.md` and refresh the store text
   files in `store/` if features changed.
6. Upload changed files through the GitHub web UI.
7. Tag `vX.Y.Z` and publish the release.
8. Wait for the `build` workflow to finish, then check the six assets and the
   release body.

## Profile data layout

- `settings.json` — global (volume, language, fullscreen), shared by all profiles
- `profiles.json` — list of profiles + which one is active
- `profiles\<id>\` — per profile: `save_slot_1..5.json`, `achievements.json`,
  `tutorial_seen.json`
- `profiles.py` migrates the old loose files (`achievements.json`,
  `tutorial_seen.json`, `save_slot_*.json`) from the user folder into the first
  profile the first time a build with profiles starts.

## Platform notes

- **Linux** builds run inside `catthehacker/ubuntu:act-20.04` so the binary needs
  an old glibc (2.31). Keep `--depends "libc6 (>= 2.31)"` / `"glibc >= 2.31"` in
  the fpm calls, otherwise old distros refuse the package.
- **Icons** live in `icons/` (`slipery.ico` multi-size, `slipery.icns`,
  `slipery.png`). The Linux tarball ships `packaging/run.sh` and a `.desktop`
  file; the workflow `chmod +x`es the binary before `tar` so it runs straight
  after unpacking.
- **Linux fullscreen** uses a real `pygame.FULLSCREEN`; Windows uses a borderless
  `NOFRAME` window. There is a fallback to a normal window if `set_mode` fails.

## Save data

Windows `%APPDATA%\A Slipery Climb`, macOS
`~/Library/Application Support/A Slipery Climb`, Linux
`~/.local/share/A Slipery Climb`. Deleting that folder resets settings,
profiles, achievements and every save slot.
