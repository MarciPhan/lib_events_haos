class RegionalEventsCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
            <div class="name">Kulturní radar</div>
            <ha-icon icon="mdi:radar"></ha-icon>
          </div>
          <div id="events-container" class="card-content"></div>
        </ha-card>
        <style>
          ha-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
          }
          .card-header {
            padding: 16px;
            font-size: 1.4em;
            font-weight: bold;
            color: var(--primary-text-color);
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
          }
          .event-item {
            display: flex;
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: background 0.3s;
            cursor: pointer;
            position: relative;
          }
          .event-item:hover {
            background: rgba(255, 255, 255, 0.05);
          }
          .event-score {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9em;
            margin-right: 12px;
            flex-shrink: 0;
            background: var(--secondary-background-color);
            border: 2px solid transparent;
          }
          .score-high { border-color: #4caf50; color: #4caf50; }
          .score-medium { border-color: #ff9800; color: #ff9800; }
          .score-low { border-color: #f44336; color: #f44336; }
          
          .event-info {
            flex-grow: 1;
            min-width: 0;
          }
          .event-title {
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 4px;
          }
          .event-meta {
            font-size: 0.85em;
            color: var(--secondary-text-color);
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
          }
          .badge {
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(0,0,0,0.2);
            font-size: 0.8em;
          }
          .badge-free { color: #4caf50; }
          .badge-indoor { color: #2196f3; }
          .reasoning {
            font-size: 0.8em;
            color: var(--accent-color);
            margin-top: 4px;
            font-style: italic;
          }
        </style>
      `;
      this.content = this.querySelector("#events-container");
    }

    this._hass = hass;
    this.updateContent();
  }

  updateContent() {
    if (!this._hass || !this.config) return;

    // Get events from sensors
    const entityId = this.config.entity || "sensor.akce_dnes";
    const state = this._hass.states[entityId];
    
    if (!state) {
      this.content.innerHTML = "Entita nenalezena";
      return;
    }

    // In a real scenario, we'd probably fetch all events from the coordinator via a service or state
    // For this preview, let's show the recommended event and maybe a few others if the state has them
    
    let html = "";
    
    // Check if it's a count sensor or a detail sensor
    if (state.attributes.reasoning) {
      // It's a detail sensor
      html = this.renderEvent(state.attributes, state.state);
    } else {
      html = `<div style="padding: 16px; text-align: center;">Počet akcí: ${state.state}</div>`;
    }

    this.content.innerHTML = html;
  }

  renderEvent(attrs, title) {
    const scoreClass = attrs.score > 80 ? "score-high" : (attrs.score > 50 ? "score-medium" : "score-low");
    const date = new Date(attrs.start).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    return `
      <div class="event-item">
        <div class="event-score ${scoreClass}">${Math.round(attrs.score)}%</div>
        <div class="event-info">
          <div class="event-title">${title}</div>
          <div class="event-meta">
            <span>${date}</span>
            <span>${attrs.location}</span>
            ${attrs.price === "Zdarma" ? '<span class="badge badge-free">ZDARMA</span>' : ''}
            ${attrs.distance_km ? `<span>${attrs.distance_km.toFixed(1)} km</span>` : ''}
          </div>
          ${attrs.reasoning ? `<div class="reasoning">${attrs.reasoning[0]}</div>` : ''}
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
  description: "Karta pro zobrazení lokálních akcí s doporučením"
});
