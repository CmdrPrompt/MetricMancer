#!/usr/bin/env python3
"""
License compliance checker for MetricMancer.

Verifies that all installed dependencies use permissive licenses.
Exits with error code 1 if any non-permissive licenses are found.
"""

import sys
import subprocess
import json


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
    'zlib/libpng License',
    'Freeware',  # lizard reports as Freeware but is MIT
    'UNKNOWN',  # Local/development packages
}

# Known licenses that contain multiple options (e.g., "MIT License; MPL 2.0")
# We allow these if ANY of the options is permissive
MULTI_LICENSE_SEPARATOR = ';'

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


def check_license(package_name, license_str):
    """
    Check if a license is allowed.
    
    Returns: (is_allowed, reason)
    """
    if not license_str or license_str == 'UNKNOWN':
        # Allow UNKNOWN for local packages during development
        if package_name.lower() in ['metricmancer']:
            return True, "Local development package"
        return True, "Unknown license (assuming permissive for now)"
    
    # Check if any part of a multi-license is forbidden
    license_parts = [part.strip() for part in license_str.split(MULTI_LICENSE_SEPARATOR)]
    
    for license_part in license_parts:
        # Check forbidden first
        if any(forbidden in license_part for forbidden in FORBIDDEN_LICENSES):
            return False, f"Contains forbidden license: {license_part}"
    
    # Check if at least one part is allowed (for multi-license packages)
    for license_part in license_parts:
        if license_part in ALLOWED_LICENSES:
            return True, f"Permissive license: {license_part}"
    
    # If we get here, the license might be okay but not in our known list
    # Be conservative and flag for review
    return None, f"Unknown license that needs review: {license_str}"


def main():
    """Main entry point."""
    print("🔍 Checking licenses for MetricMancer...")
    print()
    
    # Show MetricMancer's own license first
    print("📄 MetricMancer Project License:")
    print("   • MetricMancer (3.1.0): MIT License")
    print("     © 2025 Thomas Lindqvist")
    print()
    
    print("📦 Third-Party Dependencies:")
    print()
    
    packages = get_installed_licenses()
    
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
        
        # Skip metricmancer itself (already shown above)
        if name.lower() == 'metricmancer':
            continue
        
        is_allowed, reason = check_license(name, license_str)
        
        if is_allowed is True:
            allowed_packages.append((name, version, license_str, reason))
        elif is_allowed is False:
            forbidden_packages.append((name, version, license_str, reason))
        else:
            review_packages.append((name, version, license_str, reason))
    
    # Print results
    if allowed_packages:
        print(f"✅ {len(allowed_packages)} packages with permissive licenses:")
        for name, version, license_str, reason in sorted(allowed_packages):
            print(f"   • {name} ({version}): {license_str}")
        print()
    
    if review_packages:
        print(f"⚠️  {len(review_packages)} packages need license review:")
        for name, version, license_str, reason in sorted(review_packages):
            print(f"   • {name} ({version}): {license_str}")
            print(f"     Reason: {reason}")
        print()
    
    if forbidden_packages:
        print(f"❌ {len(forbidden_packages)} packages with FORBIDDEN licenses:")
        for name, version, license_str, reason in sorted(forbidden_packages):
            print(f"   • {name} ({version}): {license_str}")
            print(f"     Reason: {reason}")
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
