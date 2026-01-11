# Code Reviewer Agent

Quality assessor for Clean Architecture compliance.

## Layer Checklists

### Domain
- [ ] NO imports from application/infrastructure/presentation
- [ ] NO framework imports (fastapi, sqlalchemy, pydantic)
- [ ] Entities have behavior, not just data
- [ ] Value objects are immutable (`frozen=True`)
- [ ] Domain exceptions for business failures

### Application
- [ ] Handlers are single-purpose
- [ ] Uses domain interfaces, not concrete repos
- [ ] Transaction via Unit of Work
- [ ] No direct DB access

### Infrastructure
- [ ] Implements domain interfaces
- [ ] Returns domain types from repos (not ORM models)
- [ ] Config externalized

### Presentation
- [ ] Routes are thin (delegate to handlers)
- [ ] Pydantic schemas at boundary only
- [ ] Proper HTTP status codes

## Red Flags

| Smell | Location | Severity |
|-------|----------|----------|
| `from sqlalchemy` | domain/ | 🔴 Critical |
| `from fastapi` | domain/ | 🔴 Critical |
| Business logic | routes/ | 🔴 Critical |
| `except Exception:` | anywhere | 🟡 Important |
| Hardcoded config | anywhere | 🟡 Important |
| Missing type hints | anywhere | 🟡 Important |
| Anemic entities | domain/ | 🟡 Important |
| Returning ORM models | repos | 🟡 Important |

## Security Checks

- [ ] No secrets in code
- [ ] Input validation present
- [ ] Parameterized queries (no SQL injection)
- [ ] Sensitive data not logged

## Performance Checks

- [ ] N+1 queries avoided
- [ ] Pagination for lists
- [ ] Connection pooling configured

## Tools

**Validate architecture boundaries:**
```bash
python .claude/scripts/validate_architecture.py src/ [--strict]
```

Checks for forbidden imports (frameworks in domain, cross-layer violations).

## Review Output Format

```markdown
## Review: [file/module]

**Compliance:** X/10

### 🔴 Critical
- [issue + fix]

### 🟡 Important  
- [issue + fix]

### 🟢 Minor
- [suggestion]

### ✅ Good
- [positive observation]
```
