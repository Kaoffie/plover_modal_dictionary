# Modal Dictionaries for Plover
[![PyPI](https://img.shields.io/pypi/v/plover-modal-dictionary)](https://pypi.org/project/plover-modal-dictionary/)
![GitHub](https://img.shields.io/github/license/Kaoffie/plover_modal_dictionary)

**Modal Dictionaries** are dictionaries that can switch two modes - activated and deactivated. Dictionary entries are hidden until they are activated by one of the configured activation strokes, after which they can be deactivated again under user-configured conditions.

It is useful if you would like to have dictionaries that:
- Turn on with an activation stroke, then turn off when you stroke something outside of the dictionary
- Turn on for one translation only

## Example

This dictionary allows the user to enter navigation mode using one of the entries in `entry`, after which any stroke in `dict` would return an arrow key or navigation key. The dictionary will exit if the user strokes anything outside of these entries.

Stroking `STPH-R/-R/-R/WORD` would, for instance, shift the text cursor 3 characters to the left, then write "word".

```json
{
    "exclude_entry": false,
    "exit_on_mismatch": true,
    "exit_on_match": false,
    "ignore_folding": true,

    "entry": {
        "STPH-R": "{#Left}{^}",
        "STPH-P": "{#Up}{^}",
        "STPH-B": "{#Down}{^}",
        "STPH-G": "{#Right}{^}",
        "STPH-RB": "{#Control_L(Left)}{^}",
        "STPH-BG": "{#Control_L(Right)}{^}"
    },
    
    "dict": {
        "-R": "{#Left}{^}",
        "-P": "{#Up}{^}",
        "-B": "{#Down}{^}",
        "-B/-G": "{#Down}{^}{#Right}{^}",
        "-G": "{#Right}{^}",
        "-RB": "{#Control_L(Left)}{^}",
        "-BG": "{#Control_L(Right)}{^}"
    }
}
```

`-B/-G` was included to override the outline for "being" in `main.json`.


## Setup

For the plugin to work properly, go into Configuration → Plugins and turn on `modal_update`.


## Usage

Modal dictionaries have the `.modal` extension and follow the following format (using JSON syntax):

```json
{
    "exclude_entry": false,
    "exit_on_mismatch": true,
    "exit_on_match": false,
    "ignore_folding": true,

    "entry": {
        "S": "translation 1",
        "T": "translation 2"
    },
    
    "dict": {
        "K": "translation 3",
        "P": "translation 4"
    },

    "exit": {
        "W": "translation 5",
        "H": "translation 6"
    }
}
```

Any of the `true/false` options can be omitted. They are used like so:

| Option | Default | Usage |
|---|---|---|
| `exclude_entry` | `false` | Whether to exclude entry strokes when activated. If set to `true`, entry strokes can still be used to enter activated mode as usual, but after activation, they are considered to be outside the dictionary. |
| `exit_on_mismatch` | `true` | Whether to deactivate when a stroke is not found in the dictionary. Note that if you have a translation for a multistroke outline such as `-F/-L`, but none of its prefixes (such as `-F`) are defined, stroking `-F` will deactivate it and write "of" as usual, and stroking `-L` will delete the "of" and reactivate the dictionary again. |
| `exit_on_match` | `false` | Whether to deactivate after translating a single entry. This is useful if you want the dictionary to be activated for only one word/translation. |
| `ignore_folding` | `true` | Whether to ignore folding. Whenever a stroke such as `-RG` is sent to Plover and no translation can be found, Plover will split it into `-R/-G` and search its dictionaries again. If set to `true`, we will ignore such attempts and consider the input stroke as outside of the dictionary, even if `-R` and `-G` are defined. |

The dictionary contains 3 sub-dictionaries. They can be omitted, and the dictionary will treat them as empty:

| Subdictionary | Usage |
|---|---|
| `entry` | Used to enter activated mode. These entries can be used when the dictionary is deactivated. |
| `dict` | Main dictionary entries, hidden until activated. |
| `exit` | Used to exit activated mode, hidden until activated. |

These dictionaries can be defined using the usual JSON format, like so:

```json
"entry": {
    "S": "translation 1",
    "T": "translation 2"
}
```

they can also just be references to other dictionary files with formats supported by your current Plover plugin setup:

```json
"entry": "some/other/dictionary.py"
```