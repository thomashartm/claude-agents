#!/usr/bin/env python3
"""
Validate architectural layer boundaries.

Checks:
- Domain has no imports from other layers or frameworks
- Application doesn't import from infrastructure/presentation
- Proper dependency direction

Usage:
    python validate_architecture.py <src_directory>
    python validate_architecture.py src/ --strict
"""

import argparse
import ast
import sys
from pathlib import Path
from dataclasses import dataclass

# Forbidden imports per layer
FORBIDDEN_FRAMEWORKS = {
    "domain": ["fastapi", "flask", "sqlalchemy", "pydantic", "django", "celery", "redis"],
    "application": ["fastapi", "flask", "django"],
}

FORBIDDEN_LAYERS = {
    "domain": ["application", "infrastructure", "presentation"],
    "application": ["infrastructure", "presentation"],
    "infrastructure": ["presentation"],
}


@dataclass
class Violation:
    file: str
    line: int
    layer: str
    import_name: str
    reason: str


def get_layer(filepath: str) -> str | None:
    """Determine which layer a file belongs to."""
    for layer in ["domain", "application", "infrastructure", "presentation"]:
        if f"/{layer}/" in filepath or filepath.endswith(f"/{layer}"):
            return layer
    return None


def extract_imports(filepath: Path) -> list[tuple[str, int]]:
    """Extract all imports from a Python file."""
    try:
        tree = ast.parse(filepath.read_text())
    except (SyntaxError, UnicodeDecodeError):
        return []
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.module, node.lineno))
    return imports


def check_file(filepath: Path) -> list[Violation]:
    """Check a single file for violations."""
    violations = []
    path_str = str(filepath)
    layer = get_layer(path_str)
    
    if not layer:
        return []
    
    imports = extract_imports(filepath)
    
    # Check forbidden frameworks
    for module, line in imports:
        for framework in FORBIDDEN_FRAMEWORKS.get(layer, []):
            if module == framework or module.startswith(f"{framework}."):
                violations.append(Violation(
                    file=path_str,
                    line=line,
                    layer=layer,
                    import_name=module,
                    reason=f"{layer} cannot import framework '{framework}'"
                ))
        
        # Check forbidden layer imports
        for forbidden_layer in FORBIDDEN_LAYERS.get(layer, []):
            if forbidden_layer in module.split("."):
                violations.append(Violation(
                    file=path_str,
                    line=line,
                    layer=layer,
                    import_name=module,
                    reason=f"{layer} cannot import from {forbidden_layer}"
                ))
    
    return violations


def validate(src_dir: Path) -> list[Violation]:
    """Validate all Python files in directory."""
    violations = []
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        violations.extend(check_file(py_file))
    return violations


def main():
    parser = argparse.ArgumentParser(description="Validate architecture boundaries")
    parser.add_argument("src_dir", type=Path, help="Source directory")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on violations")
    args = parser.parse_args()
    
    if not args.src_dir.exists():
        print(f"Error: {args.src_dir} not found")
        sys.exit(1)
    
    violations = validate(args.src_dir)
    
    if violations:
        print(f"❌ Found {len(violations)} violation(s):\n")
        
        by_layer = {}
        for v in violations:
            by_layer.setdefault(v.layer, []).append(v)
        
        for layer, layer_violations in sorted(by_layer.items()):
            print(f"[{layer.upper()}]")
            for v in layer_violations:
                print(f"  {v.file}:{v.line}")
                print(f"    import: {v.import_name}")
                print(f"    reason: {v.reason}")
            print()
        
        if args.strict:
            sys.exit(1)
    else:
        print("✅ No architectural violations found")


if __name__ == "__main__":
    main()
