# ZMK Layer Identification Behavior

A custom ZMK behavior that sends the current layer name as typed text, similar to QMK's layer identification functionality.

## Features

- Uses `zmk_keymap_highest_layer_active()` to dynamically detect the current layer
- Configurable layer names through devicetree properties
- Configurable prefix string (defaults to "L: ")
- Can be triggered by key press or leader sequence

## Usage

### Basic Setup

Add the behavior to your keymap:

```dts
/ {
    behaviors {
        layer_id: layer_id {
            compatible = "zmk,behavior-layer-id";
            #binding-cells = <0>;
            layer-names = "base", "nav", "num", "func";  // Your layer names
            prefix = "Layer: ";  // Optional custom prefix
        };
    };
};
```

### Configuration Properties

#### `layer-names` (required)
Array of strings representing your layer names. The array index corresponds to the layer number.

```dts
layer-names = "base", "lower", "raise", "adjust";
```

#### `prefix` (optional)
String to send before the layer name. Defaults to "L: ".

```dts
prefix = "Current Layer: ";
prefix = "";  // No prefix
```

### Using in Keymap

#### Direct Key Binding
```dts
&kp ESC  &layer_id  &kp TAB
```

#### Leader Key Sequence
```dts
leader_key: leader_key {
    compatible = "zmk,behavior-leader-key";
    #binding-cells = <0>;
    timeout-ms = <1000>;
    id { sequence = <I D>; bindings = <&layer_id>; };
};
```

## Examples

### Example 1: Simple Setup
```dts
layer_id: layer_id {
    compatible = "zmk,behavior-layer-id";
    #binding-cells = <0>;
    layer-names = "qwerty", "colemak", "gaming";
};
```
- Layer 0 → types "L: qwerty"
- Layer 1 → types "L: colemak" 
- Layer 2 → types "L: gaming"

### Example 2: Custom Prefix
```dts
layer_id: layer_id {
    compatible = "zmk,behavior-layer-id";
    #binding-cells = <0>;
    layer-names = "base", "nav", "num", "sym";
    prefix = "Current: ";
};
```
- Layer 0 → types "Current: base"
- Layer 1 → types "Current: nav"

### Example 3: No Prefix
```dts
layer_id: layer_id {
    compatible = "zmk,behavior-layer-id";
    #binding-cells = <0>;
    layer-names = "DEFAULT", "LOWER", "RAISE", "ADJUST";
    prefix = "";
};
```
- Layer 0 → types "DEFAULT"
- Layer 1 → types "LOWER"

## Installation

1. Copy the behavior files to your ZMK config:
   - `dts/bindings/behaviors/zmk,behavior-layer-id.yaml`
   - `src/behaviors/behavior_layer_id.c`
   - `dts/behaviors/layer_id.dtsi` (optional, for convenience)

2. Add to your `CMakeLists.txt`:
   ```cmake
   target_sources(app PRIVATE src/behaviors/behavior_layer_id.c)
   ```

3. Include in your keymap:
   ```dts
   #include "behaviors/layer_id.dtsi"  // If using the convenience file
   ```

## Character Support

The behavior supports:
- Lowercase letters (a-z)
- Uppercase letters (A-Z) 
- Numbers (0-9)
- Space, colon (:), underscore (_)

Unknown characters are skipped silently.

## Contributing

Feel free to extend character support or add additional features! This behavior is designed to be easily customizable and reusable.