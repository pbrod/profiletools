# Changelog

## [0.2.0]  2026-08-22

### 🚀 Features
- *(profiletools)* Support profiling class-only methods and inherited methods

### 🐛 Bug Fixes
- Fix line_profiler shutdown error on Python 3.12+ by disabling weakref callback
- *(demo)* Make demo.py Windows-safe by disabling profiler after each example

### ♻️ Refactoring
- *(helpers.py)* Extract common functions from test_profiletoolsXX files into helpers.py
- Change to package layout; move demo to examples
- Isolate profiler tests and lazy-load LineProfiler

### 📚 Documentation
- *(readme)* Revise profiler decision tree and improve section structure
- *(readme)* Improve examples, quick start, and package overview
- Add demo.py showcasing all README examples
- Update README with BSD-3 license and add badges

### 🎨 Styling
- *(README.md)* Cosmetic update
- *(README.md)* Remove obsolete spaces

### 🧪 Testing
- Update tests
- Update test_profiletools02.py
- Add tests/helpers.py
- Add tests/__init__.py
- Add tests/conftest.py

### 🏗️ CI/CD
- Rename ci_test.yml to ci_tests.yml
- Update ci_test.yml
- Add GitHub Actions CI test badge to README

### ⚙️ Maintenance
- Updated test image
- Cleanup
- Update helpers.py
- Update pytest.ini
- Update imports
- Update pyproject.toml
- Prepare release
- Added profiletools.py
- Initial commit
