Phase Distorter: the EarthBound / Mother 2 C++ port, built for macOS and Windows.

**macOS:** download `Phase-Distorter-*-macos-arm64.zip` below, extract it and open
**Phase Distorter.app**. It needs an Apple Silicon Mac; the minimum macOS version
is in the `README.txt` inside the ZIP.

**Windows:** download `Phase-Distorter-*-windows-x86_64.zip`, extract the whole
folder and open **Phase Distorter.exe**, keeping `SDL2.dll` beside it.

The Mac app is signed ad hoc, so macOS blocks it the first time: open it once,
then choose **System Settings → Privacy & Security → Open Anyway**. The Windows
application is unsigned; if SmartScreen warns, choose **More info → Run anyway**.

On first launch, import a ROM from your own copy of EarthBound (US) or Mother 2
(Japan). **No ROM or game assets are included.** Saves and imported assets live in
`~/Library/Application Support/ebsrc/EarthBoundCpp/` on macOS and
`%APPDATA%\ebsrc\EarthBoundCpp\` on Windows.

This fork also widens widescreen: sprites past the original screen edge are drawn,
and **Settings → Keep characters alive in widescreen** (on by default) keeps
characters from vanishing near the edge. That option changes gameplay; turn it off
for the original behavior. Linux builds are in the
[upstream project](https://github.com/TheRunaway5/Phase-Distorter).
