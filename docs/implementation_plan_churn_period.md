# Implementation Plan: --churn-period CLI Flag

## Översikt

Lägg till en CLI-flagga `--churn-period` som gör det möjligt att styra tidsperioden (i dagar) för churn-mätningar.

**Standard**: 30 dagar (om inte annat anges)

______________________________________________________________________

## 1. Lägg till CLI-flagga

**Fil**: `src/utilities/cli_helpers.py`

**Ändring**:

```python
parser.add_argument(
    '--churn-period',
    type=int,
    default=30,
    help='Number of days to analyze for code churn (default: 30)'
)
```

______________________________________________________________________

## 2. Uppdatera MetricMancerApp

**Fil**: `src/app/metric_mancer_app.py`

**Ändring**:

- Ta emot `churn_period` som parameter i konstruktorn
- Skicka vidare `churn_period` till relevanta KPI-klasser (CodeChurn)

```python
def __init__(self, ..., churn_period=30):
    self.churn_period = churn_period
    # ...
```

______________________________________________________________________

## 3. Uppdatera CodeChurn KPI

**Fil**: `src/kpis/codechurn/code_churn.py`

**Ändring**:

- Ta emot `churn_period` som parameter
- Använd `churn_period` vid beräkning av churn (t.ex. `git log --since="{churn_period} days ago"`)

```python
def __init__(self, ..., churn_period=30):
    self.churn_period = churn_period

def calculate(self, file):
    # Använd self.churn_period i git-kommandot
    since_date = f"{self.churn_period} days ago"
    # ...
```

______________________________________________________________________

## 4. Uppdatera main.py

**Fil**: `src/main.py`

**Ändring**:

- Läs `args.churn_period` från CLI
- Skicka vidare till `MetricMancerApp`

```python
app = MetricMancerApp(
    directories=args.directories,
    churn_period=args.churn_period,
    # ...
)
```

______________________________________________________________________

## 5. Lägg till tester

**Fil**: `tests/test_main.py`

**Test**:

- Verifiera att `--churn-period 60` sätter korrekt värde
- Verifiera att default är 30

**Fil**: `tests/kpis/codechurn/test_code_churn.py`

**Test**:

- Verifiera att CodeChurn använder rätt tidsperiod vid beräkning

______________________________________________________________________

## 6. Uppdatera dokumentation

**Fil**: `README.md`

**Ändring**:

- Lägg till `--churn-period` i "Common Options"
- Lägg till exempel: `python -m src.main src --churn-period 30`

**Fil**: `docs/future_enhancements.md`

**Ändring**:

- Markera denna funktion som implementerad

______________________________________________________________________

## 7. Test och verifiering

1. Kör `python -m src.main src --churn-period 60`
2. Verifiera att churn-beräkningen använder 60 dagar
3. Kör `python -m src.main src` (utan flagga)
4. Verifiera att default (30 dagar) används
5. Kör hela testsviten: `pytest tests/ -v`

______________________________________________________________________

## Estimat

- **Tid**: 2-3 timmar
- **Komplexitet**: Låg till medel
- **Beroenden**: Ingen

______________________________________________________________________

## Checklist

- [ ] Lägg till CLI-flagga i cli_helpers.py
- [ ] Uppdatera MetricMancerApp konstruktor
- [ ] Uppdatera CodeChurn KPI
- [ ] Uppdatera main.py
- [ ] Lägg till tester
- [ ] Uppdatera README.md
- [ ] Test och verifiering
- [ ] Commit och push
