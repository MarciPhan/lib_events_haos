# Regionální akce (Liberec & Jablonec)

Home Assistant integrace, která stahuje kulturní a společenské akce pro Liberec a Jablonec nad Nisou.

## Funkce
- Kalendář pro Liberec (`calendar.akce_liberec`)
- Kalendář pro Jablonec (`calendar.akce_jablonec`)
- Automatická aktualizace každých 6 hodin.
- Kompatibilní s nativní kartou Kalendář.

## Instalace
1. Zkopírujte složku `regional_events` do adresáře `custom_components` vašeho Home Assistanta.
2. Restartujte Home Assistant.
3. V Nastavení -> Integrace klikněte na "Přidat integraci" a vyhledejte "Regionální akce".

## Zdroje dat
- **Jablonec nad Nisou**: [365jablonec.cz](https://www.365jablonec.cz/)
- **Liberec**: [visitliberec.eu](https://www.visitliberec.eu/)

## Dashboard příklad
```yaml
type: calendar
entities:
  - calendar.akce_liberec
  - calendar.akce_jablonec
initial_view: listWeek
title: Akce v okolí
```
