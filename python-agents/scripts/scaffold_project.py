#!/usr/bin/env python3
"""
Scaffold a Clean Architecture Python project.

Usage:
    python scaffold_project.py <name> [-o output_dir]
"""

import argparse
from pathlib import Path

DIRS = [
    "src/{name}/domain/entities",
    "src/{name}/domain/value_objects",
    "src/{name}/domain/events",
    "src/{name}/domain/services",
    "src/{name}/domain/interfaces",
    "src/{name}/application/commands",
    "src/{name}/application/queries",
    "src/{name}/application/handlers",
    "src/{name}/infrastructure/persistence",
    "src/{name}/infrastructure/messaging",
    "src/{name}/infrastructure/external",
    "src/{name}/presentation/api/routes",
    "src/{name}/presentation/api/schemas",
    "src/{name}/presentation/cli",
    "src/{name}/presentation/consumers",
    "tests/unit/domain",
    "tests/unit/application",
    "tests/integration",
    "tests/e2e",
]

FILES = {
    "src/{name}/domain/exceptions.py": '''"""Domain exceptions."""

class DomainException(Exception):
    """Base domain exception."""
    pass
''',
    "src/{name}/application/unit_of_work.py": '''"""Abstract Unit of Work."""
from abc import ABC, abstractmethod
from typing import Self

class AbstractUnitOfWork(ABC):
    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, *args) -> None:
        self.rollback()
    
    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError
''',
    "src/{name}/infrastructure/config.py": '''"""Configuration."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    debug: bool = False
    
    class Config:
        env_file = ".env"
''',
    "src/{name}/bootstrap.py": '''"""Dependency injection."""
from functools import lru_cache
from .infrastructure.config import Settings

@lru_cache
def get_settings() -> Settings:
    return Settings()
''',
    "src/{name}/main.py": '''"""Application entry point."""
from fastapi import FastAPI

app = FastAPI(title="{title}")

@app.get("/health")
def health():
    return {{"status": "healthy"}}
''',
    "tests/conftest.py": '''"""Pytest fixtures."""
import pytest
''',
    "tests/fakes.py": '''"""Fake implementations for testing."""
''',
    "tests/factories.py": '''"""Test factories."""
from uuid import uuid4
''',
    "pyproject.toml": '''[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov>=4.0", "ruff>=0.1", "mypy>=1.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true
''',
    ".gitignore": '''__pycache__/
*.py[cod]
.venv/
.env
*.db
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
''',
}


def main():
    parser = argparse.ArgumentParser(description="Scaffold Clean Architecture project")
    parser.add_argument("name", help="Project name (snake_case)")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    args = parser.parse_args()
    
    name = args.name.lower().replace("-", "_")
    title = name.replace("_", " ").title()
    base = Path(args.output)
    
    print(f"Creating {name}...")
    
    # Create directories
    for d in DIRS:
        path = base / d.format(name=name)
        path.mkdir(parents=True, exist_ok=True)
        (path / "__init__.py").touch()
    
    # Create files
    for filepath, content in FILES.items():
        path = base / filepath.format(name=name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.format(name=name, title=title))
        print(f"  ✓ {path}")
    
    print(f"\n✅ Project '{name}' created!")
    print(f"\nNext steps:")
    print(f"  cd {base}")
    print(f"  python -m venv .venv && source .venv/bin/activate")
    print(f"  pip install -e '.[dev]'")


if __name__ == "__main__":
    main()
