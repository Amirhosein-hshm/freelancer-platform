from app.presentation.core import providers
from tests.presentation.conftest import auth_header


class TestAdminOnBehalfRoutes:
    def _authz(self, client):
        return client.app.dependency_overrides[providers.get_authorization_service]()

    def test_admin_create_project_without_permission_is_denied(self, client, token_service):
        response = client.post(
            "/api/v1/admin/projects",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={
                "target_customer_user_id": "customer-1",
                "category_id": "cat-1",
                "title": "Admin Project",
                "description": "Created by admin",
                "visibility": "public",
                "budget_type": "fixed",
                "currency_code": "USD",
                "fixed_budget": "100.00",
            },
        )
        assert response.status_code == 403

    def test_admin_create_project_missing_target_user_returns_not_found(self, client, token_service):
        self._authz(client).grant("admin-1", "project.create_on_behalf")
        response = client.post(
            "/api/v1/admin/projects",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={
                "target_customer_user_id": "missing-customer",
                "category_id": "cat-1",
                "title": "Admin Project",
                "description": "Created by admin",
                "visibility": "public",
                "budget_type": "fixed",
                "currency_code": "USD",
                "fixed_budget": "100.00",
            },
        )
        assert response.status_code == 404

    def test_admin_apply_for_project_without_permission_is_denied(self, client, token_service):
        response = client.post(
            "/api/v1/admin/projects/project-1/applications",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={"target_freelancer_profile_id": "profile-1"},
        )
        assert response.status_code == 403

    def test_admin_apply_for_project_missing_target_profile_returns_not_found(self, client, token_service):
        self._authz(client).grant("admin-1", "project.apply_on_behalf")
        response = client.post(
            "/api/v1/admin/projects/project-1/applications",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={"target_freelancer_profile_id": "missing-profile"},
        )
        assert response.status_code == 404

    def test_admin_create_freelancer_profile_without_permission_is_denied(self, client, token_service):
        response = client.post(
            "/api/v1/admin/freelancers",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={"target_user_id": "user-1", "display_name": "Admin Created"},
        )
        assert response.status_code == 403

    def test_admin_create_freelancer_profile_missing_target_user_returns_not_found(self, client, token_service):
        self._authz(client).grant("admin-1", "freelancer.create_on_behalf")
        response = client.post(
            "/api/v1/admin/freelancers",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={"target_user_id": "missing-user", "display_name": "Admin Created"},
        )
        assert response.status_code == 404

    def test_admin_create_ticket_without_permission_is_denied(self, client, token_service):
        response = client.post(
            "/api/v1/admin/tickets",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={"target_user_id": "user-1", "subject": "Admin Ticket"},
        )
        assert response.status_code == 403

    def test_admin_create_ticket_missing_target_user_returns_not_found(self, client, token_service):
        self._authz(client).grant("admin-1", "ticket.create_on_behalf")
        response = client.post(
            "/api/v1/admin/tickets",
            headers=auth_header(token_service, "admin-1", ["admin"]),
            json={"target_user_id": "missing-user", "subject": "Admin Ticket"},
        )
        assert response.status_code == 404
