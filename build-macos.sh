#!/bin/sh
# Build the standalone root on macOS and package it as a self-contained
# "Phase Distorter.app", which runs without Homebrew:
#   ./build-macos.sh [extra CMake configuration arguments]
# The app holds the executable, its icon and, in Frameworks, Homebrew's SDL2
# (sdl2-compat) plus the SDL3 that sdl2-compat loads beside itself. It contains
# no ROM and no imported asset pack. It is signed ad hoc, so macOS asks before
# opening it the first time. Needs: Xcode command line tools, and
#   brew install cmake ninja sdl2-compat sdl3 dylibbundler
set -eu
release_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build_dir="$release_dir/build"
out_dir="$release_dir/dist"
app="$out_dir/Phase Distorter.app"

fail() { printf 'build-macos: %s\n' "$*" >&2; exit 1; }
[ "$(uname -s)" = Darwin ] || fail "this builds the macOS application; run it on macOS."
command -v dylibbundler >/dev/null 2>&1 || fail "needs dylibbundler (brew install dylibbundler)."

# PATH may hold a cross compiler named clang; the native build uses Apple's.
generator=
command -v ninja >/dev/null 2>&1 && generator="-G Ninja"
# shellcheck disable=SC2086
cmake -S "$release_dir" -B "$build_dir" $generator -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_COMPILER=/usr/bin/clang++ -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0 "$@"
cmake --build "$build_dir" --parallel "${CMAKE_BUILD_PARALLEL_LEVEL:-$(sysctl -n hw.ncpu)}" --target eb_cpp

rm -rf "$app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources" "$app/Contents/Frameworks"
cp "$build_dir/cpp/eb_cpp" "$app/Contents/MacOS/Phase Distorter"
strip -x "$app/Contents/MacOS/Phase Distorter"

# The Finder icon, from the same Saturn artwork as the window icon.
icon_src="$release_dir/cpp/resources/phase-distorter.png"
iconset=$(mktemp -d)/PhaseDistorter.iconset
mkdir -p "$iconset"
for size in 16 32 128 256 512; do
    sips -z $size $size "$icon_src" --out "$iconset/icon_${size}x${size}.png" >/dev/null
    sips -z $((size * 2)) $((size * 2)) "$icon_src" --out "$iconset/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$iconset" -o "$app/Contents/Resources/PhaseDistorter.icns"
rm -rf "$(dirname "$iconset")"

# Homebrew's libraries into Frameworks, with the executable pointing at them there.
dylibbundler -of -b -x "$app/Contents/MacOS/Phase Distorter" -d "$app/Contents/Frameworks" \
    -p @executable_path/../Frameworks/ >/dev/null
# sdl2-compat loads SDL3 at run time from its own folder (@loader_path/libSDL3.dylib),
# so dylibbundler cannot see that one: add it by hand.
sdl3="$(brew --prefix sdl3)/lib/libSDL3.0.dylib"
[ -f "$sdl3" ] || fail "no SDL3 at $sdl3 (brew install sdl3)."
cp "$sdl3" "$app/Contents/Frameworks/libSDL3.dylib"
chmod u+w "$app/Contents/Frameworks/libSDL3.dylib"
install_name_tool -id @executable_path/../Frameworks/libSDL3.dylib "$app/Contents/Frameworks/libSDL3.dylib" 2>/dev/null
dylibbundler -of -b -x "$app/Contents/Frameworks/libSDL3.dylib" -d "$app/Contents/Frameworks" \
    -p @executable_path/../Frameworks/ >/dev/null

# Nothing may still point into Homebrew.
for f in "$app/Contents/MacOS/Phase Distorter" "$app"/Contents/Frameworks/*.dylib; do
    if otool -L "$f" | tail -n +2 | grep -qE '/opt/homebrew|/usr/local'; then
        fail "$f still links to Homebrew: $(otool -L "$f" | grep -E '/opt/homebrew|/usr/local')"
    fi
done

# The oldest macOS it runs on: the newest any of its parts was built for.
min_macos=$(for f in "$app/Contents/MacOS/Phase Distorter" "$app"/Contents/Frameworks/*.dylib; do
    otool -l "$f" | awk '/LC_BUILD_VERSION/{b=1} b && $1=="minos"{print $2; exit}'
done | sort -t. -k1,1n -k2,2n | tail -1)
version=$(cat "$release_dir/VERSION" 2>/dev/null || echo 0)

cat > "$app/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Phase Distorter</string>
    <key>CFBundleIdentifier</key>
    <string>io.github.nitrostemp.PhaseDistorter</string>
    <key>CFBundleName</key>
    <string>Phase Distorter</string>
    <key>CFBundleDisplayName</key>
    <string>Phase Distorter</string>
    <key>CFBundleIconFile</key>
    <string>PhaseDistorter</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${version}</string>
    <key>CFBundleVersion</key>
    <string>${version}</string>
    <key>LSMinimumSystemVersion</key>
    <string>${min_macos}</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.games</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# No ROM or imported asset pack may end up in the app.
if find "$app" -type f \( -iname '*.sfc' -o -iname '*.smc' -o -iname '*.ebpak' -o -iname '*.srm' \) | grep -q .; then
    fail "game data found inside $app"
fi

# install_name_tool invalidated the libraries' signatures: sign everything again, ad hoc.
codesign --force --sign - "$app"/Contents/Frameworks/*.dylib
codesign --force --sign - "$app"
codesign --verify --strict "$app"
arch=$(lipo -archs "$app/Contents/MacOS/Phase Distorter" | tr ' ' '-')
echo "Packaged $app (macOS $min_macos or later, $arch)"

# The release ZIP: one folder with the app, its instructions and the licenses
# of everything bundled in it.
package="Phase-Distorter-$version-macos-$arch"
stage="$out_dir/$package"
rm -rf "$stage" "$out_dir/$package.zip"
mkdir -p "$stage/licenses"
ditto "$app" "$stage/Phase Distorter.app"
sed -e "s/@VERSION@/$version/g" -e "s/@MIN_MACOS@/$min_macos/g" \
    "$release_dir/cpp/resources/release-readme-macos.txt" > "$stage/README.txt"
cp "$release_dir/LICENSE" "$stage/LICENSE.txt"
cp "$release_dir/NOTICE.md" "$stage/NOTICE.md"
cp "$(brew --prefix sdl2-compat)/LICENSE.txt" "$stage/licenses/SDL2-compat-LICENSE.txt"
cp "$(brew --prefix sdl3)/LICENSE.txt" "$stage/licenses/SDL3-LICENSE.txt"
cp "$release_dir/cpp/external/imgui/LICENSE.txt" "$stage/licenses/imgui-LICENSE.txt"
cp "$release_dir/cpp/external/spc_dsp/LICENSE" "$stage/licenses/snes_spc-LICENSE.txt"
# Plain files only (no ._ extended-attribute entries); the signature is in the app itself.
(cd "$out_dir" && ditto -c -k --norsrc --noextattr --noacl --keepParent "$package" "$package.zip")
rm -rf "$stage"
echo "Release ZIP: $out_dir/$package.zip"
