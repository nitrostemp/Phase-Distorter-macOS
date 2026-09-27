// Generated from independent US and JP source builds. Do not edit.
// Frozen linked-symbol metadata for the two source configurations. Returning a
// const reference avoids copying this table and keeps it immutable throughout
// rendering. The values guide presentation reads; they do not alter emulated
// addresses, game scripts, entity activation or camera state.
#include "generated_profile.hpp"
namespace eb {
namespace {
constexpr SourceProfile profile_us{
    0x9643, // wram_battle_flag
    {0xadd4,0xae4b}, // wram_bg_records
    0x1b9e, // wram_psi_animation
    0xaee7, // wram_psi_targets
    0xaec2, // wram_swirl_timer
    0x200, // wram_palettes
    {0xad9e,0xada0,0xada8,0xadaa}, // wram_flash_timers
    0xad8a, // wram_current_layer_config
    0xaff1, // rom_layer_config
    0x436e, // wram_map_combo
    {0x31,0x33,0x35,0x37}, // wram_bg_scroll
    0x18000, // wram_map_arrangements
    0xa62, // wram_entity_script
    0xe5e, // wram_entity_var0
    0xe9a, // wram_entity_var1
    0x10000, // wram_lumine_header
    {0x11000,0x14000}, // wram_lumine_maps
    {0x160000,0x162800,0x165000,0x168000,0x16a800,0x16d000,0x170000,0x172800,0x175000,0x178000}, // rom_map_chunks
    0x17a800, // rom_map_sectors
    0x314, // title_event_first
    0x31e, // title_event_last
    0x3, // title_bg_mode
    {0x58,0x0}, // title_bg_maps
    {0x1c4,0x2c1,0x2c2}, // lightning_events
    0x35c, // gas_flash_event
    0x10000, // wram_gas_base_palette
    {0x21a9b7,0x21aa5d}, // rom_gas_palettes
    0x313, // file_select_event
    0x161, // lumine_event
    0x8cd5, // rom_spritemap_writer
    0x88b1, // rom_oam_clear
    {0x500,0x800}, // wram_oam_buffers
    {0x3,0x5}, // wram_oam_cursor
    0xb, // wram_spritemap_bank
    0x2e, // wram_next_frame_buffer
    0xdb0f, // rom_entity_draw_loop
    0xa3a4, // rom_entity_draw_default
    {0xa50,0xa9e,0xb16,0xb52,0x112e,0x116a,0x10f2,0x11e2,0x341a,0x2916,0x2baa,0x2be6,0x65}, // wram_entity_draw
};
constexpr SourceProfile profile_jp{
    0x993b, // wram_battle_flag
    {0xafa9,0xb020}, // wram_bg_records
    0x1b44, // wram_psi_animation
    0xb0bc, // wram_psi_targets
    0xb097, // wram_swirl_timer
    0x200, // wram_palettes
    {0xaf73,0xaf75,0xaf7d,0xaf7f}, // wram_flash_timers
    0xaf5f, // wram_current_layer_config
    0xafd0, // rom_layer_config
    0x46f4, // wram_map_combo
    {0x31,0x33,0x35,0x37}, // wram_bg_scroll
    0x18000, // wram_map_arrangements
    0xa58, // wram_entity_script
    0xe54, // wram_entity_var0
    0xe90, // wram_entity_var1
    0x10000, // wram_lumine_header
    {0x12000,0x14000}, // wram_lumine_maps
    {0x160000,0x162800,0x165000,0x168000,0x16a800,0x16d000,0x170000,0x172800,0x175000,0x178000}, // rom_map_chunks
    0x17a800, // rom_map_sectors
    0x314, // title_event_first
    0x31a, // title_event_last
    0x1, // title_bg_mode
    {0x38,0x3c}, // title_bg_maps
    {0x1c4,0x2c1,0x2c2}, // lightning_events
    0x358, // gas_flash_event
    0x10000, // wram_gas_base_palette
    {0x219cb9,0x219d5f}, // rom_gas_palettes
    0x313, // file_select_event
    0x161, // lumine_event
    0x8cc6, // rom_spritemap_writer
    0x88a4, // rom_oam_clear
    {0x500,0x800}, // wram_oam_buffers
    {0x3,0x5}, // wram_oam_cursor
    0xb, // wram_spritemap_bank
    0x2e, // wram_next_frame_buffer
    0xdad7, // rom_entity_draw_loop
    0xa383, // rom_entity_draw_default
    {0xa46,0xa94,0xb0c,0xb48,0x1124,0x1160,0x10e8,0x11d8,0x1ab8,0x2d14,0x2fa8,0x2fe4,0x65}, // wram_entity_draw
};
}
const SourceProfile& source_profile(GameVersion version) { return version == GameVersion::JP ? profile_jp : profile_us; }
}
