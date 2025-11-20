# Styling System Integration Test Suite

Comprehensive test suite for validating the styling system integration across different domains, edge cases, and scenarios.

## Overview

This test suite validates:
- ✅ Domain-specific color schemes
- ✅ Shape distribution variations
- ✅ Diagram orientation changes
- ✅ Theme application
- ✅ Edge case handling
- ✅ Visual differences between domains

## Test Domains

1. **E-Commerce** - Online shopping platform
2. **Healthcare** - Patient management system
3. **Fintech** - Banking application
4. **Education** - Online learning platform
5. **IoT** - Device management system

## Edge Cases

- Very short prompts
- Multi-domain prompts
- Empty prompts
- Special characters and unicode

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-mock

# Ensure you're in the backend directory
cd autoagents-backend
```

### Run All Tests

```bash
# Using pytest directly
pytest tests/test_styling_system_integration.py -v

# Using the test runner script
python tests/run_styling_tests.py --verbose
```

### Run Specific Domain

```bash
# Test only e-commerce domain
python tests/run_styling_tests.py --domain e-commerce --verbose

# Test only healthcare domain
python tests/run_styling_tests.py --domain healthcare --verbose
```

### Run with Debug Logging

```bash
python tests/run_styling_tests.py --verbose --debug
```

### Run Edge Cases Only

```bash
python tests/run_styling_tests.py --edge-cases --verbose
```

### Run Specific Test

```bash
# Test color scheme differences
pytest tests/test_styling_system_integration.py::test_color_scheme_differences -v

# Test shape distribution
pytest tests/test_styling_system_integration.py::test_shape_distribution_variation -v

# Test diagram orientation
pytest tests/test_styling_system_integration.py::test_diagram_orientation_changes -v
```

## Test Output

Test results are saved to `tests/output/styling_tests/`:

### Individual Domain Results

- `{domain}_style_config.json` - Style configuration for each domain
- `{domain}_styled_diagram.mmd` - Styled Mermaid diagram example

### Comparison Reports

- `color_scheme_comparison.json` - Color scheme differences
- `shape_distribution_comparison.json` - Shape usage across domains
- `orientation_comparison.json` - Diagram orientation analysis
- `theme_application_comparison.json` - Theme usage analysis
- `styling_comparison_report.json` - Comprehensive comparison report

### Edge Case Results

- `edge_case_{name}.json` - Results for each edge case

## Test Structure

### Domain Tests

```python
@pytest.mark.parametrize("domain_name,domain_data", [...])
def test_domain_styling(domain_name, domain_data, output_dir, test_results):
    """Test that each domain generates distinct styling."""
    # Validates:
    # - Domain detection
    # - Color schemes
    # - Theme application
    # - Init directive generation
```

### Validation Tests

- `test_color_scheme_differences()` - Ensures colors differ between domains
- `test_shape_distribution_variation()` - Validates shape usage
- `test_diagram_orientation_changes()` - Checks orientation changes
- `test_theme_application()` - Verifies theme application

### Edge Case Tests

```python
@pytest.mark.parametrize("edge_case_name,edge_case_data", [...])
def test_edge_cases(edge_case_name, edge_case_data, output_dir):
    """Test edge cases for styling system."""
    # Handles:
    # - Very short prompts
    # - Multi-domain prompts
    # - Empty prompts
    # - Special characters
```

## Expected Results

### Color Schemes

Each domain should have distinct colors:
- **E-Commerce**: Blue (#2563EB) and Orange (#F97316)
- **Healthcare**: Green (#10B981) and White (#F9FAFB)
- **Fintech**: Navy (#1E3A8A) and Gold (#F59E0B)
- **Education**: Purple (#7C3AED) and Yellow (#FCD34D)
- **IoT**: Cyan (#06B6D4) and Dark Gray (#374151)

### Themes

Themes should be selected from: `base`, `default`, `forest`, `dark`, `neutral`

### Diagram Types

Based on complexity, diagrams should use:
- `flowchart TD` - Simple top-down
- `flowchart LR` - Complex workflows
- `stateDiagram-v2` - State-heavy systems
- `graph TB` - Data flows

## Debugging

### Enable Debug Logging

```bash
python tests/run_styling_tests.py --verbose --debug
```

### Check Test Output

```bash
# View test results
cat tests/output/styling_tests/styling_comparison_report.json | jq

# View specific domain result
cat tests/output/styling_tests/e-commerce_style_config.json | jq
```

### Common Issues

1. **Import Errors**: Ensure you're running from the backend directory
   ```bash
   cd autoagents-backend
   python -m pytest tests/test_styling_system_integration.py
   ```

2. **Missing Output Directory**: Tests create it automatically, but ensure write permissions

3. **Style Config Errors**: Check that `StyleConfigGenerator` is properly imported

## Test Coverage

- ✅ Domain detection accuracy
- ✅ Color scheme generation
- ✅ Theme selection
- ✅ Init directive generation
- ✅ Style application to diagrams
- ✅ Shape distribution
- ✅ Diagram orientation
- ✅ Edge case handling
- ✅ Comparison report generation

## Continuous Integration

To run tests in CI:

```yaml
# Example GitHub Actions
- name: Run Styling Tests
  run: |
    cd autoagents-backend
    pip install pytest pytest-mock
    pytest tests/test_styling_system_integration.py -v --tb=short
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add debug logging for troubleshooting
3. Save results to output directory
4. Update this README with new test cases
5. Ensure tests are deterministic

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Ensure you're in the correct directory
cd autoagents-backend

# Install dependencies
pip install -r requirements.txt

# Run with Python module syntax
python -m pytest tests/test_styling_system_integration.py
```

### No Output Generated

- Check that output directory is writable
- Verify test actually ran (check pytest output)
- Enable debug logging to see what's happening

### Color Schemes Not Different

- Check domain detection is working
- Verify `DOMAIN_COLOR_PALETTES` in `style_config_generator.py`
- Review test output JSON files

## Example Output

```
============================================================
STYLING SYSTEM TEST SUMMARY
============================================================
Domains tested: 5
Unique primary colors: 5
Unique themes: 3
Average complexity: 15.2
Unique diagram types: 4
============================================================

Full report saved to: tests/output/styling_tests/styling_comparison_report.json
============================================================
```

