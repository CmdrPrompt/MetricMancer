#!/usr/bin/env python3
"""
License compliance checker for MetricMancer.

Verifies that all installed dependencies use permissive licenses.
Exits with error code 1 if any non-permissive licenses are found.
"""

import sys
import subprocess
import json
import re
import requests


# Allowed permissive licenses
ALLOWED_LICENSES = {
    'MIT License',
    'MIT',
    'Apache Software License',
    'Apache-2.0',
    'Apache 2.0',
    'Apache License 2.0',
    'BSD License',
    'BSD',
    'BSD-2-Clause',
    'BSD-3-Clause',
    'ISC License',
    'ISC',
    'Mozilla Public License 2.0 (MPL 2.0)',
    'MPL-2.0',
    'PSF-2.0',
    'Python Software Foundation License',
    'zlib/libpng License',
    'Freeware',  # lizard reports as Freeware but is MIT
    'UNKNOWN',  # Local/development packages
}

# Known licenses that contain multiple options (e.g., "MIT License; MPL 2.0")
# We allow these if ANY of the options is permissive
MULTI_LICENSE_SEPARATOR = ';'


LICENSE_NORMALIZATION_MAP = {
    'Apache Software License': 'Apache-2.0',
    'Apache 2.0': 'Apache-2.0',
    'Apache License 2.0': 'Apache-2.0',
    'BSD License': 'BSD',
    'BSD-3-Clause License': 'BSD-3-Clause',
    'BSD-2-Clause License': 'BSD-2-Clause',
    'Mozilla Public License 2.0 (MPL 2.0)': 'MPL-2.0',
    'Python Software Foundation License': 'PSF-2.0',
}

# Forbidden licenses (copyleft)
FORBIDDEN_LICENSES = {
    'GPL',
    'GPLv2',
    'GPLv3',
    'GNU General Public License',
    'LGPL',
    'LGPLv2',
    'LGPLv3',
    'GNU Lesser General Public License',
    'AGPL',
    'AGPLv3',
    'GNU Affero General Public License',
}


def normalize_license_name(license_name):
    """Normalize common license aliases to canonical identifiers."""
    cleaned = (license_name or '').strip()
    return LICENSE_NORMALIZATION_MAP.get(cleaned, cleaned)


def split_license_expression(license_str):
    """
    Split a license expression into comparable license terms.

    Handles typical pip-licenses outputs such as:
    - "MIT OR Apache-2.0"
    - "MPL-2.0 AND MIT"
    - "MIT License; BSD-3-Clause"
    """
    if not license_str:
        return []

    # Split on SPDX operators and semicolon, but keep license names intact.
    def trim_wrapping_parentheses(value):
        value = value.strip()
        while value.startswith('(') and value.endswith(')'):
            value = value[1:-1].strip()
        return value

    raw_parts = [
        trim_wrapping_parentheses(part)
        for part in re.split(r';|\bAND\b|\bOR\b|\bWITH\b', license_str, flags=re.IGNORECASE)
    ]

    return [normalize_license_name(part) for part in raw_parts if part]


def is_allowed_license_term(license_term):
    """Check if a single normalized license term is permissive."""
    if license_term in ALLOWED_LICENSES:
        return True

    # Conservative substring fallback for common, permissive families.
    permissive_markers = ['MIT', 'BSD', 'Apache', 'MPL-2.0', 'ISC', 'PSF-2.0', 'zlib']
    return any(marker in license_term for marker in permissive_markers)


def get_installed_licenses():
    """Get list of installed packages and their licenses."""
    try:
        # Use pip-licenses to get license information
        result = subprocess.run(
            ['pip-licenses', '--format=json', '--with-urls'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running pip-licenses: {e}")
        print("   Make sure pip-licenses is installed: pip install pip-licenses")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing pip-licenses output: {e}")
        sys.exit(1)


def get_license_from_pypi(package_name):
    """Hämta licens och GitHub-länk från PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.ok:
            info = resp.json().get("info", {})
            license = info.get("license", "")
            github_url = ""
            for k, v in (info.get("project_urls") or {}).items():
                if "github" in v.lower():
                    github_url = v
            return license, github_url
    except Exception:
        pass
    return "", ""


def check_license(package_name, license_str):
    """
    Check if a license is allowed.

    Returns: (is_allowed, reason)
    """
    if not license_str or license_str == 'UNKNOWN':
        # Allow UNKNOWN for local packages during development
        if package_name.lower() in ['metricmancer']:
            return True, "Local development package"
        # Försök hämta licens från PyPI
        pypi_license, github_url = get_license_from_pypi(package_name)
        if pypi_license and pypi_license != 'UNKNOWN':
            # Om licensen är tillåten, returnera som permissiv
            normalized_pypi_license = normalize_license_name(pypi_license)
            if is_allowed_license_term(normalized_pypi_license):
                return True, f"Permissive license from PyPI: {pypi_license}"
            else:
                return None, f"PyPI license needs review: {pypi_license} (GitHub: {github_url})"
        # Om ingen licens hittas, returnera info om GitHub-länk
        if github_url:
            return None, f"License UNKNOWN, check GitHub: {github_url}"
        return None, "License UNKNOWN, no PyPI or GitHub info found"

    # Parse SPDX-style expressions and multi-license strings
    license_parts = split_license_expression(license_str)

    for license_part in license_parts:
        # Check forbidden first
        if any(forbidden in license_part for forbidden in FORBIDDEN_LICENSES):
            return False, f"Contains forbidden license: {license_part}"

    # Check if at least one part is allowed (for multi-license packages)
    for license_part in license_parts:
        if is_allowed_license_term(license_part):
            return True, f"Permissive license: {license_part}"

    # If we get here, the license might be okay but not in our known list
    # Be conservative and flag for review
    return None, f"Unknown license that needs review: {license_str}"


def get_pyproject_dependencies():
    """Läs pyproject.toml och returnera runtime- och dev-beroenden."""
    import toml
    try:
        pyproject = toml.load("pyproject.toml")
        deps = set()
        dev_deps = set()
        # Runtime dependencies
        for dep in pyproject.get("project", {}).get("dependencies", []):
            pkg = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
            deps.add(pkg.lower())
        # Dev dependencies
        for dep in pyproject.get("project", {}).get("optional-dependencies", {}).get("dev", []):
            pkg = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
            dev_deps.add(pkg.lower())
        return deps, dev_deps
    except Exception as e:
        print(f"⚠️  Could not parse pyproject.toml: {e}")
        return set(), set()


def main():
    print("🔍 Checking licenses for MetricMancer...")
    print()

    print("📄 MetricMancer Project License:")
    print("   • MetricMancer (3.1.0): MIT License")
    print("     © 2025 Thomas Lindqvist")
    print()

    print("📦 Third-Party Dependencies:")
    print()

    packages = get_installed_licenses()
    runtime_deps, dev_deps = get_pyproject_dependencies()

    # Get dependency tree from pipdeptree
    try:
        result = subprocess.run([
            'pipdeptree', '--json'
        ], capture_output=True, text=True, check=True)
        dep_tree = json.loads(result.stdout)
    except Exception as e:
        print(f"⚠️  Could not get dependency tree: {e}")
        dep_tree = []

    # Build parent mapping: child -> [parents]
    parent_map = {}
    for node in dep_tree:
        parent = node['package']['package_name'].lower()
        for dep in node.get('dependencies', []):
            child = dep['package_name'].lower()
            parent_map.setdefault(child, []).append(parent)

    # Deduplicate packages (keep first occurrence)
    seen_packages = set()
    unique_packages = []
    for package in packages:
        package_key = (package['Name'].lower(), package['Version'])
        if package_key not in seen_packages:
            seen_packages.add(package_key)
            unique_packages.append(package)

    allowed_packages = []
    review_packages = []
    forbidden_packages = []

    for package in unique_packages:
        name = package['Name']
        version = package['Version']
        license_str = package['License']
        pkg_lower = name.lower()

        # Skip metricmancer itself (already shown above)
        if pkg_lower == 'metricmancer':
            continue

        is_allowed, reason = check_license(name, license_str)

        # Visa extra info om licens hämtad från PyPI
        if license_str == 'UNKNOWN' and reason:
            license_str = reason

        # Kategorisera beroende
        if pkg_lower in runtime_deps:
            dep_type = "runtime"
        elif pkg_lower in dev_deps:
            dep_type = "dev"
        else:
            dep_type = "other"

        # Transitive check
        if dep_type == "other" and pkg_lower in parent_map:
            transitive = True
            origins = parent_map[pkg_lower]
        else:
            transitive = False
            origins = []

        entry = (name, version, license_str, reason, dep_type, transitive, origins)

        if is_allowed is True:
            allowed_packages.append(entry)
        elif is_allowed is False:
            forbidden_packages.append(entry)
        else:
            review_packages.append(entry)

    def sort_key(entry):
        # runtime=0, dev=1, other=2
        dep_type = entry[4]
        return {"runtime": 0, "dev": 1, "other": 2}.get(dep_type, 3), entry[0].lower()

    def describe_other_package(name):
        # Försök ge info om vad "other"-paket används till
        # Vanliga "other" är beroenden till dev/runtime, eller installerade via pip
        # Försök hämta info från PyPI
        license, github_url = get_license_from_pypi(name)
        info = f"PyPI: https://pypi.org/project/{name}/"
        if github_url:
            info += f", GitHub: {github_url}"
        return info

    def describe_transitive(transitive, origins):
        if transitive:
            return f"Transitive dependency, required by: {', '.join(origins)}"
        return "Direct dependency"

    # Print results
    if allowed_packages:
        print(f"✅ {len(allowed_packages)} packages with permissive licenses:")
        sorted_allowed = sorted(allowed_packages, key=sort_key)
        for name, version, license_str, reason, dep_type, transitive, origins in sorted_allowed:
            print(f"   • {name} ({version}): {license_str} [{dep_type}]")
            print(f"     {describe_transitive(transitive, origins)}")
            if dep_type == "other":
                print(f"     Info: {describe_other_package(name)}")
        print()

    if review_packages:
        print(f"⚠️  {len(review_packages)} packages need license review:")
        sorted_review = sorted(review_packages, key=sort_key)
        for name, version, license_str, reason, dep_type, transitive, origins in sorted_review:
            print(f"   • {name} ({version}): {license_str} [{dep_type}]")
            print(f"     Reason: {reason}")
            print(f"     {describe_transitive(transitive, origins)}")
            if dep_type == "other":
                print(f"     Info: {describe_other_package(name)}")
        print()

    if forbidden_packages:
        print(f"❌ {len(forbidden_packages)} packages with FORBIDDEN licenses:")
        sorted_forbidden = sorted(forbidden_packages, key=sort_key)
        for name, version, license_str, reason, dep_type, transitive, origins in sorted_forbidden:
            print(f"   • {name} ({version}): {license_str} [{dep_type}]")
            print(f"     Reason: {reason}")
            print(f"     {describe_transitive(transitive, origins)}")
            if dep_type == "other":
                print(f"     Info: {describe_other_package(name)}")
        print()
        print("⛔ COMPLIANCE FAILURE: Remove packages with forbidden licenses!")
        sys.exit(1)

    if review_packages:
        print("⚠️  Some packages need manual license review.")
        print("   Please verify these licenses are permissive and update ALLOWED_LICENSES.")
        sys.exit(1)

    print(f"✅ All {len(allowed_packages)} dependencies use permissive licenses!")
    print("   License compliance check PASSED.")
    sys.exit(0)


if __name__ == '__main__':
    main()
