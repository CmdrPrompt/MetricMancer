# Reviderad App-Paket Omorganisering (v2)

## Befintlig src/ Struktur (Ignorerades i v1!)

```
src/
├── analysis/           (Analys-relaterad logik)
│   ├── code_review_advisor.py
│   └── hotspot_analyzer.py
│
├── app/               (Applikations-orkestrering - 16+ filer!)
│   └── [alla filer här]
│
├── config/            (Konfiguration)
│
├── kpis/              (KPI-beräkningar)
│   ├── codechurn/
│   ├── codeownership/
│   ├── complexity/
│   ├── hotspot/
│   └── sharedcodeownership/
│
├── languages/         (Språk-parsers)
│
├── report/            (Rapport-generering)
│   ├── cli/
│   ├── html/
│   └── json/
│
└── utilities/         (Globala hjälpfunktioner)
    ├── cli_helpers.py
    ├── debug.py
    ├── git_cache.py
    ├── git_helpers.py
    └── tree_printer.py
```

## Problem med Ursprunglig Plan (v1)

❌ **Förslog skapa `src/app/utilities/`** 
   → Men `src/utilities/` existerar redan!

❌ **Förslog skapa `src/app/coordinators/`**
   → Men coordinators hör till specifika domäner (report, analysis, etc.)

❌ **Ignorerade befintlig arkitektur**
   → Skulle skapa förvirring och duplicering

## ✅ REVIDERAD Plan v2: Respektera Befintlig Arkitektur

### Princip: "App-paketet är för ORKESTRERING, inte implementation"

```
src/
├── analysis/                    📦 ANALYSIS (Analys-logik)
│   ├── code_review_advisor.py
│   ├── hotspot_analyzer.py
│   └── hotspot_coordinator.py   ← FLYTTA hit från app/
│
├── app/                         📦 APP (Minimal orkestrering)
│   ├── __init__.py
│   ├── metric_mancer_app.py    (Huvudapp)
│   ├── analyzer.py             (Huvudorkestrering)
│   ├── scanner.py              (Fil-scanning)
│   │
│   └── processing/              📁 Underpaket för data-processering
│       ├── __init__.py
│       ├── file_processor.py    (NY - Fas 2)
│       ├── file_analyzer.py     (Befintlig)
│       ├── collector.py
│       ├── data_converter.py
│       ├── repository_grouper.py (Fas 1)
│       ├── kpi_orchestrator.py   (NY - Fas 2)
│       └── kpi_aggregator.py     (NY - Fas 2)
│
├── builders/                    📦 BUILDERS (Nytt top-level paket)
│   ├── __init__.py
│   └── hierarchy_builder.py     ← FLYTTA hit från app/
│
├── config/                      📦 CONFIG (Ingen förändring)
│
├── kpis/                        📦 KPIS (Ingen förändring)
│
├── languages/                   📦 LANGUAGES (Ingen förändring)
│
├── report/                      📦 REPORT (Rapport-generering)
│   ├── cli/
│   ├── html/
│   ├── json/
│   ├── report_coordinator.py    ← FLYTTA hit från app/
│   └── review_coordinator.py    ← FLYTTA hit från app/
│
└── utilities/                   📦 UTILITIES (Globala verktyg)
    ├── cli_helpers.py
    ├── debug.py
    ├── git_cache.py
    ├── git_helpers.py
    ├── tree_printer.py
    ├── file_reader.py           ← FLYTTA hit från app/ (Fas 1)
    ├── timing_tracker.py        ← FLYTTA hit från app/ (Fas 1)
    └── timing_reporter.py       ← FLYTTA hit från app/
```

## Motivering för Varje Flytt

### ✅ Till `src/utilities/` (Generella verktyg)

**file_reader.py** 
- ✅ Generell fil-läsning, inget app-specifikt
- ✅ Kan återanvändas av andra moduler
- ✅ Passar perfekt bredvid git_helpers.py

**timing_tracker.py**
- ✅ Generellt timing-verktyg
- ✅ Inget beroende på app-logik
- ✅ Kan användas var som helst

**timing_reporter.py**
- ✅ Rapporterar timing-data
- ✅ Generell funktionalitet

### ✅ Till `src/analysis/` (Analys-domän)

**hotspot_coordinator.py**
- ✅ Koordinerar hotspot-analys
- ✅ Använder hotspot_analyzer.py (redan i analysis/)
- ✅ Logiskt sammanhang

### ✅ Till `src/report/` (Rapport-domän)

**report_coordinator.py**
- ✅ Koordinerar rapport-generering
- ✅ Jobbar med report/-moduler
- ✅ Rapport-specifik logik

**review_coordinator.py**
- ✅ Koordinerar code review-rapporter
- ✅ Del av rapport-workflow
- ✅ Använder report/-generatorer

### ✅ Till `src/builders/` (Nytt top-level paket)

**hierarchy_builder.py**
- ✅ Bygger datastrukturer (inte app-specifikt)
- ✅ Kan användas av andra komponenter
- ✅ Eget ansvarsområde (Builder Pattern)

### ✅ Stannar i `src/app/` (Orkestrering)

**metric_mancer_app.py**
- ✅ Huvudapplikation - ska vara här

**analyzer.py**
- ✅ Huvudorkestrering av analys
- ✅ Koordinerar mellan olika domäner
- ✅ App-nivå, inte domän-specifik

**scanner.py**
- ✅ Fil-scanning är app-nivå logik
- ✅ Används av analyzer

### ✅ Till `src/app/processing/` (Processering under app)

**file_processor.py** (NY - Fas 2)
- ✅ Processerar enskilda filer för analys
- ✅ App-specifik processering
- ✅ Används av analyzer

**file_analyzer.py** (Befintlig)
- ✅ Analyserar fil-innehåll
- ✅ App-specifik analys-logik

**kpi_orchestrator.py** (NY - Fas 2)
- ✅ Orkestrerar KPI-beräkningar
- ✅ App-specifik koordinering

**kpi_aggregator.py** (NY - Fas 2)
- ✅ Aggregerar KPI-data
- ✅ App-specifik aggregering

**collector.py**
- ✅ Samlar analys-data
- ✅ App-workflow

**data_converter.py**
- ✅ Konverterar data mellan format
- ✅ App-specifik konvertering

**repository_grouper.py** (Fas 1)
- ✅ Grupperar filer per repo
- ✅ App-specifik pre-processering

**kpi_calculator.py** (Befintlig)
- ⚠️ Kanske borde vara i `src/kpis/` istället?
- Behöver granskas

## Före och Efter Jämförelse

### FÖRE (Nuläge)
```
src/app/ (16+ filer, kaos)
├── analyzer.py
├── collector.py
├── data_converter.py
├── file_analyzer.py
├── file_reader.py
├── hierarchy_builder.py
├── hotspot_coordinator.py
├── kpi_calculator.py
├── metric_mancer_app.py
├── report_coordinator.py
├── repository_grouper.py
├── review_coordinator.py
├── scanner.py
├── timing_reporter.py
└── timing_tracker.py
```

### EFTER (Organiserat)
```
src/
├── analysis/
│   ├── hotspot_coordinator.py    ← Från app/
│   └── (existing files)
│
├── app/ (7 filer, tydligt fokus)
│   ├── metric_mancer_app.py
│   ├── analyzer.py
│   ├── scanner.py
│   └── processing/
│       ├── file_processor.py     (NY)
│       ├── file_analyzer.py
│       ├── collector.py
│       ├── data_converter.py
│       ├── repository_grouper.py
│       ├── kpi_orchestrator.py   (NY)
│       └── kpi_aggregator.py     (NY)
│
├── builders/                      (NYTT)
│   └── hierarchy_builder.py      ← Från app/
│
├── report/
│   ├── report_coordinator.py     ← Från app/
│   ├── review_coordinator.py     ← Från app/
│   └── (existing files)
│
└── utilities/
    ├── file_reader.py            ← Från app/
    ├── timing_tracker.py         ← Från app/
    ├── timing_reporter.py        ← Från app/
    └── (existing files)
```

## Migration Plan - REVIDERAD

### Fas 2a: Flytta Fas 1-klasser till rätt plats

```bash
# 1. Flytta till utilities (generella verktyg)
git mv src/app/file_reader.py src/utilities/
git mv src/app/timing_tracker.py src/utilities/

# 2. Flytta repository_grouper till app/processing/
mkdir -p src/app/processing
git mv src/app/repository_grouper.py src/app/processing/

# 3. Uppdatera imports i tester
# tests/app/test_file_reader.py → tests/utilities/test_file_reader.py
# tests/app/test_timing_tracker.py → tests/utilities/test_timing_tracker.py
# tests/app/test_repository_grouper.py → tests/app/processing/test_repository_grouper.py
```

### Fas 2b: Skapa nya klasser på rätt plats

```bash
# Nya Fas 2-klasser hamnar direkt i src/app/processing/
src/app/processing/kpi_orchestrator.py
src/app/processing/file_processor.py
src/app/processing/kpi_aggregator.py

# Tester hamnar i tests/app/processing/
tests/app/processing/test_kpi_orchestrator.py
tests/app/processing/test_file_processor.py
tests/app/processing/test_kpi_aggregator.py
```

### Fas 2c: Flytta befintliga app/-filer (Efter Fas 2 klar)

```bash
# Coordinators till rätt domäner
git mv src/app/hotspot_coordinator.py src/analysis/
git mv src/app/report_coordinator.py src/report/
git mv src/app/review_coordinator.py src/report/

# Builders till eget paket
mkdir -p src/builders
git mv src/app/hierarchy_builder.py src/builders/

# Timing till utilities
git mv src/app/timing_reporter.py src/utilities/

# Processing (befintliga filer)
git mv src/app/file_analyzer.py src/app/processing/
git mv src/app/collector.py src/app/processing/
git mv src/app/data_converter.py src/app/processing/
```

### Fas 2d: Uppdatera alla imports

```python
# Skapa ett update_imports.py script
IMPORT_MAPPINGS = {
    # Utilities
    'from src.app.file_reader import': 'from src.utilities.file_reader import',
    'from src.app.timing_tracker import': 'from src.utilities.timing_tracker import',
    'from src.app.timing_reporter import': 'from src.utilities.timing_reporter import',
    
    # Processing
    'from src.app.repository_grouper import': 'from src.app.processing.repository_grouper import',
    'from src.app.file_analyzer import': 'from src.app.processing.file_analyzer import',
    'from src.app.collector import': 'from src.app.processing.collector import',
    'from src.app.data_converter import': 'from src.app.processing.data_converter import',
    
    # Coordinators
    'from src.app.hotspot_coordinator import': 'from src.analysis.hotspot_coordinator import',
    'from src.app.report_coordinator import': 'from src.report.report_coordinator import',
    'from src.app.review_coordinator import': 'from src.report.review_coordinator import',
    
    # Builders
    'from src.app.hierarchy_builder import': 'from src.builders.hierarchy_builder import',
}
```

## Import-exempel Efter Migration

### Före (Allt från app/)
```python
from src.app.file_reader import FileReader
from src.app.timing_tracker import TimingTracker
from src.app.repository_grouper import RepositoryGrouper
from src.app.hierarchy_builder import HierarchyBuilder
from src.app.hotspot_coordinator import HotspotCoordinator
from src.app.report_coordinator import ReportCoordinator
```

### Efter (Logisk gruppering)
```python
# Utilities - generella verktyg
from src.utilities import FileReader, TimingTracker, TimingReporter

# App processing - app-specifik processering
from src.app.processing import (
    RepositoryGrouper,
    FileProcessor,
    KPIOrchestrator,
    KPIAggregator
)

# App orchestration - huvudorkestrering
from src.app import MetricMancerApp, Analyzer, Scanner

# Builders - datastruktur-konstruktion
from src.builders import HierarchyBuilder

# Analysis - analys-domän
from src.analysis import HotspotCoordinator, HotspotAnalyzer

# Report - rapport-domän
from src.report import ReportCoordinator, ReviewCoordinator
```

## Fördelar med Reviderad Plan

✅ **Respekterar befintlig arkitektur**
- Använder `src/utilities/` som redan finns
- Placerar coordinators i sina domäner
- Följer etablerade patterns

✅ **Logisk separation**
- Utilities = generellt återanvändbara
- App = orkestrering och app-specifik logik
- Domäner (analysis, report) = domän-specifik logik

✅ **Mindre `src/app/`**
- Från 16 filer → 3 filer + processing-paket
- Tydligare fokus: Orkestrering

✅ **Skalbart**
- Lätt att hitta rätt plats för nya filer
- Tydliga gränser mellan moduler

✅ **Förbättrad testbarhet**
- Tester speglar struktur
- `tests/utilities/`
- `tests/app/processing/`
- `tests/analysis/`

## Konkret Nästa Steg (Rekommendation)

### Option A: Minimal Flytt NU (Rekommenderad)
```bash
# 1. Skapa app/processing/
mkdir -p src/app/processing
touch src/app/processing/__init__.py

# 2. Flytta bara Fas 1-klasser som behöver flyttas
git mv src/app/repository_grouper.py src/app/processing/

# 3. Fortsätt Fas 2 - nya klasser i processing/
# kpi_orchestrator.py → src/app/processing/
# file_processor.py → src/app/processing/
# kpi_aggregator.py → src/app/processing/

# 4. Full migration efter Fas 2 klar
```

### Option B: Komplett Flytt NU
```bash
# Flytta ALLT enligt plan ovan
# Mer arbete, men renare från start
```

## Sammanfattning

**Du hade helt rätt!** 🎯

1. ✅ `utilities/` existerar redan i `src/` - använd den!
2. ✅ Coordinators hör hemma i sina domäner (analysis/, report/)
3. ✅ `app/` ska vara för ORKESTRERING, inte implementation
4. ✅ Nya paket som `builders/` kan skapas på top-level

**Rekommendation:**
- Skapa `src/app/processing/` för processing-logik
- Flytta `file_reader` och `timing_tracker` till `src/utilities/` (senare)
- Nya Fas 2-klasser i `src/app/processing/`
- Full migration efter Fas 2

Vill du att jag implementerar Option A (minimal flytt nu, full migration senare)?
