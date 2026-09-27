#!/usr/bin/env python3
"""Build and stage the Linux runtime that package_release.py bundles as lib/.

  stage_linux_runtime.py build-sdl --archive SDL2-2.32.10.tar.gz --prefix DIR
      Verify the official SDL source archive, then build and install original
      SDL 2.32.10 into DIR with the options lib/PROVENANCE.md records upstream.
  stage_linux_runtime.py stage --sdl-prefix DIR --sdl-source DIR
                               --application FILE --output DIR
      Copy libSDL2 and the build machine's libstdc++/libgcc_s under their
      SONAMEs, give libstdc++ an $ORIGIN RUNPATH (as upstream does), write the
      licenses and a PROVENANCE.md describing this build, and print the newest
      glibc symbol version that the libraries or the application require.

Used by the GitHub Actions workflow on Ubuntu; needs cmake, gcc, patchelf,
objdump and dpkg. It never reads ROMs or asset packs.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
SDL_VERSION = "2.32.10"
SDL_URL = f"https://github.com/libsdl-org/SDL/releases/download/release-{SDL_VERSION}/SDL2-{SDL_VERSION}.tar.gz"
SDL_ARCHIVE_SHA256 = "5f5993c530f084535c65a6879e9b26ad441169b3e25d789d83287040a9ca5165"
# Upstream's options: baseline x86-64 code, shared library only. SSE3 is off
# because this SDL version otherwise adds -msse3 to all C compilation.
SDL_OPTIONS = [
    "-DCMAKE_BUILD_TYPE=Release",
    "-DCMAKE_C_FLAGS=-march=x86-64 -mtune=generic",
    "-DSDL_SHARED=ON", "-DSDL_STATIC=OFF",
    "-DSDL_TEST=OFF", "-DSDL_TESTS=OFF", "-DSDL_SSE3=OFF",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*command: str) -> str:
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def build_sdl(archive: Path, prefix: Path) -> None:
    if sha256(archive) != SDL_ARCHIVE_SHA256:
        raise SystemExit(f"{archive} does not match the SDL {SDL_VERSION} archive hash")
    work = prefix.parent / "sdl-work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    with tarfile.open(archive) as source:
        source.extractall(work, filter="data")
    source_dir = work / f"SDL2-{SDL_VERSION}"
    build_dir = work / "build"
    subprocess.run(["cmake", "-S", str(source_dir), "-B", str(build_dir), "-G", "Ninja",
                    f"-DCMAKE_INSTALL_PREFIX={prefix}", *SDL_OPTIONS], check=True)
    subprocess.run(["cmake", "--build", str(build_dir)], check=True)
    subprocess.run(["cmake", "--install", str(build_dir)], check=True)
    print(source_dir)


def glibc_requirement(path: Path) -> str:
    versions = set(re.findall(r"GLIBC_(\d+(?:\.\d+)+)", run("objdump", "-T", str(path))))
    return max(versions, key=lambda v: tuple(int(p) for p in v.split("."))) if versions else "none"


def package_of(path: Path) -> tuple[str, str]:
    # Best effort: the dpkg database names the package and version that
    # installed a library. Merged-/usr systems may register either path form.
    for candidate in (path, Path(str(path).replace("/usr/lib/", "/lib/", 1))):
        try:
            package = run("dpkg", "-S", str(candidate)).split(": ")[0]
            version = run("dpkg-query", "-W", "-f=${Version}", package)
            return package, version
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return "unknown", "unknown"


def stage(sdl_prefix: Path, sdl_source: Path, application: Path, output: Path) -> None:
    shutil.rmtree(output, ignore_errors=True)
    (output / "licenses").mkdir(parents=True)
    sdl = (sdl_prefix / "lib" / "libSDL2-2.0.so.0").resolve()
    stdcxx = Path(run("g++", "-print-file-name=libstdc++.so.6").strip()).resolve()
    libgcc = Path(run("gcc", "-print-file-name=libgcc_s.so.1").strip()).resolve()
    # Regular files under their SONAMEs, as upstream ships them.
    for source, name in ((sdl, "libSDL2-2.0.so.0"), (stdcxx, "libstdc++.so.6"), (libgcc, "libgcc_s.so.1")):
        shutil.copyfile(source, output / name)
        os.chmod(output / name, 0o755)
    subprocess.run(["patchelf", "--set-rpath", "$ORIGIN", str(output / "libstdc++.so.6")], check=True)

    shutil.copyfile(sdl_source / "LICENSE.txt", output / "licenses/SDL2-LICENSE.txt")
    for name in ("GCC-COPYING3.txt", "GCC-RUNTIME-LIBRARY-EXCEPTION.txt"):
        shutil.copyfile(ROOT / "lib/licenses" / name, output / "licenses" / name)

    gcc_version = run("g++", "-dumpfullversion").strip()
    cc_version = run("cc", "--version").splitlines()[0]
    distro = next((line.split("=", 1)[1].strip('"') for line in Path("/etc/os-release").read_text().splitlines()
                   if line.startswith("PRETTY_NAME=")), "the build machine")
    stdcxx_package, stdcxx_version = package_of(stdcxx)
    libgcc_package, libgcc_version = package_of(libgcc)
    requirements = {name: glibc_requirement(output / name)
                    for name in ("libSDL2-2.0.so.0", "libstdc++.so.6", "libgcc_s.so.1")}
    requirements["application"] = glibc_requirement(application)
    newest = max((v for v in requirements.values() if v != "none"),
                 key=lambda v: tuple(int(p) for p in v.split(".")))
    build_note = ""
    if os.environ.get("GITHUB_RUN_ID"):
        server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        build_note = f" Build: {server}/{repository}/actions/runs/{os.environ['GITHUB_RUN_ID']}"

    (output / "licenses/GCC-NOTICE.md").write_text(f"""# GCC runtime libraries

This directory contains libstdc++.so.6 and libgcc_s.so.1 from GCC
{gcc_version}, as packaged by {distro} ({stdcxx_package} {stdcxx_version},
{libgcc_package} {libgcc_version}) for x86_64.
Copyright Free Software Foundation, Inc. and the GCC contributors.

The library code is distributed under the GNU General Public License,
version 3 or later, with the GCC Runtime Library Exception, version 3.1.
The accompanying GCC-COPYING3.txt and GCC-RUNTIME-LIBRARY-EXCEPTION.txt
contain those license texts. GCC documentation licensed under the GFDL is
not included in this runtime bundle.

Upstream project and source: https://gcc.gnu.org/
The distribution's source packages for {stdcxx_package} and {libgcc_package}
hold the corresponding source. Package provenance and file hashes are in
../PROVENANCE.md.

libgcc_s.so.1 is unmodified. libstdc++.so.6 has only a loader RUNPATH of
$ORIGIN added with patchelf so its adjacent libgcc_s.so.1 can be found.
No changes were made to the GCC library implementation.
""", encoding="utf-8")

    options = " \\\n  ".join(f'"{option}"' if " " in option else option for option in SDL_OPTIONS)
    hashes = "\n".join(f"| `{name}` | `{sha256(output / name)}` |"
                       for name in ("libSDL2-2.0.so.0", "libstdc++.so.6", "libgcc_s.so.1"))
    (output / "PROVENANCE.md").write_text(f"""# Linux runtime provenance

These are the shared libraries distributed with the Phase Distorter Linux
x86-64 runtime, staged by this fork's GitHub Actions workflow with
`cpp/tools/stage_linux_runtime.py`. They contain no EarthBound or Mother 2
assets.{build_note}

## System requirements

This binary build requires **glibc {newest} or newer**, a Linux x86-64 desktop,
and working desktop OpenGL 2.1 support. The system supplies glibc, the
dynamic loader, graphics drivers, OpenGL/GLX libraries, and the X11 or
Wayland and audio libraries used by the selected SDL backends. These system
components are not included here. Build from source on an older
distribution to target that distribution's libc instead.

## SDL2

`libSDL2-2.0.so.0` is original SDL **{SDL_VERSION}**, built from the official
[SDL source archive]({SDL_URL}).
It is not SDL2-compat and does not require SDL3.
Archive SHA-256: `{SDL_ARCHIVE_SHA256}`.

Built on {distro} with CMake and `{cc_version}` using these options:

```sh
cmake -S SDL2-{SDL_VERSION} -B build -G Ninja \\
  {options}
```

SSE3 is disabled because this SDL version's CMake configuration otherwise
adds `-msse3` to all C compilation, beyond the baseline x86-64 requirement.
SDL source files are unmodified. The zlib license is included as
`licenses/SDL2-LICENSE.txt`.

## GCC runtime

`libstdc++.so.6` and `libgcc_s.so.1` come from the build machine's
{distro} packages `{stdcxx_package}` {stdcxx_version} and `{libgcc_package}`
{libgcc_version} (GCC {gcc_version}).

`libgcc_s.so.1` is unmodified. `libstdc++.so.6` has only its ELF RUNPATH
changed to `$ORIGIN` with `patchelf --set-rpath '$ORIGIN'` so its dependency
on the adjacent libgcc can be resolved independently of the executable's
RUNPATH. Both are copied as regular files under their SONAMEs.

The GNU GPL version 3 and GCC Runtime Library Exception version 3.1 are
included in `licenses/GCC-COPYING3.txt` and
`licenses/GCC-RUNTIME-LIBRARY-EXCEPTION.txt`. See
`licenses/GCC-NOTICE.md` for source and copyright information.

## Dependency audit

ELF symbol requirements after staging: SDL2 requires up to
`GLIBC_{requirements['libSDL2-2.0.so.0']}`, libstdc++ up to
`GLIBC_{requirements['libstdc++.so.6']}`, libgcc up to
`GLIBC_{requirements['libgcc_s.so.1']}`, and the application up to
`GLIBC_{requirements['application']}`.

| Distributed file | SHA-256 |
| --- | --- |
{hashes}
""", encoding="utf-8")
    print(newest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-sdl")
    build.add_argument("--archive", type=Path, required=True)
    build.add_argument("--prefix", type=Path, required=True)
    staging = commands.add_parser("stage")
    staging.add_argument("--sdl-prefix", type=Path, required=True)
    staging.add_argument("--sdl-source", type=Path, required=True)
    staging.add_argument("--application", type=Path, required=True)
    staging.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build-sdl":
        build_sdl(args.archive.resolve(), args.prefix.resolve())
    else:
        stage(args.sdl_prefix.resolve(), args.sdl_source.resolve(), args.application.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
