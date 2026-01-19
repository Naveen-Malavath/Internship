"""Code generation tool using production-ready templates"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from ..templates.generator import CodeGenerator, ProjectType
from ..templates.production_templates import ProductionCodeGenerator, ProductionTemplates
from ..core.quality_assurance import QualityAssurancePipeline
from .base import Tool, ToolParameter


class CodeGenTool(Tool):
    """Tool for generating PRODUCTION-READY code from templates"""

    name = "generate_code"
    description = "Generate complete, production-ready projects from templates (React, Express, FastAPI, full-stack apps) with beautiful, modern styling"
    parameters = [
        ToolParameter(
            name="project_type",
            type="string",
            description="Type of project to generate",
            required=True,
            enum=[
                "react",
                "react-todo",
                "express",
                "fastapi",
                "fullstack-react-express",
                "fullstack-react-fastapi",
            ],
        ),
        ToolParameter(
            name="project_name",
            type="string",
            description="Name of the project",
            required=True,
        ),
        ToolParameter(
            name="features",
            type="array",
            description="Optional features (routing, auth, database, icons, animation)",
            required=False,
        ),
        ToolParameter(
            name="app_type",
            type="string",
            description="Specific app type for styling (todo, dashboard, form, landing, generic)",
            required=False,
        ),
    ]

    def __init__(self, workspace_path: Path):
        """
        Initialize code generation tool
        
        Args:
            workspace_path: Workspace directory
        """
        self.workspace_path = workspace_path
        self.generator = CodeGenerator(workspace_path)
        self.production_generator = ProductionCodeGenerator(workspace_path)
        self.qa_pipeline = QualityAssurancePipeline()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute PRODUCTION-READY code generation with quality validation"""
        project_type = kwargs.get("project_type")
        project_name = kwargs.get("project_name")
        features = kwargs.get("features", [])
        app_type = kwargs.get("app_type", "generic")

        if not project_type or not project_name:
            return {
                "success": False,
                "error": "Missing required parameters: project_type and project_name",
            }

        try:
            logger.info(
                f"Generating PRODUCTION-READY {project_type} project: {project_name}"
            )

            # Use production templates for React projects
            files = {}
            
            if project_type == "react-todo" or (project_type == "react" and "todo" in project_name.lower()):
                # Generate production-ready Todo app
                files = self.production_generator.generate_todo_app(project_name)
                logger.info(f"Using PRODUCTION Todo template with beautiful dark theme")
                
            elif project_type == "react":
                # Generate production-ready React app
                files = self.production_generator.generate_react_app(
                    project_name, 
                    app_type=app_type,
                    features=features
                )
                logger.info(f"Using PRODUCTION React template with modern styling")
                
            elif project_type == "express":
                files = self.generator.generate_express_api(project_name, features)
                
            elif project_type == "fastapi":
                files = self.generator.generate_fastapi_app(project_name, features)
                
            elif project_type in ["fullstack-react-express", "fullstack-react-fastapi"]:
                backend = "express" if "express" in project_type else "fastapi"
                files = self.generator.generate_fullstack_app(
                    project_name, "react", backend
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown project type: {project_type}",
                }

            # Run quality assurance validation
            qa_report = self.qa_pipeline.validate_project(files)
            logger.info(f"Quality score: {qa_report.score}/100 ({qa_report.level.value})")
            
            # Auto-fix issues if needed
            if not qa_report.passed and qa_report.score >= 50:
                logger.info("Attempting to auto-fix quality issues...")
                files = self.qa_pipeline.auto_fix(files, qa_report)
                
                # Re-validate after fixes
                qa_report = self.qa_pipeline.validate_project(files)
                logger.info(f"Quality score after fixes: {qa_report.score}/100")

            # Write all generated files
            created_files = []
            for file_path, content in files.items():
                full_path = self.workspace_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

            logger.info(f"Created {len(created_files)} PRODUCTION-READY files for {project_name}")

            # Determine suggested commands based on project type
            suggested_commands = []
            project_dir = str(project_name)
            
            if project_type in ["react", "react-todo", "fullstack-react-express", "fullstack-react-fastapi"]:
                suggested_commands = [
                    f"cd {project_dir} && npm install",
                    f"cd {project_dir} && npm run dev"
                ]
            elif project_type == "express":
                suggested_commands = [
                    f"cd {project_dir} && npm install",
                    f"cd {project_dir} && npm start"
                ]
            elif project_type == "fastapi":
                suggested_commands = [
                    f"cd {project_dir} && pip install -r requirements.txt",
                    f"cd {project_dir} && uvicorn main:app --reload"
                ]

            result = {
                "success": True,
                "result": f"Generated PRODUCTION-READY {project_type} project: {project_name}",
                "files_created": created_files,
                "file_count": len(created_files),
                "suggested_commands": suggested_commands,
                "quality_report": {
                    "score": qa_report.score,
                    "level": qa_report.level.value,
                    "passed": qa_report.passed,
                    "summary": qa_report.summary,
                },
                "note": "IMPORTANT: Install dependencies and launch the application using the terminal tool to complete the task."
            }
            
            # Add fix suggestions if there are issues
            if not qa_report.passed:
                result["quality_issues"] = self.qa_pipeline.get_fix_suggestions(qa_report)
            
            return result

        except Exception as e:
            logger.error(f"Code generation error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
