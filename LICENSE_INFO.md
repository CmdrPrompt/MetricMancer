# License Information

## MetricMancer Project License

**MetricMancer** is licensed under the [MIT License](LICENSE).

**Copyright © 2025 Thomas Lindqvist**

The MIT License is a permissive free software license that allows for reuse, modification, and distribution with minimal restrictions. See the [LICENSE](LICENSE) file in the root directory for the complete license text.

---

## Third-Party Dependencies

MetricMancer uses the following third-party open-source libraries. All dependencies use permissive licenses that allow free use, modification, and distribution.

## Direct Dependencies

### Core Functionality

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| [Jinja2](https://jinja.palletsprojects.com/) | 3.1.6 | BSD License | Template engine for HTML report generation |
| [PyYAML](https://pyyaml.org/) | 6.0.3 | MIT License | YAML file parsing and configuration |
| [PyDriller](https://github.com/ishepard/pydriller) | 2.9 | Apache 2.0 | Git repository mining for churn analysis |
| [tqdm](https://github.com/tqdm/tqdm) | 4.67.1 | MIT / MPL 2.0 | Progress bars for CLI |
| [lizard](https://github.com/terryyin/lizard) | 1.17.31 | MIT License | Cyclomatic complexity calculation |

### Testing & Development

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| [pytest](https://pytest.org/) | 8.4.2 | MIT License | Testing framework |
| [pytest-cov](https://github.com/pytest-dev/pytest-cov) | 7.0.0 | MIT License | Test coverage reporting |
| [coverage](https://coverage.readthedocs.io/) | 7.10.7 | Apache 2.0 | Code coverage measurement |
| [autopep8](https://github.com/hhatto/autopep8) | 2.3.2 | MIT License | Automatic PEP 8 code formatting |
| [flake8](https://flake8.pycqa.org/) | 7.3.0 | MIT License | Code linting and style checking |

## Transitive Dependencies

### Git Operations

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| [GitPython](https://github.com/gitpython-developers/GitPython) | 3.1.45 | BSD-3-Clause | Git repository interaction |
| [gitdb](https://github.com/gitpython-developers/gitdb) | 4.0.12 | BSD License | Git object database |
| [smmap](https://github.com/gitpython-developers/smmap) | 5.0.2 | BSD License | Memory-mapped file support |

### Utilities

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| [MarkupSafe](https://palletsprojects.com/p/markupsafe/) | 3.0.2 | BSD License | String escaping for Jinja2 |
| [Pygments](https://pygments.org/) | 2.19.2 | BSD License | Syntax highlighting |
| [packaging](https://github.com/pypa/packaging) | 25.0 | Apache 2.0 / BSD | Version parsing utilities |
| [pytz](https://pythonhosted.org/pytz/) | 2025.2 | MIT License | Timezone definitions |
| [types-pytz](https://github.com/python/typeshed) | 2025.2.0.20250809 | Apache 2.0 | Typing stubs for pytz |
| [pathspec](https://github.com/cpburnz/python-pathspec) | 0.12.1 | MPL 2.0 | Path pattern matching |

### Testing Tools

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| [pluggy](https://github.com/pytest-dev/pluggy) | 1.6.0 | MIT License | Plugin system for pytest |
| [iniconfig](https://github.com/pytest-dev/iniconfig) | 2.1.0 | MIT License | INI config file parsing |
| [pycodestyle](https://pycodestyle.pycqa.org/) | 2.14.0 | MIT License | PEP 8 style checker |
| [pyflakes](https://github.com/PyCQA/pyflakes) | 3.4.0 | MIT License | Python source code checker |
| [mccabe](https://github.com/PyCQA/mccabe) | 0.7.0 | MIT License | Cyclomatic complexity checker |

## License Compatibility

All dependencies use **permissive open-source licenses**:

- **MIT License**: Most permissive, allows free use, modification, and distribution
- **Apache License 2.0**: Permissive with explicit patent grant protection
- **BSD License (2-Clause & 3-Clause)**: Permissive with minimal restrictions
- **Mozilla Public License 2.0 (MPL)**: Weak copyleft, file-level, compatible with permissive licenses

These licenses are compatible with MetricMancer's MIT License and impose no significant restrictions on use, modification, or distribution.

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

**Note**: Some packages (like `types-pytz`) may show as "UNKNOWN" in `pip-licenses` output due to the tool not fully supporting the newer `License-Expression` metadata format. These packages have been manually verified to use permissive licenses.

## Updates

This document was last updated: **October 23, 2025**

License information is automatically verified during CI/CD builds. If you add new dependencies, please:

1. Run `pip-licenses` to verify the license is permissive
2. Update this document with the new dependency
3. Ensure the license is compatible with MIT

---

For questions about licensing, please open an issue on [GitHub](https://github.com/CmdrPrompt/MetricMancer/issues).
