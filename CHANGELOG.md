# macOS port (this fork) — 2026-09-27

- Native macOS (Apple Silicon) build: `build-macos.sh` packages a self-contained
  `Phase Distorter.app` with bundled SDL2/SDL3 and a release ZIP.
- GitHub Actions workflow: builds and tests macOS and Linux on every push and pull
  request, keeps a draft "Latest build" release for `main`, and publishes tagged releases.
- README: macOS installation, build, save location and troubleshooting.
- Windows in CI: an MSYS2 UCRT64 build with the official SDL2 2.32.10 MinGW DLL
  (hash-checked), tested and packaged by `package_release.py`, whose new
  `--binaries-dir` and `--output-dir` options package a build folder into a
  chosen directory without touching `releases/`.
- Widescreen sprites: objects past the native edge are drawn in the margins (the
  game drops them when writing OAM, or skips the entity in its draw loop); the
  game's own execution is unchanged.
- "Keep characters alive in widescreen" (on by default, `--no-wide-entities`):
  a gameplay option that widens the game's spawn, despawn, draw and animation
  ranges to the wide view, so characters and objects no longer vanish past the
  original screen edge.

# Phase Distorter 0.1 — 2026-09-27

- Standalone C++20 source snapshot with compiled US and Japanese program profiles.
- Direct native Linux `Phase Distorter` and Windows `Phase Distorter.exe`
  applications beside the README; no shell or batch launcher needed to play.
- SDL2/OpenGL video, controller input, audio and saves.
- First-run own-ROM import with validation and local asset packs.
- Mother 2 Japanese program, fonts, text and assets; separate saves for each game.
- Always-visible gameplay bar with Settings (F1) and Fullscreen (F11), a floating
  Settings window, and a game picture fitted below the bar.
- Settings Assets tab lists both default caches, offers confirmed cache clearing
  without deleting ROMs or saves, and confirms game switching with normal SRAM
  persistence and retained display/fullscreen preferences.
- Persistent aspect preferences and read-only game diagnostics.
- Widescreen scene rendering with unchanged gameplay and spawning, battle patterns,
  Lumine Hall text, and presentation camera boundaries for narrow map regions.
- Fixed intro artwork uses a centered 4:3 view; the Mother 2 logo screen extends
  its background into widescreen margins without stretching or repeating the logo.
- Deterministic verification tools and documented fidelity limits.
- Phase Distorter branding and Saturn launcher/window icons on both platforms.
- Optional per-user Linux menu and Windows Desktop/Start Menu shortcut setup,
  targeting the native applications directly; Windows setup can be opened as
  `install-shortcuts.vbs`.
- Direct source-build installation with `cmake --install build --prefix dist`;
  optional developer launch scripts retain local-build priority.
- Expanded installation/build guide and explanatory source comments.
- Default-off photosensitivity filter scoped to identified flashing effects,
  including battle animations and Franklin Badge lightning; ordinary picture
  pixels retain their original colors and sharpness.
