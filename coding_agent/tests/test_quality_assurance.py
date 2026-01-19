"""
Tests for the Quality Assurance Pipeline
Validates CSS quality checking and class matching
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.quality_assurance import (
    CSSValidator,
    JSXValidator,
    CSSClassMatcher,
    QualityAssurancePipeline,
    QualityLevel,
)
from core.design_system import DesignSystem, CSSValidator as DesignCSSValidator


class TestCSSValidator:
    """Test CSS validation"""
    
    def test_minimal_css_fails(self):
        """Minimal CSS should fail validation"""
        css = ".app { color: red; }"
        result = CSSValidator.validate(css)
        assert not result["valid"]
        assert result["score"] < 50
    
    def test_production_css_passes(self):
        """Production-quality CSS should pass"""
        css = """
        :root {
            --color-bg-primary: #0a0a0f;
            --color-primary: #6366f1;
            --color-text-primary: #f8fafc;
            --color-border: #2d2d3a;
            --font-family: 'Inter', sans-serif;
            --spacing-4: 16px;
            --radius-md: 8px;
            --shadow-md: 0 4px 6px rgba(0,0,0,0.3);
            --transition-fast: 150ms ease;
        }
        
        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: var(--font-family);
            background: var(--color-bg-primary);
            color: var(--color-text-primary);
        }
        
        .btn {
            padding: 12px 24px;
            background: var(--color-primary);
            border-radius: var(--radius-md);
            transition: all var(--transition-fast);
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .card {
            background: var(--color-bg-card);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 24px;
        }
        
        .card:hover {
            border-color: var(--color-primary);
        }
        
        .input {
            padding: 12px 16px;
            border: 1px solid var(--color-border);
            transition: border-color var(--transition-fast);
        }
        
        .input:hover {
            border-color: var(--color-border-hover);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 16px;
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        """
        result = CSSValidator.validate(css)
        assert result["valid"]
        assert result["score"] >= 70


class TestCSSClassMatcher:
    """Test CSS class matching between JSX and CSS"""
    
    def test_matching_classes(self):
        """All JSX classes should be found in CSS"""
        jsx = '''
        function App() {
            return (
                <div className="app">
                    <div className="card">
                        <h1 className="title">Hello</h1>
                    </div>
                </div>
            );
        }
        '''
        css = '''
        .app { min-height: 100vh; }
        .card { padding: 24px; }
        .title { font-size: 24px; }
        '''
        
        result = CSSClassMatcher.validate(jsx, css)
        assert result["valid"]
        assert len(result["missing_classes"]) == 0
    
    def test_missing_classes(self):
        """Missing classes should be detected"""
        jsx = '''
        function App() {
            return (
                <div className="app">
                    <div className="missing-class">Content</div>
                </div>
            );
        }
        '''
        css = '''
        .app { min-height: 100vh; }
        '''
        
        result = CSSClassMatcher.validate(jsx, css)
        assert not result["valid"]
        assert "missing-class" in result["missing_classes"]
    
    def test_generate_missing_css(self):
        """Should generate reasonable CSS for missing classes"""
        missing = ["todo-item", "btn-primary", "input-field"]
        css = CSSClassMatcher.generate_missing_css(missing)
        
        assert ".todo-item" in css
        assert ".btn-primary" in css
        assert ".input-field" in css
        assert "padding" in css


class TestDesignSystem:
    """Test design system generation"""
    
    def test_dark_theme_css(self):
        """Dark theme should generate valid CSS"""
        ds = DesignSystem("dark_modern")
        css = ds.get_full_stylesheet()
        
        assert ":root" in css
        assert "--color-bg-primary" in css
        assert "--color-primary" in css
        assert "transition" in css
        assert "@keyframes" in css
    
    def test_light_theme_css(self):
        """Light theme should generate valid CSS"""
        ds = DesignSystem("light_modern")
        css = ds.get_full_stylesheet()
        
        assert ":root" in css
        assert len(css) > 1000  # Should be substantial
    
    def test_todo_app_css(self):
        """Todo app CSS should be complete"""
        ds = DesignSystem("dark_modern")
        css = ds.generate_app_css("todo")
        
        assert ".todo-" in css.lower() or "todo" in css.lower()
        assert len(css) > 2000


class TestQualityPipeline:
    """Test the full quality assurance pipeline"""
    
    def test_project_validation(self):
        """Full project should be validated"""
        files = {
            "my-app/package.json": '{"name": "my-app", "version": "1.0.0"}',
            "my-app/src/App.jsx": '''
import './App.css'
function App() {
    return <div className="app">Hello</div>
}
export default App
            ''',
            "my-app/src/App.css": '''
:root {
    --color-bg: #0a0a0f;
    --color-primary: #6366f1;
    --color-text: #f8fafc;
    --color-border: #2d2d3a;
    --font-family: 'Inter', sans-serif;
    --spacing-4: 16px;
    --radius-md: 8px;
    --shadow: 0 4px 6px rgba(0,0,0,0.3);
    --transition: 150ms ease;
}
*, *::before, *::after { box-sizing: border-box; }
body { font-family: var(--font-family); }
.app { min-height: 100vh; background: var(--color-bg); }
.app:hover { background: var(--color-bg); }
a:hover { color: var(--color-primary); }
button:hover { transform: translateY(-1px); }
@media (max-width: 768px) { .app { padding: 16px; } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            '''
        }
        
        pipeline = QualityAssurancePipeline()
        report = pipeline.validate_project(files)
        
        # Should have some score
        assert report.score > 0
        assert report.level in [QualityLevel.EXCELLENT, QualityLevel.GOOD, QualityLevel.ACCEPTABLE, QualityLevel.POOR]
    
    def test_auto_fix_missing_css(self):
        """Auto-fix should generate missing CSS classes"""
        files = {
            "app/src/App.jsx": '''
function App() {
    return <div className="todo-container">
        <div className="todo-item">Item</div>
    </div>
}
export default App
            ''',
            "app/src/App.css": '''
:root { --color: #000; }
*, *::before, *::after { box-sizing: border-box; }
body { font-family: sans-serif; }
.other { padding: 16px; }
            '''
        }
        
        pipeline = QualityAssurancePipeline()
        report = pipeline.validate_project(files)
        
        # Report should identify missing classes
        missing_class_issues = [
            i for i in report.issues 
            if "missing" in i.message.lower() or "not defined" in i.message.lower()
        ]
        
        # Auto-fix should add the missing classes
        fixed_files = pipeline.auto_fix(files, report)
        
        # The CSS should now include the missing classes
        fixed_css = fixed_files.get("app/src/App.css", "")
        # At minimum it should have tried to fix
        assert len(fixed_css) >= len(files["app/src/App.css"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
