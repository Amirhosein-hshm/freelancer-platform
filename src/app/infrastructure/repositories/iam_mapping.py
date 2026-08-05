from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash, PhoneNumber


def to_domain_user(row: object) -> User:
    return User(
        id=row.id,
        email=Email(row.email),
        phone=PhoneNumber(row.phone) if row.phone else None,
        password_hash=PasswordHash(row.password_hash),
        first_name=row.first_name,
        last_name=row.last_name,
        status=UserStatus(row.status),
        created_at=row.created_at,
        email_verified_at=row.email_verified_at,
        phone_verified_at=row.phone_verified_at,
        last_login_at=row.last_login_at,
        password_changed_at=row.password_changed_at,
        deleted_at=row.deleted_at,
    )