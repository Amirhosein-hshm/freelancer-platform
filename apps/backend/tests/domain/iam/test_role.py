from datetime import UTC, datetime

from app.domain.iam.entities import Role

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_role(**overrides: object) -> Role:
    defaults: dict[str, object] = {
        "id": "role-1",
        "role_key": "customer",
        "name": "Customer",
        "description": None,
        "is_system": True,
        "created_at": NOW,
    }
    defaults.update(overrides)
    return Role(**defaults)  # type: ignore[arg-type]


class TestRole:
    def test_rename_changes_name(self):
        role = make_role()
        role.rename("Client")
        assert role.name == "Client"

    def test_role_key_is_immutable(self):
        role = make_role(role_key="customer")
        assert role.role_key == "customer"

    def test_defaults(self):
        role = make_role()
        assert role.description is None
        assert role.is_system is True
