import inspect
from unittest.mock import AsyncMock

import pytest

from app.domain.freelancer.exceptions import ResumeNotFoundError
from app.domain.project.exceptions import RevisionRequestNotFoundError
from app.infrastructure.repositories.project_revision_request_repository import (
    SqlAlchemyProjectRevisionRequestRepository,
)
from app.infrastructure.repositories.resume_repository import SqlAlchemyResumeRepository


def test_sqlalchemy_repositories_implement_their_domain_contracts() -> None:
    repositories = (
        SqlAlchemyResumeRepository,
        SqlAlchemyProjectRevisionRequestRepository,
    )

    for repository in repositories:
        assert not inspect.isabstract(repository), (
            f"{repository.__name__} is missing implementations for "
            f"{sorted(repository.__abstractmethods__)}"
        )


async def test_resume_repository_missing_id_raises_domain_error() -> None:
    session = AsyncMock()
    session.get.return_value = None
    repository = SqlAlchemyResumeRepository(session)

    with pytest.raises(ResumeNotFoundError):
        await repository.get_by_id("missing")
    with pytest.raises(ResumeNotFoundError):
        await repository.delete("missing")


async def test_resume_repository_delete_uses_the_session() -> None:
    session = AsyncMock()
    row = object()
    session.get.return_value = row
    repository = SqlAlchemyResumeRepository(session)

    await repository.delete("resume-1")

    session.delete.assert_awaited_once_with(row)


async def test_revision_repository_missing_id_raises_specific_error() -> None:
    session = AsyncMock()
    session.get.return_value = None
    repository = SqlAlchemyProjectRevisionRequestRepository(session)

    with pytest.raises(RevisionRequestNotFoundError):
        await repository.get_by_id("missing")
