# License Information

## MetricMancer Project License

**MetricMancer** is licensed under the [MIT License](LICENSE).

**Copyright © 2025 Thomas Lindqvist**

The MIT License is a permissive free software license that allows for reuse, modification, and distribution with minimal
restrictions. See the [LICENSE](LICENSE) file in the root directory for the complete license text.

______________________________________________________________________

## Third-Party Dependencies

MetricMancer uses the following third-party open-source libraries. All dependencies use permissive licenses that allow
free use, modification, and distribution.

## Direct Dependencies

### Core Functionality

| Package                                                                           | Version | License            | Purpose                                         |
| --------------------------------------------------------------------------------- | ------- | ------------------ | ----------------------------------------------- |
| [Jinja2](https://jinja.palletsprojects.com/)                                      | 3.1.6   | BSD License        | Template engine for HTML report generation      |
| [PyYAML](https://pyyaml.org/)                                                     | 6.0.3   | MIT License        | YAML file parsing and configuration             |
| [tqdm](https://github.com/tqdm/tqdm)                                              | 4.67.1  | MIT / MPL 2.0      | Progress bars for CLI                           |
| [tree-sitter](https://tree-sitter.github.io/)                                     | 0.25.2  | MIT License        | Multi-language parsing for cognitive complexity |
| [tree-sitter-language-pack](https://github.com/Goldziher/tree-sitter-language-pack) | 0.11.0  | MIT OR Apache 2.0  | Pre-compiled tree-sitter language grammars      |
| [unidiff](https://github.com/matiasb/python-unidiff)                              | 0.7.5   | MIT License        | Unified diff parsing                            |

### Testing & Development

| Package                                                     | Version | License     | Purpose                         |
| ----------------------------------------------------------- | ------- | ----------- | ------------------------------- |
| [pytest](https://pytest.org/)                               | 8.4.2   | MIT License | Testing framework               |
| [pytest-cov](https://github.com/pytest-dev/pytest-cov)      | 7.0.0   | MIT License | Test coverage reporting         |
| [coverage](https://coverage.readthedocs.io/)                | 7.10.7  | Apache 2.0  | Code coverage measurement       |
| [autopep8](https://github.com/hhatto/autopep8)              | 2.3.2   | MIT License | Automatic PEP 8 code formatting |
| [flake8](https://flake8.pycqa.org/)                         | 7.3.0   | MIT License | Code linting and style checking |
| [mdformat](https://github.com/executablebooks/mdformat)     | 0.7.22  | MIT License | Markdown formatter              |
| [mdformat-gfm](https://github.com/hukkin/mdformat-gfm)      | 1.0.0   | MIT License | GitHub Flavored Markdown plugin |
| [mdformat-tables](https://github.com/executablebooks/mdformat-tables) | 1.0.0   | MIT License | Markdown table formatting plugin |
| [jsonschema](https://github.com/python-jsonschema/jsonschema) | 4.25.1  | MIT License | JSON schema validation          |
| [pipdeptree](https://github.com/tox-dev/pipdeptree)         | 2.30.0  | MIT License | Dependency tree visualization   |
| [requests](https://github.com/psf/requests)                 | 2.32.5  | Apache 2.0  | HTTP library                    |
| [toml](https://github.com/uiri/toml)                        | 0.10.2  | MIT License | TOML parser                     |

## Transitive Dependencies

### Git Operations

| Package                                                        | Version | License      | Purpose                    |
| -------------------------------------------------------------- | ------- | ------------ | -------------------------- |
| [GitPython](https://github.com/gitpython-developers/GitPython) | 3.1.45  | BSD-3-Clause | Git repository interaction |
| [gitdb](https://github.com/gitpython-developers/gitdb)         | 4.0.12  | BSD License  | Git object database        |
| [smmap](https://github.com/gitpython-developers/smmap)         | 5.0.2   | BSD License  | Memory-mapped file support |

### Utilities

| Package                                                      | Version           | License       | Purpose                           |
| ------------------------------------------------------------ | ----------------- | ------------- | --------------------------------- |
| [MarkupSafe](https://palletsprojects.com/p/markupsafe/)      | 3.0.2             | BSD License   | String escaping for Jinja2        |
| [Pygments](https://pygments.org/)                            | 2.19.2            | BSD License   | Syntax highlighting               |
| [packaging](https://github.com/pypa/packaging)               | 25.0              | Apache 2.0 / BSD | Version parsing utilities      |
| [pytz](https://pythonhosted.org/pytz/)                       | 2025.2            | MIT License   | Timezone definitions              |
| [rpds-py](https://github.com/orium/rpds)                     | 0.28.0            | MIT License   | Rust-powered data structures      |
| [typing_extensions](https://github.com/python/typing_extensions) | 4.15.0        | PSF           | Backports for typing module       |
| [urllib3](https://github.com/urllib3/urllib3)                | 2.5.0             | MIT License   | HTTP client for Python            |
| [types-pytz](https://github.com/python/typeshed)             | 2025.2.0.20250809 | Apache 2.0    | Typing stubs for pytz             |
| [pathspec](https://github.com/cpburnz/python-pathspec)       | 0.12.1            | MPL 2.0       | Path pattern matching             |
| [certifi](https://github.com/certifi/python-certifi)         | 2025.11.12        | MPL 2.0       | Mozilla's CA bundle               |
| [charset-normalizer](https://github.com/jawah/charset_normalizer) | 3.4.4        | MIT License   | Character encoding detection      |
| [idna](https://github.com/kjd/idna)                          | 3.11              | BSD-3-Clause  | Internationalized domain names    |
| [attrs](https://github.com/python-attrs/attrs)               | 25.4.0            | MIT License   | Python classes without boilerplate |
| [jsonschema-specifications](https://github.com/python-jsonschema/jsonschema-specifications) | 2025.9.1 | MIT License | JSON Schema meta-schemas |
| [referencing](https://github.com/python-jsonschema/referencing) | 0.37.0         | MIT License   | JSON reference resolution         |
| [markdown-it-py](https://github.com/executablebooks/markdown-it-py) | 3.0.0      | MIT License   | Markdown parser                   |
| [mdit-py-plugins](https://github.com/executablebooks/mdit-py-plugins) | 0.5.0    | MIT License   | Markdown-it plugins               |
| [mdurl](https://github.com/executablebooks/mdurl)            | 0.1.2             | MIT License   | URL utilities for Markdown        |

### Testing Tools

| Package                                              | Version | License     | Purpose                       |
| ---------------------------------------------------- | ------- | ----------- | ----------------------------- |
| [pluggy](https://github.com/pytest-dev/pluggy)       | 1.6.0   | MIT License | Plugin system for pytest      |
| [iniconfig](https://github.com/pytest-dev/iniconfig) | 2.1.0   | MIT License | INI config file parsing       |
| [pycodestyle](https://pycodestyle.pycqa.org/)        | 2.14.0  | MIT License | PEP 8 style checker           |
| [pyflakes](https://github.com/PyCQA/pyflakes)        | 3.4.0   | MIT License | Python source code checker    |
| [mccabe](https://github.com/PyCQA/mccabe)            | 0.7.0   | MIT License | Cyclomatic complexity checker |

### Tree-Sitter Language Support

| Package                                              | Version | License     | Purpose                       |
| ---------------------------------------------------- | ------- | ----------- | ----------------------------- |
| [tree-sitter-c-sharp](https://github.com/tree-sitter/tree-sitter-c-sharp) | 0.23.1 | MIT License | C# grammar for tree-sitter |
| [tree-sitter-embedded-template](https://github.com/tree-sitter/tree-sitter-embedded-template) | 0.25.0 | MIT License | Embedded template grammar |
| [tree-sitter-yaml](https://github.com/tree-sitter-grammars/tree-sitter-yaml) | 0.7.2 | MIT License | YAML grammar for tree-sitter |

### Git and Version Control

| Package                                              | Version | License     | Purpose                       |
| ---------------------------------------------------- | ------- | ----------- | ----------------------------- |
| [GitPython](https://github.com/gitpython-developers/GitPython) | 3.1.45  | BSD-3-Clause | Git repository interaction |

## License Compatibility

All dependencies use **permissive open-source licenses**:

- **MIT License**: Most permissive, allows free use, modification, and distribution
- **Apache License 2.0**: Permissive with explicit patent grant protection
- **BSD License (2-Clause & 3-Clause)**: Permissive with minimal restrictions
- **Mozilla Public License 2.0 (MPL)**: Weak copyleft, file-level, compatible with permissive licenses
- **Python Software Foundation (PSF) License**: Python's official license, permissive and GPL-compatible
- **Freeware**: Free to use without restrictions (lizard)

These licenses are compatible with MetricMancer's MIT License and impose no significant restrictions on use,
modification, or distribution.

## License Verification

To verify licenses of installed dependencies:

```bash
# Install pip-licenses
pip install pip-licenses

# Show all licenses
pip-licenses --format=markdown --order=license

# Check for specific license types
pip-licenses --fail-on="GPL;LGPL;AGPL"
```

## Compliance

MetricMancer complies with all license requirements:

1. ✅ **Attribution**: All third-party licenses are acknowledged in this document
2. ✅ **License Inclusion**: Original license texts are preserved in dependency packages
3. ✅ **No Copyleft Violations**: No GPL/LGPL/AGPL dependencies that would require MetricMancer to change its license
4. ✅ **Patent Grants**: Apache 2.0 dependencies provide explicit patent protection

**Note**: Some packages may show as "UNKNOWN" in automated license checking tools due to these tools not fully
supporting the newer `License-Expression` metadata format (PEP 639). All packages with "UNKNOWN" status have been manually
verified by checking their GitHub repositories and license files to confirm they use permissive licenses compatible with MIT.

## Updates

This document was last updated: **November 19, 2025**

### November 19, 2025

- **Major dependency update**: Migrated from `tree-sitter-languages` to `tree-sitter-language-pack` (v0.11.0, MIT OR Apache 2.0)
- Updated `tree-sitter` version from 0.21.3 to 0.25.2
- Added new direct dependencies:
  - unidiff (0.7.5, MIT License) - Unified diff parsing
  - mdformat (0.7.22, MIT License) - Markdown formatter
  - mdformat-gfm (1.0.0, MIT License) - GitHub Flavored Markdown plugin
  - mdformat-tables (1.0.0, MIT License) - Markdown table formatting
  - jsonschema (4.25.1, MIT License) - JSON schema validation
  - pipdeptree (2.30.0, MIT License) - Dependency tree visualization
  - requests (2.32.5, Apache 2.0) - HTTP library
  - toml (0.10.2, MIT License) - TOML parser
- Added new transitive dependencies with verified licenses:
  - certifi (2025.11.12, MPL 2.0) - Mozilla's CA bundle
  - charset-normalizer (3.4.4, MIT License) - Character encoding detection
  - idna (3.11, BSD-3-Clause) - Internationalized domain names
  - attrs (25.4.0, MIT License) - Python classes without boilerplate
  - jsonschema-specifications (2025.9.1, MIT License) - JSON Schema meta-schemas
  - referencing (0.37.0, MIT License) - JSON reference resolution
  - markdown-it-py (3.0.0, MIT License) - Markdown parser
  - mdit-py-plugins (0.5.0, MIT License) - Markdown-it plugins
  - mdurl (0.1.2, MIT License) - URL utilities for Markdown
  - tree-sitter-c-sharp (0.23.1, MIT License) - C# grammar
  - tree-sitter-embedded-template (0.25.0, MIT License) - Embedded template grammar
  - tree-sitter-yaml (0.7.2, MIT License) - YAML grammar
- Updated version numbers for existing dependencies (rpds-py, typing_extensions, urllib3)
- Manually verified all packages previously showing "UNKNOWN" license status
- Added Python Software Foundation (PSF) License to compatibility section

### November 14, 2025

- Added license information for the following dependencies after manual verification:
  - rpds-py (MIT License)
  - typing_extensions (PSF License)
  - urllib3 (MIT License)
- Confirmed types-pytz uses Apache 2.0 (already listed)
- Added pipdeptree as a development dependency for license checking in pyproject.toml

License information is automatically verified during CI/CD builds. If you add new dependencies, please:

1. Run `pip-licenses` to verify the license is permissive
2. Update this document with the new dependency
3. Ensure the license is compatible with MIT

______________________________________________________________________

For questions about licensing, please open an issue on [GitHub](https://github.com/CmdrPrompt/MetricMancer/issues).
