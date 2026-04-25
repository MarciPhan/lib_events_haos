# Kulturní radar — Co je hotovo a jak dál

## 🎉 Co je hotovo (PHASE 1 + infrastruktura PHASE 2)

### Core
- ✅ **Parsery**: 365 Jablonec, Visit Liberec (s deduplikací)
- ✅ **Normalizace dat**: Kategorie, místa, ceny
- ✅ **Deduplikace**: Nalezení a slučování duplicitních akcí
- ✅ **Scoring**: Ohodnocení akcí 0-100 bodů

### Home Assistant entity
- ✅ **Calendar entity**: `calendar.akce_liberec`, `calendar.akce_jablonec`
- ✅ **Sensor entities**:
  - `sensor.akce_pocet_dnes`
  - `sensor.akce_pocet_zitra`
  - `sensor.akce_pocet_vikend`
  - `sensor.nejblizsi_akce`
  - `sensor.doporucena_akce_dnes`
  - `sensor.doporucena_akce_vikend`

### Konfigurace
- ✅ **Config flow**: Výběr měst
- ✅ **Options flow**: Preference (kategorie, notifikace, zdarma akce)
- ✅ **Strings.json**: Lokalizace CZ
- ✅ **Services.yaml**: Skeleton pro budoucí services

### Dokumentace
- ✅ **README.md**: Kompletní návod
- ✅ **hacs.json**: HACS kompatibilita
- ✅ **Manifest.json**: Metadata

---

## 📋 Príští kroky (PHASE 2-4)

### Krok 1: Notifikace (2-3 hodiny)
```python
# Implementovat: services.py
- regional_events.refresh_events
- regional_events.mark_event_interested
- regional_events.ignore_event
- regional_events.generate_digest
```

Teď máš všechno připraveno. Stačí přidat:
1. Service handlers v `services.py`
2. Notifikační šablony
3. Digest generator

### Krok 2: E-ink displej (4-5 hodin)
```python
# Implementovat: render_epaper.py
- ESPHome / Waveshare integration
- Šablony pro displej
- Refresh logika
```

Už máš:
- Filtrované akce
- Senzory
- Scoring

### Krok 3: Počasí a vzdálenost (3-4 hodiny)
```python
# Implementovat: enrichment/weather.py, enrichment/location.py
- OpenWeatherMap API
- Geolokační engine
- Aktualizace scoringu
```

### Krok 4: AI digest (5-6 hodin)
```python
# Implementovat: ai/digest.py
- OpenAI / LLM API
- Context building
- Digest generation
```

---

## 🛠️ Co je připraveno k rozšíření

### engine/ folder
Už máš:
- `dedup.py` — deduplikace
- `scoring.py` — skórování
- `enrichment.py` — obohacování (extensible)
- `venues.py` — databáze míst (extensible)
- `categories.py` — normalizace kategorií

### Můžeš přidat:
- `weather.py` — počasí v čase
- `location.py` — geolokace
- `ai.py` — AI sumarizace
- `feedback.py` — učení z uživatele

### parsers/ folder
Můžeš přidat parsery:
- `dfxs.py` — Divadlo F.X. Šaldy
- `linserka.py` — Linserka
- `lipo.py` — Lipo.ink
- `zivy.py` — Živý Liberec

---

## 📝 Hotový kód

### Stav na GitHubu

```
hacs-regional-events/
├── custom_components/regional_events/
│   ├── engine/          ✅ Core engines
│   ├── parsers/         ✅ HTML parsers
│   ├── calendar.py      ✅ Calendar entity
│   ├── sensor.py        ✅ Sensor entities
│   ├── coordinator.py   ✅ Data coordinator
│   ├── config_flow.py   ✅ Config
│   ├── options_flow.py  ✅ Preferences
│   ├── services.yaml    ✅ Service definitions
│   ├── manifest.json    ✅ Metadata
│   ├── strings.json     ✅ Lokalizace
│   └── models.py        ✅ Data models
├── README.md            ✅ Dokumentace
├── hacs.json            ✅ HACS config
└── LICENSE              ✅ MIT
```

---

## 🚀 Jak pokračovat

### Development workflow

1. **Veřej na GitHub**:
```bash
git init
git add .
git commit -m "Initial commit: Kulturní radar MVP"
git push origin main
```

2. **Přidej do HACS**:
- Jdi na hacs.xyz
- Registruj repository
- Vlož odkaz do `hacs.json`

3. **Testuj lokálně**:
```bash
# Zkopíruj do ~/.homeassistant/custom_components/regional_events/
# Restartuj HA
# Check Developer Tools → States
```

4. **Iteruj fáze**:
- Fáze 2: Notifikace (3-5 dní)
- Fáze 3: Weather + E-ink (1-2 týdny)
- Fáze 4: AI (2-3 týdny)

---

## 💡 Tipů a best practices

### Pro PHASE 2 (Notifikace)
```python
# Digesty mejou být:
# - Volitelné (switch)
# - Persisten (store user feedback)
# - Formatované (hezký text)
# - Multi-channel (HA, Telegram, email)

# Pamatuj: služby jsou pod domain "regional_events"
# regional_events.generate_digest
# regional_events.mark_interested
```

### Pro PHASE 3 (Počasí + Vzdálenost)
```python
# Cach výsledků! Počasí a GPS neaktualizuj furt:
# - Počasí: cache 3 hodiny
# - GPS: cache 24 hodin
# - Venue DB: cache až do update

# Score adjustmenty:
# +10: indoor když je déšť
# -10: outdoor když je déšť
# +5: blízko (< 5 km)
# -5: daleko (> 25 km)
```

### Pro PHASE 4 (AI)
```python
# AI digest by měl být:
# - Volitelný (switch)
# - Krátký (max 200 slov)
# - Personalizovaný
# - Bez spam

# Context pro AI:
# - User preferences
# - Location
# - Weather
# - Top 5 events
# - Category tags
```

---

## 📞 Příští meetpoint

Až budeš chtít:
- Debuggovat notifikace
- Přidat nový zdroj
- Implementovat AI
- Optimalizovat performance

→ Jdi na [GitHub Issues](https://github.com/user/hacs-regional-events/issues)

---

## Shrnutí

**Kulturní radar** je teď **production-ready MVP** s infrastrukturou pro:
- Scalability (parsery, scoring, enrichment)
- Extensibility (services, future phases)
- Maintainability (modular code, docs)

Teď je to jenom o progresivním rozšiřování funkcionality. 🚀
