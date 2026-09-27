Phase Distorter @VERSION@ - macOS (Apple Silicon)
EarthBound / Mother 2 PC port

Extract this entire ZIP, then open Phase Distorter.app from the extracted
folder. You can move the app to Applications first. No compiler or terminal is
needed.

The app is signed ad hoc, not by an identified developer, so macOS blocks it
the first time. Open it once, then go to System Settings -> Privacy & Security,
click "Open Anyway" beside the Phase Distorter message and confirm. Later
launches open normally. Or, from a terminal in the extracted folder:
  xattr -dr com.apple.quarantine "Phase Distorter.app"

Requirements: an Apple Silicon Mac running macOS @MIN_MACOS@ or later. SDL2 and
SDL3 are bundled inside the app; nothing else needs installing.

On first launch, browse to or drag in a supported ROM from your own purchased
copy of EarthBound (US/English) or Mother 2 (Japan/Japanese), then click Import.
No ROM or extracted gameplay assets are included. Each unheadered image is
3,145,728 bytes; a 512-byte copier header is accepted. Patched ROMs and other
revisions are unsupported. Expected SHA-256 hashes:
EarthBound: a8fe2226728002786d68c27ddddf0b90a894db52e4dfe268fdf72a68cae5f02e
Mother 2:  1f8cfd13177d86b0eb2c8adcf9e1a4f0ec8966fa1583072b65a1b1c0e7961a5d

Importing leaves your ROM and the app unchanged. Later launches use the local
imported pack. Both games have their own program, language and saves. The app
remembers the last game played; switch games in Settings (F1) -> Assets. To
import or select a game from a terminal:
  "Phase Distorter.app/Contents/MacOS/Phase Distorter" --import-rom "/path/to/mother2.sfc" --import-only
  "Phase Distorter.app/Contents/MacOS/Phase Distorter" --game mother2
  "Phase Distorter.app/Contents/MacOS/Phase Distorter" --game earthbound

Controls: arrows move; Z=B, X=A, A=Y, S=X, Q=L, W=R; Enter=Start;
Right Shift=Select. Controllers are supported. F11 toggles fullscreen (on a
MacBook keyboard, hold fn). The always-visible top bar has Settings (F1) and
Fullscreen (F11) buttons. Settings has display, assets and diagnostics tabs;
its Display tab includes widescreen and the default-off photosensitivity
filter, an independent implementation that cannot guarantee seizure safety.
Escape closes Settings or exits.

Assets, separate game saves and display preferences live at:
  ~/Library/Application Support/ebsrc/EarthBoundCpp/
Use the game's normal save mechanism, then exit normally to write the save.
Back up earthbound.srm and mother2.srm before updating. Deleting the app does
not remove the saves or imported packs.

If the app closes immediately, run it from a terminal to read the error:
  "Phase Distorter.app/Contents/MacOS/Phase Distorter"
--help lists options; --no-config ignores saved display preferences. This is a
development release: whole-game and cycle-accurate equivalence have not been
established. The full source contains build instructions, the detailed README
and documented fidelity limits.

See NOTICE.md, LICENSE.txt and licenses/ for attribution and licenses.
