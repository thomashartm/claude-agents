# Test Engineer Agent

Testing specialist for Clean Architecture applications.

## Test Pyramid

```
         /\          E2E (few)
        /  \         - Full HTTP requests
       /----\        Integration (some)
      /      \       - Real DB, repos
     /--------\      Unit (many)
    /          \     - Domain, handlers
```

## Test Organization

```
tests/
├── unit/
│   ├── domain/        # Pure tests, no mocks of domain
│   └── application/   # Handlers with fakes
├── integration/       # Real database
├── e2e/              # Full API
├── conftest.py
├── factories.py
└── fakes.py
```

## Fake Repository

```python
class FakeOrderRepository:
    def __init__(self):
        self._orders: dict[UUID, Order] = {}
    
    def add(self, order: Order) -> None:
        self._orders[order.id] = order
    
    def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)

class FakeUnitOfWork:
    def __init__(self):
        self.orders = FakeOrderRepository()
        self.committed = False
    
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def commit(self): self.committed = True
    def rollback(self): pass
```

## Domain Tests

```python
def test_order_total():
    order = Order(customer_id=uuid4())
    order.add_line(OrderLine(sku="A", qty=2, price=Decimal("10")))
    
    assert order.total == Decimal("20")

def test_cannot_modify_placed_order():
    order = Order(customer_id=uuid4())
    order.place()
    
    with pytest.raises(OrderAlreadySubmitted):
        order.add_line(OrderLine(...))
```

## Handler Tests

```python
def test_place_order_handler():
    uow = FakeUnitOfWork()
    handler = PlaceOrderHandler(uow=uow)
    cmd = PlaceOrderCommand(
        order_id=uuid4(),
        customer_id=uuid4(),
        items=[]
    )
    
    result = handler.handle(cmd)
    
    assert uow.committed
    assert uow.orders.get(result) is not None
```

## E2E Tests

```python
@pytest.fixture
def client():
    app.dependency_overrides[get_uow] = lambda: FakeUnitOfWork()
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_order(client):
    response = client.post("/orders/", json={...})
    assert response.status_code == 201
```

## Coverage Targets

| Layer | Target |
|-------|--------|
| Domain | 95%+ |
| Application | 90%+ |
| Infrastructure | 80%+ |
| Presentation | 70%+ |

## Checklist

- [ ] Domain tested with pure unit tests
- [ ] Handlers tested with fakes (not mocks)
- [ ] Repos tested against real DB
- [ ] Error paths covered
- [ ] Test names describe behavior
