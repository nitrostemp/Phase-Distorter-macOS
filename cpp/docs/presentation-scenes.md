# Source contracts for wider presentation

These observations come from the original assembly and its linked symbols.
Addresses in the scene descriptions below use US unless a variant is identified.
They describe which existing data can extend the picture without advancing the
game, calling its map-loading routines, or changing WRAM, camera movement,
collision, event flags, entity allocation, or spawn decisions. The original
`runtime` and decompilation tools are not inputs to this analysis.

## World graphics and boundaries

`src/system/center_screen.asm` subtracts 128 and 112 from the requested world
position, then calls `REFRESH_MAP_AT_POSITION`. There is no generic map-region
camera clamp in this path. The refresh routine loads map rows/columns, collision
rows/columns, and calls `SPAWN_HORIZONTAL`/`SPAWN_VERTICAL`. A wider renderer must
not call that routine to acquire extra scenery: doing so would change gameplay.

The source instead enforces a graphics-region boundary in
`src/overworld/load_map_row.asm` and `load_map_column.asm`:

* The world is 256 by 320 metatiles, each 32 by 32 pixels: 8192 by 10240 pixels.
* A sector is 256 by 128 pixels. `GLOBAL_MAP_TILESETPALETTE_DATA` at `$D7A800`
  contains a 32 by 80 sector grid. Its high five bits identify the tileset/palette
  combination; its low three bits select the palette within that combination.
* A row/column loader replaces a metatile with **metatile zero** when its world
  coordinates are outside the map or its sector combination differs from
  `LOADED_MAP_TILE_COMBO` at WRAM `$436E`. Metatile zero is source data, not a
  guarantee of a flat black color.

Use these original visibility rules for extra picture area. A presentation-only
view adjustment can stop at the contiguous matching-sector interval, while the
game's own camera remains unchanged. Such a wider-view clamp is a port policy;
it should not be described as a pre-existing native camera constraint. Collision
walls, hotspot triggers, and NPC spawn boundaries are not interchangeable with
graphics-region boundaries.

Use current `BG1_X_POS`/`BG1_Y_POS` at WRAM `$31`/`$33`, reconciled with the actual
latched PPU scroll phase. The seemingly suitable `BG12_POSITION_X/Y_COPY` at
`$4386`/`$4388` can be stale across a full map transition; the house-exit trace
exhibited exactly that case. `SCREEN_LEFT_X`/`SCREEN_TOP_Y` at `$4374`/`$4376`
describe the source streaming position in eight-pixel units.

The following region descriptions are derived from the sector grid and named
bus-event/teleport sources. Bounds are exclusive at the right/bottom and are
bounding boxes, not substitutes for the irregular sector mask.

| Scene | Combination | Relevant source region in pixels | Source identification |
| --- | ---: | --- | --- |
| Tunnel immediately before Fourside | 5 | x 5632–6400, y 3328–3456; sector row 26, columns 22–24 | Event 214 approaches `(6320,3424)`; teleport `$4B` is `(6312,3400)` and `$D1` is `(5680,3424)` |
| Fourside exterior | 4 | Main connected component x 2048–4096, y 3328–5376 | Teleport `$4C` is `(2272,5104)`; town-map metadata identifies Fourside |
| Dusty Dunes Desert and bridge | 8 | Irregular connected component of 166 sectors, x 256–5888, y 8704–10240; road rows 77/78 span columns 1–22 | Event 210 enters via teleport `$48` at `(432,10032)` and checks `FLG_DSRT_CLEAR`; event 220 approaches `(4168,10032)` |
| Western desert tunnel | 5 | x 6144–6912, y 0–128 | Teleport `$CF` is `(6200,96)` |
| Eastern desert tunnel | 5 | x 7680–8192, y 8576–8704 | Teleport `$4A` is `(7744,8672)` |

The distinct tunnels share combination 5, so that number alone is not a unique
scene ID. World position and sector connectivity distinguish their regions.
The source stores teleport coordinates in eight-pixel units; the table above
converts them to pixels.

## Reading scenery beyond the streaming cache

`UNKNOWN_C0A156` and `UNKNOWN_C0A1CE` decode a world metatile without needing the
16 by 16 `LOADED_MAP_BLOCKS` ring at WRAM `$F000`. A read-only presentation helper
can perform the same lookup without touching the game's cached-block fields:

1. Set `bx = world_x / 32`, `by = world_y / 32`, and
   `index = (by / 8) * 256 + bx` after checking nonnegative map bounds.
2. Read the low byte from the pointer selected by `(by & 7)` in the four-byte
   pointer table at `$C42F64`, plus `index`.
3. Read the packed high bits at `$D75000 + index`, or `$D78000 + index` when
   `by & 4` is set. Shift by `2 * (by & 3)`, keep two bits, and append them above
   the low byte.
4. Apply the sector-combination rule above, using metatile zero outside the
   current combination.
5. Read the tile word from the current decompressed arrangement buffer at
   `$7F8000 + block_id * 32 + 2 * (((world_y / 8) & 3) * 4 + ((world_x / 8) & 3))`.

`C00E16`/`C00FCB` write that word to BG1. For BG2 they write `word | $2000` when
the tile index is below 384, otherwise zero. These are the original background
and foreground tilemap rules. `REPLACE_BLOCK` updates this arrangement buffer
when event flags change, so reading the live buffer preserves those changes
without replaying event logic. Tile graphics and palettes still come from the
currently loaded PPU state. Wrapping a 512-pixel VRAM tilemap at wider widths
would repeat cached scenery; this source lookup supplies the actual map.

## Lumine Hall text before the Lost Underworld

The scrolling thoughts are Lumine Hall, not a generic dialogue window. Source
text is `src/data/text/lumine_hall.asm`. Event 353 invokes preparation at
`C4880C`, then the update at `C48A6D`, with a three-frame pause. Font preparation
includes `C4838A`, `C4827B`, and `C4810E`.

Preparation creates complete column maps in `BUFFER + $1000` and
`BUFFER + $4000` (`BUFFER = $7F0000`) for the two alternating horizontal phases.
Each column contains eight tile words. The maps include 29 leading and 30
trailing blank columns. `C48A6D` selects a source offset of
`(ENTITY_SCRIPT_VAR1 / 2) * 16`, copies 30 columns by eight rows into `BUFFER + 2`,
and uploads that patch through `C3F705` at tile coordinates `(808,588)`, wrapped
to `(40,12)` in BG1's 64 by 32 tilemap at VRAM word `$3800`.

The existing prepared maps therefore contain additional text columns that a
wider presentation can expose without accelerating the scroll or changing its
script. Do not simply sample beyond the current 30-column VRAM patch; that area
contains other map tiles. Match the displayed patch against the prepared maps
to select the uploaded phase, because the source variable can advance before
the upload becomes visible.

The active entity's `ENTITY_SCRIPT_TABLE` entry at WRAM `$0A62` is **event ID
353**, not an instruction pointer. It has 30 word entries. Script pointer tables
are separate. `ENTITY_SCRIPT_VAR0_TABLE` is at `$0E5E`, and VAR1 at `$0E9A`.
`VAR0 = 2 * (prepared_text_columns + 30)` bounds the source effect.

## Static title and menu layers

`src/intro/show_title_screen.asm` deliberately configures a 256-pixel picture:
BGMODE low nibble `$0B` (mode 3), BG1SC `$58` (32 by 32 tilemap), BG1 tile base
zero, scroll zero, and main-screen enable `$11` (BG1 and OBJ). It creates event
IDs 788 through 798 (`TITLE_SCREEN_1` through `TITLE_SCREEN_11`) and removes them
on exit. This PPU signature plus an active title event is a narrow source-derived
marker. Center BG1 and OBJ in this scene; the copyright is part of BG1 and must
not repeat into the margins. Remaining margins can use the backdrop.

`src/system/file_select_init.asm` creates event 787 in slot 23, enables main
screen `$16` (BG2, BG3 and OBJ), and loads animated background 230
(`BATTLEBG_LAYER::FILE_SELECT`). File selection and naming share that setup.
Keep the BG3 text/windows and OBJ presentation centered while permitting the
animated BG2 picture to extend.

Do not suppress BG3 in every scene. `src/battle/load_battlebg.asm` targets BG2
in one configuration and BG3 in another. The active animated-layer metadata and
actual PPU configuration should control that case. The gas-station interference
intro uses BG1 main-screen `$01`, BG2 sub-screen `$02`, and palette animation;
it is distinct from the static title signature and should remain extended.

## Objects beyond the native picture

Entities do not cull themselves horizontally. Each frame, an entity's screen
position is `ENTITY_ABS_X - BG1_X_POS` (`C0A023`), its draw callback (`C0A3A4`)
queues its spritemap through `C08C58`, and `C08B8E` flushes the four priority
queues through `C08CD5`, which writes OAM. `C08CD5` is the only culling step:

* a piece whose Y is outside -32..223 is dropped;
* a piece whose 16-bit X has high byte `$00` or `$FF` (-256..255) is written,
  with the ninth X bit for negative values;
* any other piece, including every piece at X 256 or more, is dropped.

So a wider view loses objects twice: pieces past the right edge never reach
OAM, and pieces wholly left of the picture reach OAM but look the same as
hidden ones. `OAM_CLEAR` hides unused entries with Y `$E0`, not with X.

The presentation records the game's own list instead of widening the routine.
At `C08CD5` entry the CPU reports A (spritemap pointer), X and Y (screen
position); the recorder reads the spritemap from `SPRITEMAP_BANK` and the
cursor from `OAM_ADDR`/`OAM_END_ADDR`, repeats the routine's walk without
writing anything, and keeps every piece with the OAM slot it received or none.
`OAM_CLEAR` restarts the list of the buffer selected by `NEXT_FRAME_BUF_ID`
(1 selects `OAM1`, anything else `OAM2`), and the NMI's OAM upload from
`OAM1`/`OAM2` latches that buffer's list. At each frame's first row the list is
used only if every slot it names still holds its piece in OAM; margins then
draw the game's pieces in the game's order, including the ones it dropped.
Otherwise they fall back to OAM alone, where wholly offscreen entries stay hidden.

Before any of that, the entity drawing loop `C0DB0F` (run through
`CURRENT_ENTITY_DRAW_CALLBACK` once every screen position is set) queues only
entities whose screen X is within -64..319 and Y within -64..255. At its entry
the presentation walks the entity list and, for each entity skipped only for
its X whose draw callback is the usual `C0A3A4`, repeats that callback without
its writes: the spritemap from `ENTITY_SPRITEMAP_POINTER_LOW/HIGH` (advanced by
`ENTITY_SPRITEMAP_SIZES` when `ENTITY_CURRENT_DISPLAYED_SPRITES` bit 0 is set),
with the OBJ priority `C0A3A4` writes into the upper and lower body entries
from `ENTITY_SURFACE_FLAGS` and `ENTITY_UPPER_LOWER_BODY_DIVIDES`, at the
entity's screen position. Those pieces join the list of the buffer selected by
`NEXT_FRAME_BUF_ID`, after the game's own pieces, when the NMI uploads it.
Overlays that `C0AC43` adds (sweat, ripples) and entities with other draw
callbacks are not repeated. Holding Select on controller 2 switches `C0DB0F` to
a debugging loop, `C0DA31`; the presentation then adds nothing.

Spawning is unchanged: `REFRESH_MAP_AT_POSITION` spawns entities 64 pixels
beyond each native edge (columns `SCREEN_LEFT_X - 8` and `+ 40`, rows
`SCREEN_TOP_Y - 8` and `+ 36`), so objects can still appear in the outermost
pixels of margins wider than 64 pixels. A 16:9 view has 71.

## Keeping entities alive across the wide view (gameplay option)

Everything above only changes what is drawn. The game itself keeps entities
only near the native picture, and a wide view — especially a narrow room,
where the view shifts to show the whole room — exposes places where the
original game has deleted or never created them:

* Idle NPC scripts call `C40015`, whose `C0C6B6` keeps an entity only while it
  is within -64..319 of a screen centered on the leader (x from
  `leader_x - 128`, y from `leader_y - 112`); otherwise the script deletes it.
* NPCs spawn per 256-pixel sector: `C025CF` for the column 34 tiles right of
  (or 3 left of) the screen, `C0255C` for rows spanning -2..+36 tiles, and
  `C0222B` only for NPCs within -64..319 of the camera.
* `C0DB0F` draws entities within -64..319 (see above), and `C0C711` lets
  `C0A443` upload an entity's animation frame only when its left edge is within
  the native picture.

The frontend's "Keep characters alive in widescreen" option (on by default in
this build, `--no-wide-entities` to disable) widens each of these
horizontally by a reach covering the configured wide picture: the extra width
rounded up to a multiple of 64 (192 pixels at 16:9). The CPU hands the fixed
instruction sites to the Bus before running them (`run_wide_entity_site`),
which runs them with a widened operand or adjusted register. `bus_tests`
checks every site's instruction bytes in both compiled programs. Enemy
spawning is not widened.

Collision data exists only near the picture (a 64-column ring loaded from 16
tiles left to 41 tiles right), so entities that the original game would have
deleted keep their place and skip their move callback until they are back
within its range; they still animate, run scripts and are drawn. Only
entities whose own script ran the `C0C6B6` check are paused, so scripted
entities in events move as before. With the option on, gameplay differs from
the original: kept entities stay where they were instead of respawning at
their placements, and they hold entity slots. At native width, or with the
option off, the game runs unchanged; `presentation_differential` does not
enable it.

## Verification boundary

Synthetic layer tests can establish wider sampling, clipping, and unchanged
native pixels. Source-backed scene fixtures can establish use of the actual
prepared text/map data. A twin run using the same initial imported image and
controller stream must compare CPU state, WRAM, SRAM, SPC state/RAM, and hardware
state with widescreen off/on to establish unchanged game behavior on that run.
Entity allocation and spawn state live in WRAM, so exact WRAM equality includes
those decisions. A picture-only fixture is not proof of a natural full-game
route through Lumine Hall, every tunnel, or every battle background.

## Japanese source profile

The common build independently links US and JP and emits
`generated_profile.hpp` / `source_profiles.json`. The presentation renderer
selects this immutable metadata using the imported pack's `GameVersion`.
It never infers the region from a mutable game variable. Direct addresses are
resolved from each linked source symbol; world-arrangement and Lumine phase
buffer offsets follow the source's corresponding buffer-relative expressions.

| Source state | US WRAM offset | JP WRAM offset |
| --- | --- | --- |
| `BATTLE_MODE_FLAG` | `$9643` | `$993B` |
| `LOADED_BG_DATA_LAYER1` / `LAYER2` | `$ADD4` / `$AE4B` | `$AFA9` / `$B020` |
| `LOADED_MAP_TILE_COMBO` | `$436E` | `$46F4` |
| `BG1_X_POS`, `BG1_Y_POS`, `BG2_X_POS`, `BG2_Y_POS` | `$31,$33,$35,$37` | same |
| `ENTITY_SCRIPT_TABLE` | `$0A62` | `$0A58` |
| `ENTITY_SCRIPT_VAR0_TABLE` / `VAR1_TABLE` | `$0E5E` / `$0E9A` | `$0E54` / `$0E90` |
| Lumine `BUFFER` header | `$10000` | same |
| Lumine prepared alternating column maps | `$11000` / `$14000` | `$12000` / `$14000` |
| Live decompressed map arrangements | `$18000` | same |

The JP Lumine routines are `src/unknown/C4/C4880C-jp.asm` and
`C48A6D-jp.asm`. Their first phase map starts at `BUFFER + $2000`, while US
starts at `BUFFER + $1000`; the second remains `BUFFER + $4000`.
Both retain event 353, eight rows, 30 uploaded columns, the same world-tile
patch coordinates, and the same font tile-word range. Title events are
788–798 in US and 788–794 in JP; file selection remains event 787.
The ten `MAP_DATA_TILE_TABLE_CHUNK_*` symbols and
`GLOBAL_MAP_TILESETPALETTE_DATA` resolve to the same ROM offsets in both builds,
but the generated metadata still resolves them separately. The above
source-layout equivalence is distinct from proving every Japanese gameplay
route or screen visually.
