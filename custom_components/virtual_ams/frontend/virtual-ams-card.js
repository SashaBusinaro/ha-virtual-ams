// Virtual AMS Lovelace Card
// Manage your Bambulab filament inventory directly from the dashboard.
//
// Card config:
//   type: custom:virtual-ams-card
//   device_id: <device id>             # set via the visual editor (ha-form device picker)
//   active_spool_entity: sensor.xxx    # optional manual override
//   inventory_entity: sensor.xxx       # optional manual override

const _DOMAIN = "virtual_ams";
const DEFAULT_ACTIVE_SPOOL_ENTITY = "sensor.virtual_ams_active_spool";
const DEFAULT_INVENTORY_ENTITY = "sensor.virtual_ams_inventory";

// Schema for ha-form: single device selector filtered to virtual_ams integration.
const EDITOR_SCHEMA = [
  {
    name: "device_id",
    label: "Virtual AMS",
    selector: {
      device: {
        filter: [{ integration: _DOMAIN }],
      },
    },
  },
];

// ─── Translations ─────────────────────────────────────────────────────────────

const TRANSLATIONS = {
  en: {
    not_configured: "No Virtual AMS integration found.<br>Edit the card and select a device.",
    loaded_spool: "Loaded spool",
    inventory: "Inventory",
    spool_singular: "spool",
    spool_plural: "spools",
    no_inventory: "No spools in inventory.<br>Load a spool on the printer and register it.",
    no_spool_detected: "No spool detected on sensor.",
    not_in_inventory: "Not in inventory",
    register_spool: "Register current spool",
    update_spool: "Update current spool",
    form_register_title: "Register spool",
    form_edit_title: "Edit spool",
    material_label: "Material",
    material_placeholder: "PLA, PETG, ABS…",
    weight_label: "Current weight (g)",
    initial_weight_label: "Initial weight (g)",
    friendly_name_label: "Display name (optional)",
    friendly_name_placeholder: "e.g. My white PLA",
    cancel: "Cancel",
    save_register: "Register",
    save_update: "Update",
    edit_title: "Edit",
    delete_title: "Delete",
    unknown_spool: "Unknown",
    delete_confirm: (name) => `Remove "${name}" from inventory?`,
    error_msg: (msg) => `Error: ${msg}`,
    description: "Manage your Bambulab filament inventory",
  },
  it: {
    not_configured: "Nessuna integrazione Virtual AMS trovata.<br>Modifica la card e seleziona un dispositivo.",
    loaded_spool: "Bobina caricata",
    inventory: "Inventario",
    spool_singular: "bobina",
    spool_plural: "bobine",
    no_inventory: "Nessuna bobina in inventario.<br>Carica una bobina sulla stampante e registrala.",
    no_spool_detected: "Nessuna bobina rilevata sul sensore.",
    not_in_inventory: "Non in inventario",
    register_spool: "Registra bobina attuale",
    update_spool: "Aggiorna bobina attuale",
    form_register_title: "Registra bobina",
    form_edit_title: "Modifica bobina",
    material_label: "Materiale",
    material_placeholder: "PLA, PETG, ABS…",
    weight_label: "Peso attuale (g)",
    initial_weight_label: "Peso iniziale (g)",
    friendly_name_label: "Nome visualizzato (opzionale)",
    friendly_name_placeholder: "Es. La mia PLA bianca",
    cancel: "Annulla",
    save_register: "Registra",
    save_update: "Aggiorna",
    edit_title: "Modifica",
    delete_title: "Elimina",
    unknown_spool: "Sconosciuta",
    delete_confirm: (name) => `Rimuovere "${name}" dall'inventario?`,
    error_msg: (msg) => `Errore: ${msg}`,
    description: "Gestisci il tuo inventario filamenti Bambulab",
  },
};

function hexToRgba(hex) {
  if (!hex) return "rgba(128,128,128,1)";
  const clean = hex.replace("#", "");
  if (clean.length < 6) return "rgba(128,128,128,1)";
  const r = parseInt(clean.substr(0, 2), 16);
  const g = parseInt(clean.substr(2, 2), 16);
  const b = parseInt(clean.substr(4, 2), 16);
  const a = clean.length >= 8 ? (parseInt(clean.substr(6, 2), 16) / 255).toFixed(2) : "1";
  return `rgba(${r},${g},${b},${a})`;
}

function weightBarColor(pct) {
  if (pct > 50) return "var(--success-color, #4caf50)";
  if (pct > 20) return "var(--warning-color, #ff9800)";
  return "var(--error-color, #f44336)";
}

// ─── Card Editor ─────────────────────────────────────────────────────────────
//
// Uses HA's native ha-form element with a device selector.
// ha-form handles rendering; we only wire up properties and events.

class VirtualAmsCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._formAttached = false;
  }

  setConfig(config) {
    this._config = config || {};
    this._updateForm();
  }

  set hass(hass) {
    this._hass = hass;
    this._updateForm();
  }

  _updateForm() {
    if (!this._hass) return;

    // Create ha-form once, then update its properties in place.
    if (!this._formAttached) {
      this.shadowRoot.innerHTML = `<ha-form></ha-form>`;
      const form = this.shadowRoot.querySelector("ha-form");
      form.addEventListener("value-changed", (ev) => {
        this._emitConfig(ev.detail.value);
      });
      this._formAttached = true;
    }

    const form = this.shadowRoot.querySelector("ha-form");
    form.hass = this._hass;
    form.data = this._config;
    form.schema = EDITOR_SCHEMA;
    form.computeLabel = (s) => s.label;
  }

  _emitConfig(config) {
    const event = new Event("config-changed", { bubbles: true, composed: true });
    event.detail = { config };
    this.dispatchEvent(event);
  }
}

customElements.define("virtual-ams-card-editor", VirtualAmsCardEditor);

// ─── Card Styles ──────────────────────────────────────────────────────────────

const STYLES = `
  :host { display: block; }
  ha-card { padding: 16px 16px 20px; }

  /* Header */
  .card-header { display: flex; align-items: center; gap: 8px; padding-bottom: 12px; }
  .card-header ha-icon { --mdc-icon-size: 22px; color: var(--primary-color); }
  .card-title { font-size: 1.1em; font-weight: 600; color: var(--primary-text-color); }

  /* Active spool */
  .active-section { margin-bottom: 14px; }
  .section-label {
    font-size: 0.73em; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--secondary-text-color);
    margin-bottom: 8px;
  }
  .active-card {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 14px; border-radius: 10px;
    background: var(--secondary-background-color);
  }
  .color-circle {
    width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0;
    border: 2px solid var(--divider-color);
    background: var(--secondary-background-color);
  }
  .spool-info { flex: 1; min-width: 0; }
  .spool-name {
    font-size: 0.95em; font-weight: 500;
    color: var(--primary-text-color);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .spool-meta { font-size: 0.8em; color: var(--secondary-text-color); margin-top: 2px; }
  .weight-wrap { margin-top: 7px; }
  .weight-bar {
    height: 5px; background: var(--divider-color);
    border-radius: 3px; overflow: hidden;
  }
  .weight-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
  .weight-label { font-size: 0.78em; color: var(--secondary-text-color); margin-top: 3px; }
  .badge-warning {
    display: inline-block; margin-top: 4px; padding: 2px 8px;
    border-radius: 4px; font-size: 0.75em; font-weight: 500;
    background: rgba(var(--rgb-warning-color, 255,152,0), 0.15);
    color: var(--warning-color, #ff9800);
  }
  .no-spool {
    text-align: center; padding: 16px;
    color: var(--secondary-text-color); font-size: 0.9em;
  }

  /* Register button */
  .register-row { margin-bottom: 14px; }
  .btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 8px; border: none;
    cursor: pointer; font-size: 0.88em; font-family: inherit;
    font-weight: 500; transition: filter 0.15s;
  }
  .btn:hover { filter: brightness(1.1); }
  .btn-primary { background: var(--primary-color); color: var(--text-primary-color, #fff); }
  .btn-secondary {
    background: var(--secondary-background-color);
    color: var(--primary-text-color);
    border: 1px solid var(--divider-color);
  }
  .btn ha-icon { --mdc-icon-size: 16px; }

  /* Inline form */
  .form-card {
    background: var(--card-background-color);
    border: 1px solid var(--divider-color);
    border-radius: 10px; padding: 14px; margin-bottom: 14px;
  }
  .form-title { font-size: 0.88em; font-weight: 600; color: var(--primary-text-color); margin-bottom: 12px; }
  .form-info { font-size: 0.82em; color: var(--secondary-text-color); margin-bottom: 12px; }
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .form-group { display: flex; flex-direction: column; gap: 4px; }
  .form-group.full { grid-column: 1 / -1; }
  .form-label { font-size: 0.78em; color: var(--secondary-text-color); font-weight: 500; }
  .form-input {
    padding: 7px 10px; border-radius: 6px;
    border: 1px solid var(--divider-color);
    background: var(--secondary-background-color);
    color: var(--primary-text-color);
    font-family: inherit; font-size: 0.88em;
    box-sizing: border-box; width: 100%;
  }
  .form-input:focus { outline: none; border-color: var(--primary-color); }
  .form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px; }

  /* Divider */
  .divider { height: 1px; background: var(--divider-color); margin: 14px 0; }

  /* Inventory list */
  .inv-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
  }
  .inv-list { display: flex; flex-direction: column; gap: 7px; }
  .inv-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 8px;
    border: 1px solid var(--divider-color);
    transition: border-color 0.2s;
  }
  .inv-item.active {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3,169,244), 0.06);
  }
  .color-dot {
    width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0;
    border: 1px solid var(--divider-color);
  }
  .inv-info { flex: 1; min-width: 0; }
  .inv-name {
    font-size: 0.88em; font-weight: 500; color: var(--primary-text-color);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .inv-weight { font-size: 0.78em; color: var(--secondary-text-color); margin-top: 1px; }
  .inv-mini-bar { margin-top: 4px; }
  .inv-mini-bar .weight-bar { height: 3px; }
  .item-actions { display: flex; gap: 2px; flex-shrink: 0; }
  .icon-btn {
    background: none; border: none; cursor: pointer;
    color: var(--secondary-text-color); padding: 5px; border-radius: 6px;
    display: flex; align-items: center; transition: background 0.15s, color 0.15s;
  }
  .icon-btn:hover { background: var(--secondary-background-color); color: var(--primary-text-color); }
  .icon-btn.danger:hover { background: var(--error-color, #f44336); color: #fff; }
  .icon-btn ha-icon { --mdc-icon-size: 17px; }
  .empty-inv {
    text-align: center; padding: 20px;
    color: var(--secondary-text-color); font-size: 0.88em;
  }

  /* Not configured notice */
  .not-configured {
    padding: 16px; text-align: center;
    color: var(--secondary-text-color); font-size: 0.88em;
  }
`;

// ─── Card ─────────────────────────────────────────────────────────────────────

class VirtualAmsCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("virtual-ams-card-editor");
  }

  static getStubConfig() {
    return {};
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._formMode = null; // null | "register" | "edit"
    this._editFingerprint = null;
    this._formData = {};
  }

  setConfig(config) {
    this._config = config;
  }

  getCardSize() { return 4; }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;
    // Only re-render on first paint or when our sensors actually change state,
    // to avoid destroying form focus and causing flicker on unrelated updates.
    if (!oldHass) {
      this._render();
      return;
    }
    const activeId = this._activeSpoolEntity();
    const inventoryId = this._inventoryEntity();
    if (
      oldHass.states[activeId] !== hass.states[activeId] ||
      oldHass.states[inventoryId] !== hass.states[inventoryId]
    ) {
      this._render();
    }
  }

  // ──────────────────────────────────────────────
  // Localization
  // ──────────────────────────────────────────────

  _t(key) {
    const lang = (this._hass?.locale?.language || "en").split("-")[0];
    const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
    return dict[key] ?? TRANSLATIONS.en[key] ?? key;
  }

  // ──────────────────────────────────────────────
  // Entity resolution
  // ──────────────────────────────────────────────

  // Finds the entity_id matching a translation_key within the configured device.
  // Falls back to any matching virtual_ams entity if no device_id is set.
  _resolveEntity(translationKey) {
    if (!this._hass?.entities) return null;
    const deviceId = this._config.device_id;
    for (const entity of Object.values(this._hass.entities)) {
      if (entity.platform !== _DOMAIN) continue;
      if (entity.translation_key !== translationKey) continue;
      if (deviceId && entity.device_id !== deviceId) continue;
      return entity.entity_id;
    }
    return null;
  }

  _activeSpoolEntity() {
    if (this._config.active_spool_entity) return this._config.active_spool_entity;
    return this._resolveEntity("active_spool") || DEFAULT_ACTIVE_SPOOL_ENTITY;
  }

  _inventoryEntity() {
    if (this._config.inventory_entity) return this._config.inventory_entity;
    return this._resolveEntity("inventory") || DEFAULT_INVENTORY_ENTITY;
  }

  // ──────────────────────────────────────────────
  // Data helpers
  // ──────────────────────────────────────────────

  _getActiveSpool() {
    const state = this._hass.states[this._activeSpoolEntity()];
    if (!state) return null;
    return {
      ...state.attributes,
      display_name: state.attributes.display_name || state.state,
    };
  }

  _getInventory() {
    const state = this._hass.states[this._inventoryEntity()];
    return state?.attributes?.spools || {};
  }

  _weightPct(weight, initial) {
    if (!initial || initial <= 0) return 0;
    return Math.min(100, Math.max(0, (weight / initial) * 100));
  }

  // ──────────────────────────────────────────────
  // Rendering
  // ──────────────────────────────────────────────

  _render() {
    if (!this._hass) return;

    // Show a notice if no device is configured and auto-discovery found nothing.
    if (!this._config.device_id && !this._config.active_spool_entity) {
      if (!this._resolveEntity("active_spool")) {
        this.shadowRoot.innerHTML = `
          <style>${STYLES}</style>
          <ha-card>
            <div class="card-header">
              <ha-icon icon="mdi:printer-3d-nozzle-outline"></ha-icon>
              <span class="card-title">Virtual AMS</span>
            </div>
            <div class="not-configured">
              ${this._t("not_configured")}
            </div>
          </ha-card>
        `;
        return;
      }
    }

    const active = this._getActiveSpool();
    const inventory = this._getInventory();
    const inventoryList = Object.values(inventory);
    const activeFingerprint = active?.fingerprint;

    const root = this.shadowRoot;
    root.innerHTML = `<style>${STYLES}</style>${this._buildHtml(active, inventoryList, activeFingerprint)}`;
    this._attachListeners();
  }

  _buildHtml(active, inventoryList, activeFingerprint) {
    const count = inventoryList.length;
    const spoolWord = count === 1 ? this._t("spool_singular") : this._t("spool_plural");
    return `
      <ha-card>
        <div class="card-header">
          <ha-icon icon="mdi:printer-3d-nozzle-outline"></ha-icon>
          <span class="card-title">Virtual AMS</span>
        </div>

        <!-- Active spool -->
        <div class="active-section">
          <div class="section-label">${this._t("loaded_spool")}</div>
          ${this._buildActiveSpool(active)}
        </div>

        <!-- Register / edit form or register button -->
        ${this._buildFormOrButton(active)}

        <div class="divider"></div>

        <!-- Inventory -->
        <div class="inv-header">
          <span class="section-label" style="margin:0">
            ${this._t("inventory")} (${count} ${spoolWord})
          </span>
        </div>
        ${count === 0
          ? `<div class="empty-inv">${this._t("no_inventory")}</div>`
          : `<div class="inv-list">${inventoryList.map(s => this._buildInventoryItem(s, s.fingerprint === activeFingerprint)).join("")}</div>`
        }
      </ha-card>
    `;
  }

  _buildActiveSpool(active) {
    if (!active || !active.fingerprint) {
      return `<div class="no-spool">${this._t("no_spool_detected")}</div>`;
    }
    const pct = this._weightPct(active.weight, active.initial_weight);
    const fillColor = weightBarColor(pct);
    const matMeta = [active.material, active.color_hex].filter(Boolean).join(" · ");
    return `
      <div class="active-card">
        <div class="color-circle" style="background:${hexToRgba(active.color_hex)}"></div>
        <div class="spool-info">
          <div class="spool-name">${this._esc(active.display_name || active.name || this._t("unknown_spool"))}</div>
          <div class="spool-meta">${this._esc(matMeta)}</div>
          ${active.in_inventory ? `
            <div class="weight-wrap">
              <div class="weight-bar">
                <div class="weight-fill" style="width:${pct.toFixed(1)}%;background:${fillColor}"></div>
              </div>
              <div class="weight-label">${active.weight}g / ${active.initial_weight}g (${Math.round(pct)}%)</div>
            </div>
          ` : `<span class="badge-warning">${this._t("not_in_inventory")}</span>`}
        </div>
      </div>
    `;
  }

  _buildFormOrButton(active) {
    if (this._formMode === "register") {
      return this._buildForm("register", active);
    }
    if (this._formMode === "edit" && this._editFingerprint) {
      const inventory = this._getInventory();
      const spool = inventory[this._editFingerprint];
      return this._buildForm("edit", spool);
    }
    if (!active || !active.fingerprint) return "";
    const btnLabel = active.in_inventory ? this._t("update_spool") : this._t("register_spool");
    return `
      <div class="register-row">
        <button class="btn btn-primary" id="btn-open-register">
          <ha-icon icon="mdi:plus-circle-outline"></ha-icon>${btnLabel}
        </button>
      </div>
    `;
  }

  _buildForm(mode, spool) {
    const isEdit = mode === "edit";
    const fd = this._formData;
    const name = fd.name ?? spool?.name ?? "";
    const material = fd.material ?? spool?.material ?? "";
    const weight = fd.weight ?? (isEdit ? (spool?.weight || 1000) : (spool?.in_inventory ? spool?.weight || 1000 : 1000));
    const initialWeight = fd.initialWeight ?? (spool?.initial_weight || 1000);
    const friendlyName = fd.friendlyName ?? (isEdit ? (spool?.friendly_name ?? "") : "");
    const colorHex = spool?.color_hex ?? "";
    const colorRgba = hexToRgba(colorHex);

    return `
      <div class="form-card">
        <div class="form-title">${isEdit ? this._t("form_edit_title") : this._t("form_register_title")}</div>
        ${colorHex ? `<div class="form-info">
          <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${colorRgba};vertical-align:middle;margin-right:6px;border:1px solid var(--divider-color)"></span>
          <strong>${this._esc(spool?.friendly_name || spool?.display_name || spool?.name || name)}</strong> &mdash; ${this._esc(colorHex)}
        </div>` : ""}
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">${this._t("material_label")}</label>
            <input class="form-input" id="f-material" value="${this._esc(String(material))}" placeholder="${this._t("material_placeholder")}">
          </div>
          <div class="form-group">
            <label class="form-label">${this._t("weight_label")}</label>
            <input class="form-input" type="number" id="f-weight" value="${weight}" min="0" max="9999" step="1">
          </div>
          ${!isEdit ? `
          <div class="form-group">
            <label class="form-label">${this._t("initial_weight_label")}</label>
            <input class="form-input" type="number" id="f-initial-weight" value="${initialWeight}" min="0" max="9999" step="1">
          </div>
          ` : ""}
          <div class="form-group ${!isEdit ? "" : "full"}">
            <label class="form-label">${this._t("friendly_name_label")}</label>
            <input class="form-input" id="f-friendly-name" value="${this._esc(String(friendlyName))}" placeholder="${this._t("friendly_name_placeholder")}">
          </div>
        </div>
        <div class="form-actions">
          <button class="btn btn-secondary" id="btn-cancel">${this._t("cancel")}</button>
          <button class="btn btn-primary" id="btn-save">
            <ha-icon icon="mdi:content-save-outline"></ha-icon>
            ${isEdit ? this._t("save_update") : this._t("save_register")}
          </button>
        </div>
      </div>
    `;
  }

  _buildInventoryItem(spool, isActive) {
    const pct = this._weightPct(spool.weight, spool.initial_weight);
    const fillColor = weightBarColor(pct);
    return `
      <div class="inv-item ${isActive ? "active" : ""}">
        <div class="color-dot" style="background:${hexToRgba(spool.color_hex)}"></div>
        <div class="inv-info">
          <div class="inv-name">${this._esc(spool.friendly_name || spool.name)}</div>
          <div class="inv-weight">${this._esc(spool.material || "")} · ${spool.weight}g / ${spool.initial_weight}g (${Math.round(pct)}%)</div>
          <div class="inv-mini-bar">
            <div class="weight-bar">
              <div class="weight-fill" style="width:${pct.toFixed(1)}%;background:${fillColor}"></div>
            </div>
          </div>
        </div>
        <div class="item-actions">
          <button class="icon-btn" data-action="edit" data-fp="${this._esc(spool.fingerprint)}" title="${this._t("edit_title")}">
            <ha-icon icon="mdi:pencil-outline"></ha-icon>
          </button>
          <button class="icon-btn danger" data-action="delete" data-fp="${this._esc(spool.fingerprint)}" title="${this._t("delete_title")}">
            <ha-icon icon="mdi:delete-outline"></ha-icon>
          </button>
        </div>
      </div>
    `;
  }

  // ──────────────────────────────────────────────
  // Event listeners
  // ──────────────────────────────────────────────

  _attachListeners() {
    const root = this.shadowRoot;

    root.getElementById("btn-open-register")?.addEventListener("click", () => {
      this._formMode = "register";
      this._editFingerprint = null;
      this._formData = {};
      this._render();
    });

    root.getElementById("btn-cancel")?.addEventListener("click", () => {
      this._formMode = null;
      this._editFingerprint = null;
      this._formData = {};
      this._render();
    });

    root.getElementById("btn-save")?.addEventListener("click", () => this._handleSave());

    root.querySelectorAll("[data-action='edit']").forEach(btn => {
      btn.addEventListener("click", () => {
        this._formMode = "edit";
        this._editFingerprint = btn.dataset.fp;
        this._formData = {};
        this._render();
      });
    });

    root.querySelectorAll("[data-action='delete']").forEach(btn => {
      btn.addEventListener("click", () => this._handleDelete(btn.dataset.fp));
    });

    // Preserve form data across hass updates while form is open
    ["f-material", "f-weight", "f-initial-weight", "f-friendly-name"].forEach(id => {
      const el = root.getElementById(id);
      if (el) {
        el.addEventListener("input", () => {
          if (id === "f-material") this._formData.material = el.value;
          else if (id === "f-weight") this._formData.weight = el.value;
          else if (id === "f-initial-weight") this._formData.initialWeight = el.value;
          else if (id === "f-friendly-name") this._formData.friendlyName = el.value;
        });
      }
    });
  }

  async _handleSave() {
    const root = this.shadowRoot;
    const material = root.getElementById("f-material")?.value?.trim() || "";
    const weight = parseFloat(root.getElementById("f-weight")?.value || "1000");
    const friendlyName = root.getElementById("f-friendly-name")?.value?.trim() || undefined;

    if (this._formMode === "edit" && this._editFingerprint) {
      const payload = { fingerprint: this._editFingerprint, weight, material };
      if (friendlyName) payload.friendly_name = friendlyName;
      await this._callService("update_spool", payload);
    } else {
      const initialWeight = parseFloat(root.getElementById("f-initial-weight")?.value || String(weight));
      const payload = { material, weight, initial_weight: initialWeight };
      if (friendlyName) payload.friendly_name = friendlyName;
      await this._callService("register_spool", payload);
    }

    this._formMode = null;
    this._editFingerprint = null;
    this._formData = {};
  }

  async _handleDelete(fingerprint) {
    const inventory = this._getInventory();
    const spool = inventory[fingerprint];
    const name = spool?.friendly_name || spool?.name || fingerprint;
    const lang = (this._hass?.locale?.language || "en").split("-")[0];
    const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
    const confirmMsg = dict.delete_confirm
      ? dict.delete_confirm(name)
      : TRANSLATIONS.en.delete_confirm(name);
    if (!confirm(confirmMsg)) return;
    await this._callService("remove_spool", { fingerprint });
  }

  async _callService(service, data) {
    try {
      await this._hass.callService(_DOMAIN, service, data);
    } catch (err) {
      console.error(`${_DOMAIN}.${service} failed:`, err);
      const lang = (this._hass?.locale?.language || "en").split("-")[0];
      const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
      const errMsg = dict.error_msg
        ? dict.error_msg(err.message || err)
        : TRANSLATIONS.en.error_msg(err.message || err);
      alert(errMsg);
    }
  }

  _esc(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}

customElements.define("virtual-ams-card", VirtualAmsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "virtual-ams-card",
  name: "Virtual AMS",
  description: "Manage your Bambulab filament inventory",
  preview: false,
  documentationURL: "https://github.com/SashaBusinaro/ha-virtual-ams",
});
