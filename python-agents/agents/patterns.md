# Patterns Quick Reference

## Dependency Rule

```
Presentation → Application → Domain ← Infrastructure
```

**Domain has NO dependencies.**

## Repository

Abstract data access. Interface in domain, implementation in infrastructure.

```python
# domain/interfaces/
class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...
    def get(self, id: UUID) -> Order | None: ...

# infrastructure/persistence/
class SqlAlchemyOrderRepo:
    def add(self, order: Order) -> None:
        self.session.add(to_model(order))
```

## Unit of Work

Transaction boundary across repositories.

```python
class AbstractUnitOfWork(ABC):
    orders: OrderRepository
    
    def __enter__(self) -> Self: return self
    def __exit__(self, *args): self.rollback()
    
    @abstractmethod
    def commit(self): ...
    @abstractmethod  
    def rollback(self): ...

# Usage
with uow:
    order = uow.orders.get(id)
    order.cancel()
    uow.commit()
```

## CQRS

Separate read and write models.

```python
# Command (write) - goes through domain
class PlaceOrderHandler:
    def handle(self, cmd):
        with self.uow:
            order = Order(...)
            self.uow.orders.add(order)
            self.uow.commit()

# Query (read) - can bypass domain
class GetOrderHandler:
    def handle(self, query):
        return self.session.execute(
            "SELECT * FROM orders WHERE id = :id", 
            {"id": query.order_id}
        ).first()
```

## Domain Events

Record state changes, publish after commit.

```python
@dataclass(frozen=True)
class OrderPlaced:
    order_id: UUID
    occurred_at: datetime

# In entity
def place(self):
    self.status = "placed"
    self.events.append(OrderPlaced(self.id))

# In UoW
def commit(self):
    self.session.commit()
    for entity in self._tracked:
        for event in entity.events:
            self.publisher.publish(event)
```

## Adapter/Port

Isolate external systems.

```python
# Port (interface)
class PaymentGateway(Protocol):
    def charge(self, amount: Money) -> Result: ...

# Adapter (implementation)
class StripeAdapter:
    def charge(self, amount: Money) -> Result:
        return self.client.charges.create(...)
```

## Pattern Selection

| Need | Pattern |
|------|---------|
| Abstract data access | Repository |
| Transaction boundary | Unit of Work |
| Separate read/write | CQRS |
| Cross-boundary notify | Domain Events |
| Complex construction | Factory |
| External service | Adapter/Port |
