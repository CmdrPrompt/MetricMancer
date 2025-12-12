# 📋 Refaktoreringsplan för Release

**Datum:** 2025-12-12
**Mål:** Reducera kognitiv komplexitet till acceptabla nivåer före release

## 📊 Nuläge

| Metrik | Nuvarande | Målvärde |
|--------|-----------|----------|
| Max Cognitive Complexity | 82 | < 40 |
| Max Cyclomatic Complexity | 170 | < 100 |
| Kritiska filer (Cog > 40) | 4 | 0 |
| Totala förbättringsmöjligheter | 29 | - |

---

## 🚫 Fas 1: Blockers (Måste göras)

**Uppskattad tid:** 1-2 dagar

### 1.1 `src/analysis/delta/delta_review_format.py`
- **Cog: 82** → Mål: < 40
- **Åtgärd:** Extrahera helper-metoder för formattering, bryt ner stora metoder
- **Risk:** Hög - central rapportfunktionalitet
- **Tid:** 4-8 timmar

### 1.2 `src/kpis/cognitive_complexity/calculator_c.py`
- **Cog: 57** → Mål: < 30
- **Åtgärd:** Extrahera AST-traverseringslogik till separata metoder
- **Risk:** Medium - isolerad parser-modul
- **Tid:** 2-4 timmar

---

## ⚠️ Fas 2: High Priority (Bör göras)

**Uppskattad tid:** 2-3 dagar

### 2.1 `src/analysis/delta/delta_analyzer.py`
- **Cog: 46** → Mål: < 30
- **Åtgärd:** Förenkla jämförelselogik, extrahera diff-beräkningar
- **Tid:** 4-8 timmar

### 2.2 `src/app/core/analyzer.py`
- **Cog: 42** → Mål: < 30
- **Åtgärd:** Extrahera KPI-beräkningar till separata metoder
- **Tid:** 4-8 timmar

### 2.3 `src/utilities/git_cache.py`
- **CC: 170**, Cog: 39 → Mål: CC < 100
- **Åtgärd:** Bryt ut git-operationer, skapa command-pattern
- **Tid:** 4-8 timmar

---

## 📅 Fas 3: Post-release (Kan vänta)

**24 ytterligare förbättringsmöjligheter**

| Fil | CC | Cog | Prioritet |
|-----|-----|-----|-----------|
| `cli_summary_format.py` | 104 | 39 | Medium |
| `calculator_go.py` | 44 | 38 | Medium |
| `calculator_java.py` | 44 | 38 | Medium |
| `cli_quick_wins_format.py` | 98 | 35 | Låg |
| `cli_report_format.py` | 135 | 28 | Låg |
| *+ 19 övriga filer* | - | - | Låg |

---

## ✅ Definition of Done

- [ ] Ingen fil med Cog > 40
- [ ] Ingen fil med CC > 100
- [ ] Alla 1003+ tester passerar
- [ ] Flake8 utan varningar
- [ ] Quick-wins visar 0 kritiska filer

---

## 🔄 Refaktoreringsmönster att använda

1. **Extract Method** - Bryt ut nästlade loopar/villkor till separata metoder
2. **Replace Conditional with Polymorphism** - Använd strategy pattern
3. **Introduce Parameter Object** - Gruppera relaterade parametrar
4. **Replace Nested Conditionals with Guard Clauses** - Early returns
5. **Extract Constants** - Ersätt magic numbers med namngivna konstanter

---

## 📈 Spårning

| Fas | Status | Startdatum | Slutdatum |
|-----|--------|------------|-----------|
| Fas 1 | ⏳ Ej påbörjad | - | - |
| Fas 2 | ⏳ Ej påbörjad | - | - |
| Fas 3 | 📅 Planerad post-release | - | - |

---

*Genererad av MetricMancer quick-wins analys*
