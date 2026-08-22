# ruff: noqa: B008  (Depends() in defaults is the FastAPI DI idiom, not an "in-band arg")
"""Provider stubs for the Presentation layer.

Every signature here is the contract between ``presentation`` and the
``bootstrap`` Composition Root. The stubs raise ``NotImplementedError`` by
default; ``bootstrap/container.py`` overrides each one with a real
infrastructure implementation via ``app.dependency_overrides``.

This file must never import from ``app.infrastructure``.
"""

from fastapi import Depends

from app.application.category.use_cases.assign_supervisor import AssignSupervisorUseCase
from app.application.category.use_cases.create_category import CreateCategoryUseCase
from app.application.category.use_cases.delete_category import DeleteCategoryUseCase
from app.application.category.use_cases.get_categories import GetCategoriesUseCase
from app.application.category.use_cases.get_category import GetCategoryUseCase
from app.application.category.use_cases.get_category_projects import GetCategoryProjectsUseCase
from app.application.category.use_cases.list_category_supervisors import ListCategorySupervisorsUseCase
from app.application.category.use_cases.remove_supervisor import RemoveSupervisorUseCase
from app.application.category.use_cases.update_category import UpdateCategoryUseCase
from app.application.feedback.use_cases.delete_customer_review import DeleteCustomerReviewUseCase
from app.application.feedback.use_cases.delete_rating import DeleteRatingUseCase
from app.application.feedback.use_cases.get_customer_review import GetCustomerReviewUseCase
from app.application.feedback.use_cases.get_freelancer_ratings import GetFreelancerRatingsUseCase
from app.application.feedback.use_cases.get_project_rating import GetProjectRatingUseCase
from app.application.feedback.use_cases.list_customer_reviews import ListCustomerReviewsUseCase
from app.application.feedback.use_cases.submit_rating import SubmitRatingUseCase
from app.application.feedback.use_cases.submit_review import SubmitReviewUseCase
from app.application.feedback.use_cases.update_customer_review import UpdateCustomerReviewUseCase
from app.application.feedback.use_cases.update_rating import UpdateRatingUseCase
from app.application.file.use_cases.get_file_asset import GetFileAssetUseCase
from app.application.file.use_cases.upload_file import UploadFileUseCase
from app.application.form.use_cases.add_field import AddFieldUseCase
from app.application.form.use_cases.add_field_option import AddFieldOptionUseCase
from app.application.form.use_cases.create_form_template import CreateFormTemplateUseCase
from app.application.form.use_cases.delete_form_template import DeleteFormTemplateUseCase
from app.application.form.use_cases.get_form_template import GetFormTemplateUseCase
from app.application.form.use_cases.get_form_template_by_id import GetFormTemplateByIdUseCase
from app.application.form.use_cases.list_form_template_versions import ListFormTemplateVersionsUseCase
from app.application.form.use_cases.list_form_templates import ListFormTemplatesUseCase
from app.application.form.use_cases.publish_form_template import PublishFormTemplateUseCase
from app.application.form.use_cases.remove_field import RemoveFieldUseCase
from app.application.form.use_cases.remove_field_option import RemoveFieldOptionUseCase
from app.application.form.use_cases.update_field import UpdateFieldUseCase
from app.application.form.use_cases.update_field_option import UpdateFieldOptionUseCase
from app.application.form.use_cases.update_form_template import UpdateFormTemplateUseCase
from app.application.freelancer.use_cases.add_portfolio_item import AddPortfolioItemUseCase
from app.application.freelancer.use_cases.admin_create_freelancer_profile_on_behalf import (
    AdminCreateFreelancerProfileOnBehalfUseCase,
)
from app.application.freelancer.use_cases.approve_freelancer import ApproveFreelancerUseCase
from app.application.freelancer.use_cases.assign_freelancer_level import AssignFreelancerLevelUseCase
from app.application.freelancer.use_cases.create_freelancer_profile import CreateFreelancerProfileUseCase
from app.application.freelancer.use_cases.delete_portfolio_item import DeletePortfolioItemUseCase
from app.application.freelancer.use_cases.delete_resume import DeleteResumeUseCase
from app.application.freelancer.use_cases.get_current_resume import GetCurrentResumeUseCase
from app.application.freelancer.use_cases.get_freelancer_profile import GetFreelancerProfileUseCase
from app.application.freelancer.use_cases.get_portfolio_item import GetPortfolioItemUseCase
from app.application.freelancer.use_cases.get_resume import GetResumeUseCase
from app.application.freelancer.use_cases.list_freelancer_level_history import ListFreelancerLevelHistoryUseCase
from app.application.freelancer.use_cases.list_freelancer_profiles_by_approval_status import (
    ListFreelancerProfilesByApprovalStatusUseCase,
)
from app.application.freelancer.use_cases.list_portfolio_items import ListPortfolioItemsUseCase
from app.application.freelancer.use_cases.list_resume_versions import ListResumeVersionsUseCase
from app.application.freelancer.use_cases.set_current_resume import SetCurrentResumeUseCase
from app.application.freelancer.use_cases.soft_delete_freelancer_profile import SoftDeleteFreelancerProfileUseCase
from app.application.freelancer.use_cases.submit_freelancer_approval import SubmitFreelancerApprovalUseCase
from app.application.freelancer.use_cases.update_freelancer_profile import UpdateFreelancerProfileUseCase
from app.application.freelancer.use_cases.update_portfolio_item import UpdatePortfolioItemUseCase
from app.application.freelancer.use_cases.update_resume import UpdateResumeUseCase
from app.application.freelancer.use_cases.upload_resume import UploadResumeUseCase
from app.application.iam.use_cases.activate_user import ActivateUserUseCase
from app.application.iam.use_cases.admin_create_user import AdminCreateUserUseCase
from app.application.iam.use_cases.admin_delete_user import AdminDeleteUserUseCase
from app.application.iam.use_cases.admin_get_user import AdminGetUserUseCase
from app.application.iam.use_cases.admin_list_users import AdminListUsersUseCase
from app.application.iam.use_cases.admin_update_user import AdminUpdateUserUseCase
from app.application.iam.use_cases.assign_role import AssignRoleUseCase
from app.application.iam.use_cases.block_user import BlockUserUseCase
from app.application.iam.use_cases.change_password import ChangePasswordUseCase
from app.application.iam.use_cases.forgot_password import ForgotPasswordUseCase
from app.application.iam.use_cases.grant_permission import GrantPermissionUseCase
from app.application.iam.use_cases.list_permissions import ListPermissionsUseCase
from app.application.iam.use_cases.list_roles import ListRolesUseCase
from app.application.iam.use_cases.login_user import LoginUserUseCase
from app.application.iam.use_cases.logout_user import LogoutUserUseCase
from app.application.iam.use_cases.refresh_token import RefreshTokenUseCase
from app.application.iam.use_cases.register_user import RegisterUserUseCase
from app.application.iam.use_cases.remove_role import RemoveRoleUseCase
from app.application.iam.use_cases.revoke_permission import RevokePermissionUseCase
from app.application.project.use_cases.accept_freelancer import AcceptFreelancerUseCase
from app.application.project.use_cases.admin_apply_for_project_on_behalf import AdminApplyForProjectOnBehalfUseCase
from app.application.project.use_cases.admin_create_project_on_behalf import AdminCreateProjectOnBehalfUseCase
from app.application.project.use_cases.apply_for_project import ApplyForProjectUseCase
from app.application.project.use_cases.cancel_project import CancelProjectUseCase
from app.application.project.use_cases.close_project_revision_request import CloseProjectRevisionRequestUseCase
from app.application.project.use_cases.complete_project import CompleteProjectUseCase
from app.application.project.use_cases.create_project import CreateProjectUseCase
from app.application.project.use_cases.delete_project import DeleteProjectUseCase
from app.application.project.use_cases.get_available_projects import GetAvailableProjectsUseCase
from app.application.project.use_cases.get_my_projects import GetMyProjectsUseCase
from app.application.project.use_cases.get_project_application import GetProjectApplicationUseCase
from app.application.project.use_cases.get_project_delivery import GetProjectDeliveryUseCase
from app.application.project.use_cases.get_project_details import GetProjectDetailsUseCase
from app.application.project.use_cases.get_project_revision_request import GetProjectRevisionRequestUseCase
from app.application.project.use_cases.list_project_deliveries import ListProjectDeliveriesUseCase
from app.application.project.use_cases.list_project_revision_requests import ListProjectRevisionRequestsUseCase
from app.application.project.use_cases.list_project_status_history import ListProjectStatusHistoryUseCase
from app.application.project.use_cases.publish_project import PublishProjectUseCase
from app.application.project.use_cases.reject_freelancer import RejectFreelancerUseCase
from app.application.project.use_cases.request_revision import RequestRevisionUseCase
from app.application.project.use_cases.start_project import StartProjectUseCase
from app.application.project.use_cases.submit_delivery import SubmitDeliveryUseCase
from app.application.project.use_cases.update_project import UpdateProjectUseCase
from app.application.project.use_cases.view_applications import ViewApplicationsUseCase
from app.application.project.use_cases.withdraw_application import WithdrawApplicationUseCase
from app.application.reporting.use_cases.get_customer_statistics import GetCustomerStatisticsUseCase
from app.application.reporting.use_cases.get_dashboard_statistics import GetDashboardStatisticsUseCase
from app.application.reporting.use_cases.get_freelancer_statistics import GetFreelancerStatisticsUseCase
from app.application.reporting.use_cases.get_project_statistics import GetProjectStatisticsUseCase
from app.application.reporting.use_cases.get_system_analytics import GetSystemAnalyticsUseCase
from app.application.reporting.use_cases.get_user_statistics import GetUserStatisticsUseCase
from app.application.review.use_cases.approve_delivery import ApproveDeliveryUseCase
from app.application.review.use_cases.get_pending_reviews import GetPendingReviewsUseCase
from app.application.review.use_cases.get_supervisor_projects import GetSupervisorProjectsUseCase
from app.application.review.use_cases.get_supervisor_review import GetSupervisorReviewUseCase
from app.application.review.use_cases.reject_delivery import RejectDeliveryUseCase
from app.application.review.use_cases.review_delivery import ReviewDeliveryUseCase
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import (
    IClock,
    IFileAccessPolicy,
    IFileStorageService,
    IIdGenerator,
    INotificationService,
    IRealtimeNotifier,
    IPasswordHasher,
    IProjectCodeGenerator,
    ITicketCodeGenerator,
    ITokenService,
    IUnitOfWork,
)
from app.application.ticketing.use_cases.admin_create_ticket_on_behalf import AdminCreateTicketOnBehalfUseCase
from app.application.ticketing.use_cases.close_ticket import CloseTicketUseCase
from app.application.ticketing.use_cases.create_ticket import CreateTicketUseCase
from app.application.ticketing.use_cases.delete_ticket_message import DeleteTicketMessageUseCase
from app.application.ticketing.use_cases.get_ticket import GetTicketUseCase
from app.application.ticketing.use_cases.get_ticket_messages import GetTicketMessagesUseCase
from app.application.ticketing.use_cases.get_user_tickets import GetUserTicketsUseCase
from app.application.ticketing.use_cases.list_related_users import ListRelatedUsersUseCase
from app.application.ticketing.use_cases.send_message import SendMessageUseCase
from app.application.ticketing.use_cases.update_ticket import UpdateTicketUseCase
from app.application.ticketing.use_cases.update_ticket_message import UpdateTicketMessageUseCase
from app.domain.category.repositories import ICategoryRepository, ICategorySupervisorRepository
from app.domain.feedback.repositories import ICustomerReviewRepository, IRatingRepository
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.freelancer.repositories import (
    IFreelancerLevelHistoryRepository,
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
    IResumeRepository,
)
from app.domain.iam.repositories import (
    IPermissionRepository,
    IRefreshTokenRepository,
    IRolePermissionRepository,
    IRoleRepository,
    IUserRepository,
    IUserRoleRepository,
)
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.reporting.repositories import IReportingReadRepository
from app.domain.review.repositories import ISupervisorReviewRepository
from app.domain.ticketing.repositories import (
    IRelatedUsersRepository,
    ITicketMessageRepository,
    ITicketRepository,
)
from app.domain.ticketing.services import RelationshipEligibilityService


def get_authorization_service() -> IAuthorizationService:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_category_repository() -> ICategoryRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_category_supervisor_repository() -> ICategorySupervisorRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_clock() -> IClock:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_customer_review_repository() -> ICustomerReviewRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_file_access_policy() -> IFileAccessPolicy:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_file_storage_service() -> IFileStorageService:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_form_template_repository() -> IFormTemplateRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_freelancer_level_history_repository() -> IFreelancerLevelHistoryRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")



def get_freelancer_profile_repository() -> IFreelancerProfileRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_id_generator() -> IIdGenerator:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_notification_service() -> INotificationService:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_realtime_notifier() -> IRealtimeNotifier:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_password_hasher() -> IPasswordHasher:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_permission_repository() -> IPermissionRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_portfolio_item_repository() -> IPortfolioItemRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_project_application_repository() -> IProjectApplicationRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_project_code_generator() -> IProjectCodeGenerator:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_project_delivery_repository() -> IProjectDeliveryRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_project_repository() -> IProjectRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_project_revision_request_repository() -> IProjectRevisionRequestRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_project_status_history_repository() -> IProjectStatusHistoryRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_rating_repository() -> IRatingRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_refresh_token_repository() -> IRefreshTokenRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_reporting_read_repository() -> IReportingReadRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_resume_repository() -> IResumeRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_role_permission_repository() -> IRolePermissionRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_role_repository() -> IRoleRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_supervisor_review_repository() -> ISupervisorReviewRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_ticket_code_generator() -> ITicketCodeGenerator:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_ticket_message_repository() -> ITicketMessageRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_related_users_repository() -> IRelatedUsersRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_ticket_repository() -> ITicketRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_relationship_eligibility_service() -> RelationshipEligibilityService:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_token_service() -> ITokenService:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_unit_of_work() -> IUnitOfWork:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_user_repository() -> IUserRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_user_role_repository() -> IUserRoleRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")


def get_accept_freelancer_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AcceptFreelancerUseCase:
    return AcceptFreelancerUseCase(
        authorization_service,
        project_repo,
        application_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_activate_user_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> ActivateUserUseCase:
    return ActivateUserUseCase(authorization_service, user_repo, clock, uow)


def get_add_field_option_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AddFieldOptionUseCase:
    return AddFieldOptionUseCase(authorization_service, template_repo, id_generator, clock, uow)


def get_add_field_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AddFieldUseCase:
    return AddFieldUseCase(authorization_service, template_repo, id_generator, clock, uow)


def get_add_portfolio_item_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    portfolio_item_repo: IPortfolioItemRepository = Depends(get_portfolio_item_repository),
    file_storage: IFileStorageService = Depends(get_file_storage_service),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AddPortfolioItemUseCase:
    return AddPortfolioItemUseCase(
        profile_repo,
        portfolio_item_repo,
        file_storage,
        id_generator,
        clock,
        uow,
    )


def get_admin_apply_for_project_on_behalf_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminApplyForProjectOnBehalfUseCase:
    return AdminApplyForProjectOnBehalfUseCase(
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        id_generator,
        clock,
        uow,
    )


def get_admin_create_freelancer_profile_on_behalf_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminCreateFreelancerProfileOnBehalfUseCase:
    return AdminCreateFreelancerProfileOnBehalfUseCase(
        authorization_service,
        user_repo,
        profile_repo,
        id_generator,
        clock,
        uow,
    )


def get_admin_create_project_on_behalf_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
    form_template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    project_code_generator: IProjectCodeGenerator = Depends(get_project_code_generator),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminCreateProjectOnBehalfUseCase:
    return AdminCreateProjectOnBehalfUseCase(
        authorization_service,
        user_repo,
        project_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
    )


def get_admin_create_ticket_on_behalf_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    ticket_code_generator: ITicketCodeGenerator = Depends(get_ticket_code_generator),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    relationship_service: RelationshipEligibilityService = Depends(get_relationship_eligibility_service),
) -> AdminCreateTicketOnBehalfUseCase:
    return AdminCreateTicketOnBehalfUseCase(
        authorization_service,
        user_repo,
        ticket_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
        relationship_service,
    )


def get_admin_create_user_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminCreateUserUseCase:
    return AdminCreateUserUseCase(
        authorization_service,
        user_repo,
        password_hasher,
        id_generator,
        clock,
        uow,
    )


def get_admin_delete_user_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminDeleteUserUseCase:
    return AdminDeleteUserUseCase(
        authorization_service,
        user_repo,
        user_role_repo,
        role_repo,
        clock,
        uow,
    )


def get_admin_get_user_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
) -> AdminGetUserUseCase:
    return AdminGetUserUseCase(authorization_service, user_repo, user_role_repo)


def get_admin_list_users_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> AdminListUsersUseCase:
    return AdminListUsersUseCase(authorization_service, user_repo)


def get_admin_update_user_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminUpdateUserUseCase:
    return AdminUpdateUserUseCase(authorization_service, user_repo, uow)


def get_apply_for_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> ApplyForProjectUseCase:
    return ApplyForProjectUseCase(
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        id_generator,
        clock,
        uow,
    )


def get_approve_delivery_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
    category_supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
    review_repo: ISupervisorReviewRepository = Depends(get_supervisor_review_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> ApproveDeliveryUseCase:
    return ApproveDeliveryUseCase(
        authorization_service,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_approve_freelancer_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> ApproveFreelancerUseCase:
    return ApproveFreelancerUseCase(authorization_service, profile_repo, clock, uow)


def get_assign_freelancer_level_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    level_history_repo: IFreelancerLevelHistoryRepository = Depends(get_freelancer_level_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AssignFreelancerLevelUseCase:
    return AssignFreelancerLevelUseCase(
        authorization_service,
        profile_repo,
        level_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_assign_role_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AssignRoleUseCase:
    return AssignRoleUseCase(
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        id_generator,
        clock,
        uow,
    )


def get_assign_supervisor_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    category_repo: ICategoryRepository = Depends(get_category_repository),
    category_supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AssignSupervisorUseCase:
    return AssignSupervisorUseCase(
        authorization_service,
        category_repo,
        category_supervisor_repo,
        user_repo,
        id_generator,
        clock,
        uow,
    )


def get_block_user_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> BlockUserUseCase:
    return BlockUserUseCase(authorization_service, user_repo, clock, uow)


def get_update_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    form_template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(authorization_service, project_repo, form_template_repo, uow)


def get_delete_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(authorization_service, project_repo, clock, uow)


def get_cancel_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CancelProjectUseCase:
    return CancelProjectUseCase(
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_change_password_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(user_repo, password_hasher, clock, uow)


def get_close_project_revision_request_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    clock: IClock = Depends(get_clock),
) -> CloseProjectRevisionRequestUseCase:
    return CloseProjectRevisionRequestUseCase(
        authorization_service,
        project_repo,
        revision_repo,
        clock,
    )


def get_close_ticket_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CloseTicketUseCase:
    return CloseTicketUseCase(authorization_service, ticket_repo, clock, uow)


def get_complete_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CompleteProjectUseCase:
    return CompleteProjectUseCase(
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_create_category_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    category_repo: ICategoryRepository = Depends(get_category_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CreateCategoryUseCase:
    return CreateCategoryUseCase(authorization_service, category_repo, id_generator, clock, uow)


def get_create_form_template_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CreateFormTemplateUseCase:
    return CreateFormTemplateUseCase(authorization_service, template_repo, id_generator, clock, uow)


def get_create_freelancer_profile_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CreateFreelancerProfileUseCase:
    return CreateFreelancerProfileUseCase(
        authorization_service,
        profile_repo,
        id_generator,
        clock,
        uow,
    )


def get_create_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    form_template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    project_code_generator: IProjectCodeGenerator = Depends(get_project_code_generator),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CreateProjectUseCase:
    return CreateProjectUseCase(
        authorization_service,
        project_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
    )


def get_create_ticket_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    ticket_code_generator: ITicketCodeGenerator = Depends(get_ticket_code_generator),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    relationship_service: RelationshipEligibilityService = Depends(get_relationship_eligibility_service),
) -> CreateTicketUseCase:
    return CreateTicketUseCase(
        ticket_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
        relationship_service,
    )


def get_delete_category_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    category_repo: ICategoryRepository = Depends(get_category_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase(authorization_service, category_repo, project_repo, clock, uow)


def get_delete_customer_review_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    customer_review_repo: ICustomerReviewRepository = Depends(get_customer_review_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeleteCustomerReviewUseCase:
    return DeleteCustomerReviewUseCase(
        project_repo,
        customer_review_repo,
        authorization_service,
        uow,
    )


def get_delete_form_template_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeleteFormTemplateUseCase:
    return DeleteFormTemplateUseCase(authorization_service, template_repo, project_repo, clock, uow)


def get_delete_portfolio_item_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    portfolio_item_repo: IPortfolioItemRepository = Depends(get_portfolio_item_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeletePortfolioItemUseCase:
    return DeletePortfolioItemUseCase(profile_repo, portfolio_item_repo, clock, uow)


def get_delete_rating_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    rating_repo: IRatingRepository = Depends(get_rating_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeleteRatingUseCase:
    return DeleteRatingUseCase(project_repo, rating_repo, authorization_service, uow)


def get_delete_resume_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
) -> DeleteResumeUseCase:
    return DeleteResumeUseCase(authorization_service, profile_repo, resume_repo)


def get_delete_ticket_message_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    message_repo: ITicketMessageRepository = Depends(get_ticket_message_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DeleteTicketMessageUseCase:
    return DeleteTicketMessageUseCase(
        ticket_repo,
        message_repo,
        authorization_service,
        clock,
        uow,
    )


def get_forgot_password_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    notification_service: INotificationService = Depends(get_notification_service),
) -> ForgotPasswordUseCase:
    return ForgotPasswordUseCase(user_repo, id_generator, notification_service)


def get_get_available_projects_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> GetAvailableProjectsUseCase:
    return GetAvailableProjectsUseCase(project_repo, profile_repo)


def get_get_categories_use_case(
    category_repo: ICategoryRepository = Depends(get_category_repository),
) -> GetCategoriesUseCase:
    return GetCategoriesUseCase(category_repo)


def get_get_category_projects_use_case(
    category_repo: ICategoryRepository = Depends(get_category_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
) -> GetCategoryProjectsUseCase:
    return GetCategoryProjectsUseCase(category_repo, project_repo)


def get_get_category_use_case(
    category_repo: ICategoryRepository = Depends(get_category_repository),
) -> GetCategoryUseCase:
    return GetCategoryUseCase(category_repo)


def get_get_current_resume_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
) -> GetCurrentResumeUseCase:
    return GetCurrentResumeUseCase(authorization_service, profile_repo, resume_repo)


def get_get_customer_review_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    customer_review_repo: ICustomerReviewRepository = Depends(get_customer_review_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
) -> GetCustomerReviewUseCase:
    return GetCustomerReviewUseCase(project_repo, customer_review_repo, authorization_service)


def get_get_customer_statistics_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    reporting_read_repo: IReportingReadRepository = Depends(get_reporting_read_repository),
) -> GetCustomerStatisticsUseCase:
    return GetCustomerStatisticsUseCase(authorization_service, reporting_read_repo)


def get_get_dashboard_statistics_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    reporting_read_repo: IReportingReadRepository = Depends(get_reporting_read_repository),
) -> GetDashboardStatisticsUseCase:
    return GetDashboardStatisticsUseCase(authorization_service, reporting_read_repo)


def get_get_file_asset_use_case(
    file_storage: IFileStorageService = Depends(get_file_storage_service),
    access_policy: IFileAccessPolicy = Depends(get_file_access_policy),
) -> GetFileAssetUseCase:
    return GetFileAssetUseCase(file_storage, access_policy)


def get_get_form_template_by_id_use_case(
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
) -> GetFormTemplateByIdUseCase:
    return GetFormTemplateByIdUseCase(template_repo)


def get_get_form_template_use_case(
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
) -> GetFormTemplateUseCase:
    return GetFormTemplateUseCase(template_repo)


def get_get_freelancer_profile_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> GetFreelancerProfileUseCase:
    return GetFreelancerProfileUseCase(profile_repo)


def get_get_freelancer_ratings_use_case(
    rating_repo: IRatingRepository = Depends(get_rating_repository),
) -> GetFreelancerRatingsUseCase:
    return GetFreelancerRatingsUseCase(rating_repo)


def get_get_freelancer_statistics_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    reporting_read_repo: IReportingReadRepository = Depends(get_reporting_read_repository),
) -> GetFreelancerStatisticsUseCase:
    return GetFreelancerStatisticsUseCase(authorization_service, reporting_read_repo)


def get_get_my_projects_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
) -> GetMyProjectsUseCase:
    return GetMyProjectsUseCase(project_repo)


def get_get_pending_reviews_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    review_repo: ISupervisorReviewRepository = Depends(get_supervisor_review_repository),
) -> GetPendingReviewsUseCase:
    return GetPendingReviewsUseCase(review_repo, authorization_service)


def get_get_portfolio_item_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    portfolio_item_repo: IPortfolioItemRepository = Depends(get_portfolio_item_repository),
) -> GetPortfolioItemUseCase:
    return GetPortfolioItemUseCase(authorization_service, profile_repo, portfolio_item_repo)


def get_get_project_application_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> GetProjectApplicationUseCase:
    return GetProjectApplicationUseCase(
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
    )


def get_get_project_delivery_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
) -> GetProjectDeliveryUseCase:
    return GetProjectDeliveryUseCase(authorization_service, project_repo, delivery_repo)


def get_get_project_details_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> GetProjectDetailsUseCase:
    return GetProjectDetailsUseCase(project_repo, application_repo, delivery_repo, authorization_service, profile_repo)


def get_get_project_rating_use_case(
    rating_repo: IRatingRepository = Depends(get_rating_repository),
) -> GetProjectRatingUseCase:
    return GetProjectRatingUseCase(rating_repo)


def get_get_project_revision_request_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> GetProjectRevisionRequestUseCase:
    return GetProjectRevisionRequestUseCase(
        authorization_service, project_repo, revision_repo, application_repo, profile_repo
    )


def get_get_project_statistics_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    reporting_read_repo: IReportingReadRepository = Depends(get_reporting_read_repository),
) -> GetProjectStatisticsUseCase:
    return GetProjectStatisticsUseCase(authorization_service, reporting_read_repo)


def get_get_resume_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
) -> GetResumeUseCase:
    return GetResumeUseCase(authorization_service, profile_repo, resume_repo)


def get_get_supervisor_projects_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
) -> GetSupervisorProjectsUseCase:
    return GetSupervisorProjectsUseCase(project_repo, authorization_service)


def get_get_supervisor_review_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    review_repo: ISupervisorReviewRepository = Depends(get_supervisor_review_repository),
    category_supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
) -> GetSupervisorReviewUseCase:
    return GetSupervisorReviewUseCase(
        project_repo,
        delivery_repo,
        review_repo,
        category_supervisor_repo,
        authorization_service,
    )


def get_get_system_analytics_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    reporting_read_repo: IReportingReadRepository = Depends(get_reporting_read_repository),
) -> GetSystemAnalyticsUseCase:
    return GetSystemAnalyticsUseCase(authorization_service, reporting_read_repo)


def get_get_ticket_messages_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    message_repo: ITicketMessageRepository = Depends(get_ticket_message_repository),
) -> GetTicketMessagesUseCase:
    return GetTicketMessagesUseCase(ticket_repo, message_repo)


def get_get_ticket_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
) -> GetTicketUseCase:
    return GetTicketUseCase(ticket_repo, authorization_service)


def get_get_user_statistics_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    reporting_read_repo: IReportingReadRepository = Depends(get_reporting_read_repository),
) -> GetUserStatisticsUseCase:
    return GetUserStatisticsUseCase(authorization_service, reporting_read_repo)


def get_get_user_tickets_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
) -> GetUserTicketsUseCase:
    return GetUserTicketsUseCase(authorization_service, ticket_repo)


def get_list_related_users_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    related_users_repo: IRelatedUsersRepository = Depends(get_related_users_repository),
) -> ListRelatedUsersUseCase:
    return ListRelatedUsersUseCase(authorization_service, related_users_repo)


def get_grant_permission_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    role_repo: IRoleRepository = Depends(get_role_repository),
    permission_repo: IPermissionRepository = Depends(get_permission_repository),
    role_permission_repo: IRolePermissionRepository = Depends(get_role_permission_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> GrantPermissionUseCase:
    return GrantPermissionUseCase(
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        id_generator,
        clock,
        uow,
    )


def get_list_category_supervisors_use_case(
    category_repo: ICategoryRepository = Depends(get_category_repository),
    supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
) -> ListCategorySupervisorsUseCase:
    return ListCategorySupervisorsUseCase(category_repo, supervisor_repo)


def get_list_customer_reviews_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    customer_review_repo: ICustomerReviewRepository = Depends(get_customer_review_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
) -> ListCustomerReviewsUseCase:
    return ListCustomerReviewsUseCase(project_repo, customer_review_repo, authorization_service)


def get_list_form_templates_use_case(
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
) -> ListFormTemplatesUseCase:
    return ListFormTemplatesUseCase(template_repo)


def get_list_form_template_versions_use_case(
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
) -> ListFormTemplateVersionsUseCase:
    return ListFormTemplateVersionsUseCase(template_repo)


def get_list_freelancer_level_history_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    level_history_repo: IFreelancerLevelHistoryRepository = Depends(get_freelancer_level_history_repository),
) -> ListFreelancerLevelHistoryUseCase:
    return ListFreelancerLevelHistoryUseCase(
        authorization_service,
        profile_repo,
        level_history_repo,
    )


def get_list_freelancer_profiles_by_approval_status_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> ListFreelancerProfilesByApprovalStatusUseCase:
    return ListFreelancerProfilesByApprovalStatusUseCase(authorization_service, profile_repo)


def get_list_permissions_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    permission_repo: IPermissionRepository = Depends(get_permission_repository),
) -> ListPermissionsUseCase:
    return ListPermissionsUseCase(authorization_service, permission_repo)


def get_list_portfolio_items_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    portfolio_item_repo: IPortfolioItemRepository = Depends(get_portfolio_item_repository),
) -> ListPortfolioItemsUseCase:
    return ListPortfolioItemsUseCase(authorization_service, profile_repo, portfolio_item_repo)


def get_list_project_deliveries_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> ListProjectDeliveriesUseCase:
    return ListProjectDeliveriesUseCase(
        authorization_service, project_repo, delivery_repo, application_repo, profile_repo
    )


def get_list_project_revision_requests_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> ListProjectRevisionRequestsUseCase:
    return ListProjectRevisionRequestsUseCase(
        authorization_service, project_repo, revision_repo, application_repo, profile_repo
    )


def get_list_project_status_history_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
) -> ListProjectStatusHistoryUseCase:
    return ListProjectStatusHistoryUseCase(authorization_service, project_repo, status_history_repo)


def get_list_resume_versions_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
) -> ListResumeVersionsUseCase:
    return ListResumeVersionsUseCase(authorization_service, profile_repo, resume_repo)


def get_list_roles_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    role_repo: IRoleRepository = Depends(get_role_repository),
) -> ListRolesUseCase:
    return ListRolesUseCase(authorization_service, role_repo)


def get_login_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    token_service: ITokenService = Depends(get_token_service),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repo,
        user_role_repo,
        refresh_token_repo,
        password_hasher,
        token_service,
        id_generator,
        clock,
        uow,
    )


def get_logout_user_use_case(
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> LogoutUserUseCase:
    return LogoutUserUseCase(refresh_token_repo, clock, uow)


def get_publish_form_template_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> PublishFormTemplateUseCase:
    return PublishFormTemplateUseCase(authorization_service, template_repo, clock, uow)


def get_publish_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> PublishProjectUseCase:
    return PublishProjectUseCase(
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_refresh_token_use_case(
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
    token_service: ITokenService = Depends(get_token_service),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
    )


def get_register_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    notification_service: INotificationService = Depends(get_notification_service),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo,
        user_role_repo,
        role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
    )


def get_reject_delivery_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
    category_supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
    review_repo: ISupervisorReviewRepository = Depends(get_supervisor_review_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RejectDeliveryUseCase:
    return RejectDeliveryUseCase(
        authorization_service,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_reject_freelancer_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RejectFreelancerUseCase:
    return RejectFreelancerUseCase(
        authorization_service,
        project_repo,
        application_repo,
        clock,
        uow,
    )


def get_remove_field_option_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RemoveFieldOptionUseCase:
    return RemoveFieldOptionUseCase(authorization_service, template_repo, uow)


def get_remove_field_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RemoveFieldUseCase:
    return RemoveFieldUseCase(authorization_service, template_repo, uow)


def get_remove_role_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    user_repo: IUserRepository = Depends(get_user_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
    user_role_repo: IUserRoleRepository = Depends(get_user_role_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RemoveRoleUseCase:
    return RemoveRoleUseCase(
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        clock,
        uow,
    )


def get_remove_supervisor_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    category_supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RemoveSupervisorUseCase:
    return RemoveSupervisorUseCase(authorization_service, category_supervisor_repo, clock, uow)


def get_request_revision_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RequestRevisionUseCase:
    return RequestRevisionUseCase(
        authorization_service,
        project_repo,
        revision_repo,
        delivery_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_review_delivery_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    project_repo: IProjectRepository = Depends(get_project_repository),
    category_supervisor_repo: ICategorySupervisorRepository = Depends(get_category_supervisor_repository),
    review_repo: ISupervisorReviewRepository = Depends(get_supervisor_review_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    notifier: IRealtimeNotifier = Depends(get_realtime_notifier),
) -> ReviewDeliveryUseCase:
    return ReviewDeliveryUseCase(
        authorization_service,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        notifier,
    )


def get_revoke_permission_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    role_repo: IRoleRepository = Depends(get_role_repository),
    permission_repo: IPermissionRepository = Depends(get_permission_repository),
    role_permission_repo: IRolePermissionRepository = Depends(get_role_permission_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> RevokePermissionUseCase:
    return RevokePermissionUseCase(
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        uow,
    )


def get_send_message_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    message_repo: ITicketMessageRepository = Depends(get_ticket_message_repository),
    file_storage: IFileStorageService = Depends(get_file_storage_service),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> SendMessageUseCase:
    return SendMessageUseCase(
        ticket_repo,
        message_repo,
        file_storage,
        id_generator,
        clock,
        uow,
    )


def get_set_current_resume_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
) -> SetCurrentResumeUseCase:
    return SetCurrentResumeUseCase(authorization_service, profile_repo, resume_repo)


def get_soft_delete_freelancer_profile_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    clock: IClock = Depends(get_clock),
) -> SoftDeleteFreelancerProfileUseCase:
    return SoftDeleteFreelancerProfileUseCase(authorization_service, profile_repo, clock)


def get_start_project_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> StartProjectUseCase:
    return StartProjectUseCase(
        authorization_service,
        project_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
    )


def get_submit_delivery_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    review_repo: ISupervisorReviewRepository = Depends(get_supervisor_review_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    file_storage: IFileStorageService = Depends(get_file_storage_service),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    notifier: IRealtimeNotifier = Depends(get_realtime_notifier),
) -> SubmitDeliveryUseCase:
    return SubmitDeliveryUseCase(
        project_repo,
        application_repo,
        delivery_repo,
        status_history_repo,
        profile_repo,
        review_repo,
        revision_repo,
        file_storage,
        id_generator,
        clock,
        uow,
        notifier,
    )


def get_submit_freelancer_approval_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> SubmitFreelancerApprovalUseCase:
    return SubmitFreelancerApprovalUseCase(profile_repo, uow)


def get_submit_rating_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    customer_review_repo: ICustomerReviewRepository = Depends(get_customer_review_repository),
    rating_repo: IRatingRepository = Depends(get_rating_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> SubmitRatingUseCase:
    return SubmitRatingUseCase(
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
    )


def get_submit_review_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    customer_review_repo: ICustomerReviewRepository = Depends(get_customer_review_repository),
    delivery_repo: IProjectDeliveryRepository = Depends(get_project_delivery_repository),
    revision_repo: IProjectRevisionRequestRepository = Depends(get_project_revision_request_repository),
    status_history_repo: IProjectStatusHistoryRepository = Depends(get_project_status_history_repository),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> SubmitReviewUseCase:
    return SubmitReviewUseCase(
        authorization_service,
        project_repo,
        customer_review_repo,
        delivery_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        application_repo,
        profile_repo,
    )


def get_update_category_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    category_repo: ICategoryRepository = Depends(get_category_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(authorization_service, category_repo, uow)


def get_update_customer_review_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    customer_review_repo: ICustomerReviewRepository = Depends(get_customer_review_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateCustomerReviewUseCase:
    return UpdateCustomerReviewUseCase(
        project_repo,
        customer_review_repo,
        authorization_service,
        uow,
    )


def get_update_field_option_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateFieldOptionUseCase:
    return UpdateFieldOptionUseCase(authorization_service, template_repo, uow)


def get_update_field_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
) -> UpdateFieldUseCase:
    return UpdateFieldUseCase(authorization_service, template_repo)


def get_update_form_template_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    template_repo: IFormTemplateRepository = Depends(get_form_template_repository),
) -> UpdateFormTemplateUseCase:
    return UpdateFormTemplateUseCase(authorization_service, template_repo)


def get_update_freelancer_profile_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
) -> UpdateFreelancerProfileUseCase:
    return UpdateFreelancerProfileUseCase(profile_repo)


def get_update_portfolio_item_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    portfolio_item_repo: IPortfolioItemRepository = Depends(get_portfolio_item_repository),
    file_storage: IFileStorageService = Depends(get_file_storage_service),
) -> UpdatePortfolioItemUseCase:
    return UpdatePortfolioItemUseCase(profile_repo, portfolio_item_repo, file_storage)


def get_update_rating_use_case(
    project_repo: IProjectRepository = Depends(get_project_repository),
    rating_repo: IRatingRepository = Depends(get_rating_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateRatingUseCase:
    return UpdateRatingUseCase(project_repo, rating_repo, authorization_service, uow)


def get_update_resume_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
) -> UpdateResumeUseCase:
    return UpdateResumeUseCase(profile_repo, resume_repo)


def get_update_ticket_message_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    message_repo: ITicketMessageRepository = Depends(get_ticket_message_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateTicketMessageUseCase:
    return UpdateTicketMessageUseCase(
        ticket_repo,
        message_repo,
        authorization_service,
        clock,
        uow,
    )


def get_update_ticket_use_case(
    ticket_repo: ITicketRepository = Depends(get_ticket_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UpdateTicketUseCase:
    return UpdateTicketUseCase(ticket_repo, authorization_service, clock, uow)


def get_upload_file_use_case(
    file_storage: IFileStorageService = Depends(get_file_storage_service),
    clock: IClock = Depends(get_clock),
) -> UploadFileUseCase:
    return UploadFileUseCase(file_storage, clock)


def get_upload_resume_use_case(
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    resume_repo: IResumeRepository = Depends(get_resume_repository),
    file_storage: IFileStorageService = Depends(get_file_storage_service),
    id_generator: IIdGenerator = Depends(get_id_generator),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UploadResumeUseCase:
    return UploadResumeUseCase(profile_repo, resume_repo, file_storage, id_generator, clock, uow)


def get_view_applications_use_case(
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
) -> ViewApplicationsUseCase:
    return ViewApplicationsUseCase(authorization_service, project_repo, application_repo)


def get_withdraw_application_use_case(
    application_repo: IProjectApplicationRepository = Depends(get_project_application_repository),
    profile_repo: IFreelancerProfileRepository = Depends(get_freelancer_profile_repository),
    clock: IClock = Depends(get_clock),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> WithdrawApplicationUseCase:
    return WithdrawApplicationUseCase(application_repo, profile_repo, clock, uow)
