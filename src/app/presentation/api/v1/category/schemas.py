from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    category_id: str
    category_key: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    sort_order: int
    parent_category_id: str | None


class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    category_key: str = Field(..., min_length=1)
    description: str | None = None
    parent_category_id: str | None = None
    sort_order: int = 0


class UpdateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    description: str | None = None
    sort_order: int = 0


class DeleteCategoryResponse(BaseModel):
    category_id: str


class AssignSupervisorRequest(BaseModel):
    supervisor_user_id: str


class AssignSupervisorResponse(BaseModel):
    link_id: str
    category_id: str
    supervisor_user_id: str


class RemoveSupervisorResponse(BaseModel):
    category_id: str
    supervisor_user_id: str
    revoked_at: str


class CategorySupervisorResponse(BaseModel):
    link_id: str
    category_id: str
    supervisor_user_id: str
    is_primary: bool
    assigned_at: str


class ListCategorySupervisorsResponse(BaseModel):
    supervisors: list[CategorySupervisorResponse]