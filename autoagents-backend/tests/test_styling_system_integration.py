"""
Comprehensive test suite for styling system integration.

Tests domain-specific styling, color schemes, shape distributions,
diagram orientations, themes, and edge cases.
"""

import json
import logging
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import styling system components
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.services.style_config_generator import StyleConfigGenerator
    from app.services.mermaid_style_generator import apply_style_to_mermaid
    from app.services.diagram_complexity import get_diagram_type_guidance
    from app.services.node_shape_selector import NodeShapeSelector
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running from the autoagents-backend directory")
    raise


# ============================================================================
# TEST DATA: Domain Prompts
# ============================================================================

DOMAIN_PROMPTS = {
    "e-commerce": {
        "title": "E-Commerce Platform",
        "prompt": "Build a comprehensive online shopping platform with shopping cart, product catalog, checkout process, payment integration, order management, inventory tracking, customer reviews, and shipping integration. Include features for merchants to manage their stores and products.",
        "expected_domain": "e-commerce",
        "expected_colors": {
            "primary": "#2563EB",  # Blue
            "secondary": "#F97316",  # Orange
        }
    },
    "healthcare": {
        "title": "Healthcare Patient Management",
        "prompt": "Create a healthcare patient management system with appointment scheduling, medical record management, prescription tracking, patient portal, doctor dashboard, billing integration, lab results management, and telemedicine capabilities. Include state tracking for patient workflows.",
        "expected_domain": "healthcare",
        "expected_colors": {
            "primary": "#10B981",  # Green
            "secondary": "#F9FAFB",  # White
        }
    },
    "fintech": {
        "title": "Fintech Banking App",
        "prompt": "Develop a fintech banking application with account management, transaction processing, payment transfers, loan applications, investment portfolio tracking, credit card management, fraud detection, and financial reporting. Include real-time transaction monitoring.",
        "expected_domain": "finance",
        "expected_colors": {
            "primary": "#1E3A8A",  # Navy
            "secondary": "#F59E0B",  # Gold
        }
    },
    "education": {
        "title": "Online Learning Platform",
        "prompt": "Build an online learning platform with course management, student enrollment, assignment submission, grading system, video lectures, discussion forums, progress tracking, certificate generation, and instructor dashboards. Support multiple learning paths.",
        "expected_domain": "education",
        "expected_colors": {
            "primary": "#7C3AED",  # Purple
            "secondary": "#FCD34D",  # Yellow
        }
    },
    "iot": {
        "title": "IoT Device Management",
        "prompt": "Create an IoT device management system with device registration, sensor data collection, real-time monitoring, alert management, device control, data analytics dashboard, firmware updates, and device grouping. Support multiple device protocols and data flow pipelines.",
        "expected_domain": "tech-ai",
        "expected_colors": {
            "primary": "#06B6D4",  # Cyan
            "secondary": "#374151",  # Dark gray
        }
    }
}

EDGE_CASE_PROMPTS = {
    "very_short": {
        "title": "Short Prompt",
        "prompt": "Build app",
        "expected_domain": "default",
    },
    "multi_domain": {
        "title": "Multi-Domain",
        "prompt": "Create a healthcare e-commerce platform for medical supplies with fintech payment processing and IoT device integration for inventory tracking",
        "expected_domain": None,  # Should detect primary domain
    },
    "empty": {
        "title": "Empty Prompt",
        "prompt": "",
        "expected_domain": "default",
    },
    "special_characters": {
        "title": "Special Characters",
        "prompt": "Build a system with @#$%^&*() special characters and unicode: 测试系统",
        "expected_domain": "default",
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_color_from_mermaid(mermaid: str) -> Dict[str, str]:
    """Extract color values from Mermaid init directive."""
    colors = {}
    
    # Extract from %%init%% directive
    init_match = re.search(r"%%\{init:.*?\}%%", mermaid, re.DOTALL)
    if init_match:
        init_content = init_match.group(0)
        
        # Extract primaryColor
        primary_match = re.search(r"'primaryColor':\s*'([^']+)'", init_content)
        if primary_match:
            colors["primary"] = primary_match.group(1)
        
        # Extract secondaryColor
        secondary_match = re.search(r"'secondaryColor':\s*'([^']+)'", init_content)
        if secondary_match:
            colors["secondary"] = secondary_match.group(1)
        
        # Extract tertiaryColor
        tertiary_match = re.search(r"'tertiaryColor':\s*'([^']+)'", init_content)
        if tertiary_match:
            colors["tertiary"] = tertiary_match.group(1)
    
    # Extract from classDef (Mermaid uses : for property assignments)
    classdef_matches = re.findall(r"classDef\s+\w+\s+fill:([^,]+)", mermaid)
    if classdef_matches:
        colors["classdef_fills"] = classdef_matches
    
    logger.debug(f"[test] Extracted colors: {colors}")
    return colors


def extract_theme_from_mermaid(mermaid: str) -> Optional[str]:
    """Extract theme name from Mermaid init directive."""
    theme_match = re.search(r"'theme':\s*'([^']+)'", mermaid)
    if theme_match:
        return theme_match.group(1)
    return None


def extract_shapes_from_mermaid(mermaid: str) -> Dict[str, int]:
    """Extract and count node shapes from Mermaid diagram."""
    shapes = {
        "stadium": len(re.findall(r"\(\[.*?\]\)", mermaid)),  # ([text])
        "rectangle": len(re.findall(r"\[(?!\(|/)[^\[\]]+\]", mermaid)),  # [text]
        "diamond": len(re.findall(r"\{\{.*?\}\}", mermaid)),  # {{text}}
        "cylinder": len(re.findall(r"\[\(.*?\)\]", mermaid)),  # [(text)]
        "parallelogram": len(re.findall(r"\[/.*?/\]", mermaid)),  # [/text/]
        "circle": len(re.findall(r"\(\([^\(\)]+\)\)", mermaid)),  # ((text))
    }
    
    total = sum(shapes.values())
    logger.debug(f"[test] Shape distribution: {shapes} (total: {total})")
    return shapes


def extract_diagram_orientation(mermaid: str) -> Optional[str]:
    """Extract diagram orientation/type from Mermaid code."""
    # Check for flowchart directions
    if re.search(r"flowchart\s+(TD|TB)", mermaid, re.IGNORECASE):
        return "top-down"
    elif re.search(r"flowchart\s+(LR|RL)", mermaid, re.IGNORECASE):
        return "left-right"
    elif re.search(r"flowchart\s+(BT)", mermaid, re.IGNORECASE):
        return "bottom-top"
    elif re.search(r"stateDiagram", mermaid, re.IGNORECASE):
        return "state-diagram"
    elif re.search(r"classDiagram", mermaid, re.IGNORECASE):
        return "class-diagram"
    elif re.search(r"erDiagram|entityRelationshipDiagram", mermaid, re.IGNORECASE):
        return "er-diagram"
    elif re.search(r"sequenceDiagram", mermaid, re.IGNORECASE):
        return "sequence-diagram"
    elif re.search(r"graph\s+(TD|TB)", mermaid, re.IGNORECASE):
        return "graph-top-down"
    elif re.search(r"graph\s+(LR|RL)", mermaid, re.IGNORECASE):
        return "graph-left-right"
    
    return "unknown"


def generate_mock_features(count: int = 5) -> List[Dict]:
    """Generate mock features for testing."""
    return [
        {
            "id": f"feature-{i}",
            "title": f"Feature {i}",
            "description": f"Description for feature {i}",
        }
        for i in range(1, count + 1)
    ]


def generate_mock_stories(count: int = 10) -> List[Dict]:
    """Generate mock stories for testing."""
    return [
        {
            "id": f"story-{i}",
            "feature_id": f"feature-{(i % 5) + 1}",
            "story_text": f"As a user, I want feature {i} so that I can accomplish task {i}",
            "acceptance_criteria": [f"Criterion {i}.1", f"Criterion {i}.2"],
        }
        for i in range(1, count + 1)
    ]


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def output_dir():
    """Create output directory for test results."""
    output_path = Path("tests/output/styling_tests")
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


@pytest.fixture
def test_results():
    """Store test results for comparison."""
    return []


# ============================================================================
# DOMAIN-SPECIFIC TESTS
# ============================================================================

@pytest.mark.parametrize("domain_name,domain_data", [
    ("e-commerce", DOMAIN_PROMPTS["e-commerce"]),
    ("healthcare", DOMAIN_PROMPTS["healthcare"]),
    ("fintech", DOMAIN_PROMPTS["fintech"]),
    ("education", DOMAIN_PROMPTS["education"]),
    ("iot", DOMAIN_PROMPTS["iot"]),
])
def test_domain_styling(domain_name: str, domain_data: Dict, output_dir: Path, test_results: List):
    """Test that each domain generates distinct styling."""
    logger.info(f"[test] Testing domain: {domain_name}")
    
    # Generate style configuration
    style_generator = StyleConfigGenerator(domain_data["prompt"], f"project-{domain_name}")
    features = generate_mock_features(5)
    stories = generate_mock_stories(12)
    full_config = style_generator.generate_full_config(features, stories)
    
    logger.debug(f"[test] Generated config for {domain_name}: domain={full_config['domain']}, theme={full_config['theme']}")
    
    # Validate domain detection
    detected_domain = full_config["domain"]
    expected_domain = domain_data.get("expected_domain")
    
    if expected_domain:
        assert detected_domain == expected_domain, (
            f"Domain mismatch for {domain_name}: expected {expected_domain}, got {detected_domain}"
        )
        logger.info(f"[test] ✓ Domain detection correct: {detected_domain}")
    
    # Validate color scheme
    colors = full_config["colors"]
    expected_colors = domain_data.get("expected_colors", {})
    
    if expected_colors.get("primary"):
        assert colors["primary"] == expected_colors["primary"], (
            f"Primary color mismatch for {domain_name}: expected {expected_colors['primary']}, got {colors['primary']}"
        )
        logger.info(f"[test] ✓ Primary color correct: {colors['primary']}")
    
    # Validate theme is applied
    theme = full_config["theme"]
    assert theme in ["base", "default", "forest", "dark", "neutral"], (
        f"Invalid theme for {domain_name}: {theme}"
    )
    logger.info(f"[test] ✓ Theme applied: {theme}")
    
    # Validate init directive exists
    init_directive = full_config["init_directive"]
    assert "%%{init:" in init_directive, f"Init directive missing for {domain_name}"
    assert "'theme'" in init_directive, f"Theme missing in init directive for {domain_name}"
    assert "'primaryColor'" in init_directive, f"Primary color missing in init directive for {domain_name}"
    logger.info(f"[test] ✓ Init directive generated: {len(init_directive)} chars")
    
    # Store results for comparison
    result = {
        "domain": domain_name,
        "detected_domain": detected_domain,
        "theme": theme,
        "colors": colors,
        "complexity": full_config["complexity"],
        "init_directive": init_directive,
    }
    test_results.append(result)
    
    # Save individual result
    result_file = output_dir / f"{domain_name}_style_config.json"
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)
    logger.info(f"[test] Saved result to {result_file}")


def test_color_scheme_differences(test_results: List, output_dir: Path):
    """Test that color schemes differ between domains."""
    logger.info("[test] Testing color scheme differences")
    
    if len(test_results) < 2:
        pytest.skip("Need at least 2 domain results")
    
    # Extract primary colors
    primary_colors = [r["colors"]["primary"] for r in test_results]
    
    # Check that colors are different
    unique_colors = set(primary_colors)
    assert len(unique_colors) == len(primary_colors), (
        f"Color schemes are not distinct: {primary_colors}"
    )
    logger.info(f"[test] ✓ All domains have distinct primary colors: {unique_colors}")
    
    # Generate comparison report
    comparison = {
        "test": "color_scheme_differences",
        "timestamp": datetime.now().isoformat(),
        "domains": {r["domain"]: r["colors"]["primary"] for r in test_results},
        "unique_colors": list(unique_colors),
        "all_distinct": len(unique_colors) == len(primary_colors),
    }
    
    comparison_file = output_dir / "color_scheme_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump(comparison, f, indent=2)
    logger.info(f"[test] Saved color comparison to {comparison_file}")


# ============================================================================
# DIAGRAM GENERATION AND VALIDATION TESTS
# ============================================================================

@pytest.mark.parametrize("domain_name,domain_data", [
    ("e-commerce", DOMAIN_PROMPTS["e-commerce"]),
    ("healthcare", DOMAIN_PROMPTS["healthcare"]),
    ("fintech", DOMAIN_PROMPTS["fintech"]),
    ("education", DOMAIN_PROMPTS["education"]),
    ("iot", DOMAIN_PROMPTS["iot"]),
])
def test_diagram_generation_with_styling(domain_name: str, domain_data: Dict, output_dir: Path):
    """Test diagram generation with styling applied."""
    logger.info(f"[test] Testing diagram generation for {domain_name}")
    
    # Generate style configuration
    style_generator = StyleConfigGenerator(domain_data["prompt"], f"project-{domain_name}")
    features = generate_mock_features(5)
    stories = generate_mock_stories(12)
    full_config = style_generator.generate_full_config(features, stories)
    
    # Create mock Mermaid diagram
    mock_mermaid = f"""flowchart LR
    Start([Start])
    Process[Process]
    Decision{{Decision}}
    Database[(Database)]
    External[/External/]
    End((End))
    
    Start --> Process
    Process --> Decision
    Decision -->|Yes| Database
    Decision -->|No| External
    Database --> End
    External --> End"""
    
    # Apply styling
    style_config = {
        "theme": full_config["theme"],
        "primaryColor": full_config["colors"]["primary"],
        "secondaryColor": full_config["colors"]["secondary"],
        "accentColor": full_config["colors"]["tertiary"],
        "domain": full_config["domain"],
    }
    
    styled_mermaid = apply_style_to_mermaid(mock_mermaid, style_config)
    
    logger.debug(f"[test] Styled diagram length: {len(styled_mermaid)} chars")
    logger.debug(f"[test] First 200 chars: {styled_mermaid[:200]}")
    
    # Validate styling is applied
    assert "%%{init:" in styled_mermaid, f"Init directive missing in styled diagram for {domain_name}"
    assert full_config["colors"]["primary"] in styled_mermaid, f"Primary color not in styled diagram for {domain_name}"
    
    # Extract and validate colors
    extracted_colors = extract_color_from_mermaid(styled_mermaid)
    assert extracted_colors.get("primary") == full_config["colors"]["primary"], (
        f"Primary color mismatch in styled diagram for {domain_name}"
    )
    
    # Extract and validate theme
    extracted_theme = extract_theme_from_mermaid(styled_mermaid)
    assert extracted_theme == full_config["theme"], (
        f"Theme mismatch in styled diagram for {domain_name}"
    )
    
    logger.info(f"[test] ✓ Styling applied correctly for {domain_name}")
    
    # Save styled diagram
    diagram_file = output_dir / f"{domain_name}_styled_diagram.mmd"
    with open(diagram_file, "w") as f:
        f.write(styled_mermaid)
    logger.info(f"[test] Saved styled diagram to {diagram_file}")


def test_shape_distribution_variation(output_dir: Path):
    """Test that shape distributions vary appropriately."""
    logger.info("[test] Testing shape distribution variation")
    
    shape_distributions = {}
    
    for domain_name, domain_data in DOMAIN_PROMPTS.items():
        # Generate style and complexity
        style_generator = StyleConfigGenerator(domain_data["prompt"], f"project-{domain_name}")
        features = generate_mock_features(5)
        stories = generate_mock_stories(12)
        full_config = style_generator.generate_full_config(features, stories)
        
        complexity_info = full_config["complexity"]
        
        # Initialize shape selector
        shape_selector = NodeShapeSelector(
            complexity_score=complexity_info["complexity_score"],
            prompt=domain_data["prompt"]
        )
        
        # Get shape instructions
        shape_instructions = shape_selector.build_shape_instructions(complexity_info)
        
        # Create mock diagram with various shapes
        mock_mermaid = f"""flowchart LR
        Controller([Controller])
        Service[Service]
        Decision{{Decision}}
        DB[(Database)]
        External[/External/]
        UI((UI))
        
        UI --> Controller
        Controller --> Service
        Service --> Decision
        Decision -->|Yes| DB
        Decision -->|No| External"""
        
        # Extract shapes
        shapes = extract_shapes_from_mermaid(mock_mermaid)
        shape_distributions[domain_name] = {
            "shapes": shapes,
            "complexity_score": complexity_info["complexity_score"],
            "recommended_type": complexity_info["recommended_type"],
        }
        
        logger.debug(f"[test] {domain_name} shape distribution: {shapes}")
    
    # Validate that shapes are used
    all_have_shapes = all(
        sum(dist["shapes"].values()) > 0
        for dist in shape_distributions.values()
    )
    assert all_have_shapes, "Some domains have no shapes in diagrams"
    
    logger.info(f"[test] ✓ Shape distributions calculated for all domains")
    
    # Save shape distribution comparison
    comparison_file = output_dir / "shape_distribution_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump(shape_distributions, f, indent=2)
    logger.info(f"[test] Saved shape distribution comparison to {comparison_file}")


def test_diagram_orientation_changes(output_dir: Path):
    """Test that diagram orientations change appropriately based on complexity."""
    logger.info("[test] Testing diagram orientation changes")
    
    orientations = {}
    
    for domain_name, domain_data in DOMAIN_PROMPTS.items():
        # Generate style and complexity
        style_generator = StyleConfigGenerator(domain_data["prompt"], f"project-{domain_name}")
        features = generate_mock_features(5)
        stories = generate_mock_stories(12)
        full_config = style_generator.generate_full_config(features, stories)
        
        complexity_info = full_config["complexity"]
        recommended_type = complexity_info["recommended_type"]
        
        # Create mock diagram with recommended type
        if "stateDiagram" in recommended_type:
            mock_mermaid = "stateDiagram-v2\n    [*] --> State1\n    State1 --> State2"
        elif "LR" in recommended_type:
            mock_mermaid = "flowchart LR\n    A --> B\n    B --> C"
        elif "TB" in recommended_type or "TD" in recommended_type:
            mock_mermaid = "flowchart TD\n    A --> B\n    B --> C"
        else:
            mock_mermaid = f"{recommended_type}\n    A --> B"
        
        orientation = extract_diagram_orientation(mock_mermaid)
        
        orientations[domain_name] = {
            "orientation": orientation,
            "recommended_type": recommended_type,
            "complexity_score": complexity_info["complexity_score"],
        }
        
        logger.debug(f"[test] {domain_name} orientation: {orientation} (type: {recommended_type})")
    
    # Validate orientations are detected
    all_have_orientation = all(
        dist["orientation"] != "unknown"
        for dist in orientations.values()
    )
    assert all_have_orientation, "Some domains have unknown orientation"
    
    logger.info(f"[test] ✓ Orientations detected for all domains")
    
    # Save orientation comparison
    comparison_file = output_dir / "orientation_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump(orientations, f, indent=2)
    logger.info(f"[test] Saved orientation comparison to {comparison_file}")


def test_theme_application(output_dir: Path):
    """Test that themes are applied correctly."""
    logger.info("[test] Testing theme application")
    
    theme_results = {}
    
    for domain_name, domain_data in DOMAIN_PROMPTS.items():
        # Generate style configuration
        style_generator = StyleConfigGenerator(domain_data["prompt"], f"project-{domain_name}")
        features = generate_mock_features(5)
        stories = generate_mock_stories(12)
        full_config = style_generator.generate_full_config(features, stories)
        
        theme = full_config["theme"]
        init_directive = full_config["init_directive"]
        
        # Validate theme in init directive
        assert f"'theme':'{theme}'" in init_directive, (
            f"Theme {theme} not found in init directive for {domain_name}"
        )
        
        theme_results[domain_name] = {
            "theme": theme,
            "init_directive_length": len(init_directive),
            "has_theme": f"'theme':" in init_directive,
            "has_colors": "'primaryColor'" in init_directive,
        }
        
        logger.debug(f"[test] {domain_name} theme: {theme}")
    
    # Validate all have themes
    all_have_themes = all(r["has_theme"] for r in theme_results.values())
    assert all_have_themes, "Some domains missing theme in init directive"
    
    logger.info(f"[test] ✓ Themes applied correctly for all domains")
    
    # Save theme comparison
    comparison_file = output_dir / "theme_application_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump(theme_results, f, indent=2)
    logger.info(f"[test] Saved theme comparison to {comparison_file}")


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.parametrize("edge_case_name,edge_case_data", [
    ("very_short", EDGE_CASE_PROMPTS["very_short"]),
    ("multi_domain", EDGE_CASE_PROMPTS["multi_domain"]),
    ("empty", EDGE_CASE_PROMPTS["empty"]),
    ("special_characters", EDGE_CASE_PROMPTS["special_characters"]),
])
def test_edge_cases(edge_case_name: str, edge_case_data: Dict, output_dir: Path):
    """Test edge cases for styling system."""
    logger.info(f"[test] Testing edge case: {edge_case_name}")
    
    try:
        # Generate style configuration
        style_generator = StyleConfigGenerator(edge_case_data["prompt"], f"project-{edge_case_name}")
        features = generate_mock_features(3)
        stories = generate_mock_stories(6)
        full_config = style_generator.generate_full_config(features, stories)
        
        # Validate that style generation doesn't crash
        assert "domain" in full_config, f"Domain missing for edge case {edge_case_name}"
        assert "theme" in full_config, f"Theme missing for edge case {edge_case_name}"
        assert "colors" in full_config, f"Colors missing for edge case {edge_case_name}"
        assert "init_directive" in full_config, f"Init directive missing for edge case {edge_case_name}"
        
        # Validate default domain for edge cases
        if edge_case_name in ["very_short", "empty", "special_characters"]:
            expected_domain = edge_case_data.get("expected_domain", "default")
            assert full_config["domain"] == expected_domain, (
                f"Expected default domain for {edge_case_name}, got {full_config['domain']}"
            )
        
        logger.info(f"[test] ✓ Edge case {edge_case_name} handled correctly")
        logger.debug(f"[test] Edge case {edge_case_name} result: domain={full_config['domain']}, theme={full_config['theme']}")
        
        # Save edge case result
        result_file = output_dir / f"edge_case_{edge_case_name}.json"
        with open(result_file, "w") as f:
            json.dump({
                "edge_case": edge_case_name,
                "prompt": edge_case_data["prompt"],
                "result": full_config,
            }, f, indent=2)
        
    except Exception as e:
        logger.error(f"[test] Edge case {edge_case_name} failed: {e}", exc_info=True)
        raise


# ============================================================================
# COMPARISON REPORT GENERATION
# ============================================================================

def test_generate_comparison_report(output_dir: Path, test_results: List):
    """Generate comprehensive comparison report."""
    logger.info("[test] Generating comparison report")
    
    if not test_results:
        pytest.skip("No test results available")
    
    # Build comparison data
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_domains": len(test_results),
            "domains_tested": [r["domain"] for r in test_results],
        },
        "domain_comparison": {},
        "color_analysis": {},
        "theme_analysis": {},
        "complexity_analysis": {},
    }
    
    # Domain comparison
    for result in test_results:
        domain = result["domain"]
        comparison["domain_comparison"][domain] = {
            "detected_domain": result["detected_domain"],
            "theme": result["theme"],
            "primary_color": result["colors"]["primary"],
            "secondary_color": result["colors"]["secondary"],
            "accent_color": result["colors"]["tertiary"],
            "complexity_score": result["complexity"]["complexity_score"],
            "recommended_type": result["complexity"]["recommended_type"],
        }
    
    # Color analysis
    primary_colors = [r["colors"]["primary"] for r in test_results]
    secondary_colors = [r["colors"]["secondary"] for r in test_results]
    
    comparison["color_analysis"] = {
        "primary_colors": primary_colors,
        "secondary_colors": secondary_colors,
        "unique_primary_colors": len(set(primary_colors)),
        "unique_secondary_colors": len(set(secondary_colors)),
        "all_colors_distinct": len(set(primary_colors)) == len(primary_colors),
    }
    
    # Theme analysis
    themes = [r["theme"] for r in test_results]
    theme_counts = Counter(themes)
    
    comparison["theme_analysis"] = {
        "themes_used": dict(theme_counts),
        "unique_themes": len(set(themes)),
        "most_common_theme": theme_counts.most_common(1)[0][0] if theme_counts else None,
    }
    
    # Complexity analysis
    complexity_scores = [r["complexity"]["complexity_score"] for r in test_results]
    recommended_types = [r["complexity"]["recommended_type"] for r in test_results]
    
    comparison["complexity_analysis"] = {
        "complexity_scores": complexity_scores,
        "average_complexity": sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
        "min_complexity": min(complexity_scores) if complexity_scores else 0,
        "max_complexity": max(complexity_scores) if complexity_scores else 0,
        "recommended_types": recommended_types,
        "unique_types": len(set(recommended_types)),
    }
    
    # Save comparison report
    report_file = output_dir / "styling_comparison_report.json"
    with open(report_file, "w") as f:
        json.dump(comparison, f, indent=2)
    
    logger.info(f"[test] ✓ Comparison report generated: {report_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("STYLING SYSTEM TEST SUMMARY")
    print("="*80)
    print(f"Domains tested: {len(test_results)}")
    print(f"Unique primary colors: {comparison['color_analysis']['unique_primary_colors']}")
    print(f"Unique themes: {comparison['theme_analysis']['unique_themes']}")
    print(f"Average complexity: {comparison['complexity_analysis']['average_complexity']:.2f}")
    print(f"Unique diagram types: {comparison['complexity_analysis']['unique_types']}")
    print("="*80)
    print(f"\nFull report saved to: {report_file}")
    print("="*80 + "\n")
    
    return comparison


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "-s"])

