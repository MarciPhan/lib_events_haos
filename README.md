# Kulturní radar pro Home Assistant

Integrace přináší **lokální kulturní doporučovací systém** pro Liberec a Jablonec. Nejen kalendář akcí, ale **chytré doporučování** podle vašich zájmů, času, počasí a vzdálenosti.

## Funkce

### Základní
- 📅 **Kalendářové entity** pro Liberec a Jablonec
- 📊 **Senzory** — počet akcí dnes, zítřek, víkend, nejbližší akce
- 🔄 Automatické aktualizace každých 6 hodin
- 🏙️ Extrakce z webů Visit Liberec a 365 Jablonec
- ♻️ Deduplikace akcí ze více zdrojů

### Doporučování  
- ⭐ **Skórování akcí** (0-100) podle vašich preferencí
- 💾 **Uložené preference** — zájmy, oblíbená místa, blacklist
- 🌧️ **Počasí** — zvyšuje skóre indoor akcí při špatném počasí
- 📍 **Vzdálenost** — zvyšuje skóre akcí blízkých domu
- 💰 **Ceny** — zvyšuje skóre zdarma akcí

### Budoucí rozšíření
- 🤖 AI digest — víkendový plán
- 📱 Notifikace a digesty
- 📺 E-ink displej v domě
- 🎴 Custom dashboard karta s obrázky

## Instalace

### Via HACS

1. Jděte do HACS → Integrations
2. Klikněte na `Explore & Download Repositories`
3. Vyhledejte `Kulturní radar`
4. Klikněte na `Download`
5. Restartujte Home Assistant

### Manuálně

```bash
mkdir -p /config/custom_components
cd /config/custom_components
git clone https://github.com/user/hacs-regional-events.git regional_events
```

## Nastavení

1. **Settings** → **Devices & Services** → **Integrations**
2. Klikněte na **Create Integration** a vyhledejte **Kulturní radar**
3. Vyberte měst, která chcete sledovat
4. V možnostech si nastavte preference:
   - Oblíbené kategorie (hudba, divadlo, vzdělání, ...)
   - Blokované kategorie
   - Notifikace
   - Preference bezplatných akcí

## Entity

### Kalendáře

```text
calendar.akce_liberec       — akce v Liberci
calendar.akce_jablonec      — akce v Jablonci
```

### Senzory

```text
sensor.akce_pocet_dnes                — počet akcí dnes
sensor.akce_pocet_zitra               — počet akcí zítřa
sensor.akce_pocet_vikend              — počet akcí o víkendu
sensor.nejblizsi_akce                 — nejbližší akce (titulek)
sensor.doporucena_akce_dnes           — doporučená akce dnes
sensor.doporucena_akce_vikend         — doporučená akce o víkendu
```

Každý senzor má atributy s detaily:
- `location` — místo
- `start` — čas začátku
- `category` — kategorie
- `url` — odkaz na webem
- `score` — skóre doporučení (0-100)

## Příklady v dashboardu

### Jednoduchý kalendář

```yaml
type: calendar
entities:
  - calendar.akce_liberec
  - calendar.akce_jablonec
initial_view: listWeek
title: Akce v okolí
```

### Doporučené akce

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      # Doporučení
      - {{ states('sensor.doporucena_akce_dnes') }}
      - {{ states('sensor.doporucena_akce_vikend') }}

  - type: entities
    entities:
      - sensor.akce_pocet_dnes
      - sensor.akce_pocet_vikend
      - sensor.nejblizsi_akce
```

## Příklady automatizací

### Denní digest

```yaml
alias: Kulturní radar - denní digest
trigger:
  - platform: time
    at: "09:00:00"
action:
  - service: notify.mobile_app_telefon
    data:
      title: Kulturní radar
      message: |
        Dnes: {{ states('sensor.akce_pocet_dnes') }} akcí
        Nejlepší: {{ states('sensor.doporucena_akce_dnes') }}
      data:
        url: /lovelace/events
```

### Páteční víkendový plán

```yaml
alias: Kulturní radar - víkendový plán
trigger:
  - platform: time
    at: "16:00:00"
condition:
  - condition: time
    weekday:
      - fri
action:
  - service: notify.mobile_app_telefon
    data:
      title: Víkend v okolí
      message: |
        Akce o víkendu: {{ states('sensor.akce_pocet_vikend') }}
        Doporučuji: {{ states('sensor.doporucena_akce_vikend') }}
```

## Konfigurace preference

V možnostech integrace si nastavíte:

```yaml
preferred_categories:
  - music       # 🎵 Hudba
  - theatre     # 🎭 Divadlo
  - education   # 📚 Vzdělání

blocked_categories:
  - sports      # ⚽ Sport

enable_notifications: true
prefer_free_events: true
```

## Zdroje dat

### Primární
- 365 Jablonec (https://www.365jablonec.cz)
- Visit Liberec (https://www.visitliberec.eu/kalendar-akci)

### Plánované
- DFXŠ (Divadlo F. X. Šaldy)
- Linserka
- Lipo.ink
- Živý Liberec

## Řešení problémů

### Entita se nezobrazuje

Zkontrolujte, zda je integrace správně nastavena:

```yaml
# Developer Tools → States
# Vyhledejte sensor.akce_pocet_dnes
```

### Akce se neaktualizují

Integrace se aktualizuje každých 6 hodin. Ruční aktualizace:

```yaml
# Developer Tools → Services
# regional_events.refresh_events
```

## Roadmap

| Fáze | Stav | Obsah |
|------|------|-------|
| **MVP** | ✅ | Parsery, kalendáře, senzory |
| **Phase 2** | 🚧 | Scoring, notifikace, digesty |
| **Phase 3** | 📅 | Počasí, vzdálenost, e-ink |
| **Phase 4** | 📅 | AI, feedback, učení |

## Přispívání

Issues a pull requesty jsou vítané! Pokud máte nápad na nový zdroj akcí nebo chcete rozšířit funkcionalitu, napište issue.

## Licence

MIT

---

**Kulturní radar** — váš osobní event engine pro Home Assistant 🎭📅🏠

