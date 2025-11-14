# Root Directory Cleanup Plan

**Created:** 2025-11-12 **Status:** Draft **Goal:** Reorganize project root from 45+ files/directories to a clean,
maintainable structure

## Current Problems

1. **45+ items in root directory** - hard to navigate
2. **Documentation scattered** - Some in root, some in docs/
3. **Utility scripts mixed** with core config files
4. **Temporary/generated files** tracked in git
5. **Old/unused directories** (labs/, venv/, custom_output/, test_output/)

## Target Structure

```
MetricMancer/
├── .github/workflows/        # CI/CD (keep as-is)
├── docs/                     # ALL documentation here
│   ├── chores/              # Maintenance plans (this file!)
│   ├── notes/               # Issue notes, planning docs
│   ├── presentations/       # Presentation materials
│   └── *.md                 # All major documentation
├── mermaid/                  # Diagram sources
├── plantuml/                 # Diagram sources
├── scripts/                  # NEW - Utility scripts
│   ├── check_licenses.py
│   ├── clean_output.py
│   ├── code_quality.py
│   └── *.sh, *.py
├── src/                      # Source code (keep as-is)
├── tests/                    # Tests (keep as-is)
├── .coveragerc               # Config files (keep in root)
├── .flake8
├── .gitignore
├── .python-version
├── CHANGELOG.md              # User-facing docs (keep in root)
├── CLAUDE.md                 # Used by Claude Code
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── pyproject.toml            # MAIN config
├── README.md
└── setup.py
```

**Result:** ~15 files/dirs in root (down from 45+)

______________________________________________________________________

## Implementation Plan

### Phase 1: Create New Structure ✅

```bash
# Create new directories
mkdir -p docs/chores
mkdir -p docs/notes
mkdir -p docs/presentations
mkdir -p scripts
```

### Phase 2: Move Documentation Files 📝

```bash
# Major documentation → docs/
git mv ARCHITECTURE.md docs/
git mv MIGRATION_GUIDE.md docs/
git mv SoftwareSpecificationAndDesign.md docs/
git mv LICENSE_INFO.md docs/

# Issue notes → docs/notes/
git mv issue--code-churn-time-based-fix.md docs/notes/
git mv issue-fix--churn-fix-implementation-plan.md docs/notes/

# Presentations → docs/presentations/
git mv MetricMancer_presentation.md docs/presentations/
git mv MetricMancer_presentation.pptx docs/presentations/
```

**Files moved:** 8 files

### Phase 3: Move Utility Scripts 🔧

```bash
# Python scripts → scripts/
git mv check_licenses.py scripts/
git mv clean_output.py scripts/
git mv code_quality.py scripts/
git mv MD012-no-multiple-blanks-fixer.py scripts/
git mv run_tests.sh scripts/

# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

**Files moved:** 5 files

### Phase 4: Remove Temporary/Generated Files 🗑️

```bash
# Generated reports (should never be in git)
git rm --cached complexity_report.json
git rm --cached quick-wins-report.txt
rm -f complexity_report.json quick-wins-report.txt

# MacOS metadata
rm -f .DS_Store

# Unnecessary files
git rm __init__.py  # Not needed in project root
git rm --cached .bashrc  # Why is this here?

# Empty/unused directories
rm -rf custom_output/  # Empty
rm -rf test_output/    # Contains 1 test file - review.md
```

**Files removed:** ~6 files

### Phase 5: Handle Special Cases 🤔

#### A. Labs directory

**Options:**

1. Keep as-is (if actively used for experiments)
2. Archive to `archive/labs/`
3. Delete entirely (if obsolete)

**Decision needed:** Check with team/user

```bash
# Option 1: Keep (do nothing)
# Option 2: Archive
mkdir -p archive
git mv labs/ archive/

# Option 3: Delete
git rm -rf labs/
```

#### B. Old venv directories

```bash
# Remove old venv (use .venv instead)
rm -rf venv/
rm -rf .venv-py310/  # Development venv, not tracked

# Already in .gitignore, verify:
git check-ignore venv/ .venv/ .venv-py310/
```

#### C. Sample/Test directories

```bash
# SampleWebpage - old HTML sample, likely obsolete
git rm -rf SampleWebpage/

# test_output - temporary test artifacts
rm -rf test_output/
```

#### D. MetricMancer.code-workspace

**Decision:** Keep or remove?

- **Keep:** If team uses VSCode workspaces
- **Remove:** Personal preference, not needed for project

```bash
# Option to remove:
git rm MetricMancer.code-workspace
```

### Phase 6: Update .gitignore 📝

Add patterns for files that should never be tracked:

```bash
# Edit .gitignore - add these patterns:
```

```gitignore
# Python
__pycache__/
*.egg-info/
*.pyc
*.pyo

# Virtual environments
.venv/
.venv-*/
venv/
venv-*/

# IDE
.vscode/
*.code-workspace
.DS_Store

# Generated reports (should go in output/)
complexity_report*.json
quick-wins-report.txt
*report*.json  # Already there but verify
*report*.txt   # Already there but verify

# Temporary directories
custom_output/
test_output/
tmp/

# Issue notes (use docs/notes/ instead)
issue--*.md
issue-fix--*.md
```

### Phase 7: Update References 🔗

#### A. Update Makefile

```bash
# Edit Makefile - update script paths
```

**Changes needed:**

```makefile
# OLD
python check_licenses.py
python clean_output.py
python code_quality.py

# NEW
python scripts/check_licenses.py
python scripts/clean_output.py
python scripts/code_quality.py
```

**Files to update:** `Makefile`

#### B. Update README.md

```bash
# Edit README.md - update documentation links
```

**Changes needed:**

```markdown
# OLD
[Architecture Documentation](ARCHITECTURE.md)
[Migration Guide](MIGRATION_GUIDE.md)
[Software Specification](SoftwareSpecificationAndDesign.md)
[License Information](LICENSE_INFO.md)

# NEW
[Architecture Documentation](docs/ARCHITECTURE.md)
[Migration Guide](docs/MIGRATION_GUIDE.md)
[Software Specification](docs/SoftwareSpecificationAndDesign.md)
[License Information](docs/LICENSE_INFO.md)
```

#### C. Update CLAUDE.md

```bash
# Edit CLAUDE.md - update documentation references
```

**Changes needed:**

```markdown
# OLD
- `ARCHITECTURE.md` - Detailed patterns
- `SoftwareSpecificationAndDesign.md` - Requirements
- `MIGRATION_GUIDE.md` - Migration guide

# NEW
- `docs/ARCHITECTURE.md` - Detailed patterns
- `docs/SoftwareSpecificationAndDesign.md` - Requirements
- `docs/MIGRATION_GUIDE.md` - Migration guide
```

#### D. Update CONTRIBUTING.md

```bash
# Edit CONTRIBUTING.md - update script references
```

**Changes needed:**

```markdown
# OLD
python code_quality.py help
./run_tests.sh

# NEW
python scripts/code_quality.py help
./scripts/run_tests.sh
```

#### E. Update cross-references in docs/

Search all documentation for broken links:

```bash
# Find all markdown files referencing moved docs
grep -r "ARCHITECTURE\.md" docs/
grep -r "SoftwareSpecificationAndDesign\.md" docs/
grep -r "LICENSE_INFO\.md" docs/
grep -r "MIGRATION_GUIDE\.md" docs/

# Update each reference from root path to docs/ path
```

### Phase 8: Verify Everything Works ✅

```bash
# 1. Check all tests pass
make test

# 2. Check linting works
make lint

# 3. Check Makefile commands work
make help
make clean
make check

# 4. Verify scripts are executable
ls -l scripts/*.sh scripts/*.py

# 5. Check documentation links
# Manually verify links in README.md, CLAUDE.md, CONTRIBUTING.md

# 6. Run MetricMancer
python -m src.main src/ --output-format summary

# 7. Check git status
git status
```

### Phase 9: Commit Changes 📦

```bash
# Stage all changes
git add -A

# Commit with detailed message
git commit -m "chore: reorganize project root directory structure

## Summary
Reduced root directory from 45+ items to ~15 core files by consolidating
documentation, scripts, and removing temporary/generated files.

## Changes

### Documentation (moved to docs/)
- ARCHITECTURE.md → docs/ARCHITECTURE.md
- MIGRATION_GUIDE.md → docs/MIGRATION_GUIDE.md
- SoftwareSpecificationAndDesign.md → docs/SoftwareSpecificationAndDesign.md
- LICENSE_INFO.md → docs/LICENSE_INFO.md
- issue--*.md → docs/notes/
- MetricMancer_presentation.* → docs/presentations/

### Scripts (moved to scripts/)
- check_licenses.py → scripts/check_licenses.py
- clean_output.py → scripts/clean_output.py
- code_quality.py → scripts/code_quality.py
- MD012-no-multiple-blanks-fixer.py → scripts/MD012-no-multiple-blanks-fixer.py
- run_tests.sh → scripts/run_tests.sh

### Removed
- complexity_report.json (generated file)
- quick-wins-report.txt (generated file)
- __init__.py (unnecessary in root)
- .DS_Store (MacOS metadata)
- SampleWebpage/ (obsolete sample)
- custom_output/ (empty directory)
- test_output/ (temporary test artifacts)
- venv/ (old virtual environment)

### Updated
- Makefile: Updated script paths
- README.md: Updated documentation links
- CLAUDE.md: Updated documentation references
- CONTRIBUTING.md: Updated script references
- .gitignore: Added patterns for temporary/generated files

## Testing
✅ All 839 tests pass
✅ Makefile commands work
✅ Scripts executable and functional
✅ Documentation links verified

## Motivation
Improves project navigation and maintainability by organizing files into
logical directories. Follows Python project best practices with clean root
containing only essential configuration and user-facing documentation.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

______________________________________________________________________

## Rollback Plan 🔄

If something breaks:

```bash
# Rollback all changes
git reset --hard HEAD~1

# Or rollback specific files
git checkout HEAD~1 -- <file_path>
```

______________________________________________________________________

## Detailed File Inventory

### ✅ Keep in Root (15 items)

```
.github/          # CI/CD workflows
.coveragerc       # Coverage config
.flake8           # Linting config
.gitignore        # Git ignore patterns
.python-version   # Python version requirement
CHANGELOG.md      # Release history (user-facing)
CLAUDE.md         # Claude Code instructions
CONTRIBUTING.md   # Contributor guide (user-facing)
LICENSE           # License file
Makefile          # Build commands
pyproject.toml    # Main configuration
README.md         # Project overview (user-facing)
setup.py          # Setup script
src/              # Source code
tests/            # Test code
```

### 📦 Move to docs/ (8 files)

```
ARCHITECTURE.md                           → docs/ARCHITECTURE.md
LICENSE_INFO.md                           → docs/LICENSE_INFO.md
MIGRATION_GUIDE.md                        → docs/MIGRATION_GUIDE.md
SoftwareSpecificationAndDesign.md         → docs/SoftwareSpecificationAndDesign.md
issue--code-churn-time-based-fix.md       → docs/notes/issue--code-churn-time-based-fix.md
issue-fix--churn-fix-implementation-plan.md → docs/notes/issue-fix--churn-fix-implementation-plan.md
MetricMancer_presentation.md              → docs/presentations/MetricMancer_presentation.md
MetricMancer_presentation.pptx            → docs/presentations/MetricMancer_presentation.pptx
```

### 🔧 Move to scripts/ (5 files)

```
check_licenses.py              → scripts/check_licenses.py
clean_output.py                → scripts/clean_output.py
code_quality.py                → scripts/code_quality.py
MD012-no-multiple-blanks-fixer.py → scripts/MD012-no-multiple-blanks-fixer.py
run_tests.sh                   → scripts/run_tests.sh
```

### 🗑️ Remove (10+ items)

```
complexity_report.json         # Generated file
quick-wins-report.txt          # Generated file
.DS_Store                      # MacOS metadata
__init__.py                    # Unnecessary in root
.bashrc                        # Why is this here?
SampleWebpage/                 # Obsolete sample
custom_output/                 # Empty directory
test_output/                   # Temporary artifacts
venv/                          # Old virtual environment
MetricMancer.code-workspace    # Optional - decide with team
```

### ⚠️ Evaluate (keep or archive)

```
labs/                          # Experimental scripts - archive or keep?
```

______________________________________________________________________

## Post-Cleanup Checklist

After running all commands:

- [ ] Root directory has ~15 items (down from 45+)
- [ ] All tests pass (`make test`)
- [ ] Linting works (`make lint`)
- [ ] Makefile commands functional (`make help`)
- [ ] Scripts executable (`ls -l scripts/`)
- [ ] Documentation links work (manual check)
- [ ] MetricMancer runs (`python -m src.main src/`)
- [ ] Git status clean (or only expected changes)
- [ ] No broken imports or paths
- [ ] `.gitignore` prevents re-tracking removed files

______________________________________________________________________

## Benefits After Cleanup

1. **🧹 Cleaner root** - Easy to find core files (README, LICENSE, pyproject.toml)
2. **📚 Organized docs** - All documentation in one place
3. **🔧 Logical scripts/** - All utilities together
4. **🚫 No tracked artifacts** - Generated files stay local
5. **📖 Better navigation** - Clear separation of concerns
6. **🤝 Easier onboarding** - New contributors find things quickly
7. **✨ Professional structure** - Follows Python best practices

______________________________________________________________________

## Reference: Common Python Project Structure

```
project/
├── docs/              # Documentation
├── src/               # Source code
├── tests/             # Tests
├── scripts/           # Utility scripts
├── .github/           # GitHub-specific (workflows, etc.)
├── pyproject.toml     # Main config (PEP 621)
├── README.md          # Project overview
├── LICENSE            # License
├── CHANGELOG.md       # Version history
├── CONTRIBUTING.md    # Contribution guide
└── Makefile           # Task automation
```

This is what we're aiming for! ✨

______________________________________________________________________

## Questions to Answer Before Execution

1. **labs/ directory** - Keep, archive, or delete?
2. **MetricMancer.code-workspace** - Keep or remove?
3. **.bashrc** - Why is this in the repo? Remove?
4. **test_output/review.md** - Keep or delete?
5. **Presentations** - Are these actively used/updated?

______________________________________________________________________

## Timeline

**Estimated time:** 30-45 minutes

- Phase 1-3: 10 minutes (file moves)
- Phase 4-5: 5 minutes (deletions)
- Phase 6: 5 minutes (.gitignore)
- Phase 7: 15 minutes (update references)
- Phase 8: 10 minutes (verification)
- Phase 9: 5 minutes (commit)

**Ready to execute?** Run commands in order, test after each phase!
