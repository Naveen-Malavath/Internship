# Styling System Test Suite

## Overview

A comprehensive test suite that validates the styling system integration across 5 different domains, tests edge cases, and generates comparison reports showing visual differences.

## Test Coverage

### 1. Domain-Specific Tests (5 Domains)

- **E-Commerce**: Online shopping platform
- **Healthcare**: Patient management system  
- **Fintech**: Banking application
- **Education**: Online learning platform
- **IoT**: Device management system

### 2. Validation Tests

- ✅ **Color Scheme Differences**: Ensures each domain has distinct colors
- ✅ **Shape Distribution**: Validates shape usage varies appropriately
- ✅ **Diagram Orientation**: Checks orientation changes based on complexity
- ✅ **Theme Application**: Verifies themes are correctly applied

### 3. Edge Cases

- Very short prompts ("Build app")
- Multi-domain prompts (healthcare + e-commerce + fintech)
- Empty prompts
- Special characters and unicode

## Quick Start

### Installation

```bash
cd autoagents-backend
pip install pytest pytest-mock
```

### Run All Tests

```bash
# Using pytest
pytest tests/test_styling_system_integration.py -v

# Using test runner
python tests/run_styling_tests.py --verbose
```

### Run Specific Domain

```bash
python tests/run_styling_tests.py --domain healthcare --verbose
```

### Run with Debug Logging

```bash
python tests/run_styling_tests.py --verbose --debug
```

## Test Structure

```
tests/
├── test_styling_system_integration.py  # Main test suite
├── run_styling_tests.py                # Test runner script
├── conftest.py                         # Pytest fixtures
└── README_STYLING_TESTS.md            # Detailed documentation

tests/output/styling_tests/            # Test results (generated)
├── e-commerce_style_config.json
├── healthcare_style_config.json
├── ...
├── color_scheme_comparison.json
├── shape_distribution_comparison.json
├── orientation_comparison.json
└── styling_comparison_report.json
```

## What Gets Tested

### 1. Domain Detection

```python
def test_domain_styling(domain_name, domain_data):
    """Validates domain is correctly detected from prompt."""
    # Checks:
    # - Domain matches expected domain
    # - Color scheme matches domain
    # - Theme is selected
    # - Init directive is generated
```

### 2. Color Scheme Validation

```python
def test_color_scheme_differences(test_results):
    """Ensures colors differ between domains."""
    # Validates:
    # - Each domain has unique primary color
    # - Colors match expected domain colors
    # - No duplicate color schemes
```

### 3. Shape Distribution

```python
def test_shape_distribution_variation():
    """Tests that shape distributions vary appropriately."""
    # Analyzes:
    # - Stadium shapes (controllers)
    # - Rectangles (services)
    # - Diamonds (decisions)
    # - Cylinders (databases)
    # - Parallelograms (external)
    # - Circles (UI)
```

### 4. Diagram Orientation

```python
def test_diagram_orientation_changes():
    """Tests that orientations change based on complexity."""
    # Checks:
    # - flowchart TD (top-down) for simple
    # - flowchart LR (left-right) for complex
    # - stateDiagram-v2 for state-heavy
    # - graph TB for data flows
```

### 5. Theme Application

```python
def test_theme_application():
    """Validates themes are applied correctly."""
    # Verifies:
    # - Theme in init directive
    # - Theme variables included
    # - Valid theme names
```

### 6. Edge Cases

```python
def test_edge_cases(edge_case_name, edge_case_data):
    """Tests edge cases don't crash."""
    # Handles:
    # - Very short prompts
    # - Multi-domain prompts
    # - Empty prompts
    # - Special characters
```

## Expected Results

### Color Schemes by Domain

| Domain | Primary Color | Secondary Color |
|--------|--------------|-----------------|
| E-Commerce | #2563EB (Blue) | #F97316 (Orange) |
| Healthcare | #10B981 (Green) | #F9FAFB (White) |
| Fintech | #1E3A8A (Navy) | #F59E0B (Gold) |
| Education | #7C3AED (Purple) | #FCD34D (Yellow) |
| IoT | #06B6D4 (Cyan) | #374151 (Dark Gray) |

### Themes

Themes should be selected from: `base`, `default`, `forest`, `dark`, `neutral`

### Diagram Types

Based on complexity score:
- **< 10**: `flowchart TD` (simple)
- **10-15**: `flowchart LR` (complex workflow)
- **> 15 + state**: `stateDiagram-v2` (state-heavy)
- **> 12 + data flow**: `graph TB` (data flows)

## Test Output

### Individual Domain Results

Each domain generates:
- `{domain}_style_config.json` - Complete style configuration
- `{domain}_styled_diagram.mmd` - Example styled Mermaid diagram

### Comparison Reports

- **color_scheme_comparison.json**: Color differences between domains
- **shape_distribution_comparison.json**: Shape usage analysis
- **orientation_comparison.json**: Diagram orientation analysis
- **theme_application_comparison.json**: Theme usage
- **styling_comparison_report.json**: Comprehensive comparison

### Example Report

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "test_summary": {
    "total_domains": 5,
    "domains_tested": ["e-commerce", "healthcare", "fintech", "education", "iot"]
  },
  "color_analysis": {
    "unique_primary_colors": 5,
    "all_colors_distinct": true
  },
  "theme_analysis": {
    "unique_themes": 3,
    "most_common_theme": "forest"
  },
  "complexity_analysis": {
    "average_complexity": 15.2,
    "unique_types": 4
  }
}
```

## Debugging

### Enable Debug Logging

```bash
python tests/run_styling_tests.py --verbose --debug
```

### View Test Results

```bash
# View comprehensive report
cat tests/output/styling_tests/styling_comparison_report.json | jq

# View specific domain
cat tests/output/styling_tests/healthcare_style_config.json | jq

# View color comparison
cat tests/output/styling_tests/color_scheme_comparison.json | jq
```

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd autoagents-backend
   python -m pytest tests/test_styling_system_integration.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install pytest pytest-mock
   ```

3. **Output Directory Permissions**
   ```bash
   # Tests create directory automatically, but check permissions
   chmod -R 755 tests/output
   ```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Styling System Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd autoagents-backend
          pip install -r requirements.txt
          pip install pytest pytest-mock
      - name: Run styling tests
        run: |
          cd autoagents-backend
          pytest tests/test_styling_system_integration.py -v --tb=short
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: styling-test-results
          path: autoagents-backend/tests/output/styling_tests/
```

## Test Metrics

The test suite validates:

- ✅ **5 domains** tested
- ✅ **4 edge cases** handled
- ✅ **Color uniqueness** across domains
- ✅ **Theme application** correctness
- ✅ **Shape distribution** variation
- ✅ **Orientation changes** based on complexity
- ✅ **Comparison reports** generated

## Contributing

When adding new tests:

1. Follow existing test structure
2. Add debug logging
3. Save results to output directory
4. Update documentation
5. Ensure tests are deterministic

## Related Documentation

- `STYLING_SYSTEM_INTEGRATION.md` - Integration guide
- `STYLING_INTEGRATION_CODE_EXAMPLES.py` - Code examples
- `STYLING_INTEGRATION_QUICK_REFERENCE.md` - Quick reference
- `tests/README_STYLING_TESTS.md` - Detailed test documentation

