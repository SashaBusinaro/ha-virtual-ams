# Virtual AMS — Filament Inventory Manager for Bambulab

[![Validate][validate-badge]][validate-url]
[![HACS Custom][hacs-badge]][hacs-url]
[![Release][release-badge]][release-url]
[![License][license-badge]][license-url]

[validate-badge]: https://img.shields.io/github/actions/workflow/status/SashaBusinaro/ha-virtual-ams/validate.yml?style=for-the-badge&label=Validate
[validate-url]: https://github.com/SashaBusinaro/ha-virtual-ams/actions/workflows/validate.yml
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white
[hacs-url]: https://www.hacs.xyz/docs/faq/custom_repositories/
[release-badge]: https://img.shields.io/github/v/release/SashaBusinaro/ha-virtual-ams?style=for-the-badge&color=blue
[release-url]: https://github.com/SashaBusinaro/ha-virtual-ams/releases
[license-badge]: https://img.shields.io/github/license/SashaBusinaro/ha-virtual-ams?style=for-the-badge
[license-url]: https://github.com/SashaBusinaro/ha-virtual-ams/blob/main/LICENSE

A Home Assistant custom integration that provides a virtual AMS (Automated Material System) experience for **Bambulab A1** and similar printers that don't have a physical AMS unit.

Virtual AMS tracks your filament spool inventory, automatically deducts filament weight after each successful print, and includes a dedicated Lovelace card for managing your stock from the dashboard.

> **Requires** the [ha-bambulab](https://github.com/greghesp/ha-bambulab) integration to be installed and configured first — it provides the printer sensors that Virtual AMS reads.

---

## Features

- **Automatic weight deduction** — filament usage is subtracted from the spool's remaining weight after every successful print
- **Lovelace card** — custom dashboard card included, auto-registered on setup (no manual resource configuration needed)
- **Full inventory management** — register, update and remove spools via HA services or directly from the card
- **Active spool tracking** — see at a glance which spool is loaded and how much filament remains
- **Color mapping** — Bambulab color hex values are resolved to human-friendly color names

## Requirements

- Home Assistant **2026.4** or newer
- [ha-bambulab](https://github.com/greghesp/ha-bambulab) integration (provides the printer sensors)
- [HACS](https://hacs.xyz) (recommended for installation)

---

## Installation

### Step 1: Install the Integration

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=SashaBusinaro&repository=ha-virtual-ams&category=integration)

Then:

1. Click "Download" to install the integration
2. **Restart Home Assistant** (required after installation)

> [!NOTE]
> The My Home Assistant redirect will first take you to a landing page. Click the button there to open your Home Assistant instance.

<details>
<summary><strong>Manual Installation (Advanced)</strong></summary>

If you prefer not to use HACS:

1. Download the latest release from the [releases page](https://github.com/SashaBusinaro/ha-virtual-ams/releases)
2. Copy the `custom_components/virtual_ams/` folder into your Home Assistant's `config/custom_components/` directory
3. Restart Home Assistant

</details>

### Step 2: Configure the Integration

**Important:** Complete Step 1 and restart Home Assistant before proceeding.

#### Option 1: One-Click Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=virtual_ams)

#### Option 2: Manual Setup

1. Go to **Settings → Devices & Services**
2. Click **"+ Add Integration"** and search for **Virtual AMS**
3. Select the three sensors provided by ha-bambulab for your printer:

   | Field | Example (A1) | Description |
   |---|---|---|
   | **Spool sensor** | `sensor.a1_external_spool` | Reports the loaded filament (name, color, material) |
   | **Print state sensor** | `sensor.a1_current_stage` | Reports the current print phase (`printing` / `idle`) |
   | **Print weight sensor** | `sensor.a1_print_weight` | Reports filament used in grams for the last print |

4. Click **Submit**. The Lovelace card is registered automatically.

To change sensors later, go to the integration page and click **Reconfigure**.

### Lovelace Card

The card is auto-registered on setup. To add it to a dashboard:

1. Edit your dashboard → **Add card**
2. Search for **Virtual AMS**
3. Select your Virtual AMS device from the picker

The card lets you view the active spool, register or update a spool, and manage your inventory — all without leaving the dashboard.

---

## Services

### `virtual_ams.register_spool`

Registers a new spool or overwrites an existing one. If `name` and `color_hex` are omitted, they are auto-detected from the spool currently loaded on the printer.

| Field | Required | Default | Description |
|---|---|---|---|
| `fingerprint` | No | auto | Spool identifier (`name_#COLORHEX`). Auto-detected if omitted. |
| `name` | No | auto | Raw spool name (e.g. `Bambu PLA Basic`). |
| `color_hex` | No | auto | Color in `#RRGGBBAA` format. |
| `material` | No | | Filament material (e.g. `PLA`, `PETG`). |
| `weight` | No | `1000` | Current weight in grams. |
| `initial_weight` | No | = `weight` | Full spool weight in grams. |
| `friendly_name` | No | auto | Custom display name. |

### `virtual_ams.update_spool`

Updates an existing spool's weight, material or display name. If `fingerprint` is omitted, the currently loaded spool is used.

| Field | Required | Description |
|---|---|---|
| `fingerprint` | No | Defaults to the currently loaded spool. |
| `weight` | No | New current weight in grams. |
| `initial_weight` | No | New full spool weight in grams. |
| `material` | No | Updated material. |
| `friendly_name` | No | Updated display name. |

### `virtual_ams.remove_spool`

Removes a spool from the inventory.

| Field | Required | Description |
|---|---|---|
| `fingerprint` | Yes | Spool identifier to remove (e.g. `Bambu PLA Basic_#FFFFFFFF`). |

---

## Entities

| Entity | State | Key Attributes |
|---|---|---|
| `sensor.virtual_ams_active_spool` | Display name of the loaded spool | `fingerprint`, `name`, `color_hex`, `material`, `weight`, `initial_weight`, `in_inventory` |
| `sensor.virtual_ams_inventory` | Count of spools in inventory | `spools` — full inventory dict keyed by fingerprint |

---

## How Fingerprints Work

Each spool is identified by a **fingerprint** in the format `{name}_{#COLORHEX}`, for example `Bambu PLA Basic_#FFFFFFFF`. This is derived automatically from the spool sensor's `name` and `color` attributes.

**Known limitation**: two physical spools of the same manufacturer, material, and color share the same fingerprint and cannot be tracked separately.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).
