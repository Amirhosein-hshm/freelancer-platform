from app.domain.category.entities import Category, CategorySupervisor


def to_domain_category(row: object) -> Category:
    return Category(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        parent_category_id=row.parent_category_id,
        category_key=row.category_key,
        name=row.name,
        slug=row.slug,
        description=row.description,
        is_active=row.is_active,
        sort_order=row.sort_order,
        deleted_at=row.deleted_at,
    )


def to_domain_category_supervisor(row: object) -> CategorySupervisor:
    return CategorySupervisor(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        category_id=row.category_id,
        supervisor_user_id=row.supervisor_user_id,
        assigned_by_user_id=row.assigned_by_user_id,
        is_primary=row.is_primary,
        is_active=row.is_active,
        assigned_at=row.assigned_at,
        revoked_at=row.revoked_at,
    )