from tests.presentation.conftest import auth_header


class TestFileRouter:
    def test_upload_and_download_file(self, client, token_service):
        headers = auth_header(token_service, "user-1", ["freelancer"])
        content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"

        response = client.post(
            "/api/v1/files",
            headers=headers,
            files={"file": ("report.pdf", content, "application/pdf")},
            data={"context": "generic"},
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["mime_type"] == "application/pdf"
        assert payload["data"]["size_bytes"] == len(content)
        assert payload["data"]["context"] == "generic"
        file_asset_id = payload["data"]["file_asset_id"]

        get_response = client.get(
            f"/api/v1/files/{file_asset_id}",
            headers=headers,
        )

        assert get_response.status_code == 200
        assert get_response.headers["content-type"] == "application/pdf"
        assert get_response.content == content

    def test_get_foreign_file_denied(self, client, token_service):
        owner_headers = auth_header(token_service, "user-1", ["freelancer"])
        other_headers = auth_header(token_service, "user-2", ["customer"])
        content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"

        upload_response = client.post(
            "/api/v1/files",
            headers=owner_headers,
            files={"file": ("report.pdf", content, "application/pdf")},
            data={"context": "generic"},
        )
        file_asset_id = upload_response.json()["data"]["file_asset_id"]

        response = client.get(
            f"/api/v1/files/{file_asset_id}",
            headers=other_headers,
        )

        assert response.status_code == 403
