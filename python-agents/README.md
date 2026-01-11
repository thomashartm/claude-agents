# Python Clean Architecture Agents

Development agents for Claude Code following Clean Architecture, DDD, and Event-Driven patterns.

## Installation

Use the installer skill in `~/.claude/skills/install-python-agents/`:

```bash
# Install to a project
python ~/.claude/skills/install-python-agents/scripts/install.py /path/to/project

# Or with this repo as source
python install.py /path/to/project --repo yourusername/python-agents
```

## Agents

| Agent | Purpose |
|-------|---------|
| `architect.md` | System design, layers, patterns |
| `domain-modeler.md` | Entities, Value Objects, Aggregates |
| `implementer.md` | Production code implementation |
| `test-engineer.md` | Testing strategy & implementation |
| `code-reviewer.md` | Quality & compliance review |
| `patterns.md` | Quick pattern reference |

## Scripts

- `scaffold_project.py` - Generate project structure
- `validate_architecture.py` - Check layer boundaries

## Usage in Claude Code

After installation, invoke agents:

```
Read .claude/agents/architect.md and design a payment service
Read .claude/agents/code-reviewer.md and review src/domain/
```

## Project Structure (Generated)

```
src/{name}/
├── domain/           # Pure business logic
├── application/      # Use cases
├── infrastructure/   # External adapters  
└── presentation/     # API, CLI, consumers
```
