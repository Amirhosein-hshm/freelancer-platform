from app.application.shared.ports import INotificationService


class FakeNotificationService(INotificationService):
    def __init__(self) -> None:
        self.emails: list[tuple[str, str, str]] = []
        self.verification_tokens: list[str] = []
        self.reset_tokens: list[str] = []

    async def send_email(self, to: str, subject: str, body: str) -> None:
        self.emails.append((to, subject, body))

    async def send_verification_email(self, to: str, token: str) -> None:
        self.verification_tokens.append(token)
        await self.send_email(to, "Verify your email", token)

    async def send_password_reset_email(self, to: str, token: str) -> None:
        self.reset_tokens.append(token)
        await self.send_email(to, "Reset your password", token)
