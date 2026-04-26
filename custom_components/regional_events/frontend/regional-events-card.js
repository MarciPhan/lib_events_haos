/**
 * Kulturní radar - Premium Lovelace Card
 */

class RegionalEventsCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-header">
            <div class="brand">
              <ha-icon icon="mdi:radar"></ha-icon>
              <span>Kulturní radar</span>
            </div>
            <ha-icon icon="mdi:chevron-right" class="open-panel" id="open-panel"></ha-icon>
          </div>
          <div id="events-container" class="card-content"></div>
        </ha-card>
        <style>
          ha-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            font-family: 'Inter', sans-serif;
          }
          .card-header {
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(to bottom, rgba(255,255,255,0.05), transparent);
          }
          .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            color: #00d2ff;
          }
          .open-panel {
            cursor: pointer;
            opacity: 0.5;
            transition: opacity 0.3s;
          }
          .open-panel:hover { opacity: 1; }
          
          .event-item {
            display: flex;
            padding: 12px;
            gap: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: background 0.3s;
            cursor: pointer;
          }
          .event-item:last-child { border-bottom: none; }
          .event-item:hover { background: rgba(255, 255, 255, 0.05); }
          
          .event-score {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 11px;
            flex-shrink: 0;
            background: rgba(255,255,255,0.1);
            border: 2px solid transparent;
          }
          .score-high { border-color: #4caf50; color: #4caf50; }
          .score-medium { border-color: #ff9800; color: #ff9800; }
          .score-low { border-color: #f44336; color: #f44336; }
          
          .event-info { flex-grow: 1; min-width: 0; }
          .event-title {
            font-weight: 600;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
          }
          .event-meta {
            font-size: 11px;
            color: rgba(255,255,255,0.5);
            display: flex;
            gap: 8px;
          }
          .reasoning {
            font-size: 11px;
            color: #00d2ff;
            margin-top: 4px;
            opacity: 0.8;
          }
        </style>
      `;
      this.content = this.querySelector("#events-container");
      this.querySelector("#open-panel").onclick = () => {
        window.history.pushState(null, null, "/kulturni-radar");
        window.dispatchEvent(new CustomEvent("location-changed"));
      };
    }

    this._hass = hass;
    this.updateContent();
  }

  updateContent() {
    if (!this._hass || !this.config) return;

    const entityId = this.config.entity || "sensor.nejblizsi_akce";
    const state = this._hass.states[entityId];
    
    if (!state) {
      this.content.innerHTML = `<div style="padding: 20px; text-align: center; opacity: 0.5;">Hledám akce...</div>`;
      return;
    }

    // Show top 3 events from all_events attribute
    const events = state.attributes.all_events || [];
    if (events.length === 0) {
      this.content.innerHTML = `<div style="padding: 20px; text-align: center; opacity: 0.5;">Žádné akce v okolí</div>`;
      return;
    }

    const topEvents = events.slice(0, 3);
    this.content.innerHTML = topEvents.map(e => this.renderEvent(e)).join("");
  }

  renderEvent(event) {
    const scoreClass = event.score > 80 ? "score-high" : (event.score > 50 ? "score-medium" : "score-low");
    const date = new Date(event.start).toLocaleDateString("cs-CZ", {day: 'numeric', month: 'short'});
    
    return `
      <div class="event-item">
        <div class="event-score ${scoreClass}">${Math.round(event.score)}</div>
        <div class="event-info">
          <div class="event-title">${event.title}</div>
          <div class="event-meta">
            <span>${date}</span>
            <span>•</span>
            <span>${event.location || event.city}</span>
          </div>
          ${event.reasoning ? `<div class="reasoning">${event.reasoning[0]}</div>` : ''}
        </div>
      </div>
    `;
  }

  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("regional-events-card", RegionalEventsCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "regional-events-card",
  name: "Kulturní radar",
  description: "Prémiová karta pro kulturní akce"
});
