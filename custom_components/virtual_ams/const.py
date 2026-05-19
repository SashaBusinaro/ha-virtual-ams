"""Constants for virtual_ams."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "virtual_ams"

CARD_URL_BASE = f"/{DOMAIN}"
CARD_FILENAME = "virtual-ams-card.js"
CARD_VERSION = "0.2.0"

CONF_SPOOL_SENSOR = "spool_sensor"
CONF_PRINT_STATE_SENSOR = "print_state_sensor"
CONF_PRINT_WEIGHT_SENSOR = "print_weight_sensor"

PRINT_STATE_PRINTING = "printing"
PRINT_STATE_IDLE = "idle"

STORAGE_KEY = DOMAIN
STORAGE_VERSION = 1

# Spool data attribute keys
ATTR_FINGERPRINT = "fingerprint"
ATTR_NAME = "name"
ATTR_COLOR_HEX = "color_hex"
ATTR_FRIENDLY_COLOR = "friendly_color"
ATTR_FRIENDLY_NAME = "friendly_name"
# Display name as exposed on the active_spool sensor attributes.
# Cannot reuse "friendly_name" because HA overrides it with the entity name.
ATTR_DISPLAY_NAME = "display_name"
ATTR_MATERIAL = "material"
ATTR_WEIGHT = "weight"
ATTR_INITIAL_WEIGHT = "initial_weight"
ATTR_IN_INVENTORY = "in_inventory"
ATTR_LAST_USED = "last_used"
ATTR_SPOOLS = "spools"

# Bambulab color map: normalized hex (with #, uppercase, RRGGBBAA) -> friendly name
COLOR_MAP: dict[str, str] = {
    "#FFFFFFFF": "Jade White",
    "#CBC6B8FF": "Bone White",
    "#E8DBB7FF": "Desert Tan",
    "#D3B7A7FF": "Latte Brown",
    "#AE835BFF": "Caramel",
    "#B15533FF": "Terracotta",
    "#7D6556FF": "Dark Brown",
    "#4D3324FF": "Dark Chocolate",
    "#AE96D4FF": "Lilac Purple",
    "#E8AFCFFF": "Sakura Pink",
    "#F99963FF": "Mandarin Orange",
    "#F7D959FF": "Lemon Yellow",
    "#950051FF": "Plum",
    "#DE4343FF": "Scarlet Red",
    "#BB3D43FF": "Dark Red",
    "#68724DFF": "Dark Green",
    "#61C680FF": "Grass Green",
    "#C2E189FF": "Apple Green",
    "#A3D8E1FF": "Ice Blue",
    "#56B7E6FF": "Sky Blue",
    "#0078BFFF": "Marine Blue",
    "#042F56FF": "Dark Blue",
    "#9B9EA0FF": "Ash Gray",
    "#757575FF": "Nardo Gray",
    "#000000FF": "Black",
    "#EC008CFF": "Magenta",
    "#E4BD68FF": "Gold",
    "#3F8E43FF": "Mistletoe Green",
    "#C12E1FFF": "Red",
    "#5E43B7FF": "Purple",
    "#F7E6DEFF": "Beige",
    "#F55A74FF": "Pink",
    "#FEC600FF": "Sunflower Yellow",
    "#847D48FF": "Bronze",
    "#00B1B7FF": "Turquoise",
    "#482960FF": "Indigo Purple",
    "#D1D3D5FF": "Light Gray",
    "#F5547CFF": "Hot Pink",
    "#F4EE2AFF": "Yellow",
    "#6F5034FF": "Cocoa Brown",
    "#0086D6FF": "Cyan",
    "#5B6579FF": "Blue Grey",
    "#A6A9AAFF": "Silver",
    "#FF6A13FF": "Orange",
    "#BECF00FF": "Bright Green",
    "#9D432CFF": "Brown",
    "#0A2989FF": "Blue",
    "#545454FF": "Dark Gray",
    "#8E9089FF": "Gray",
    "#FF9016FF": "Pumpkin Orange",
    "#00AE42FF": "Bambu Green",
    "#9D2235FF": "Maroon Red",
    "#0056B8FF": "Cobalt Blue",
    "#8E8E8EFF": "Translucent Gray",
    "#61B0FFFF": "Translucent Light Blue",
    "#748C45FF": "Translucent Olive",
    "#C9A381FF": "Translucent Brown",
    "#77EDD7FF": "Translucent Teal",
    "#FF911AFF": "Translucent Orange",
    "#D6ABFFFF": "Translucent Purple",
    "#F9C1BDFF": "Translucent Pink",
}
