from datetime import UTC, datetime
from decimal import Decimal

from app.application.form.dto import (
    AddFieldCommand,
    CreateFormTemplateCommand,
    PublishFormTemplateCommand,
)
from app.application.form.use_cases.add_field import AddFieldUseCase
from app.application.form.use_cases.create_form_template import CreateFormTemplateUseCase
from app.application.form.use_cases.publish_form_template import PublishFormTemplateUseCase
from app.application.project.dto import (
    AcceptFreelancerCommand,
    ApplyForProjectCommand,
    CompleteProjectCommand,
    CreateProjectCommand,
    FormValueInput,
    PublishProjectCommand,
    RequestRevisionCommand,
    StartProjectCommand,
    SubmitDeliveryCommand,
)
from app.application.project.use_cases.accept_freelancer import AcceptFreelancerUseCase
from app.application.project.use_cases.apply_for_project import ApplyForProjectUseCase
from app.application.project.use_cases.complete_project import CompleteProjectUseCase
from app.application.project.use_cases.create_project import CreateProjectUseCase
from app.application.project.use_cases.publish_project import PublishProjectUseCase
from app.application.project.use_cases.request_revision import RequestRevisionUseCase
from app.application.project.use_cases.start_project import StartProjectUseCase
from app.application.project.use_cases.submit_delivery import SubmitDeliveryUseCase
from app.domain.form.enums import FormFieldType
from app.domain.project.enums import (
    BudgetType,
    ProjectStatus,
    ProjectVisibility,
)

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def test_full_project_lifecycle(
    project_repo,
    category_repo,
    form_template_repo,
    status_history_repo,
    application_repo,
    delivery_repo,
    revision_repo,
    review_repo,
    profile_repo,
    level_repo,
    project_code_generator,
    id_generator,
    clock,
    uow,
    make_category,
    make_profile,
    make_level,
):
    make_category(category_id="cat-1")
    make_level(level_id="level-1", max_active_applications=3)
    make_profile(profile_id="profile-1", user_id="freelancer-1")

    create_template = CreateFormTemplateUseCase(
        template_repo=form_template_repo, id_generator=id_generator, clock=clock, uow=uow
    )
    template_result = create_template.execute(
        CreateFormTemplateCommand(category_id="cat-1", name="Project Form", template_key="project-form")
    )
    add_field = AddFieldUseCase(
        template_repo=form_template_repo, id_generator=id_generator, clock=clock, uow=uow
    )
    add_field_result = add_field.execute(
        AddFieldCommand(
            template_id=template_result.template_id,
            field_key="title",
            label="Title",
            field_type=FormFieldType.TEXT,
            is_required=True,
        )
    )
    publish_template = PublishFormTemplateUseCase(
        template_repo=form_template_repo, clock=clock, uow=uow
    )
    publish_template.execute(
        PublishFormTemplateCommand(template_id=template_result.template_id, published_by="admin-1")
    )

    create_project = CreateProjectUseCase(
        project_repo=project_repo,
        category_repo=category_repo,
        form_template_repo=form_template_repo,
        status_history_repo=status_history_repo,
        project_code_generator=project_code_generator,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    created = create_project.execute(
        CreateProjectCommand(
            customer_user_id="customer-1",
            category_id="cat-1",
            title="Build an API",
            description="REST API for orders",
            visibility=ProjectVisibility.PUBLIC,
            budget_type=BudgetType.FIXED,
            currency_code="USD",
            fixed_budget=Decimal("1000"),
            form_values=[FormValueInput(field_id=add_field_result.field_id, value="Orders")],
        )
    )
    assert created.status == ProjectStatus.DRAFT

    publish_project = PublishProjectUseCase(
        project_repo=project_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    published = publish_project.execute(
        PublishProjectCommand(actor_id="customer-1", project_id=created.project_id)
    )
    assert published.status == ProjectStatus.COLLECTING_APPLICATIONS

    apply = ApplyForProjectUseCase(
        project_repo=project_repo,
        application_repo=application_repo,
        profile_repo=profile_repo,
        level_repo=level_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    application = apply.execute(
        ApplyForProjectCommand(
            actor_id="freelancer-1",
            project_id=created.project_id,
            proposed_amount=Decimal("900"),
        )
    )

    accept = AcceptFreelancerUseCase(
        project_repo=project_repo,
        application_repo=application_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    accepted = accept.execute(
        AcceptFreelancerCommand(actor_id="customer-1", application_id=application.application_id)
    )
    assert accepted.status == ProjectStatus.ASSIGNED

    start = StartProjectUseCase(
        project_repo=project_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    started = start.execute(
        StartProjectCommand(actor_id="customer-1", project_id=created.project_id)
    )
    assert started.status == ProjectStatus.IN_PROGRESS

    submit = SubmitDeliveryUseCase(
        project_repo=project_repo,
        application_repo=application_repo,
        delivery_repo=delivery_repo,
        status_history_repo=status_history_repo,
        profile_repo=profile_repo,
        review_repo=review_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    first_delivery = submit.execute(
        SubmitDeliveryCommand(actor_id="freelancer-1", project_id=created.project_id, delivery_note="v1")
    )
    assert first_delivery.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW

    revise = RequestRevisionUseCase(
        project_repo=project_repo,
        revision_repo=revision_repo,
        delivery_repo=delivery_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    revised = revise.execute(
        RequestRevisionCommand(actor_id="customer-1", project_id=created.project_id, reason="Fix auth")
    )
    assert revised.project_status == ProjectStatus.REVISION_REQUESTED

    second_delivery = submit.execute(
        SubmitDeliveryCommand(actor_id="freelancer-1", project_id=created.project_id, delivery_note="v2")
    )
    assert second_delivery.version_no == 2
    assert second_delivery.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW
    assert delivery_repo.get_by_id(first_delivery.delivery_id).status.value == "superseded"

    complete = CompleteProjectUseCase(
        project_repo=project_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )
    completed = complete.execute(
        CompleteProjectCommand(actor_id="customer-1", project_id=created.project_id)
    )
    assert completed.status == ProjectStatus.COMPLETED

    project = project_repo.get_by_id(created.project_id)
    assert project.is_locked() is True
    assert project.completed_at == NOW
    assert len(revision_repo.list_by_project(project.id)) == 1
