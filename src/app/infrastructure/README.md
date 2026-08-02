# infrastructure (Phase 2)

In Phase One this package is intentionally empty. Per `AGENTS.md` §2, real
implementations must only be written in Phase 2, and must never change
`domain`/`application` (Dependency Inversion Principle).

Planned implementations here:

- **Persistence**: SQLAlchemy + PostgreSQL repository classes that implement every
  `I*Repository` interface defined in `app/domain/*/repositories.py`
  (`IUserRepository`, `IProjectRepository`, ...).
- **Security** (`infrastructure/security`):
  - `ITokenService` via PyJWT (access + refresh tokens),
  - `IPasswordHasher` via argon2/bcrypt.
- **Storage** (`infrastructure/storage`): `IFileStorageService` for local/S3 file assets.
- **Ports**: implementations of `IClock`, `IIdGenerator`, `IEventPublisher`,
  `INotificationService`, `IUnitOfWork`, `IAuthorizationService`,
  `IProjectCodeGenerator` (all defined in `app/application/shared/ports.py` and
  `app/application/shared/authorization.py`).

Every infrastructure error (DB/network/external API) must be translated/wrapped into a
`DomainError`/`ApplicationError` before reaching `application` (see `ERROR_HANDLING.md`).
