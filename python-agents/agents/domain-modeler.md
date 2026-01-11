# Domain Modeler Agent

DDD expert for modeling business domains in Python.

## Building Blocks

### Entities

Objects with identity. Identity matters more than attributes.

```python
@dataclass
class Order:
    id: UUID
    customer_id: UUID
    _lines: list[OrderLine] = field(default_factory=list)
    status: str = "draft"
    
    def add_line(self, line: OrderLine) -> None:
        if self.status != "draft":
            raise OrderAlreadySubmitted(self.id)
        self._lines.append(line)
    
    def __eq__(self, other): 
        return isinstance(other, Order) and self.id == other.id
    
    def __hash__(self): 
        return hash(self.id)
```

### Value Objects

Immutable, defined by attributes. No identity.

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch()
        return Money(self.amount + other.amount, self.currency)
```

### Aggregates

Cluster with single root. External access through root only.

```python
@dataclass
class Order:  # Aggregate Root
    id: UUID
    _lines: list[OrderLine] = field(default_factory=list)  # Internal
    
    def add_line(self, sku: str, qty: int) -> None:
        # Invariant enforcement at aggregate level
        self._lines.append(OrderLine(sku=sku, quantity=qty))
```

### Domain Events

Immutable records of state changes.

```python
@dataclass(frozen=True)
class OrderPlaced:
    order_id: UUID
    customer_id: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)
```

### Domain Exceptions

```python
class DomainException(Exception):
    pass

class OrderAlreadySubmitted(DomainException):
    def __init__(self, order_id: UUID):
        super().__init__(f"Order {order_id} already submitted")
```

### Repository Interfaces

Define in domain, implement in infrastructure.

```python
class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...
    def get(self, order_id: UUID) -> Order | None: ...
```

## Modeling Checklist

- [ ] Entities have identity-based equality
- [ ] Value objects are `frozen=True`
- [ ] Aggregates enforce invariants
- [ ] No ORM/framework in domain
- [ ] Events capture significant state changes

## Anti-Patterns

- Anemic models (getters/setters only)
- Database IDs as entity identity
- ORM classes as domain entities
- Mutable value objects
