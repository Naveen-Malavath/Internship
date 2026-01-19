"""Template engine for code generation using Jinja2"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger
from pydantic import BaseModel


class TemplateContext(BaseModel):
    """Context for template rendering"""

    project_name: str
    description: str = ""
    author: str = "AI Coding Agent"
    features: List[str] = []
    dependencies: Dict[str, str] = {}
    variables: Dict[str, Any] = {}


class TemplateEngine:
    """
    Template engine for generating code from templates
    Uses Jinja2 for flexible templating
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize template engine
        
        Args:
            templates_dir: Directory containing template files
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        logger.info(f"Initialized TemplateEngine with dir: {templates_dir}")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context
        
        Args:
            template_name: Name of template file
            context: Variables for template
            
        Returns:
            Rendered template string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise

    def render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """
        Render a template string directly
        
        Args:
            template_str: Template string
            context: Variables for template
            
        Returns:
            Rendered string
        """
        template = Template(template_str)
        return template.render(**context)

    def generate_from_template(
        self,
        template_name: str,
        output_path: Path,
        context: Dict[str, Any],
    ) -> Path:
        """
        Generate file from template
        
        Args:
            template_name: Template file name
            output_path: Where to save generated file
            context: Template variables
            
        Returns:
            Path to generated file
        """
        content = self.render_template(template_name, context)

        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Generated file: {output_path}")

        return output_path

    def list_templates(self, pattern: str = "*") -> List[str]:
        """
        List available templates
        
        Args:
            pattern: Glob pattern to filter templates
            
        Returns:
            List of template names
        """
        templates = []
        for path in self.templates_dir.rglob(pattern):
            if path.is_file() and not path.name.startswith("_"):
                rel_path = path.relative_to(self.templates_dir)
                templates.append(str(rel_path))

        return templates
