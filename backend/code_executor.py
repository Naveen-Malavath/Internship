"""
Code Execution Service - Generates and runs applications in Docker
"""
import os
import shutil
import subprocess
import time
from pathlib import Path
import random
import json
from datetime import datetime


class CodeExecutor:
    def __init__(self, workspace_dir="./generated_apps"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.port_file = self.workspace_dir / "ports.json"
        self.used_ports = self._load_used_ports()
        print(f"[EXECUTOR INIT] Workspace: {self.workspace_dir}")
        print(f"[EXECUTOR INIT] Currently used ports: {self.used_ports}")
        
    def _cleanup_old_apps(self):
        """Stop and remove all previously generated app containers"""
        try:
            print(f"[CLEANUP] Checking for old generated apps...")
            # Get all running containers with generated app pattern
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                # Filter for generated app containers (exclude main app containers)
                # Match patterns like: project_name_20251224_013230_backend
                generated_containers = []
                for c in containers:
                    if c and 'autoagents-' not in c:
                        # Match containers with timestamp pattern _YYYYMMDD_
                        import re
                        if re.search(r'_20\d{6}_\d{6}', c):
                            generated_containers.append(c)
                
                if generated_containers:
                    print(f"[CLEANUP] Found {len(generated_containers)} old containers to remove:")
                    for container in generated_containers:
                        print(f"[CLEANUP]   - {container}")
                    # Stop and remove them
                    for container in generated_containers:
                        try:
                            subprocess.run(
                                ["docker", "stop", container],
                                capture_output=True,
                                timeout=15
                            )
                            subprocess.run(
                                ["docker", "rm", "-f", container],
                                capture_output=True,
                                timeout=10
                            )
                            print(f"[CLEANUP]   ✓ Removed: {container}")
                        except Exception as e:
                            print(f"[CLEANUP]   ✗ Failed to remove {container}: {e}")
                    print(f"[CLEANUP] Cleaned up {len(generated_containers)} containers")
                else:
                    print(f"[CLEANUP] No old containers found")
            
            # Also clean up any dangling Docker resources
            try:
                subprocess.run(
                    ["docker", "system", "prune", "-f"],
                    capture_output=True,
                    timeout=30
                )
                print(f"[CLEANUP] Docker system pruned")
            except Exception as e:
                print(f"[CLEANUP] Prune warning: {e}")
                    
            # Clear port tracking
            self.used_ports = {}
            self._save_used_ports()
            print(f"[CLEANUP] Port tracking reset")
            
        except Exception as e:
            print(f"[CLEANUP WARNING] Cleanup failed: {e}")
        
    def _load_used_ports(self):
        """Load used ports from file"""
        if self.port_file.exists():
            try:
                with open(self.port_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_used_ports(self):
        """Save used ports to file"""
        with open(self.port_file, 'w') as f:
            json.dump(self.used_ports, f)
    
    def _allocate_ports(self, project_name: str):
        """Allocate unique ports for frontend and backend"""
        base_frontend = 3000
        base_backend = 8100
        
        # CRITICAL: Stop old containers using the same project name's ports FIRST
        if project_name in self.used_ports:
            old_ports = self.used_ports[project_name]
            print(f"[PORT ALLOCATION] Found existing allocation for {project_name}: {old_ports}")
            print(f"[PORT ALLOCATION] Stopping old containers on these ports...")
            
            # Stop containers on these ports
            for port_type, port_num in old_ports.items():
                try:
                    find_result = subprocess.run(
                        ["docker", "ps", "-q", "-f", f"publish={port_num}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if find_result.stdout.strip():
                        container_ids = find_result.stdout.strip().split('\n')
                        for container_id in container_ids:
                            print(f"[PORT ALLOCATION] Stopping container {container_id} on port {port_num}")
                            subprocess.run(["docker", "stop", container_id], timeout=10)
                            subprocess.run(["docker", "rm", "-f", container_id], timeout=10)
                except Exception as e:
                    print(f"[PORT ALLOCATION] Warning: Could not clean up port {port_num}: {e}")
            
            # Clear the old port allocation
            del self.used_ports[project_name]
            self._save_used_ports()
        
        # Find available ports
        frontend_port = base_frontend
        backend_port = base_backend
        
        existing_ports = [p for ports in self.used_ports.values() for p in ports.values()]
        
        while frontend_port in existing_ports:
            frontend_port += 1
        
        while backend_port in existing_ports:
            backend_port += 1
        
        ports = {
            "frontend": frontend_port,
            "backend": backend_port
        }
        
        self.used_ports[project_name] = ports
        self._save_used_ports()
        
        print(f"[PORT ALLOCATION] Project: {project_name}")
        print(f"[PORT ALLOCATION] Frontend: {frontend_port}")
        print(f"[PORT ALLOCATION] Backend: {backend_port}")
        
        return ports
    
    def _release_ports(self, project_name: str):
        """Release ports when app is stopped"""
        if project_name in self.used_ports:
            print(f"[PORT RELEASE] Releasing ports for: {project_name}")
            del self.used_ports[project_name]
            self._save_used_ports()
        
    def create_project(self, project_name: str, frontend_code: dict, backend_code: dict, ports: dict):
        """Create project directory structure with generated code"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{project_name.lower().replace(' ', '_').replace('-', '_')}_{timestamp}"
        project_path = self.workspace_dir / safe_name
        
        print(f"[PROJECT CREATE] Starting project creation")
        print(f"[PROJECT CREATE] Project name: {project_name}")
        print(f"[PROJECT CREATE] Safe name: {safe_name}")
        print(f"[PROJECT CREATE] Path: {project_path}")
        
        # Clean up if exists
        if project_path.exists():
            print(f"[PROJECT CREATE] Removing existing directory")
            shutil.rmtree(project_path)
        
        project_path.mkdir(parents=True)
        print(f"[PROJECT CREATE] Created project directory")
        
        # Create backend directory
        backend_dir = project_path / "backend"
        backend_dir.mkdir()
        print(f"[PROJECT CREATE] Created backend directory")
        
        # Write backend files
        for filename, content in backend_code.items():
            file_path = backend_dir / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"[PROJECT CREATE] Wrote backend file: {filename} ({len(content)} chars)")
        
        # Create backend Dockerfile
        backend_dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""
        (backend_dir / "Dockerfile").write_text(backend_dockerfile)
        print(f"[PROJECT CREATE] Created backend Dockerfile")
        
        # Create frontend directory
        frontend_dir = project_path / "frontend"
        frontend_dir.mkdir()
        frontend_src = frontend_dir / "src"
        frontend_src.mkdir()
        print(f"[PROJECT CREATE] Created frontend directories")
        
        # Write frontend files
        for filename, content in frontend_code.items():
            if filename in ["App.jsx", "main.jsx"]:
                file_path = frontend_src / filename
            else:
                file_path = frontend_dir / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"[PROJECT CREATE] Wrote frontend file: {filename} ({len(content)} chars)")
        
        # Create frontend Dockerfile
        frontend_dockerfile = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""
        (frontend_dir / "Dockerfile").write_text(frontend_dockerfile)
        print(f"[PROJECT CREATE] Created frontend Dockerfile")
        
        # Create docker-compose.yml with allocated ports
        docker_compose = f"""version: '3.8'

services:
  backend:
    build: ./backend
    container_name: {safe_name}_backend
    ports:
      - "{ports['backend']}:8000"
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - {safe_name}_network
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3

  frontend:
    build: ./frontend
    container_name: {safe_name}_frontend
    ports:
      - "{ports['frontend']}:5173"
    environment:
      - VITE_API_URL=http://localhost:{ports['backend']}
    depends_on:
      - backend
    networks:
      - {safe_name}_network

networks:
  {safe_name}_network:
    driver: bridge
"""
        (project_path / "docker-compose.yml").write_text(docker_compose)
        print(f"[PROJECT CREATE] Created docker-compose.yml")
        print(f"[PROJECT CREATE] Project creation completed successfully")
        
        return str(project_path), safe_name
    
    def start_application(self, project_path: str, safe_name: str, allocated_ports: dict = None):
        """Start the application using docker compose"""
        try:
            print(f"\n{'='*80}")
            print(f"[APP START] Starting application")
            print(f"[APP START] Project path: {project_path}")
            print(f"[APP START] Safe name: {safe_name}")
            print(f"{'='*80}\n")
            
            # Check if Docker is available
            print(f"[APP START] Checking Docker availability...")
            docker_check = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if docker_check.returncode != 0:
                error_msg = f"Docker is not available: {docker_check.stderr}"
                print(f"[APP START ERROR] {error_msg}")
                return False, error_msg
            
            print(f"[APP START] Docker is available ✓")
            
            # Stop any existing containers with same name FIRST
            print(f"[APP START] Stopping existing containers for this project...")
            subprocess.run(
                ["docker-compose", "down", "--remove-orphans"],
                cwd=project_path,
                capture_output=True,
                timeout=30
            )
            
            # ALSO stop any containers using our ports (force cleanup)
            project_ports = self.used_ports.get(safe_name.rsplit('_', 2)[0], {})
            if project_ports:
                print(f"[APP START] Cleaning up containers on ports {project_ports}")
                # Stop containers by port (find and kill)
                for port_type, port_num in project_ports.items():
                    try:
                        # Find container using this port
                        find_result = subprocess.run(
                            ["docker", "ps", "-q", "-f", f"publish={port_num}"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if find_result.stdout.strip():
                            container_ids = find_result.stdout.strip().split('\n')
                            for container_id in container_ids:
                                print(f"[APP START] Stopping container {container_id} on port {port_num}")
                                subprocess.run(["docker", "stop", container_id], timeout=10)
                                subprocess.run(["docker", "rm", "-f", container_id], timeout=10)
                    except Exception as e:
                        print(f"[APP START] Warning: Could not clean up port {port_num}: {e}")
            
            print(f"[APP START] Cleanup completed")
            
            # Build and start containers
            print(f"[APP START] Building Docker images...")
            print(f"[APP START] This may take 2-3 minutes on first run...")
            
            build_result = subprocess.run(
                ["docker-compose", "build", "--no-cache"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for build
            )
            
            if build_result.returncode != 0:
                error_msg = f"Docker build failed: {build_result.stderr}"
                print(f"[APP START ERROR] {error_msg}")
                print(f"[APP START ERROR] Build stdout: {build_result.stdout}")
                return False, error_msg
            
            print(f"[APP START] Build completed successfully ✓")
            print(f"[APP START] Starting containers...")
            
            start_result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes for startup
            )
            
            if start_result.returncode != 0:
                error_msg = f"Docker compose up failed: {start_result.stderr}"
                print(f"[APP START ERROR] {error_msg}")
                print(f"[APP START ERROR] Startup stdout: {start_result.stdout}")
                return False, error_msg
            
            print(f"[APP START] Containers started successfully ✓")
            print(f"[APP START] Waiting for services to be ready...")
            
            # Get allocated ports - use passed ports if available, otherwise lookup
            if allocated_ports:
                frontend_port = allocated_ports.get('frontend', 3000)
                backend_port = allocated_ports.get('backend', 8100)
            else:
                # Fallback: try to find by project name (without timestamp)
                project_name = safe_name.rsplit('_', 2)[0]  # Remove timestamp
                ports = self.used_ports.get(project_name, {})
                frontend_port = ports.get('frontend', 3000)
                backend_port = ports.get('backend', 8100)
            
            print(f"[APP START] Frontend port: {frontend_port}")
            print(f"[APP START] Backend port: {backend_port}")
            
            # Wait for services to be healthy
            max_wait = 60  # seconds
            wait_interval = 5
            elapsed = 0
            
            while elapsed < max_wait:
                print(f"[APP START] Checking container status... ({elapsed}/{max_wait}s)")
                
                ps_result = subprocess.run(
                    ["docker-compose", "ps"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if ps_result.returncode == 0:
                    print(f"[APP START] Containers are running")
                    break
                
                time.sleep(wait_interval)
                elapsed += wait_interval
            
            preview_url = f"http://localhost:{frontend_port}"
            
            print(f"\n{'='*80}")
            print(f"[APP START SUCCESS] Application is ready!")
            print(f"[APP START SUCCESS] Frontend URL: {preview_url}")
            print(f"[APP START SUCCESS] Backend URL: http://localhost:{backend_port}")
            print(f"{'='*80}\n")
            
            return True, preview_url
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Timeout: Operation took too long - {str(e)}"
            print(f"[APP START ERROR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to start application: {str(e)}"
            print(f"[APP START ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def stop_application(self, project_path: str, safe_name: str):
        """Stop the running application"""
        try:
            print(f"\n[APP STOP] Stopping application: {safe_name}")
            print(f"[APP STOP] Project path: {project_path}")
            
            result = subprocess.run(
                ["docker-compose", "down", "-v"],  # -v removes volumes too
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"[APP STOP WARNING] Stop command failed: {result.stderr}")
            else:
                print(f"[APP STOP] Containers stopped successfully")
            
            # Release ports
            self._release_ports(safe_name)
            
            print(f"[APP STOP] Application stopped: {safe_name}\n")
            return True
            
        except Exception as e:
            print(f"[APP STOP ERROR] Failed to stop application: {str(e)}")
            return False
    
    def cleanup_project(self, project_path: str, safe_name: str):
        """Stop and remove project"""
        print(f"\n[CLEANUP] Starting cleanup for: {safe_name}")
        
        self.stop_application(project_path, safe_name)
        
        try:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
                print(f"[CLEANUP] Project directory removed: {project_path}")
            print(f"[CLEANUP] Cleanup completed\n")
        except Exception as e:
            print(f"[CLEANUP ERROR] Failed to cleanup: {str(e)}")
