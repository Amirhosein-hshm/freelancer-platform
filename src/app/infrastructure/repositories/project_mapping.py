from app.domain.project.entities import (
    Project,
    ProjectApplication,
    ProjectDelivery,
    ProjectRevisionRequest,
    ProjectStatusHistory,
)
from app.domain.project.enums import (
    BudgetType,
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
    RevisionRequestStatus,
)
from app.domain.project.value_objects import Budget, ProjectCode


def to_domain_project(row: object) -> Project:
    return Project(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        project_code=ProjectCode(row.project_code),
        customer_user_id=row.customer_user_id,
        category_id=row.category_id,
        form_template_id=row.form_template_id,
        assigned_supervisor_user_id=row.assigned_supervisor_user_id,
        selected_application_id=row.selected_application_id,
        title=row.title,
        description=row.description,
        visibility=ProjectVisibility(row.visibility),
        priority=ProjectPriority(row.priority),
        budget=Budget(
            budget_type=BudgetType(row.budget_type),
            fixed_amount=row.fixed_amount,
            min_amount=row.min_amount,
            max_amount=row.max_amount,
            currency_code=row.currency_code,
        ),
        status=ProjectStatus(row.status),
        application_deadline=row.application_deadline,
        start_at=row.start_at,
        due_at=row.due_at,
        completed_at=row.completed_at,
        cancelled_at=row.cancelled_at,
        locked_at=row.locked_at,
        deleted_at=row.deleted_at,
        created_by_user_id=row.created_by_user_id,
    )


def to_domain_project_application(row: object) -> ProjectApplication:
    return ProjectApplication(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        project_id=row.project_id,
        freelancer_profile_id=row.freelancer_profile_id,
        status=ProjectApplicationStatus(row.status),
        cover_letter=row.cover_letter,
        proposed_amount=row.proposed_amount,
        proposed_days=row.proposed_days,
        applied_at=row.applied_at,
        decided_by_user_id=row.decided_by_user_id,
        decided_at=row.decided_at,
        decision_note=row.decision_note,
        withdrawn_at=row.withdrawn_at,
        submitted_by_user_id=row.submitted_by_user_id,
    )


def to_domain_project_delivery(row: object) -> ProjectDelivery:
    return ProjectDelivery(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        project_id=row.project_id,
        version_no=row.version_no,
        submitted_by_user_id=row.submitted_by_user_id,
        status=DeliveryStatus(row.status),
        delivery_note=row.delivery_note,
        submitted_at=row.submitted_at,
        reviewed_at=row.reviewed_at,
        reviewer_user_id=row.reviewer_user_id,
        superseded_by_delivery_id=row.superseded_by_delivery_id,
        file_asset_ids=list(row.file_asset_ids),
    )


def to_domain_project_revision_request(row: object) -> ProjectRevisionRequest:
    return ProjectRevisionRequest(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        project_id=row.project_id,
        project_delivery_id=row.project_delivery_id,
        requested_by_user_id=row.requested_by_user_id,
        requested_to_user_id=row.requested_to_user_id,
        round_no=row.round_no,
        status=RevisionRequestStatus(row.status),
        reason=row.reason,
        resolved_by_user_id=row.resolved_by_user_id,
        requested_at=row.requested_at,
        resolved_at=row.resolved_at,
    )


def to_domain_project_status_history(row: object) -> ProjectStatusHistory:
    return ProjectStatusHistory(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        project_id=row.project_id,
        from_status=ProjectStatus(row.from_status) if row.from_status else None,
        to_status=ProjectStatus(row.to_status),
        changed_by_user_id=row.changed_by_user_id,
        reason=row.reason,
        changed_at=row.changed_at,
    )
