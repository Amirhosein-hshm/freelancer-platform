from dataclasses import dataclass

from app.application.project.dto import SupervisorResult
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.category.repositories import ICategoryRepository, ICategorySupervisorRepository
from app.domain.iam.repositories import IUserRepository
from app.domain.project.entities import Project

MAX_CATEGORY_SUPERVISOR_DEPTH = 64


class CategoryHierarchyError(RuntimeError):
    """Raised when category ancestry is cyclic or exceeds the supported depth."""


@dataclass(frozen=True)
class EffectiveSupervisor:
    user: SupervisorResult
    category_id: str


async def get_effective_supervisor(
    project: Project,
    category_repo: ICategoryRepository | None,
    category_supervisor_repo: ICategorySupervisorRepository,
    user_repo: IUserRepository | None,
) -> EffectiveSupervisor | None:
    category_id: str | None = project.category_id
    visited: set[str] = set()
    depth = 0
    while category_id is not None:
        if category_id in visited:
            raise CategoryHierarchyError(f"Cycle detected in category hierarchy at {category_id}")
        if depth >= MAX_CATEGORY_SUPERVISOR_DEPTH:
            raise CategoryHierarchyError("Category hierarchy exceeds maximum supported depth")
        visited.add(category_id)
        depth += 1
        supervisors = await category_supervisor_repo.list_active_supervisors(category_id)
        if supervisors:
            link = next((item for item in supervisors if item.is_primary), supervisors[0])
            user = await user_repo.find_by_id(link.supervisor_user_id) if user_repo is not None else None
            if user_repo is None:
                return EffectiveSupervisor(
                    user=SupervisorResult(
                        user_id=link.supervisor_user_id,
                        email="",
                        first_name="",
                        last_name="",
                    ),
                    category_id=category_id,
                )
            if user is not None and user.is_active():
                return EffectiveSupervisor(
                    user=SupervisorResult(
                        user_id=user.id,
                        email=user.email.value,
                        first_name=user.first_name,
                        last_name=user.last_name,
                    ),
                    category_id=category_id,
                )
        if category_repo is None:
            break
        try:
            category = await category_repo.get_by_id(category_id)
        except CategoryNotFoundError:
            return None
        category_id = category.parent_category_id
    return None
