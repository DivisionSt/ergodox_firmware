#include QMK_KEYBOARD_H
#include "version.h"


enum custom_keycodes {
  ALT_TAB = SAFE_RANGE,
  CMD_TAB,
  LAYER_ID,
};


// custom declarations
void send_current_layer_name(void);
bool is_alt_tab_active = false;
uint16_t alt_tab_timer = 0;
bool is_cmd_tab_active = false;
uint16_t cmd_tab_timer = 0;



#define DUAL_FUNC_0 LT(12, KC_F2)
#define DUAL_FUNC_1 LT(11, KC_F9)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [0] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           QK_LEAD,                                        QK_REPEAT_KEY, KC_6,           KC_7,           KC_8,           KC_9,           KC_0,           KC_MINUS,
    KC_TAB,         KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_GRAVE,                                       KC_EQUAL,       KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,           KC_BSLS,
    KC_TRANSPARENT, KC_A,           KC_S,           KC_D,           KC_F,           KC_G,                                                                           KC_H,           KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_QUOTE,
    KC_TRANSPARENT, KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           KC_LBRC,                                        KC_RBRC,        KC_N,           KC_M,           KC_COMMA,       KC_DOT,         KC_SLASH,       KC_TRANSPARENT,
    LGUI(LCTL(KC_SPACE)),KC_TRANSPARENT, KC_TRANSPARENT, CMD_TAB,   OSM(MOD_LSFT),                                                                                                  OSM(MOD_RSFT), QK_REPEAT_KEY, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    QK_LEAD,          DUAL_FUNC_0,    TO(9),          QK_REPEAT_KEY,
                                                                                                                    KC_AUDIO_VOL_UP,LAYER_ID,
                                                                                    LT(3, KC_BSPC), OSM(MOD_LGUI),  KC_AUDIO_VOL_DOWN,KC_TRANSPARENT, MT(MOD_RGUI, KC_ENTER),LT(4, KC_SPACE)
  ),
  [1] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_6,           KC_7,           KC_8,           KC_9,           KC_0,           KC_MINUS,
    KC_TAB,         KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_GRAVE,                                       KC_EQUAL,       KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,           KC_BSLS,
    KC_TRANSPARENT, KC_A,           KC_S,           KC_D,           KC_F,           KC_G,                                                                           KC_H,           KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_QUOTE,
    KC_TRANSPARENT, KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           KC_LBRC,                                        KC_RBRC,        KC_N,           KC_M,           KC_COMMA,       KC_DOT,         KC_SLASH,       KC_TRANSPARENT,
    LGUI(KC_DOT),   KC_TRANSPARENT, KC_TRANSPARENT, ALT_TAB,        OSM(MOD_LSFT),                                                                                                  OSM(MOD_RSFT),  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, DUAL_FUNC_1,    TO(9),          KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, LAYER_ID,
                                                                                    LT(5, KC_BSPC), OSM(MOD_LCTL),  KC_TRANSPARENT, KC_TRANSPARENT, MT(MOD_RCTL, KC_ENTER),LT(6, KC_SPACE)
  ),
  [2] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_LEFT_GUI,    KC_A,           KC_S,           KC_D,           KC_F,           KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_TRANSPARENT,
    KC_LEFT_SHIFT,  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_RIGHT_SHIFT,
    KC_NO,          KC_LEFT_CTRL,   KC_LEFT_ALT,    KC_NO,          KC_LEFT_GUI,                                                                                                    KC_RIGHT_GUI,   KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_BSPC,        KC_DELETE,      KC_TRANSPARENT, KC_TRANSPARENT, KC_ENTER,       KC_SPACE
  ),
  [3] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_F1,          KC_F2,          KC_F3,          KC_F4,          KC_F5,          KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F6,          KC_F7,          KC_F8,          KC_F9,          KC_F10,         KC_F11,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, LGUI(KC_GRAVE),                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F12,
    CW_TOGG,        OSM(MOD_LSFT),  OSM(MOD_LCTL),  OSM(MOD_LALT),  OSM(MOD_LGUI),  LCTL(KC_TAB),                                                                   KC_LEFT,        KC_DOWN,        KC_UP,          KC_RIGHT,       KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, LGUI(KC_LEFT),  KC_LPRN,                                        KC_RPRN,        KC_TRANSPARENT, KC_PGDN,        KC_PAGE_UP,     KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, LGUI(KC_TAB),   KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, LCTL(KC_ENTER), KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_MEDIA_NEXT_TRACK,KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_MEDIA_PREV_TRACK,KC_TRANSPARENT, KC_TRANSPARENT, KC_DELETE
  ),
  [4] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_KP_SLASH,    KC_KP_ASTERISK, KC_MINUS,       KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_7,           KC_8,           KC_9,           KC_KP_PLUS,     KC_TRANSPARENT,
    KC_TRANSPARENT, OSM(MOD_LSFT),  OSM(MOD_LCTL),  OSM(MOD_LALT),  OSM(MOD_LGUI),  KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_4,           KC_5,           KC_6,           KC_KP_PLUS,     KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_LPRN,                                        KC_RPRN,        KC_TRANSPARENT, KC_1,           KC_2,           KC_3,           KC_KP_ENTER,    KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_0,           KC_0,           KC_KP_DOT,      KC_KP_ENTER,    KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_BRIGHTNESS_UP,KC_TRANSPARENT,
                                                                                    KC_BSPC,        KC_DELETE,      KC_BRIGHTNESS_DOWN,KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [5] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_F1,          KC_F2,          KC_F3,          KC_F4,          KC_F5,          KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F6,          KC_F7,          KC_F8,          KC_F9,          KC_F10,         KC_F11,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F12,
    KC_TRANSPARENT, OSM(MOD_LSFT),  OSM(MOD_LGUI),  OSM(MOD_LALT),  OSM(MOD_LCTL),  LCTL(KC_TAB),                                                                   KC_LEFT,        KC_DOWN,        KC_UP,          KC_RIGHT,       KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, LCTL(KC_LEFT),  KC_LPRN,                                        KC_RPRN,        KC_TRANSPARENT, KC_PGDN,        KC_PAGE_UP,     KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, LALT(KC_TAB),   KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, LGUI(KC_X),     KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, OSM(MOD_LCTL),  KC_TRANSPARENT, KC_TRANSPARENT, MT(MOD_RCTL, KC_ENTER),KC_DELETE
  ),
  [6] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_KP_SLASH,    KC_KP_ASTERISK, KC_MINUS,       KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_7,           KC_8,           KC_9,           KC_KP_PLUS,     KC_TRANSPARENT,
    KC_TRANSPARENT, OSM(MOD_LSFT),  OSM(MOD_LGUI),  OSM(MOD_LALT),  OSM(MOD_LCTL),  KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_4,           KC_5,           KC_6,           KC_KP_PLUS,     KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_LPRN,                                        KC_RPRN,        KC_TRANSPARENT, KC_1,           KC_2,           KC_3,           KC_KP_ENTER,    KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_0,           KC_0,           KC_KP_DOT,      KC_KP_ENTER,    KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_BRIGHTNESS_UP,KC_TRANSPARENT,
                                                                                    KC_BSPC,        KC_DELETE,      KC_BRIGHTNESS_DOWN,KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [7] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_F10,         KC_F11,         KC_F12,         KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F12,         KC_F7,          KC_F8,          KC_F9,          KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, OSM(MOD_LSFT),  OSM(MOD_LCTL),  OSM(MOD_LALT),  OSM(MOD_LGUI),  KC_TRANSPARENT,                                                                 KC_F11,         KC_F4,          KC_F5,          KC_F6,          KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F10,         KC_F1,          KC_F2,          KC_F3,          KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_BRIGHTNESS_UP,KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_BRIGHTNESS_DOWN,KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [8] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                 KC_MS_LEFT,     KC_MS_DOWN,     KC_MS_UP,       KC_MS_RIGHT,    KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_MS_WH_LEFT,  KC_MS_WH_DOWN,  KC_MS_WH_UP,    KC_MS_WH_RIGHT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_MS_BTN3,     KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_NO,          KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_MS_BTN1,     KC_MS_BTN2
  ),
  [9] = LAYOUT_ergodox_pretty(
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,
    KC_NO,          KC_NO,          TO(1),          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                          KC_NO,          KC_NO,          KC_NO,          KC_NO,          TO(2),          KC_NO,          KC_NO,
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                                                          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                          KC_NO,          KC_NO,          TO(8),          KC_NO,          KC_NO,          QK_DYNAMIC_TAPPING_TERM_PRINT,KC_NO,
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                                                                                          KC_NO,          KC_NO,          QK_DYNAMIC_TAPPING_TERM_DOWN,QK_DYNAMIC_TAPPING_TERM_UP,KC_NO,
                                                                                                    KC_NO,          KC_NO,          TO(0),          KC_NO,
                                                                                                                    KC_NO,          KC_NO,
                                                                                    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO
  ),
};


const char chordal_hold_layout[MATRIX_ROWS][MATRIX_COLS] PROGMEM = LAYOUT_ergodox(
  'L', 'L', 'L', 'L', 'L', 'L', 'L', 
  'L', 'L', 'L', 'L', 'L', 'L', 'L', 
  'L', 'L', 'L', 'L', 'L', 'L', 
  'L', 'L', 'L', 'L', 'L', 'L', 'L', 
  'L', 'L', 'L', 'L', 'L',
  '*', '*',
  '*', '*', '*', '*',
  'R', 'R', 'R', 'R', 'R', 'R', 'R', 
  'R', 'R', 'R', 'R', 'R', 'R', 'R', 
  'R', 'R', 'R', 'R', 'R', 'R', 
  'R', 'R', 'R', 'R', 'R', 'R', 'R', 
  'R', 'R', 'R', 'R', 'R', 
  '*', '*',
  '*', '*', '*', '*'
);

const uint16_t PROGMEM combo0[] = { LT(3, KC_BSPC), LT(4, KC_SPACE), COMBO_END};
const uint16_t PROGMEM combo1[] = { OSM(MOD_LGUI), LT(3, KC_BSPC), COMBO_END};
const uint16_t PROGMEM combo2[] = { MT(MOD_RGUI, KC_ENTER), LT(4, KC_SPACE), COMBO_END};
const uint16_t PROGMEM combo3[] = { KC_Q, KC_W, COMBO_END};
const uint16_t PROGMEM combo4[] = { KC_Z, KC_X, COMBO_END};
const uint16_t PROGMEM combo5[] = { KC_B, KC_V, COMBO_END};
const uint16_t PROGMEM combo6[] = { LT(3, KC_BSPC), OSM(MOD_LGUI), COMBO_END};
const uint16_t PROGMEM combo7[] = { LT(4, KC_SPACE), MT(MOD_RGUI, KC_ENTER), COMBO_END};

combo_t key_combos[COMBO_COUNT] = {
    COMBO(combo0, TG(7)),
    COMBO(combo1, TG(3)),
    COMBO(combo2, TG(4)),
    COMBO(combo3, LSFT(KC_LEFT_CTRL)),
    COMBO(combo4, LSFT(KC_LEFT_ALT)),
    COMBO(combo5, LGUI(LSFT(KC_V))),
    COMBO(combo6, TG(5)),
    COMBO(combo7, TG(6)),
};

uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case LT(4, KC_SPACE):
            return g_tapping_term + 40;
        case LT(6, KC_SPACE):
            return g_tapping_term + 40;
        default:
            return g_tapping_term;
    }
}




bool process_record_user(uint16_t keycode, keyrecord_t *record) {
  switch (keycode) {

    case DUAL_FUNC_0:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(KC_MEDIA_PLAY_PAUSE);
        } else {
          unregister_code16(KC_MEDIA_PLAY_PAUSE);
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(LCTL(KC_Q)));
        } else {
          unregister_code16(LGUI(LCTL(KC_Q)));
        }  
      }  
      return false;
    case DUAL_FUNC_1:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(KC_MEDIA_PLAY_PAUSE);
        } else {
          unregister_code16(KC_MEDIA_PLAY_PAUSE);
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(KC_L));
        } else {
          unregister_code16(LGUI(KC_L));
        }  
      }  
      return false;
    case LAYER_ID:
      if (record->event.pressed) {
        send_current_layer_name();
      }
      return false;
    case ALT_TAB:
      if (record->event.pressed) {
        if (!is_alt_tab_active) {
          is_alt_tab_active = true;
          register_code(KC_LALT);
        }
        alt_tab_timer = timer_read();
        register_code(KC_TAB);
      } else {
        unregister_code(KC_TAB);
      }
      break;
    case CMD_TAB:
      if (record->event.pressed) {
        if (!is_cmd_tab_active) {
          is_cmd_tab_active = true;
          register_code(KC_LGUI);
        }
        cmd_tab_timer = timer_read();
        register_code(KC_TAB);
      } else {
        unregister_code(KC_TAB);
      }
      break;
    default:
      if (is_cmd_tab_active) {
        if (keycode != KC_TAB && !(get_mods() & MOD_MASK_SHIFT) && !(get_oneshot_mods() & MOD_MASK_SHIFT) && record->event.pressed) {
          unregister_code(KC_LGUI);
          is_cmd_tab_active = false;
        }
      }
      if (is_alt_tab_active) {
        if (keycode != KC_TAB && !(get_mods() & MOD_MASK_SHIFT) && !(get_oneshot_mods() & MOD_MASK_SHIFT) && record->event.pressed) {
          unregister_code(KC_LALT);
          is_alt_tab_active = false;
        }
      }
    break;
  }
  return true;
}

void matrix_scan_user(void) { 
  if (is_alt_tab_active) {
    if (timer_elapsed(alt_tab_timer) > 9000) {
      unregister_code(KC_LALT);
      is_alt_tab_active = false;
    }
  }
  if (is_cmd_tab_active) {
    if (timer_elapsed(cmd_tab_timer) > 9000) {
      unregister_code(KC_LGUI);
      is_cmd_tab_active = false;
    }
  }
}


uint16_t layer_state_set_user(uint16_t state) {
    uint8_t layer = biton16(state);
  ergodox_board_led_off();
  ergodox_right_led_1_off();
  ergodox_right_led_2_off();
  ergodox_right_led_3_off();
  switch (layer) {
    case 1:
      ergodox_right_led_1_on();
      break;
    case 2:
      ergodox_right_led_2_on();
      break;
    case 3:
      ergodox_right_led_1_on();
      ergodox_right_led_2_on();
      break;
    case 4:
      ergodox_right_led_3_on();
      break;
    case 5:
      ergodox_right_led_1_on();
      ergodox_right_led_3_on();
      break;
    case 6:
      ergodox_right_led_2_on();
      ergodox_right_led_3_on();
      break;
    case 7:
      ergodox_right_led_1_on();
      ergodox_right_led_2_on();
      ergodox_right_led_3_on();
      break;
    default:
      break;
  }
  return state;
};














/* Custom QMK Features */

void send_current_layer_name(void) {
  uint8_t current_layer = get_highest_layer(layer_state);
  
  SEND_STRING("L: ");
  switch (current_layer) {
    case 0:
      SEND_STRING("base-mac");
      break;
    case 1:
      SEND_STRING("base-win");
      break;
    case 2:
      SEND_STRING("base-old");
      break;
    case 3:
      SEND_STRING("ext-nav");
      break;
    case 4:
      SEND_STRING("ext-num");
      break;
    case 5:
      SEND_STRING("ext-func");
      break;
    case 6:
      SEND_STRING("mouse");
      break;
    case 7:
      SEND_STRING("layers");
      break;
    default:
      SEND_STRING("unknown");
      break;
  }
}

void leader_end_user(void) {
  // leaves
  if (leader_sequence_one_key(KC_T)) { // t
    tap_code16(LGUI(LSFT(KC_T)));
  } else if (leader_sequence_one_key(KC_V)) { // v
    tap_code16(LGUI(LSFT(KC_V)));
  } else if (leader_sequence_one_key(KC_A)) { // a
    tap_code16(LGUI(LSFT(KC_A)));
  } 

  // system (/)
  else if (leader_sequence_two_keys(KC_SLASH, KC_I)) { // /, i
    send_current_layer_name();
  } 

  // rectangle (r)
  else if (leader_sequence_two_keys(KC_R, KC_1)) { // r, 1
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_1)))));
  } else if (leader_sequence_two_keys(KC_R, KC_2)) { // r, 2
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_2)))));
  } else if (leader_sequence_two_keys(KC_R, KC_3)) { // r, 3
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_3)))));
  } else if (leader_sequence_two_keys(KC_R, KC_6)) { // r, 6
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_6)))));
  } else if (leader_sequence_two_keys(KC_R, KC_7)) { // r, 7
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_7)))));
  } else if (leader_sequence_two_keys(KC_R, KC_8)) { // r, 8
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_8)))));
  } else if (leader_sequence_three_keys(KC_R, KC_W, KC_O)) { // r, w, o
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_1)))));
  } else if (leader_sequence_three_keys(KC_R, KC_W, KC_M)) { // r, w, m
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_2)))));
  } else if (leader_sequence_three_keys(KC_R, KC_W, KC_C)) { // r, w, c
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_3)))));
  } else if (leader_sequence_three_keys(KC_R, KC_H, KC_O)) { // r, h, o
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_6)))));
  } else if (leader_sequence_three_keys(KC_R, KC_H, KC_M)) { // r, h, m
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_7)))));
  } else if (leader_sequence_three_keys(KC_R, KC_H, KC_C)) { // r, h, c
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_8)))));
  } else if (leader_sequence_two_keys(KC_R, KC_G)) { // r, g
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_RIGHT)))));
  } else if (leader_sequence_two_keys(KC_R, KC_L)) { // r, n
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_RIGHT)))));
  } else if (leader_sequence_two_keys(KC_R, KC_S)) { // r, s
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_LEFT)))));
  } else if (leader_sequence_two_keys(KC_R, KC_P)) { // r, p
    tap_code16(LALT(LGUI(LCTL(LSFT(KC_LEFT)))));
  } else if (leader_sequence_two_keys(KC_R, KC_D)) { // r, d
    tap_code16(LALT(LCTL(KC_ENTER)));
  } else if (leader_sequence_two_keys(KC_R, KC_M)) { // r, m
    tap_code16(LALT(LCTL(KC_ENTER)));
  } else if (leader_sequence_two_keys(KC_R, KC_F)) { // r, f
    tap_code16(LALT(LCTL(KC_C)));
  } else if (leader_sequence_two_keys(KC_R, KC_C)) { // r, c
    tap_code16(LALT(LCTL(KC_C)));
  }

  // desktop (d)
  else if (leader_sequence_two_keys(KC_D, KC_M)) { // d, m
    tap_code16(LCTL(KC_UP));
  } else if (leader_sequence_two_keys(KC_D, KC_D)) { // d, d
    tap_code16(LCTL(KC_UP));
  } else if (leader_sequence_two_keys(KC_D, KC_K)) { // d, k
    tap_code16(LCTL(KC_UP));
  } else if (leader_sequence_two_keys(KC_D, KC_F)) { // d, f
    tap_code16(LGUI(LCTL(KC_F)));
  } else if (leader_sequence_two_keys(KC_D, KC_E)) { // d, e
    tap_code16(LCTL(KC_DOWN));
  } else if (leader_sequence_two_keys(KC_D, KC_N)) { // d, n
    tap_code16(LCTL(KC_RIGHT));
  } else if (leader_sequence_two_keys(KC_D, KC_G)) { // d, g
    tap_code16(LCTL(KC_RIGHT));
  } else if (leader_sequence_two_keys(KC_D, KC_L)) { // d, l
    tap_code16(LCTL(KC_RIGHT));
  } else if (leader_sequence_two_keys(KC_D, KC_P)) { // d, p
    tap_code16(LCTL(KC_LEFT));
  } else if (leader_sequence_two_keys(KC_D, KC_S)) { // d, s
    tap_code16(LCTL(KC_LEFT));
  } else if (leader_sequence_two_keys(KC_D, KC_H)) { // d, h
    tap_code16(LCTL(KC_LEFT));
  }

  // shortcut (s)
  else if (leader_sequence_two_keys(KC_S, KC_S)) { // s, s
    tap_code16(LGUI(LSFT(KC_1)));
  } else if (leader_sequence_two_keys(KC_S, KC_W)) { // s, w
    tap_code16(LGUI(LSFT(KC_2)));
  }
}

bool get_permissive_hold(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {

        //case LT(3, KC_BSPC):
        //case LT(4, KC_SPACE):
            // Do not select the hold action when another key is tapped.
        //    return false;
        default:
            // Immediately select the hold action when another key is tapped.
            return true;
    }
}