# Föreslagen App-Paket Omorganisering

## Nuvarande Struktur (Problem)
```
src/app/
├── analyzer.py              (Complexity: 121, kritisk hotspot)
├── collector.py
├── data_converter.py
├── file_analyzer.py
├── file_reader.py           (NY - Fas 1)
├── hierarchy_builder.py
├── hotspot_coordinator.py
├── kpi_calculator.py
├── metric_mancer_app.py     (Huvudapp)
├── report_coordinator.py
├── repository_grouper.py    (NY - Fas 1)
├── review_coordinator.py
├── scanner.py
├── timing_reporter.py
├── timing_tracker.py        (NY - Fas 1)
└── __init__.py
```

**Problem:**
- 16+ filer i ett paket
- Ingen tydlig separation of concerns
- Svårt att hitta rätt fil
- Blandar olika ansvarsområden

## Föreslagen Ny Struktur

### Option 1: Funktionell Gruppering (Rekommenderad)

```
src/app/
├── __init__.py
├── metric_mancer_app.py     (Huvudapp - behåll här)
│
├── core/                     📦 CORE - Huvudlogik
│   ├── __init__.py
│   ├── analyzer.py          (Orkestrering av analys)
│   ├── scanner.py           (Fil-scanning)
│   └── kpi_calculator.py    (KPI-beräkningar)
│
├── processing/               📦 PROCESSING - Fil/Data-processering
│   ├── __init__.py
│   ├── file_reader.py       (Läs filer)
│   ├── file_analyzer.py     (Analysera fil-innehåll)
│   ├── collector.py         (Samla data)
│   ├── data_converter.py    (Konvertera data)
│   └── repository_grouper.py (Gruppera repos)
│
├── builders/                 📦 BUILDERS - Konstruktion av datastrukturer
│   ├── __init__.py
│   └── hierarchy_builder.py (Bygg hierarki)
│
├── coordinators/             📦 COORDINATORS - Koordinering av workflows
│   ├── __init__.py
│   ├── report_coordinator.py
│   ├── review_coordinator.py
│   └── hotspot_coordinator.py
│
└── utilities/                📦 UTILITIES - Hjälpklasser
    ├── __init__.py
    ├── timing_tracker.py    (Timing)
    └── timing_reporter.py   (Timing rapportering)
```

### Option 2: Layer-baserad Gruppering

```
src/app/
├── __init__.py
├── metric_mancer_app.py
│
├── orchestration/            📦 Orkestrering
│   ├── __init__.py
│   ├── analyzer.py
│   ├── report_coordinator.py
│   ├── review_coordinator.py
│   └── hotspot_coordinator.py
│
├── analysis/                 📦 Analys
│   ├── __init__.py
│   ├── file_analyzer.py
│   ├── kpi_calculator.py
│   └── scanner.py
│
├── io/                       📦 Input/Output
│   ├── __init__.py
│   ├── file_reader.py
│   ├── collector.py
│   └── repository_grouper.py
│
├── transformation/           📦 Transformation
│   ├── __init__.py
│   ├── data_converter.py
│   └── hierarchy_builder.py
│
└── support/                  📦 Support
    ├── __init__.py
    ├── timing_tracker.py
    └── timing_reporter.py
```

### Option 3: Domain-driven Design (Mest modulärt)

```
src/app/
├── __init__.py
├── metric_mancer_app.py     (Entry point)
│
├── scanning/                 📦 SCANNING DOMAIN
│   ├── __init__.py
│   ├── scanner.py
│   ├── file_reader.py
│   └── repository_grouper.py
│
├── analyzing/                📦 ANALYZING DOMAIN
│   ├── __init__.py
│   ├── analyzer.py          (Orchestrator)
│   ├── file_analyzer.py
│   └── kpi_calculator.py
│
├── building/                 📦 BUILDING DOMAIN
│   ├── __init__.py
│   ├── hierarchy_builder.py
│   ├── collector.py
│   └── data_converter.py
│
├── coordinating/             📦 COORDINATING DOMAIN
│   ├── __init__.py
│   ├── report_coordinator.py
│   ├── review_coordinator.py
│   └── hotspot_coordinator.py
│
└── timing/                   📦 TIMING DOMAIN
    ├── __init__.py
    ├── timing_tracker.py
    └── timing_reporter.py
```

## Rekommendation: Option 1 (Funktionell Gruppering)

### Fördelar:
✅ **Tydlig separation av concerns**
- Core: Huvudlogik
- Processing: Data-hantering
- Builders: Konstruktion
- Coordinators: Workflow-koordinering
- Utilities: Hjälpfunktioner

✅ **Lätt att hitta rätt fil**
- "Var läser vi filer?" → `processing/file_reader.py`
- "Var koordineras rapporter?" → `coordinators/report_coordinator.py`
- "Var byggs hierarkin?" → `builders/hierarchy_builder.py`

✅ **Skalbart**
- Lätt att lägga till nya filer i rätt kategori
- Varje paket kan växa oberoende

✅ **Förbättrad testbarhet**
- `tests/app/core/`
- `tests/app/processing/`
- `tests/app/coordinators/`
- etc.

✅ **Enklare imports**
```python
# Före
from src.app.file_reader import FileReader
from src.app.timing_tracker import TimingTracker
from src.app.hierarchy_builder import HierarchyBuilder

# Efter
from src.app.processing import FileReader
from src.app.utilities import TimingTracker
from src.app.builders import HierarchyBuilder
```

### Migration Plan (Fas 2b - Efter KPIOrchestrator)

#### Steg 1: Skapa nya paket-strukturer
```bash
mkdir -p src/app/core
mkdir -p src/app/processing
mkdir -p src/app/builders
mkdir -p src/app/coordinators
mkdir -p src/app/utilities
```

#### Steg 2: Flytta filer (med git mv för att behålla historik)
```bash
# Core
git mv src/app/analyzer.py src/app/core/
git mv src/app/scanner.py src/app/core/
git mv src/app/kpi_calculator.py src/app/core/

# Processing
git mv src/app/file_reader.py src/app/processing/
git mv src/app/file_analyzer.py src/app/processing/
git mv src/app/collector.py src/app/processing/
git mv src/app/data_converter.py src/app/processing/
git mv src/app/repository_grouper.py src/app/processing/

# Builders
git mv src/app/hierarchy_builder.py src/app/builders/

# Coordinators
git mv src/app/report_coordinator.py src/app/coordinators/
git mv src/app/review_coordinator.py src/app/coordinators/
git mv src/app/hotspot_coordinator.py src/app/coordinators/

# Utilities
git mv src/app/timing_tracker.py src/app/utilities/
git mv src/app/timing_reporter.py src/app/utilities/
```

#### Steg 3: Uppdatera __init__.py filer för clean imports
```python
# src/app/processing/__init__.py
from .file_reader import FileReader
from .file_analyzer import FileAnalyzer
from .collector import Collector
from .data_converter import DataConverter
from .repository_grouper import RepositoryGrouper

__all__ = [
    'FileReader',
    'FileAnalyzer',
    'Collector',
    'DataConverter',
    'RepositoryGrouper'
]
```

#### Steg 4: Uppdatera alla imports (automatiskt med script)
```python
# update_imports.py
import re
from pathlib import Path

IMPORT_MAPPINGS = {
    'from src.app.file_reader import': 'from src.app.processing.file_reader import',
    'from src.app.timing_tracker import': 'from src.app.utilities.timing_tracker import',
    # ... etc
}

def update_imports(file_path):
    content = file_path.read_text()
    for old, new in IMPORT_MAPPINGS.items():
        content = content.replace(old, new)
    file_path.write_text(content)
```

#### Steg 5: Kör alla tester för att verifiera
```bash
python -m pytest tests/ -v
```

### Impact på Befintlig Kod

#### Minimal Impact med Backward Compatibility:
```python
# src/app/__init__.py
# Maintain backward compatibility
from .processing.file_reader import FileReader
from .utilities.timing_tracker import TimingTracker
from .processing.repository_grouper import RepositoryGrouper

# Old imports still work!
# from src.app.file_reader import FileReader  ✅ Still works
# from src.app.processing import FileReader   ✅ New preferred way
```

## Timing för Omorganisering

### Option A: Omorganisera NU (Före Fas 2 fortsätter)
**Fördelar:**
- Nya klasser (KPIOrchestrator, FileProcessor, KPIAggregator) hamnar direkt på rätt plats
- Undviker dubbel-migration

**Nackdelar:**
- Avbryter Fas 2-momentum
- Stor commit med många ändringar

### Option B: Omorganisera Efter Fas 2 (Rekommenderad)
**Fördelar:**
- Slutför refaktoreringen först
- Separat commit för omorganisering
- Mindre risk

**Nackdelar:**
- Nya filer behöver flyttas efteråt

### Option C: Gradvis (Pragmatisk)
**Fördelar:**
- Nya filer i Fas 2 hamnar direkt i nya strukturen
- Gamla filer flyttas när de modifieras

**Nackdelar:**
- Blandad struktur under övergångsperiod

## Min Rekommendation

**OPTION B + Kompromiss:**

1. **NU:** Skapa nya paket för Fas 2
   ```
   src/app/processing/  (för nya FileProcessor, KPIOrchestrator)
   src/app/utilities/   (timing_tracker, file_reader)
   ```

2. **Efter Fas 2 komplett:** Full omorganisering av gamla filer

3. **Resultat:**
   - Fas 2-klasser hamnar direkt rätt
   - Mindre förvirring
   - Tydlig migration-path

### Konkret Plan för NÄSTA STEG:

```bash
# 1. Skapa nya paket-strukturer
mkdir -p src/app/processing
mkdir -p src/app/utilities

# 2. Flytta Fas 1-klasser
git mv src/app/file_reader.py src/app/utilities/
git mv src/app/timing_tracker.py src/app/utilities/
git mv src/app/repository_grouper.py src/app/processing/

# 3. Skapa __init__.py
# src/app/utilities/__init__.py
# src/app/processing/__init__.py

# 4. Placera nya Fas 2-klasser i processing/
# - kpi_orchestrator.py → src/app/processing/
# - file_processor.py → src/app/processing/
# - kpi_aggregator.py → src/app/processing/

# 5. Uppdatera imports i test-filer
# 6. Kör alla tester
# 7. Commit som "refactor: Organize app package structure"
```

## Sammanfattning

**JA, det är mycket klokt att dela upp app-paketet!**

**Rekommenderad approach:**
1. Skapa `processing/` och `utilities/` NU
2. Flytta Fas 1-klasser dit
3. Placera Fas 2-klasser där direkt
4. Full omorganisering av gamla filer efter Fas 2

**Detta ger:**
- ✅ Bättre struktur från start
- ✅ Enklare att hitta kod
- ✅ Skalbar arkitektur
- ✅ Tydlig separation of concerns
- ✅ Förbättrad testbarhet

Vill du att jag implementerar detta NU innan vi fortsätter med Fas 2?
