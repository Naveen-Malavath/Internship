"""Code generator using templates"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from .engine import TemplateContext, TemplateEngine


class ProjectType(str, Enum):
    """Supported project types"""

    REACT = "react"
    NEXTJS = "nextjs"
    VUE = "vue"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    NESTJS = "nestjs"
    FULLSTACK_REACT_EXPRESS = "fullstack-react-express"
    FULLSTACK_REACT_FASTAPI = "fullstack-react-fastapi"


class CodeGenerator:
    """
    High-level code generator for common project types
    Combines templates to create complete projects
    """

    def __init__(self, workspace: Path):
        """
        Initialize code generator
        
        Args:
            workspace: Workspace directory
        """
        self.workspace = workspace
        self.template_engine = TemplateEngine()

    def generate_react_app(
        self, project_name: str, features: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate a React + Vite application
        
        Args:
            project_name: Project name
            features: Optional features (routing, state-management, etc.)
            
        Returns:
            Dict of {file_path: content}
        """
        features = features or []
        files = {}

        context = {
            "project_name": project_name,
            "features": features,
            "has_routing": "routing" in features,
            "has_state": "state-management" in features,
        }

        # Package.json
        files[f"{project_name}/package.json"] = self._generate_react_package_json(
            project_name, features
        )

        # Vite config
        files[f"{project_name}/vite.config.js"] = self._generate_vite_config()

        # index.html
        files[f"{project_name}/index.html"] = self._generate_react_index_html(
            project_name
        )

        # Main App component
        files[f"{project_name}/src/App.jsx"] = self._generate_react_app_component(
            context
        )

        # Main entry point
        files[f"{project_name}/src/main.jsx"] = self._generate_react_main()

        # Styles
        files[f"{project_name}/src/App.css"] = self._generate_react_styles()

        # README
        files[f"{project_name}/README.md"] = self._generate_readme(project_name, "React + Vite")

        logger.info(f"Generated React app: {project_name} with {len(files)} files")
        return files

    def generate_express_api(
        self, project_name: str, features: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate an Express API with TypeScript
        
        Args:
            project_name: Project name
            features: Optional features (auth, database, etc.)
            
        Returns:
            Dict of {file_path: content}
        """
        features = features or []
        files = {}

        context = {
            "project_name": project_name,
            "features": features,
            "has_auth": "auth" in features,
            "has_database": "database" in features,
        }

        # Package.json
        files[f"{project_name}/package.json"] = self._generate_express_package_json(
            project_name, features
        )

        # TypeScript config
        files[f"{project_name}/tsconfig.json"] = self._generate_tsconfig()

        # Main server file
        files[f"{project_name}/src/index.ts"] = self._generate_express_server(context)

        # Routes
        files[f"{project_name}/src/routes/index.ts"] = self._generate_express_routes(
            context
        )

        # .env.example
        files[f"{project_name}/.env.example"] = self._generate_env_example()

        # README
        files[f"{project_name}/README.md"] = self._generate_readme(
            project_name, "Express API"
        )

        logger.info(f"Generated Express API: {project_name} with {len(files)} files")
        return files

    def generate_fastapi_app(
        self, project_name: str, features: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate a FastAPI application
        
        Args:
            project_name: Project name
            features: Optional features
            
        Returns:
            Dict of {file_path: content}
        """
        features = features or []
        files = {}

        # Main app
        files[f"{project_name}/main.py"] = self._generate_fastapi_main(
            project_name, features
        )

        # Requirements
        files[f"{project_name}/requirements.txt"] = self._generate_fastapi_requirements(
            features
        )

        # Router
        files[f"{project_name}/routers/__init__.py"] = ""
        files[f"{project_name}/routers/items.py"] = self._generate_fastapi_router()

        # Models
        files[f"{project_name}/models/__init__.py"] = ""
        files[f"{project_name}/models/item.py"] = self._generate_fastapi_model()

        # .env.example
        files[f"{project_name}/.env.example"] = "DATABASE_URL=postgresql://localhost/mydb"

        # README
        files[f"{project_name}/README.md"] = self._generate_readme(
            project_name, "FastAPI"
        )

        logger.info(f"Generated FastAPI app: {project_name} with {len(files)} files")
        return files

    def generate_fullstack_app(
        self,
        project_name: str,
        frontend: str = "react",
        backend: str = "express",
    ) -> Dict[str, str]:
        """
        Generate a complete full-stack application
        
        Args:
            project_name: Project name
            frontend: Frontend framework
            backend: Backend framework
            
        Returns:
            Dict of {file_path: content}
        """
        files = {}

        # Generate frontend
        if frontend == "react":
            frontend_files = self.generate_react_app(f"{project_name}/frontend")
            files.update(frontend_files)

        # Generate backend
        if backend == "express":
            backend_files = self.generate_express_api(f"{project_name}/backend")
            files.update(backend_files)
        elif backend == "fastapi":
            backend_files = self.generate_fastapi_app(f"{project_name}/backend")
            files.update(backend_files)

        # Root README
        files[f"{project_name}/README.md"] = self._generate_fullstack_readme(
            project_name, frontend, backend
        )

        logger.info(
            f"Generated full-stack app: {project_name} ({frontend} + {backend}) with {len(files)} files"
        )
        return files

    # Template generation methods (inline templates for now)

    def _generate_react_package_json(
        self, project_name: str, features: List[str]
    ) -> str:
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        }

        if "routing" in features:
            dependencies["react-router-dom"] = "^6.20.0"

        if "state-management" in features:
            dependencies["zustand"] = "^4.4.0"

        return f'''{{
  "name": "{project_name}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {json.dumps(dependencies, indent=4)},
  "devDependencies": {{
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }}
}}'''

    def _generate_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
})"""

    def _generate_react_index_html(self, project_name: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""

    def _generate_react_app_component(self, context: Dict[str, Any]) -> str:
        return """import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>Welcome to """ + context["project_name"] + """</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div>
    </div>
  )
}

export default App"""

    def _generate_react_main(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""

    def _generate_react_styles(self) -> str:
        return """.App {
  text-align: center;
  padding: 2rem;
}

.card {
  padding: 2em;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.25s;
}

button:hover {
  border-color: #646cff;
}"""

    def _generate_express_package_json(
        self, project_name: str, features: List[str]
    ) -> str:
        dependencies = {
            "express": "^4.18.0",
            "cors": "^2.8.5",
            "dotenv": "^16.3.0",
        }

        if "auth" in features:
            dependencies["jsonwebtoken"] = "^9.0.0"
            dependencies["bcrypt"] = "^5.1.0"

        return f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "main": "dist/index.js",
  "scripts": {{
    "dev": "ts-node-dev --respawn src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }},
  "dependencies": {json.dumps(dependencies, indent=4)},
  "devDependencies": {{
    "@types/express": "^4.17.0",
    "@types/node": "^20.0.0",
    "ts-node-dev": "^2.0.0",
    "typescript": "^5.0.0"
  }}
}}'''

    def _generate_tsconfig(self) -> str:
        return """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}"""

    def _generate_express_server(self, context: Dict[str, Any]) -> str:
        return f"""import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import router from './routes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.use('/api', router);

app.get('/', (req, res) => {{
  res.json({{ message: 'Welcome to {context["project_name"]} API' }});
}});

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});"""

    def _generate_express_routes(self, context: Dict[str, Any]) -> str:
        return """import { Router } from 'express';

const router = Router();

router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

router.get('/items', (req, res) => {
  res.json({ items: [] });
});

export default router;"""

    def _generate_fastapi_main(self, project_name: str, features: List[str]) -> str:
        return f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import items

app = FastAPI(title="{project_name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api/items", tags=["items"])

@app.get("/")
def read_root():
    return {{"message": "Welcome to {project_name} API"}}

@app.get("/health")
def health_check():
    return {{"status": "ok"}}'''

    def _generate_fastapi_requirements(self, features: List[str]) -> str:
        packages = ["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0", "pydantic>=2.5.0"]
        return "\n".join(packages)

    def _generate_fastapi_router(self) -> str:
        return """from fastapi import APIRouter
from models.item import Item

router = APIRouter()

@router.get("/")
def get_items():
    return {"items": []}

@router.post("/")
def create_item(item: Item):
    return {"item": item, "id": 1}"""

    def _generate_fastapi_model(self) -> str:
        return """from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str = ""
    price: float
    quantity: int = 0"""

    def _generate_env_example(self) -> str:
        return """PORT=5000
NODE_ENV=development
DATABASE_URL=postgresql://localhost/mydb"""

    def _generate_readme(self, project_name: str, tech: str) -> str:
        return f"""# {project_name}

{tech} application generated by AI Coding Agent.

## Setup

```bash
npm install  # or pip install -r requirements.txt
```

## Run

```bash
npm run dev  # or uvicorn main:app --reload
```
"""

    def _generate_fullstack_readme(
        self, project_name: str, frontend: str, backend: str
    ) -> str:
        return f"""# {project_name}

Full-stack application with {frontend} frontend and {backend} backend.

## Structure

- `frontend/` - {frontend} application
- `backend/` - {backend} API

## Setup

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Backend:
```bash
cd backend
npm install  # or pip install -r requirements.txt
npm run dev  # or uvicorn main:app --reload
```
"""
