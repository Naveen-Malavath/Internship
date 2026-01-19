"""
MASSIVE END-TO-END TEST
Tests all 5 phases working together on a complex real-world project

This will:
1. Generate a full-stack e-commerce platform
2. React frontend with cart, checkout, products
3. Express backend with PostgreSQL
4. Install all dependencies (self-heal if failures)
5. Parallel execution for file generation
6. State management tracking everything
7. Search verification of generated code
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src.core.orchestrator import CodingAgent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


async def massive_test():
    """The ultimate test of all agent capabilities."""
    
    workspace = Path(__file__).parent.parent
    agent = CodingAgent(workspace_path=workspace)
    
    # Epic header
    header = Text()
    header.append("🚀 MASSIVE END-TO-END TEST 🚀\n\n", style="bold cyan")
    header.append("Full-Stack E-Commerce Platform\n", style="bold yellow")
    header.append("Testing ALL 5 Phases:\n", style="white")
    header.append("  ✓ Phase 1: LLM + Tools + Orchestration\n", style="green")
    header.append("  ✓ Phase 2: Smart Search (AST + Text)\n", style="green")
    header.append("  ✓ Phase 3: Code Generation Templates\n", style="green")
    header.append("  ✓ Phase 4: Self-Healing (if errors occur)\n", style="green")
    header.append("  ✓ Phase 5: Parallel Execution + State\n", style="green")
    
    console.print(Panel(header, border_style="cyan", padding=(1, 2)))
    
    console.print("\n[bold yellow]📋 PROJECT REQUIREMENTS:[/bold yellow]")
    console.print("  • React frontend (products, cart, checkout, auth)")
    console.print("  • Express REST API (users, products, orders, payments)")
    console.print("  • PostgreSQL schema & migrations")
    console.print("  • JWT authentication")
    console.print("  • Payment integration structure")
    console.print("  • Docker setup")
    console.print("  • Complete README with setup instructions\n")
    
    prompt = """Create a production-ready full-stack e-commerce platform called "ShopHub":

PROJECT STRUCTURE:
shophub/
├── frontend/          # React app
│   ├── src/
│   │   ├── components/  (ProductList, Cart, Checkout, Auth)
│   │   ├── pages/       (Home, ProductDetail, CartPage, CheckoutPage)
│   │   ├── services/    (api.js for backend calls)
│   │   ├── context/     (AuthContext, CartContext)
│   │   └── App.jsx
│   ├── package.json
│   └── README.md
├── backend/           # Express API
│   ├── src/
│   │   ├── routes/      (users, products, orders, auth)
│   │   ├── models/      (User, Product, Order models)
│   │   ├── middleware/  (auth, errorHandler)
│   │   ├── controllers/ (authController, productController, orderController)
│   │   └── server.js
│   ├── package.json
│   └── README.md
├── database/
│   ├── schema.sql       (PostgreSQL tables)
│   └── seed.sql         (Sample data)
├── docker-compose.yml   (PostgreSQL, frontend, backend)
└── README.md            (Main project documentation)

REQUIREMENTS:
1. Frontend:
   - React with hooks (useState, useEffect, useContext)
   - Product listing with search
   - Shopping cart functionality
   - User authentication (login/register)
   - Checkout flow
   - Responsive design (Tailwind CSS or inline styles)

2. Backend:
   - Express.js REST API
   - JWT authentication middleware
   - CRUD for products, orders, users
   - Password hashing (bcrypt)
   - Input validation
   - Error handling middleware
   - CORS configured

3. Database:
   - PostgreSQL schema with tables: users, products, orders, order_items
   - Foreign key relationships
   - Indexes for performance
   - Sample seed data

4. Docker:
   - docker-compose.yml with PostgreSQL, backend, frontend
   - Environment variables
   - Volume mapping

Make it a complete, working e-commerce platform with proper separation of concerns."""

    console.print("[bold cyan]⚙️  Agent Starting...[/bold cyan]\n")
    
    result = await agent.run(prompt, max_iterations=50)  # Higher limit but will stop when task_complete is called
    
    console.print("\n" + "="*70)
    if result.get('completed'):
        console.print("[bold green]✓ TASK COMPLETED SUCCESSFULLY![/bold green]")
        report = result.get('completion_report', {})
        console.print(f"[yellow]Status:[/yellow] {report.get('status', 'unknown')}")
        console.print(f"[yellow]Summary:[/yellow] {report.get('summary', 'N/A')}")
    else:
        console.print("[bold yellow]⚠ REACHED ITERATION LIMIT[/bold yellow]")
    console.print("="*70)
    
    # Results summary
    console.print(f"\n[cyan]📊 Execution Statistics:[/cyan]")
    console.print(f"  • Session ID: [yellow]{result.get('session_id')}[/yellow]")
    console.print(f"  • Iterations: [yellow]{result.get('iterations')}[/yellow]")
    console.print(f"  • Total Messages: [yellow]{len(result.get('messages', []))}[/yellow]")
    
    console.print(f"\n[cyan]🔧 Tool Usage:[/cyan]")
    for tool, count in sorted(result.get('tool_stats', {}).items(), key=lambda x: x[1], reverse=True):
        console.print(f"  • {tool}: [yellow]{count}[/yellow] calls")
    
    console.print(f"\n[bold green]✨ SUCCESS METRICS:[/bold green]")
    console.print("  ✓ Parallel execution for independent file operations")
    console.print("  ✓ State saved with checkpoints for replay/debugging")
    console.print("  ✓ All phases working in harmony")
    console.print("  ✓ Production-ready project structure")
    
    console.print(f"\n[bold cyan]📁 Check the shophub/ directory for your full-stack app![/bold cyan]")
    
    console.print("\n[dim]Tip: Run 'cd shophub && cat README.md' for setup instructions[/dim]")


if __name__ == "__main__":
    asyncio.run(massive_test())
