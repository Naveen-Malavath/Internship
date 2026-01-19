"""
Production-Ready Design System
Provides consistent, beautiful design tokens for generated applications
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


@dataclass
class DesignTheme:
    """Design theme configuration"""
    name: str
    is_dark: bool
    colors: Dict[str, str]
    fonts: Dict[str, str]
    spacing: List[int]
    radii: Dict[str, str]
    shadows: Dict[str, str]


# =============================================================================
# DESIGN TOKENS - Production-ready color palettes and styles
# =============================================================================

DESIGN_TOKENS = {
    "dark_modern": {
        "name": "Dark Modern",
        "is_dark": True,
        "colors": {
            # Backgrounds
            "bg_primary": "#0a0a0f",
            "bg_secondary": "#12121a",
            "bg_tertiary": "#1a1a24",
            "bg_card": "#16161f",
            "bg_elevated": "#1e1e28",
            "bg_hover": "#252530",
            
            # Brand colors
            "primary": "#6366f1",
            "primary_hover": "#818cf8",
            "primary_muted": "#4f46e5",
            "secondary": "#22d3ee",
            "accent": "#f472b6",
            
            # Text
            "text_primary": "#f8fafc",
            "text_secondary": "#94a3b8",
            "text_muted": "#64748b",
            "text_inverse": "#0f172a",
            
            # Semantic
            "success": "#10b981",
            "success_bg": "rgba(16, 185, 129, 0.1)",
            "warning": "#f59e0b",
            "warning_bg": "rgba(245, 158, 11, 0.1)",
            "error": "#ef4444",
            "error_bg": "rgba(239, 68, 68, 0.1)",
            "info": "#3b82f6",
            "info_bg": "rgba(59, 130, 246, 0.1)",
            
            # Borders
            "border": "#2d2d3a",
            "border_hover": "#3d3d4a",
            "border_focus": "#6366f1",
            
            # Gradients
            "gradient_primary": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
            "gradient_accent": "linear-gradient(135deg, #f472b6 0%, #ec4899 100%)",
            "gradient_success": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        },
        "fonts": {
            "heading": "'Cal Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "body": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "mono": "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
        },
        "spacing": [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128],
        "radii": {
            "none": "0",
            "sm": "4px",
            "md": "8px",
            "lg": "12px",
            "xl": "16px",
            "2xl": "24px",
            "full": "9999px",
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.3)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.2)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.2)",
            "glow_primary": "0 0 20px rgba(99, 102, 241, 0.3)",
            "glow_success": "0 0 20px rgba(16, 185, 129, 0.3)",
            "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.3)",
        }
    },
    
    "light_modern": {
        "name": "Light Modern",
        "is_dark": False,
        "colors": {
            # Backgrounds
            "bg_primary": "#ffffff",
            "bg_secondary": "#f8fafc",
            "bg_tertiary": "#f1f5f9",
            "bg_card": "#ffffff",
            "bg_elevated": "#ffffff",
            "bg_hover": "#f1f5f9",
            
            # Brand colors
            "primary": "#4f46e5",
            "primary_hover": "#6366f1",
            "primary_muted": "#818cf8",
            "secondary": "#0891b2",
            "accent": "#db2777",
            
            # Text
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
            "text_muted": "#94a3b8",
            "text_inverse": "#f8fafc",
            
            # Semantic
            "success": "#059669",
            "success_bg": "rgba(5, 150, 105, 0.1)",
            "warning": "#d97706",
            "warning_bg": "rgba(217, 119, 6, 0.1)",
            "error": "#dc2626",
            "error_bg": "rgba(220, 38, 38, 0.1)",
            "info": "#2563eb",
            "info_bg": "rgba(37, 99, 235, 0.1)",
            
            # Borders
            "border": "#e2e8f0",
            "border_hover": "#cbd5e1",
            "border_focus": "#4f46e5",
            
            # Gradients
            "gradient_primary": "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
            "gradient_accent": "linear-gradient(135deg, #db2777 0%, #be185d 100%)",
            "gradient_success": "linear-gradient(135deg, #059669 0%, #047857 100%)",
        },
        "fonts": {
            "heading": "'Cal Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            "body": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "mono": "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
        },
        "spacing": [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128],
        "radii": {
            "none": "0",
            "sm": "4px",
            "md": "8px",
            "lg": "12px",
            "xl": "16px",
            "2xl": "24px",
            "full": "9999px",
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
            "glow_primary": "0 0 20px rgba(79, 70, 229, 0.2)",
            "glow_success": "0 0 20px rgba(5, 150, 105, 0.2)",
            "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)",
        }
    }
}


class DesignSystem:
    """
    Production-ready design system generator
    Creates consistent, beautiful CSS for applications
    """
    
    def __init__(self, theme: str = "dark_modern"):
        """Initialize with a theme"""
        self.theme_name = theme
        self.theme = DESIGN_TOKENS.get(theme, DESIGN_TOKENS["dark_modern"])
    
    def get_css_variables(self) -> str:
        """Generate CSS custom properties from design tokens"""
        colors = self.theme["colors"]
        fonts = self.theme["fonts"]
        radii = self.theme["radii"]
        shadows = self.theme["shadows"]
        spacing = self.theme["spacing"]
        
        css_vars = [":root {"]
        
        # Colors
        for name, value in colors.items():
            css_vars.append(f"  --color-{name.replace('_', '-')}: {value};")
        
        # Fonts
        for name, value in fonts.items():
            css_vars.append(f"  --font-{name}: {value};")
        
        # Border radius
        for name, value in radii.items():
            css_vars.append(f"  --radius-{name}: {value};")
        
        # Shadows
        for name, value in shadows.items():
            css_vars.append(f"  --shadow-{name.replace('_', '-')}: {value};")
        
        # Spacing
        for i, value in enumerate(spacing):
            css_vars.append(f"  --spacing-{i}: {value}px;")
        
        # Animation
        css_vars.extend([
            "  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);",
            "  --transition-normal: 200ms cubic-bezier(0.4, 0, 0.2, 1);",
            "  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);",
            "  --transition-bounce: 500ms cubic-bezier(0.68, -0.55, 0.265, 1.55);",
        ])
        
        css_vars.append("}")
        return "\n".join(css_vars)
    
    def get_base_styles(self) -> str:
        """Generate base/reset styles"""
        return """/* Base Reset & Typography */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  font-family: var(--font-body);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.6;
  min-height: 100vh;
}

/* Typography Scale */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

h1 { font-size: 2.5rem; margin-bottom: var(--spacing-6); }
h2 { font-size: 2rem; margin-bottom: var(--spacing-5); }
h3 { font-size: 1.5rem; margin-bottom: var(--spacing-4); }
h4 { font-size: 1.25rem; margin-bottom: var(--spacing-3); }
h5 { font-size: 1.125rem; margin-bottom: var(--spacing-3); }
h6 { font-size: 1rem; margin-bottom: var(--spacing-2); }

p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-4);
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--color-primary-hover);
}

/* Focus States */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Selection */
::selection {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-hover);
}

/* Utility Classes */
.text-primary { color: var(--color-text-primary); }
.text-secondary { color: var(--color-text-secondary); }
.text-muted { color: var(--color-text-muted); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-error { color: var(--color-error); }
.text-info { color: var(--color-info); }

.bg-primary { background-color: var(--color-bg-primary); }
.bg-secondary { background-color: var(--color-bg-secondary); }
.bg-card { background-color: var(--color-bg-card); }
"""

    def get_component_styles(self) -> str:
        """Generate reusable component styles"""
        return """/* ============================================
   COMPONENT LIBRARY - Production Ready
   ============================================ */

/* Container */
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--spacing-6);
}

/* Card Component */
.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  transition: all var(--transition-normal);
}

.card:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-4);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.card-body {
  color: var(--color-text-secondary);
}

/* Button Component */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-5);
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-gradient-primary);
  color: white;
  box-shadow: var(--shadow-md), var(--shadow-glow-primary);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg), var(--shadow-glow-primary);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-bg-hover);
  border-color: var(--color-border-hover);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.btn-danger {
  background: var(--color-error);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
}

.btn-sm {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: 0.75rem;
}

.btn-lg {
  padding: var(--spacing-4) var(--spacing-7);
  font-size: 1rem;
}

.btn-icon {
  padding: var(--spacing-3);
}

/* Input Component */
.input-group {
  margin-bottom: var(--spacing-5);
}

.input-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.input {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-body);
  font-size: 0.9375rem;
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.input:hover {
  border-color: var(--color-border-hover);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.input::placeholder {
  color: var(--color-text-muted);
}

.input-error {
  border-color: var(--color-error);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

/* Textarea */
.textarea {
  min-height: 120px;
  resize: vertical;
}

/* Select */
.select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right var(--spacing-3) center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: var(--spacing-10);
}

/* Checkbox & Radio */
.checkbox-group,
.radio-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  cursor: pointer;
}

.checkbox,
.radio {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

/* Badge Component */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-3);
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge-primary {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-primary);
}

.badge-success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.badge-warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.badge-error {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.badge-info {
  background: var(--color-info-bg);
  color: var(--color-info);
}

/* Avatar Component */
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--color-gradient-primary);
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-sm { width: 32px; height: 32px; font-size: 0.75rem; }
.avatar-lg { width: 56px; height: 56px; font-size: 1.125rem; }
.avatar-xl { width: 80px; height: 80px; font-size: 1.5rem; }

/* Table Component */
.table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.table th {
  padding: var(--spacing-4);
  text-align: left;
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--color-bg-tertiary);
  border-bottom: 1px solid var(--color-border);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.table td {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.table tr:last-child td {
  border-bottom: none;
}

.table tr:hover td {
  background: var(--color-bg-hover);
}

/* Alert Component */
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.alert-success {
  background: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid var(--color-success);
}

.alert-warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border: 1px solid var(--color-warning);
}

.alert-error {
  background: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid var(--color-error);
}

.alert-info {
  background: var(--color-info-bg);
  color: var(--color-info);
  border: 1px solid var(--color-info);
}

/* Modal Component */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.modal {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  animation: slideUp 0.3s ease-out;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-5);
  border-bottom: 1px solid var(--color-border);
}

.modal-body {
  padding: var(--spacing-5);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding: var(--spacing-5);
  border-top: 1px solid var(--color-border);
}

/* Dropdown Component */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-2);
  z-index: 100;
  animation: fadeIn 0.15s ease-out;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dropdown-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

/* Tooltip */
.tooltip {
  position: relative;
}

.tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-8px);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  font-size: 0.75rem;
  border-radius: var(--radius-md);
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-lg);
}

.tooltip:hover::after {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(-4px);
}

/* Progress Bar */
.progress {
  height: 8px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--color-gradient-primary);
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

/* Skeleton Loader */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 25%,
    var(--color-bg-hover) 50%,
    var(--color-bg-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: skeleton 1.5s infinite;
  border-radius: var(--radius-md);
}

/* Divider */
.divider {
  height: 1px;
  background: var(--color-border);
  margin: var(--spacing-6) 0;
}

/* ============================================
   LAYOUT COMPONENTS
   ============================================ */

/* Flex Utilities */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }
.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
.gap-1 { gap: var(--spacing-1); }
.gap-2 { gap: var(--spacing-2); }
.gap-3 { gap: var(--spacing-3); }
.gap-4 { gap: var(--spacing-4); }
.gap-5 { gap: var(--spacing-5); }
.gap-6 { gap: var(--spacing-6); }

/* Grid Utilities */
.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 1024px) {
  .lg\\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .md\\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\\:grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
}

@media (max-width: 640px) {
  .sm\\:grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
}

/* Spacing Utilities */
.m-0 { margin: 0; }
.m-auto { margin: auto; }
.mt-4 { margin-top: var(--spacing-4); }
.mt-6 { margin-top: var(--spacing-6); }
.mb-4 { margin-bottom: var(--spacing-4); }
.mb-6 { margin-bottom: var(--spacing-6); }
.p-4 { padding: var(--spacing-4); }
.p-6 { padding: var(--spacing-6); }
.px-4 { padding-left: var(--spacing-4); padding-right: var(--spacing-4); }
.py-4 { padding-top: var(--spacing-4); padding-bottom: var(--spacing-4); }

/* Width & Height */
.w-full { width: 100%; }
.h-full { height: 100%; }
.min-h-screen { min-height: 100vh; }

/* ============================================
   ANIMATIONS
   ============================================ */

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes skeleton {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

.animate-fadeIn { animation: fadeIn 0.3s ease-out; }
.animate-slideUp { animation: slideUp 0.3s ease-out; }
.animate-slideDown { animation: slideDown 0.3s ease-out; }
.animate-pulse { animation: pulse 2s infinite; }
.animate-spin { animation: spin 1s linear infinite; }
.animate-bounce { animation: bounce 1s infinite; }

/* Staggered animations for lists */
.stagger-1 { animation-delay: 50ms; }
.stagger-2 { animation-delay: 100ms; }
.stagger-3 { animation-delay: 150ms; }
.stagger-4 { animation-delay: 200ms; }
.stagger-5 { animation-delay: 250ms; }
"""

    def get_full_stylesheet(self) -> str:
        """Generate complete production-ready stylesheet"""
        return f"""/* ============================================
   PRODUCTION-READY DESIGN SYSTEM
   Generated by AI Coding Agent
   Theme: {self.theme['name']}
   ============================================ */

/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

{self.get_css_variables()}

{self.get_base_styles()}

{self.get_component_styles()}
"""

    @staticmethod
    def get_available_themes() -> List[str]:
        """Get list of available themes"""
        return list(DESIGN_TOKENS.keys())
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get color palette for current theme"""
        return self.theme["colors"]
    
    def generate_app_css(self, app_type: str = "generic") -> str:
        """
        Generate complete CSS for a specific app type
        
        Args:
            app_type: Type of application (todo, dashboard, form, etc.)
        """
        base_css = self.get_full_stylesheet()
        
        app_specific = ""
        
        if app_type == "todo":
            app_specific = self._get_todo_app_styles()
        elif app_type == "dashboard":
            app_specific = self._get_dashboard_styles()
        elif app_type == "form":
            app_specific = self._get_form_styles()
        elif app_type == "landing":
            app_specific = self._get_landing_styles()
        
        return f"{base_css}\n\n{app_specific}"
    
    def _get_todo_app_styles(self) -> str:
        """Get todo app specific styles"""
        return """/* ============================================
   TODO APP SPECIFIC STYLES
   ============================================ */

.todo-app {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-8);
}

.todo-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
}

.todo-header h1 {
  font-size: 2.5rem;
  background: var(--color-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.todo-input-section {
  display: flex;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
}

.todo-input {
  flex: 1;
}

.todo-filters {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.todo-filter-btn {
  flex: 1;
  padding: var(--spacing-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.todo-filter-btn:hover {
  color: var(--color-text-primary);
}

.todo-filter-btn.active {
  background: var(--color-bg-card);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.todo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.todo-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  animation: slideUp 0.3s ease-out;
}

.todo-item:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-md);
}

.todo-item.completed {
  opacity: 0.6;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: var(--color-text-muted);
}

.todo-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  appearance: none;
  transition: all var(--transition-fast);
  position: relative;
}

.todo-checkbox:checked {
  background: var(--color-gradient-success);
  border-color: var(--color-success);
}

.todo-checkbox:checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
}

.todo-text {
  flex: 1;
  color: var(--color-text-primary);
  font-size: 1rem;
}

.todo-delete-btn {
  padding: var(--spacing-2);
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  opacity: 0;
}

.todo-item:hover .todo-delete-btn {
  opacity: 1;
}

.todo-delete-btn:hover {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.todo-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.todo-clear-btn {
  color: var(--color-text-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.todo-clear-btn:hover {
  color: var(--color-error);
}

.todo-empty {
  text-align: center;
  padding: var(--spacing-10);
  color: var(--color-text-muted);
}

.todo-empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-4);
  opacity: 0.5;
}
"""

    def _get_dashboard_styles(self) -> str:
        """Get dashboard specific styles"""
        return """/* ============================================
   DASHBOARD SPECIFIC STYLES
   ============================================ */

.dashboard {
  display: flex;
  min-height: 100vh;
}

.dashboard-sidebar {
  width: 260px;
  background: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  padding: var(--spacing-6);
  display: flex;
  flex-direction: column;
}

.dashboard-logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-8);
}

.dashboard-logo-icon {
  width: 40px;
  height: 40px;
  background: var(--color-gradient-primary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
}

.dashboard-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  flex: 1;
}

.dashboard-nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.dashboard-nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.dashboard-nav-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
}

.dashboard-main {
  flex: 1;
  padding: var(--spacing-8);
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-8);
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-8);
}

@media (max-width: 1200px) {
  .dashboard-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-stats {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-lg);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 600;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-full);
}

.stat-change.positive {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.stat-change.negative {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-description {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-top: var(--spacing-2);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-6);
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
"""

    def _get_form_styles(self) -> str:
        """Get form-focused app styles"""
        return """/* ============================================
   FORM APP SPECIFIC STYLES
   ============================================ */

.form-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
}

.form-container {
  width: 100%;
  max-width: 480px;
}

.form-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-xl);
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
}

.form-logo {
  width: 64px;
  height: 64px;
  background: var(--color-gradient-primary);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--spacing-5);
  font-size: 1.5rem;
}

.form-title {
  font-size: 1.5rem;
  margin-bottom: var(--spacing-2);
}

.form-subtitle {
  color: var(--color-text-muted);
  font-size: 0.9375rem;
}

.form-group {
  margin-bottom: var(--spacing-5);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
}

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-divider {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  margin: var(--spacing-6) 0;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.form-divider::before,
.form-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-border);
}

.form-social {
  display: flex;
  gap: var(--spacing-3);
}

.form-social-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.form-social-btn:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-border-hover);
}

.form-footer {
  text-align: center;
  margin-top: var(--spacing-6);
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.form-footer a {
  color: var(--color-primary);
  font-weight: 500;
}
"""

    def _get_landing_styles(self) -> str:
        """Get landing page styles"""
        return """/* ============================================
   LANDING PAGE SPECIFIC STYLES
   ============================================ */

.landing {
  min-height: 100vh;
}

.landing-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: var(--spacing-4) var(--spacing-8);
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
}

.landing-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1280px;
  margin: 0 auto;
}

.landing-logo {
  font-size: 1.5rem;
  font-weight: 700;
  background: var(--color-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.landing-nav-links {
  display: flex;
  gap: var(--spacing-8);
}

.landing-nav-link {
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: color var(--transition-fast);
}

.landing-nav-link:hover {
  color: var(--color-text-primary);
}

.landing-hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--spacing-8);
  background: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
}

.landing-hero-content {
  max-width: 800px;
}

.landing-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-full);
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: var(--spacing-6);
}

.landing-title {
  font-size: 4rem;
  line-height: 1.1;
  margin-bottom: var(--spacing-6);
}

@media (max-width: 768px) {
  .landing-title {
    font-size: 2.5rem;
  }
}

.landing-title-highlight {
  background: var(--color-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.landing-description {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto var(--spacing-8);
}

.landing-cta {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
}

.landing-features {
  padding: var(--spacing-13) var(--spacing-8);
  background: var(--color-bg-secondary);
}

.landing-features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-8);
  max-width: 1280px;
  margin: 0 auto;
}

@media (max-width: 1024px) {
  .landing-features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .landing-features-grid {
    grid-template-columns: 1fr;
  }
}

.landing-feature {
  padding: var(--spacing-8);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  transition: all var(--transition-normal);
}

.landing-feature:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-glow-primary);
  transform: translateY(-4px);
}

.landing-feature-icon {
  width: 48px;
  height: 48px;
  background: var(--color-gradient-primary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-5);
  font-size: 1.5rem;
}

.landing-feature-title {
  font-size: 1.25rem;
  margin-bottom: var(--spacing-3);
}

.landing-feature-description {
  color: var(--color-text-muted);
  font-size: 0.9375rem;
  line-height: 1.6;
}
"""


# =============================================================================
# CSS VALIDATOR
# =============================================================================

class CSSValidator:
    """Validates CSS class usage between JSX and CSS files"""
    
    @staticmethod
    def extract_jsx_classes(jsx_content: str) -> set:
        """Extract className values from JSX content"""
        import re
        # Match className="..." and className={`...`}
        patterns = [
            r'className="([^"]+)"',
            r"className='([^']+)'",
            r'className=\{["`]([^"`]+)["`]\}',
        ]
        
        classes = set()
        for pattern in patterns:
            matches = re.findall(pattern, jsx_content)
            for match in matches:
                # Split by spaces for multiple classes
                for cls in match.split():
                    # Remove conditional syntax like ${...}
                    if not cls.startswith('$'):
                        classes.add(cls)
        
        return classes
    
    @staticmethod
    def extract_css_classes(css_content: str) -> set:
        """Extract class definitions from CSS content"""
        import re
        # Match .classname
        pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)'
        matches = re.findall(pattern, css_content)
        return set(matches)
    
    @staticmethod
    def validate(jsx_content: str, css_content: str) -> dict:
        """
        Validate that all JSX classes are defined in CSS
        
        Returns:
            dict with 'valid', 'missing_classes', 'unused_classes'
        """
        jsx_classes = CSSValidator.extract_jsx_classes(jsx_content)
        css_classes = CSSValidator.extract_css_classes(css_content)
        
        # Find missing classes (used in JSX but not defined in CSS)
        missing = jsx_classes - css_classes
        
        # Find unused classes (defined in CSS but not used in JSX)
        unused = css_classes - jsx_classes
        
        # Filter out utility classes that might be from frameworks
        utility_prefixes = ['flex', 'grid', 'items', 'justify', 'gap', 'p-', 'm-', 'w-', 'h-', 'text-', 'bg-']
        missing = {cls for cls in missing if not any(cls.startswith(p) for p in utility_prefixes)}
        
        return {
            'valid': len(missing) == 0,
            'missing_classes': list(missing),
            'unused_classes': list(unused),
            'jsx_classes': list(jsx_classes),
            'css_classes': list(css_classes),
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_app_styles(app_type: str = "generic", theme: str = "dark_modern") -> str:
    """
    Factory function to create complete styles for an application
    
    Args:
        app_type: Type of app (todo, dashboard, form, landing, generic)
        theme: Theme name (dark_modern, light_modern)
    
    Returns:
        Complete CSS string
    """
    design_system = DesignSystem(theme)
    return design_system.generate_app_css(app_type)
