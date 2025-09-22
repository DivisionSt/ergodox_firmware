/*
 * Copyright (c) 2025 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

#define DT_DRV_COMPAT zmk_behavior_layer_id

#include <zephyr/device.h>
#include <drivers/behavior.h>
#include <zephyr/logging/log.h>

#include <zmk/behavior.h>
#include <zmk/keymap.h>
#include <zmk/hid.h>
#include <zmk/endpoints.h>

LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

#if DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT)

// Configuration struct to hold instance-specific data
struct behavior_layer_id_config {
    const char **layer_names;
    size_t layer_names_len;
    const char *prefix;
};

static void send_string(const char* str) {
    for (int i = 0; str[i] != '\0'; i++) {
        char c = str[i];
        uint16_t keycode = 0;
        uint8_t modifiers = 0;
        
        // Convert character to HID keycode
        if (c >= 'a' && c <= 'z') {
            keycode = HID_USAGE_KEY_KEYBOARD_A + (c - 'a');
        } else if (c >= 'A' && c <= 'Z') {
            keycode = HID_USAGE_KEY_KEYBOARD_A + (c - 'A');
            modifiers = MOD_LSFT;
        } else if (c >= '0' && c <= '9') {
            keycode = HID_USAGE_KEY_KEYBOARD_1_AND_EXCLAMATION + (c - '1');
            if (c == '0') {
                keycode = HID_USAGE_KEY_KEYBOARD_0_AND_RIGHT_PARENTHESIS;
            }
        } else {
            // Handle special characters
            switch (c) {
                case ' ':
                    keycode = HID_USAGE_KEY_KEYBOARD_SPACEBAR;
                    break;
                case ':':
                    keycode = HID_USAGE_KEY_KEYBOARD_SEMICOLON_AND_COLON;
                    modifiers = MOD_LSFT;
                    break;
                case '_':
                    keycode = HID_USAGE_KEY_KEYBOARD_MINUS_AND_UNDERSCORE;
                    modifiers = MOD_LSFT;
                    break;
                default:
                    continue; // Skip unknown characters
            }
        }
        
        // Send key press
        if (keycode != 0) {
            zmk_hid_keyboard_press(keycode);
            if (modifiers != 0) {
                zmk_hid_keyboard_modifiers_press(modifiers);
            }
            zmk_endpoints_send_report(HID_USAGE_KEYBOARD);
            
            // Send key release
            if (modifiers != 0) {
                zmk_hid_keyboard_modifiers_release(modifiers);
            }
            zmk_hid_keyboard_release(keycode);
            zmk_endpoints_send_report(HID_USAGE_KEYBOARD);
        }
        
        // Small delay between characters
        k_msleep(10);
    }
}

static int on_layer_id_binding_pressed(struct zmk_behavior_binding *binding,
                                      struct zmk_behavior_binding_event event) {
    // Get device and configuration
    const struct device *dev = zmk_behavior_get_binding(binding->behavior_dev);
    const struct behavior_layer_id_config *config = dev->config;
    
    // Get the highest active layer
    uint8_t layer = zmk_keymap_highest_layer_active();
    
    LOG_DBG("Layer ID pressed, current layer: %d", layer);
    
    // Send prefix
    send_string(config->prefix);
    
    // Send layer name
    if (layer < config->layer_names_len && config->layer_names[layer] != NULL) {
        send_string(config->layer_names[layer]);
    } else {
        send_string("unknown");
    }
    
    return ZMK_BEHAVIOR_OPAQUE;
}

static int on_layer_id_binding_released(struct zmk_behavior_binding *binding,
                                       struct zmk_behavior_binding_event event) {
    return ZMK_BEHAVIOR_OPAQUE;
}

static const struct behavior_driver_api behavior_layer_id_driver_api = {
    .binding_pressed = on_layer_id_binding_pressed,
    .binding_released = on_layer_id_binding_released,
    .locality = BEHAVIOR_LOCALITY_CENTRAL,
};

// Macro to create instances with configuration
#define LAYER_ID_INST(n)                                                                          \
    static const char *const layer_names_##n[] = DT_INST_PROP(n, layer_names);                   \
    static const struct behavior_layer_id_config behavior_layer_id_config_##n = {                \
        .layer_names = layer_names_##n,                                                           \
        .layer_names_len = DT_INST_PROP_LEN(n, layer_names),                                      \
        .prefix = DT_INST_PROP(n, prefix),                                                        \
    };                                                                                             \
    BEHAVIOR_DT_INST_DEFINE(n, NULL, NULL, NULL, &behavior_layer_id_config_##n, POST_KERNEL,     \
                            CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &behavior_layer_id_driver_api);

DT_INST_FOREACH_STATUS_OKAY(LAYER_ID_INST)

#endif /* DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT) */