from datetime import UTC, datetime

from app.domain.shared.entity import AggregateRoot, Entity
from app.domain.shared.events import DomainEvent


class FakeEntity(Entity):
    pass


class FakeAggregate(AggregateRoot):
    pass


class FakeEvent(DomainEvent):
    pass


def _now() -> datetime:
    return datetime(2026, 8, 2, tzinfo=UTC)


class TestEntityEquality:
    def test_entities_with_same_id_are_equal(self):
        e1 = FakeEntity(id="x", created_at=_now())
        e2 = FakeEntity(id="x", created_at=_now().replace(second=1))
        assert e1 == e2

    def test_entities_with_different_ids_are_not_equal(self):
        e1 = FakeEntity(id="x", created_at=_now())
        e3 = FakeEntity(id="y", created_at=_now())
        assert e1 != e3

    def test_entity_is_not_equal_to_non_entity(self):
        assert FakeEntity(id="x", created_at=_now()) != "x"

    def test_hash_is_based_on_id(self):
        e1 = FakeEntity(id="x", created_at=_now())
        e2 = FakeEntity(id="x", created_at=_now().replace(second=1))
        assert hash(e1) == hash(e2)
        assert len({e1, e2}) == 1

    def test_created_at_defaults_are_exposed(self):
        entity = FakeEntity(id="x", created_at=_now())
        assert entity.created_at == _now()
        assert entity.updated_at is None


class TestAggregateRootEvents:
    def test_recorded_event_can_be_pulled(self):
        aggregate = FakeAggregate(id="a", created_at=_now())
        event = FakeEvent(occurred_at=_now())
        aggregate._record_event(event)

        events = aggregate.pull_domain_events()

        assert events == [event]

    def test_pull_clears_recorded_events(self):
        aggregate = FakeAggregate(id="a", created_at=_now())
        aggregate._record_event(FakeEvent(occurred_at=_now()))

        assert aggregate.pull_domain_events()
        assert aggregate.pull_domain_events() == []
