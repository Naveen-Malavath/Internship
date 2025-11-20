#!/usr/bin/env python3
"""
Test runner script for styling system integration tests.

This script runs the comprehensive test suite and generates comparison reports.
"""

import argparse
import logging
import sys
from pathlib import Path

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run styling system integration tests."""
    parser = argparse.ArgumentParser(description="Run styling system integration tests")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="tests/output/styling_tests",
        help="Output directory for test results"
    )
    parser.add_argument(
        "--domain",
        type=str,
        choices=["e-commerce", "healthcare", "fintech", "education", "iot", "all"],
        default="all",
        help="Test specific domain or all domains"
    )
    parser.add_argument(
        "--edge-cases",
        action="store_true",
        help="Run edge case tests"
    )
    parser.add_argument(
        "--comparison-only",
        action="store_true",
        help="Only generate comparison report (requires existing test results)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    # Build pytest arguments
    pytest_args = [
        "tests/test_styling_system_integration.py",
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    else:
        pytest_args.append("-q")
    
    if args.debug:
        pytest_args.append("-s")  # Don't capture output
    
    # Add markers for filtering
    if args.domain != "all":
        pytest_args.extend(["-k", f"test_domain_styling[{args.domain}]"])
    
    if not args.edge_cases:
        pytest_args.extend(["-m", "not edge_case"])
    
    # Add output directory as environment variable
    import os
    os.environ["TEST_OUTPUT_DIR"] = str(output_dir.absolute())
    
    logger.info("="*80)
    logger.info("RUNNING STYLING SYSTEM INTEGRATION TESTS")
    logger.info("="*80)
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Domain filter: {args.domain}")
    logger.info(f"Edge cases: {args.edge_cases}")
    logger.info("="*80)
    
    # Run tests
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        logger.info("\n" + "="*80)
        logger.info("ALL TESTS PASSED")
        logger.info("="*80)
        logger.info(f"Test results saved to: {output_dir}")
        logger.info("="*80)
    else:
        logger.error("\n" + "="*80)
        logger.error("SOME TESTS FAILED")
        logger.error("="*80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

