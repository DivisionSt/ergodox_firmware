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


#define DUAL_FUNC_0 LT(8, KC_F9)
#define DUAL_FUNC_1 LT(8, KC_F4)
#define DUAL_FUNC_2 LT(15, KC_D)
#define DUAL_FUNC_3 LT(4, KC_F8)
#define DUAL_FUNC_4 LT(3, KC_4)
#define DUAL_FUNC_5 LT(12, KC_C)
#define DUAL_FUNC_6 LT(5, KC_F18)
#define DUAL_FUNC_7 LT(13, KC_C)
#define DUAL_FUNC_8 LT(5, KC_Q)
#define DUAL_FUNC_9 LT(2, KC_2)
#define DUAL_FUNC_10 LT(5, KC_I)
#define DUAL_FUNC_11 LT(15, KC_F18)
#define DUAL_FUNC_12 LT(3, KC_F1)
#define DUAL_FUNC_13 LT(2, KC_E)
#define DUAL_FUNC_14 LT(3, KC_F17)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [0] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           QK_LEADER,                                      QK_REPEAT_KEY, KC_6,           KC_7,           KC_8,           KC_9,           KC_0,           KC_MINUS,
    KC_TAB,         KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_GRAVE,                                       KC_EQUAL,       KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,           KC_BSLS,
    KC_TRANSPARENT, KC_A,           MT(MOD_LCTL, KC_S),MT(MOD_LALT, KC_D),MT(MOD_LGUI, KC_F),KC_G,                                                                           KC_H,           MT(MOD_RGUI, KC_J),MT(MOD_LALT, KC_K),MT(MOD_RCTL, KC_L),KC_SCLN,        KC_QUOTE,
    KC_TRANSPARENT, KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           DUAL_FUNC_0,                                    DUAL_FUNC_2,    KC_N,           KC_M,           KC_COMMA,       KC_DOT,         KC_SLASH,       KC_TRANSPARENT,
    LGUI(LCTL(KC_SPACE)),KC_TRANSPARENT, KC_TRANSPARENT, CMD_TAB, KC_LEFT_SHIFT,                                                                                                    KC_RIGHT_SHIFT,   KC_LEFT,        KC_DOWN,        KC_UP,          KC_RIGHT,
                                                                                                    TT(6),          DUAL_FUNC_1,    TO(11),         TT(8),
                                                                                                                    KC_AUDIO_VOL_UP,LAYER_ID,
                                                                                    LT(6, KC_BSPC), LT(7, KC_DELETE),KC_AUDIO_VOL_DOWN,KC_TRANSPARENT, LT(9, KC_ENTER),LT(8, KC_SPACE)
  ),
  [1] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           KC_TRANSPARENT,                                 KC_MEDIA_PLAY_PAUSE,KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F11,
    KC_J,           KC_Z,           KC_W,           KC_X,           KC_R,           KC_I,           KC_U,                                           DUAL_FUNC_3,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_LEFT_CTRL,   KC_A,           KC_S,           KC_D,           KC_5,           KC_H,                                                                           KC_TRANSPARENT, KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_TRANSPARENT,
    KC_LEFT_SHIFT,  KC_1,           KC_2,           KC_3,           KC_4,           KC_1,           KC_F,                                           DUAL_FUNC_4,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_B,           KC_TRANSPARENT, KC_TRANSPARENT, KC_E,           KC_G,                                                                                                           KC_LEFT_GUI,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_M,           KC_7,           TO(11),         KC_NO,
                                                                                                                    KC_N,           KC_TRANSPARENT,
                                                                                    KC_SPACE,       KC_U,           KC_EQUAL,       TG(4),          KC_ENTER,       KC_SPACE
  ),
  [2] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           KC_H,                                           KC_MEDIA_PLAY_PAUSE,KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F11,
    KC_H,           KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_GRAVE,                                       DUAL_FUNC_3,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_LEFT_SHIFT,  KC_A,           KC_S,           KC_D,           KC_F5,          KC_F,                                                                           KC_TRANSPARENT, KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_TRANSPARENT,
    KC_LEFT_CTRL,   KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           KC_LBRC,                                        DUAL_FUNC_4,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_NO,          KC_TRANSPARENT, KC_TRANSPARENT, KC_NO,          KC_NO,                                                                                                          KC_LEFT_GUI,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_NO,          KC_NO,          TO(11),         KC_NO,
                                                                                                                    KC_NO,          KC_TRANSPARENT,
                                                                                    KC_SPACE,       KC_J,           KC_NO,          TG(4),          KC_ENTER,       KC_SPACE
  ),
  [3] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           KC_NO,                                          KC_MEDIA_PLAY_PAUSE,KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_F11,
    KC_TAB,         KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_GRAVE,                                       DUAL_FUNC_3,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_LEFT_CTRL,   KC_A,           KC_S,           KC_D,           KC_F,           KC_G,                                                                           KC_TRANSPARENT, KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_TRANSPARENT,
    KC_LEFT_SHIFT,  KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           KC_LBRC,                                        DUAL_FUNC_4,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_NO,          KC_TRANSPARENT, KC_TRANSPARENT, KC_NO,          KC_NO,                                                                                                          KC_LEFT_GUI,    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_M,           KC_NO,          TO(11),         KC_NO,
                                                                                                                    KC_NO,          KC_TRANSPARENT,
                                                                                    KC_SPACE,       KC_NO,          KC_NO,          TG(4),          KC_ENTER,       KC_SPACE
  ),
  [4] = LAYOUT_ergodox_pretty(
    KC_ESCAPE,      KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_6,           KC_7,           KC_8,           KC_9,           KC_0,           KC_MINUS,
    KC_TAB,         KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_GRAVE,                                       KC_EQUAL,       KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,           KC_BSLS,
    KC_TRANSPARENT, KC_A,           MT(MOD_LGUI, KC_S),MT(MOD_LALT, KC_D),MT(MOD_LCTL, KC_F),KC_G,                                                                           KC_H,           MT(MOD_RCTL, KC_J),MT(MOD_LALT, KC_K),MT(MOD_RGUI, KC_L),KC_SCLN,        KC_QUOTE,
    KC_TRANSPARENT, KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           DUAL_FUNC_0,                                    DUAL_FUNC_2,    KC_N,           KC_M,           KC_COMMA,       KC_DOT,         KC_SLASH,       KC_TRANSPARENT,
    LGUI(KC_DOT),   KC_TRANSPARENT, KC_TRANSPARENT, ALT_TAB, KC_LEFT_SHIFT,                                                                                                   KC_RIGHT_SHIFT,  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, DUAL_FUNC_3,    TO(11),         KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [5] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_LEFT_GUI,    KC_A,           KC_S,           KC_D,           KC_F,           KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_TRANSPARENT,
    KC_LEFT_SHIFT,  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_RIGHT_SHIFT,
    KC_TRANSPARENT, KC_LEFT_CTRL,   KC_LEFT_ALT,    KC_TRANSPARENT, KC_LEFT_GUI,                                                                                                    KC_RIGHT_GUI,   KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [6] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, LALT(LGUI(LCTL(LSFT(KC_1)))),LALT(LGUI(LCTL(LSFT(KC_2)))),LALT(LGUI(LCTL(LSFT(KC_3)))),KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, LALT(LGUI(LCTL(LSFT(KC_6)))),LALT(LGUI(LCTL(LSFT(KC_7)))),LALT(LGUI(LCTL(LSFT(KC_8)))),KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, LCTL(KC_LEFT),  DUAL_FUNC_6,    LCTL(KC_DOWN),  LCTL(KC_RIGHT), LGUI(KC_GRAVE),                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    CW_TOGG,        LGUI(LSFT(KC_A)),DUAL_FUNC_7,    DUAL_FUNC_8,    LGUI(KC_W),     DUAL_FUNC_9,                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, DUAL_FUNC_10,   LALT(LCTL(KC_ENTER)),LALT(LCTL(KC_C)),DUAL_FUNC_11,   DUAL_FUNC_12,                                   KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, KC_DELETE,      KC_TRANSPARENT, KC_TRANSPARENT, KC_ENTER,       KC_SPACE
  ),
  [7] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_INSERT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, LALT(KC_LEFT_SHIFT),LSFT(KC_LEFT_CTRL),KC_MEH,         KC_TRANSPARENT,                                 KC_TRANSPARENT, LALT(LSFT(KC_LEFT)),LSFT(KC_DOWN),  LSFT(KC_UP),    LALT(LSFT(KC_RIGHT)),KC_TRANSPARENT, KC_TRANSPARENT,
    CW_TOGG,        LGUI(KC_A),     LGUI(KC_S),     KC_TRANSPARENT, DUAL_FUNC_13,   KC_TRANSPARENT,                                                                 KC_LEFT,        KC_DOWN,        KC_UP,          KC_RIGHT,       KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, LGUI(KC_Z),     LGUI(KC_X),     LGUI(KC_C),     DUAL_FUNC_14,   LGUI(LSFT(KC_Z)),KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_HOME,        KC_PGDN,        KC_PAGE_UP,     KC_END,         KC_UP,          KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, LCTL(KC_ENTER), KC_LEFT,        KC_DOWN,        KC_RIGHT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_MEDIA_NEXT_TRACK,KC_TRANSPARENT,
                                                                                    KC_BSPC,        KC_TRANSPARENT, KC_MEDIA_PREV_TRACK,KC_TRANSPARENT, KC_ENTER,       KC_SPACE
  ),
  [8] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_KP_SLASH,    KC_KP_ASTERISK, KC_MINUS,       KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_7,           KC_8,           KC_9,           KC_KP_PLUS,     KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_4,           KC_5,           KC_6,           KC_KP_PLUS,     KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_1,           KC_2,           KC_3,           KC_KP_ENTER,    KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_0,           KC_0,           KC_KP_DOT,      KC_KP_ENTER,    KC_NO,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_BRIGHTNESS_UP,KC_NO,
                                                                                    KC_BSPC,        KC_DELETE,      KC_BRIGHTNESS_DOWN,KC_NO,          KC_ENTER,       KC_TRANSPARENT
  ),
  [9] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F12,         KC_F7,          KC_F8,          KC_F9,          KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                 KC_F11,         KC_F4,          KC_F5,          KC_F6,          KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F10,         KC_F1,          KC_F2,          KC_F3,          KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_BRIGHTNESS_UP,KC_TRANSPARENT,
                                                                                    KC_BSPC,        KC_DELETE,      KC_BRIGHTNESS_DOWN,KC_TRANSPARENT, KC_TRANSPARENT, KC_SPACE
  ),
  [10] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                 KC_MS_LEFT,     KC_MS_DOWN,     KC_MS_UP,       KC_MS_RIGHT,    KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_MS_WH_LEFT,  KC_MS_WH_DOWN,  KC_MS_WH_UP,    KC_MS_WH_RIGHT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_MS_BTN3,     KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_MS_BTN1,     KC_MS_BTN2
  ),
  [11] = LAYOUT_ergodox_pretty(
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,
    KC_NO,          KC_NO,          TO(4),          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                          KC_NO,          KC_NO,          KC_NO,          KC_NO,          TO(5),          KC_NO,          KC_NO,
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          TO(1),          TO(3),                                                                          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,
    KC_NO,          KC_NO,          KC_NO,          TO(2),          KC_NO,          KC_NO,          KC_NO,                                          KC_NO,          KC_NO,          TO(10),         KC_NO,          KC_NO,          QK_DYNAMIC_TAPPING_TERM_PRINT,KC_NO,
    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,                                                                                                          KC_NO,          KC_NO,          QK_DYNAMIC_TAPPING_TERM_DOWN,QK_DYNAMIC_TAPPING_TERM_UP,KC_NO,
                                                                                                    KC_NO,          KC_NO,          TO(0),          KC_NO,
                                                                                                                    KC_NO,          KC_NO,
                                                                                    KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO
  ),
  [12] = LAYOUT_ergodox_pretty(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
    KC_TRANSPARENT, KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,           KC_TRANSPARENT,
    KC_LEFT_CTRL,   KC_A,           KC_S,           KC_D,           KC_F,           KC_G,                                                                           KC_H,           KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_TRANSPARENT,
    KC_LEFT_SHIFT,  KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,           KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_N,           KC_M,           KC_COMMA,       KC_DOT,         KC_QUOTE,       KC_RIGHT_SHIFT,
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_LEFT_CTRL,                                                                                                   KC_RIGHT_CTRL,  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                                                    KC_TRANSPARENT, KC_TRANSPARENT,
                                                                                    KC_BSPC,        KC_DELETE,      KC_TRANSPARENT, KC_TRANSPARENT, KC_ENTER,       KC_SPACE
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


uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case LT(8, KC_SPACE):
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
          register_code16(KC_LBRC);
        } else {
          unregister_code16(KC_LBRC);
        }
      } else {
        if (record->event.pressed) {
          register_code16(KC_LPRN);
        } else {
          unregister_code16(KC_LPRN);
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
          register_code16(LGUI(LCTL(KC_Q)));
        } else {
          unregister_code16(LGUI(LCTL(KC_Q)));
        }  
      }  
      return false;
    case DUAL_FUNC_2:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(KC_RBRC);
        } else {
          unregister_code16(KC_RBRC);
        }
      } else {
        if (record->event.pressed) {
          register_code16(KC_RPRN);
        } else {
          unregister_code16(KC_RPRN);
        }  
      }  
      return false;
    case DUAL_FUNC_3:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(KC_AUDIO_VOL_UP);
        } else {
          unregister_code16(KC_AUDIO_VOL_UP);
        }
      } else {
        if (record->event.pressed) {
          register_code16(KC_MEDIA_NEXT_TRACK);
        } else {
          unregister_code16(KC_MEDIA_NEXT_TRACK);
        }  
      }  
      return false;
    case DUAL_FUNC_4:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(KC_AUDIO_VOL_DOWN);
        } else {
          unregister_code16(KC_AUDIO_VOL_DOWN);
        }
      } else {
        if (record->event.pressed) {
          register_code16(KC_MEDIA_PREV_TRACK);
        } else {
          unregister_code16(KC_MEDIA_PREV_TRACK);
        }  
      }  
      return false;
    case DUAL_FUNC_5:
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
    case DUAL_FUNC_6:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LCTL(KC_UP));
        } else {
          unregister_code16(LCTL(KC_UP));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(LCTL(KC_F)));
        } else {
          unregister_code16(LGUI(LCTL(KC_F)));
        }  
      }  
      return false;
    case DUAL_FUNC_7:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LCTL(LSFT(KC_TAB)));
        } else {
          unregister_code16(LCTL(LSFT(KC_TAB)));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(KC_LEFT));
        } else {
          unregister_code16(LGUI(KC_LEFT));
        }  
      }  
      return false;
    case DUAL_FUNC_8:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LGUI(KC_T));
        } else {
          unregister_code16(LGUI(KC_T));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(LSFT(KC_T)));
        } else {
          unregister_code16(LGUI(LSFT(KC_T)));
        }  
      }  
      return false;
    case DUAL_FUNC_9:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LCTL(KC_TAB));
        } else {
          unregister_code16(LCTL(KC_TAB));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(KC_RIGHT));
        } else {
          unregister_code16(LGUI(KC_RIGHT));
        }  
      }  
      return false;
    case DUAL_FUNC_10:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LALT(LGUI(LCTL(LSFT(KC_LEFT)))));
        } else {
          unregister_code16(LALT(LGUI(LCTL(LSFT(KC_LEFT)))));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LALT(LGUI(LCTL(KC_LEFT))));
        } else {
          unregister_code16(LALT(LGUI(LCTL(KC_LEFT))));
        }  
      }  
      return false;
    case DUAL_FUNC_11:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LALT(LGUI(LCTL(LSFT(KC_RIGHT)))));
        } else {
          unregister_code16(LALT(LGUI(LCTL(LSFT(KC_RIGHT)))));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LALT(LGUI(LCTL(KC_RIGHT))));
        } else {
          unregister_code16(LALT(LGUI(LCTL(KC_RIGHT))));
        }  
      }  
      return false;
    case DUAL_FUNC_12:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LGUI(LSFT(KC_1)));
        } else {
          unregister_code16(LGUI(LSFT(KC_1)));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(LSFT(KC_2)));
        } else {
          unregister_code16(LGUI(LSFT(KC_2)));
        }  
      }  
      return false;
    case DUAL_FUNC_13:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LGUI(KC_F));
        } else {
          unregister_code16(LGUI(KC_F));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(LSFT(KC_F)));
        } else {
          unregister_code16(LGUI(LSFT(KC_F)));
        }  
      }  
      return false;
    case DUAL_FUNC_14:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(LGUI(KC_V));
        } else {
          unregister_code16(LGUI(KC_V));
        }
      } else {
        if (record->event.pressed) {
          register_code16(LGUI(LSFT(KC_V)));
        } else {
          unregister_code16(LGUI(LSFT(KC_V)));
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
  }
  return true;
}

void matrix_scan_user(void) { // The very important timer.
  if (is_alt_tab_active) {
    if (timer_elapsed(alt_tab_timer) > 2000) {
      unregister_code(KC_LALT);
      is_alt_tab_active = false;
    }
  }
  if (is_cmd_tab_active) {
    if (timer_elapsed(cmd_tab_timer) > 2000) {
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
      ergodox_right_led_3_on();
      break;
    case 4:
      ergodox_right_led_1_on();
      ergodox_right_led_2_on();
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
      SEND_STRING("macos");
      break;
    case 1:
      SEND_STRING("fortnite");
      break;
    case 2:
      SEND_STRING("minecraft");
      break;
    case 3:
      SEND_STRING("gaming");
      break;
    case 4:
      SEND_STRING("win");
      break;
    case 5:
      SEND_STRING("old_mac");
      break;
    case 6:
      SEND_STRING("shortcut");
      break;
    case 7:
      SEND_STRING("nav");
      break;
    case 8:
      SEND_STRING("num");
      break;
    case 9:
      SEND_STRING("func");
      break;
    case 10:
      SEND_STRING("mouse");
      break;
    case 11:
      SEND_STRING("layers");
      break;
    default:
      SEND_STRING("unknown");
      break;
  }
}

void leader_end_user(void) {
  if (leader_sequence_two_keys(KC_I, KC_D)) {
    send_current_layer_name();
  } else if (leader_sequence_three_keys(KC_Y, KC_S, KC_Q)) {
    SEND_STRING("Yours sincerely, QMK User");
  }
  /*} else if (leader_sequence_one_key(KC_C)) {
    register_code(KC_LGUI); // Windows key
    register_code(KC_R);    // R key
    unregister_code(KC_R);
    unregister_code(KC_LGUI);
    send_string("calc\n"); // Opens calculator
  }*/
}

bool get_permissive_hold(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {

        case LT(6, KC_BSPC):
        case LT(7, KC_DELETE):
        case LT(9, KC_ENTER):
        case LT(8, KC_SPACE):
            // Do not select the hold action when another key is tapped.
            return false;
        default:
            // Immediately select the hold action when another key is tapped.
            return true;
    }
}