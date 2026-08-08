#define FLOW_TAP_TERM 150
#define CHORDAL_HOLD
#undef DEBOUNCE
#define DEBOUNCE 5

#undef TAPPING_TERM
#define TAPPING_TERM 185

#define ONESHOT_TAP_TOGGLE 3

#undef ONESHOT_TIMEOUT
#define ONESHOT_TIMEOUT 1000

#define PERMISSIVE_HOLD

#define USB_SUSPEND_WAKEUP_DELAY 0
#define SERIAL_NUMBER "DYrAK/6aRpJL"
#define LAYER_STATE_16BIT
#define COMBO_COUNT 13

#define TAPPING_TERM_PER_KEY














/* Custom QMK Features */
#define LEADER_TIMEOUT 750
#define LEADER_PER_KEY_TIMING
#define LEADER_NO_TIMEOUT
#define PERMISSIVE_HOLD_PER_KEY

/* Required for combo_should_trigger() to be consulted at all: process_combo.c
   only calls it inside #ifdef COMBO_SHOULD_TRIGGER. Without this the Mac and
   Windows variants of the reopen-tab and tabs-list chords both fire. */
#define COMBO_SHOULD_TRIGGER

/* Workaround for an upstream ZSA bug in zsa/qmk_modules (oryx/oryx.c).
   The module guards <automouse.h> with `#if COMMUNITY_MODULE_AUTOMOUSE_ENABLE == TRUE`.
   AVR/LUFA never defines TRUE, so on the m32u4 that collapses to 0 == 0 and pulls in a
   header that is not on the include path. ARM builds escape it because ChibiOS defines
   TRUE. Remove once ZSA switches the guard to `#if defined(...)`. */
#ifndef TRUE
#    define TRUE 1
#endif
#ifndef FALSE
#    define FALSE 0
#endif