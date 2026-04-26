/**
 * Kulturní radar - Premium Dashboard Panel
 */

class RegionalEventsPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._panel) {
      this.initPanel();
    }
    this.updateContent();
  }

  set panel(panel) {
    this._panel = panel;
  }

  initPanel() {
    this.innerHTML = `
      <div class="app-container">
        <header class="glass-header">
          <div class="brand">
            <ha-icon icon="mdi:radar" class="logo-icon"></ha-icon>
            <div class="brand-text">
              <h1>Kulturní radar</h1>
              <p>Liberec & Jablonec nad Nisou</p>
            </div>
          </div>
          <div class="header-actions">
            <button class="btn-refresh glass-btn" id="refresh-btn">
              <ha-icon icon="mdi:refresh"></ha-icon>
              <span>Aktualizovat</span>
            </button>
            <button class="btn-ai glass-btn primary" id="digest-btn">
              <ha-icon icon="mdi:sparkles"></ha-icon>
              <span>AI Přehled</span>
            </button>
          </div>
        </header>

        <main class="content-grid">
          <aside class="sidebar-filters glass-card">
            <div class="filter-group">
              <h3>Filtry</h3>
              <div class="chips">
                <button class="chip active" data-filter="all">Vše</button>
                <button class="chip" data-filter="today">Dnes</button>
                <button class="chip" data-filter="weekend">Víkend</button>
                <button class="chip" data-filter="free">Zdarma</button>
                <button class="chip" data-filter="kids">Pro děti</button>
              </div>
            </div>
            
            <div class="filter-group">
              <h3>Zdroje</h3>
              <div class="source-list" id="source-list">
                <!-- Sources will be injected here -->
              </div>
            </div>

            <div class="stats-card">
              <div class="stat-item">
                <span class="stat-value" id="total-count">0</span>
                <span class="stat-label">Akcí celkem</span>
              </div>
            </div>
          </aside>

          <section class="events-list" id="events-grid">
            <!-- Events will be injected here -->
          </section>
        </main>
      </div>

      <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        :host {
          --glass-bg: rgba(255, 255, 255, 0.05);
          --glass-border: rgba(255, 255, 255, 0.1);
          --accent-color: #00d2ff;
          --accent-gradient: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
          --text-primary: #ffffff;
          --text-secondary: rgba(255, 255, 255, 0.7);
          font-family: 'Inter', sans-serif;
          color: var(--text-primary);
          background: #0f0f13;
          display: block;
          height: 100vh;
          overflow: hidden;
        }

        .app-container {
          height: 100%;
          display: flex;
          flex-direction: column;
          padding: 24px;
          box-sizing: border-box;
          background: radial-gradient(circle at top right, rgba(58, 123, 213, 0.1), transparent),
                      radial-gradient(circle at bottom left, rgba(0, 210, 255, 0.05), transparent);
        }

        .glass-header {
          background: var(--glass-bg);
          backdrop-filter: blur(20px);
          border: 1px solid var(--glass-border);
          border-radius: 20px;
          padding: 20px 32px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
          box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .logo-icon {
          --mdc-icon-size: 40px;
          color: var(--accent-color);
          filter: drop-shadow(0 0 8px var(--accent-color));
        }

        .brand-text h1 {
          margin: 0;
          font-size: 24px;
          font-weight: 700;
          letter-spacing: -0.5px;
        }

        .brand-text p {
          margin: 0;
          font-size: 14px;
          color: var(--text-secondary);
        }

        .header-actions {
          display: flex;
          gap: 12px;
        }

        .glass-btn {
          background: var(--glass-bg);
          border: 1px solid var(--glass-border);
          border-radius: 12px;
          color: white;
          padding: 10px 20px;
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          font-weight: 600;
        }

        .glass-btn:hover {
          background: rgba(255, 255, 255, 0.1);
          transform: translateY(-2px);
          border-color: rgba(255, 255, 255, 0.3);
        }

        .glass-btn.primary {
          background: var(--accent-gradient);
          border: none;
          box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3);
        }

        .glass-btn.primary:hover {
          box-shadow: 0 6px 20px rgba(0, 210, 255, 0.5);
        }

        .content-grid {
          display: grid;
          grid-template-columns: 300px 1fr;
          gap: 24px;
          flex-grow: 1;
          overflow: hidden;
        }

        .glass-card {
          background: var(--glass-bg);
          backdrop-filter: blur(10px);
          border: 1px solid var(--glass-border);
          border-radius: 20px;
          padding: 24px;
        }

        .sidebar-filters {
          display: flex;
          flex-direction: column;
          gap: 32px;
          overflow-y: auto;
        }

        .filter-group h3 {
          margin: 0 0 16px 0;
          font-size: 14px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: var(--text-secondary);
        }

        .chips {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .chip {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          border-radius: 20px;
          padding: 6px 16px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.2s;
          font-size: 13px;
        }

        .chip:hover {
          background: rgba(255, 255, 255, 0.1);
        }

        .chip.active {
          background: var(--accent-color);
          color: white;
          border-color: var(--accent-color);
          font-weight: 600;
        }

        .events-list {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
          overflow-y: auto;
          padding-right: 8px;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

        .event-card {
          background: var(--glass-bg);
          border: 1px solid var(--glass-border);
          border-radius: 20px;
          overflow: hidden;
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          position: relative;
          display: flex;
          flex-direction: column;
        }

        .event-card:hover {
          transform: translateY(-8px) scale(1.02);
          border-color: var(--accent-color);
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
          z-index: 10;
        }

        .event-image {
          height: 180px;
          background-size: cover;
          background-position: center;
          position: relative;
        }

        .event-badge {
          position: absolute;
          top: 16px;
          right: 16px;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(5px);
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 700;
          color: var(--accent-color);
          border: 1px solid var(--accent-color);
        }

        .event-score-orb {
          position: absolute;
          bottom: -20px;
          left: 20px;
          width: 44px;
          height: 44px;
          border-radius: 50%;
          background: var(--accent-gradient);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 14px;
          box-shadow: 0 4px 15px rgba(0, 210, 255, 0.5);
          border: 2px solid #0f0f13;
        }

        .event-content {
          padding: 24px 20px 20px 20px;
          flex-grow: 1;
          display: flex;
          flex-direction: column;
        }

        .event-title {
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 12px;
          line-height: 1.3;
        }

        .event-meta {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
        }

        .meta-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: var(--text-secondary);
        }

        .meta-item ha-icon {
          --mdc-icon-size: 16px;
          color: var(--accent-color);
        }

        .event-tags {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
          margin-top: auto;
        }

        .tag {
          font-size: 10px;
          background: rgba(255, 255, 255, 0.05);
          padding: 2px 8px;
          border-radius: 4px;
          text-transform: uppercase;
        }

        .reasoning-popover {
          font-size: 12px;
          font-style: italic;
          color: #ff9800;
          margin-top: 8px;
        }

        .empty-state {
          grid-column: 1 / -1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 400px;
          color: var(--text-secondary);
        }

        .empty-state ha-icon {
          --mdc-icon-size: 64px;
          margin-bottom: 16px;
          opacity: 0.3;
        }

        @media (max-width: 900px) {
          .content-grid { grid-template-columns: 1fr; }
          .sidebar-filters { display: none; }
        }
      </style>
    `;

    this.querySelector("#refresh-btn").onclick = () => this.callService("refresh_events");
    this.querySelector("#digest-btn").onclick = () => this.showDigest();
    
    // Filter logic
    this.querySelectorAll(".chip").forEach(chip => {
      chip.onclick = (e) => {
        this.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
        e.target.classList.add("active");
        this._filter = e.target.dataset.filter;
        this.updateContent();
      };
    });
  }

  async callService(service) {
    const btn = this.querySelector(".btn-refresh");
    btn.style.opacity = "0.5";
    try {
      await this._hass.callService("regional_events", service, {});
    } finally {
      btn.style.opacity = "1";
    }
  }

  async showDigest() {
    const btn = this.querySelector(".btn-ai");
    btn.innerHTML = `<ha-icon icon="mdi:loading" class="spin"></ha-icon> <span>Generuji...</span>`;
    try {
      await this._hass.callService("regional_events", "generate_digest", {
        period: "weekend",
        use_ai: true
      });
      // We'd normally wait for the bus event or state change, but for UI feedback:
      setTimeout(() => {
        btn.innerHTML = `<ha-icon icon="mdi:check"></ha-icon> <span>Hotovo</span>`;
        setTimeout(() => {
          btn.innerHTML = `<ha-icon icon="mdi:sparkles"></ha-icon> <span>AI Přehled</span>`;
        }, 2000);
      }, 1000);
    } catch (e) {
      btn.innerHTML = `<span>Chyba</span>`;
    }
  }

  updateContent() {
    if (!this._hass) return;

    // Get events from a special state attribute if we had it, or from coordinator data
    // In this panel, we'll fetch from the 'calendar' or specific sensors
    // For now, let's look for any 'regional_events' domain data
    const events = this.getEvents();
    this.renderEvents(events);
    this.updateStats(events);
  }

  getEvents() {
    // This is a bit tricky as HA doesn't expose the full internal list of events via states easily
    // unless we put them in a sensor attribute. 
    // Let's assume we have a master sensor sensor.regional_events_data
    const sensor = this._hass.states["sensor.nejblizsi_akce"];
    if (!sensor || !sensor.attributes) return [];
    
    // In a real functional integration, we would probably use a WebSocket to get the full list
    // Or just look at all regional_events sensors.
    // For this demonstration, we'll "simulate" getting the data from the coordinator's state
    
    // For now, let's try to get all events by finding all sensors of this domain
    const allEvents = [];
    Object.keys(this._hass.states).forEach(id => {
      if (id.startsWith("calendar.akce_")) {
        // Calendars don't show future events in state, we'd need to call API
      }
    });

    // Fallback: search for the next event and maybe some others we can find
    // In a production version, we should ensure coordinator puts a 'all_events' list in a sensor
    return sensor.attributes.all_events || [];
  }

  renderEvents(events) {
    const grid = this.querySelector("#events-grid");
    if (!grid) return;

    let filtered = events;
    const now = new Date();
    
    if (this._filter === "today") {
      filtered = events.filter(e => new Date(e.start).toDateString() === now.toDateString());
    } else if (this._filter === "weekend") {
      filtered = events.filter(e => {
        const d = new Date(e.start);
        return d.getDay() === 0 || d.getDay() === 6;
      });
    } else if (this._filter === "free") {
      filtered = events.filter(e => e.is_free);
    } else if (this._filter === "kids") {
      filtered = events.filter(e => e.category === "kids" || (e.description && e.description.toLowerCase().includes("děti")));
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <ha-icon icon="mdi:calendar-search"></ha-icon>
          <p>Žádné akce nenalezeny pro tento filtr.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(event => this.renderEventCard(event)).join("");
  }

  renderEventCard(event) {
    const date = new Date(event.start);
    const dateStr = date.toLocaleDateString("cs-CZ", { day: 'numeric', month: 'long' });
    const timeStr = date.toLocaleTimeString("cs-CZ", { hour: '2-digit', minute: '2-digit' });
    
    return `
      <div class="event-card">
        <div class="event-image" style="background-image: url('${event.image_url || 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?auto=format&fit=crop&q=80&w=800'}')">
          <div class="event-badge">${event.source}</div>
          <div class="event-score-orb">${Math.round(event.score)}%</div>
        </div>
        <div class="event-content">
          <div class="event-title">${event.title}</div>
          <div class="event-meta">
            <div class="meta-item">
              <ha-icon icon="mdi:calendar-clock"></ha-icon>
              <span>${dateStr} v ${timeStr}</span>
            </div>
            <div class="meta-item">
              <ha-icon icon="mdi:map-marker"></ha-icon>
              <span>${event.location || event.city}</span>
            </div>
            <div class="meta-item">
              <ha-icon icon="mdi:tag-outline"></ha-icon>
              <span>${event.category || 'Ostatní'}</span>
            </div>
          </div>
          ${event.reasoning ? `<div class="reasoning-popover">${event.reasoning[0]}</div>` : ''}
          <div class="event-tags">
            <span class="tag">${event.price || 'Dle ceníku'}</span>
            ${event.is_free ? '<span class="tag" style="background: rgba(76, 175, 80, 0.2); color: #4caf50;">Zdarma</span>' : ''}
            ${event.indoor_outdoor === 'indoor' ? '<span class="tag">Interiér</span>' : ''}
          </div>
        </div>
      </div>
    `;
  }

  updateStats(events) {
    const counter = this.querySelector("#total-count");
    if (counter) counter.innerText = events.length;
    
    const sourceList = this.querySelector("#source-list");
    if (sourceList) {
      const sources = [...new Set(events.map(e => e.source))];
      sourceList.innerHTML = sources.map(s => `
        <div class="meta-item" style="margin-bottom: 8px;">
          <ha-icon icon="mdi:check-circle-outline"></ha-icon>
          <span>${s}</span>
        </div>
      `).join("");
    }
  }
}

customElements.define("regional-events-panel", RegionalEventsPanel);
