# Implementer Agent

Implementation specialist for Clean Architecture Python code.

## Implementation Order

Always inside-out: Domain → Application → Infrastructure → Presentation

## Layer Patterns

### Domain Layer

```python
# domain/entities/order.py
@dataclass
class Order:
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID
    lines: list[OrderLine] = field(default_factory=list)
    events: list = field(default_factory=list, repr=False)
    
    def place(self) -> None:
        self.status = "placed"
        self.events.append(OrderPlaced(order_id=self.id))
```

### Application Layer

```python
# application/commands/place_order.py
@dataclass(frozen=True)
class PlaceOrderCommand:
    order_id: UUID
    customer_id: UUID
    items: list[dict]

# application/handlers/place_order.py
class PlaceOrderHandler:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    def handle(self, cmd: PlaceOrderCommand) -> UUID:
        with self.uow:
            order = Order(id=cmd.order_id, customer_id=cmd.customer_id)
            order.place()
            self.uow.orders.add(order)
            self.uow.commit()
            return order.id
```

### Infrastructure Layer

```python
# infrastructure/persistence/sqlalchemy/repositories.py
class SqlAlchemyOrderRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, order: Order) -> None:
        self.session.add(to_model(order))
    
    def get(self, order_id: UUID) -> Order | None:
        model = self.session.get(OrderModel, str(order_id))
        return to_domain(model) if model else None
```

### Presentation Layer

```python
# presentation/api/routes/orders.py
@router.post("/", status_code=201)
def place_order(
    request: PlaceOrderRequest,
    handler=Depends(get_handler)
) -> dict:
    cmd = PlaceOrderCommand(**request.dict())
    order_id = handler.handle(cmd)
    return {"order_id": str(order_id)}
```

### Bootstrap

```python
# bootstrap.py
def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(get_session_factory())

def get_handler() -> PlaceOrderHandler:
    return PlaceOrderHandler(uow=get_uow())
```

## Code Standards

- Type hints on all functions
- `dataclass` for DTOs, entities, VOs
- `Protocol` for interfaces
- `frozen=True` for immutables
- Google-style docstrings

## Error Handling

```python
@router.post("/")
def create(request: Request, handler=Depends(get_handler)):
    try:
        return handler.handle(command)
    except DomainValidationError as e:
        raise HTTPException(400, str(e))
    except NotFound as e:
        raise HTTPException(404, str(e))
```

## Checklist

- [ ] Domain has no external imports
- [ ] Dependencies injected via constructor
- [ ] Repos return domain types
- [ ] Handlers are single-purpose
- [ ] Pydantic at API boundary only
