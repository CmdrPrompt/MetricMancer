# PlantUML Diagrams

This folder contains PlantUML class diagrams for MetricMancer.

## Architecture Diagrams

### Current Architecture (Configuration Object Pattern)

**[architecture_config_pattern_2025-10-14.puml](architecture_config_pattern_2025-10-14.puml)** ⭐ **NEW**
- Shows the new architecture with Configuration Object Pattern and Factory Pattern
- Documents the refactoring that reduced main.py code churn
- Includes AppConfig, ReportGeneratorFactory, and MetricMancerApp
- **[Description](architecture_config_pattern_2025-10-14_description.md)**

**Key highlights:**
- Configuration Object Pattern for centralized settings
- Factory Pattern for report generator selection
- Dependency Injection for clean architecture
- 100% backward compatibility maintained

## Data Model Diagrams

### Current Data Model

**[data_model_2025-09-24.puml](data_model_2025-09-24.puml)** ⭐ **LATEST**
- Complete data model for MetricMancer
- Shows RepoInfo, ScanDir, File, Function, BaseKPI
- **[Description](data_model_2025-09-24_descriptions.md)**
- **[SVG Export](data_model_2025-09-24.svg)**

**Note:** This data model is **unchanged** by the Configuration Object Pattern refactoring. The refactoring affected application architecture, not data structures.

### Previous Data Model

**[datamodel_2025-09-16.puml](datamodel_2025-09-16.puml)**
- Earlier version of the data model
- Kept for historical reference
- Use latest version (2025-09-24) instead

## Diagram Types

### Architecture Diagrams
Focus on **application structure** and **design patterns**:
- Main entry point flow
- Configuration management
- Factory patterns
- Component relationships

### Data Model Diagrams
Focus on **data structures** and **relationships**:
- Entity relationships
- Data flow
- Hierarchical models
- KPI associations

## Generating Diagrams

### Using PlantUML

1. **Install PlantUML**:
   ```bash
   # Via package manager
   brew install plantuml  # macOS
   apt install plantuml   # Ubuntu/Debian
   
   # Or download from: https://plantuml.com/download
   ```

2. **Generate PNG**:
   ```bash
   plantuml diagram.puml
   ```

3. **Generate SVG**:
   ```bash
   plantuml -tsvg diagram.puml
   ```

### Using VS Code

Install the "PlantUML" extension:
- Extension ID: `jebbs.plantuml`
- Preview: `Alt + D` (Windows/Linux) or `Option + D` (macOS)
- Export: Use command palette "PlantUML: Export Current Diagram"

### Online

Use the online editor: https://www.plantuml.com/plantuml/uml/

## Documentation Links

- **Architecture Documentation**: [/ARCHITECTURE.md](../ARCHITECTURE.md)
- **Migration Guide**: [/MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
- **Mermaid Flow Diagrams**: [/mermaid/](../mermaid/)
- **README**: [/README.md](../README.md)

## Diagram Conventions

### Colors
- 🟢 **Green** (#E8F5E9): New/Updated components
- 🟡 **Orange** (#FFF3E0): Design patterns
- 🔵 **Blue** (#E3F2FD): Core application components
- 🔴 **Red** (#FFEBEE): Legacy/Deprecated

### Stereotypes
- `<<PATTERN>>`: Design pattern implementation
- `<<NEWCLASS>>`: Newly created class
- `<<LEGACY>>`: Deprecated/backward compatibility

### Naming
- Format: `category_description_YYYY-MM-DD.puml`
- Examples:
  - `architecture_config_pattern_2025-10-14.puml`
  - `data_model_2025-09-24.puml`

## Changelog

| Date | Diagram | Change |
|------|---------|--------|
| 2025-10-14 | architecture_config_pattern | New architecture diagram for Configuration Object Pattern |
| 2025-09-24 | data_model | Updated data model with latest structure |
| 2025-09-16 | data_model | Initial data model diagram |

---

**Last Updated**: 2025-10-14
