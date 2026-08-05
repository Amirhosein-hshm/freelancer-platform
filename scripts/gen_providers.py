"""Generate presentation/core/providers.py from application use cases."""
import importlib
import inspect
import pkgutil

import app.application as app_app
from app.application.shared.use_case import UseCase

PARAM_TO_STUB = {
    "authorization_service": "get_authorization_service",
    "user_repo": "get_user_repository",
    "role_repo": "get_role_repository",
    "permission_repo": "get_permission_repository",
    "user_role_repo": "get_user_role_repository",
    "role_permission_repo": "get_role_permission_repository",
    "refresh_token_repo": "get_refresh_token_repository",
    "profile_repo": "get_freelancer_profile_repository",
    "level_repo": "get_freelancer_level_repository",
    "level_history_repo": "get_freelancer_level_history_repository",
    "resume_repo": "get_resume_repository",
    "portfolio_item_repo": "get_portfolio_item_repository",
    "category_repo": "get_category_repository",
    "category_supervisor_repo": "get_category_supervisor_repository",
    "template_repo": "get_form_template_repository",
    "form_template_repo": "get_form_template_repository",
    "project_repo": "get_project_repository",
    "application_repo": "get_project_application_repository",
    "delivery_repo": "get_project_delivery_repository",
    "revision_repo": "get_project_revision_request_repository",
    "status_history_repo": "get_project_status_history_repository",
    "review_repo": "get_supervisor_review_repository",
    "customer_review_repo": "get_customer_review_repository",
    "rating_repo": "get_rating_repository",
    "ticket_repo": "get_ticket_repository",
    "message_repo": "get_ticket_message_repository",
    "participant_repo": "get_ticket_participant_repository",
    "reporting_read_repo": "get_reporting_read_repository",
    "password_hasher": "get_password_hasher",
    "token_service": "get_token_service",
    "id_generator": "get_id_generator",
    "clock": "get_clock",
    "uow": "get_unit_of_work",
    "notification_service": "get_notification_service",
    "file_storage": "get_file_storage_service",
    "project_code_generator": "get_project_code_generator",
    "ticket_code_generator": "get_ticket_code_generator",
}

# stub getter -> interface type import path
INTERFACE_TYPE = {
    "authorization_service": "app.application.shared.authorization:IAuthorizationService",
    "user_repo": "app.domain.iam.repositories:IUserRepository",
    "role_repo": "app.domain.iam.repositories:IRoleRepository",
    "permission_repo": "app.domain.iam.repositories:IPermissionRepository",
    "user_role_repo": "app.domain.iam.repositories:IUserRoleRepository",
    "role_permission_repo": "app.domain.iam.repositories:IRolePermissionRepository",
    "refresh_token_repo": "app.domain.iam.repositories:IRefreshTokenRepository",
    "profile_repo": "app.domain.freelancer.repositories:IFreelancerProfileRepository",
    "level_repo": "app.domain.freelancer.repositories:IFreelancerLevelRepository",
    "level_history_repo": "app.domain.freelancer.repositories:IFreelancerLevelHistoryRepository",
    "resume_repo": "app.domain.freelancer.repositories:IResumeRepository",
    "portfolio_item_repo": "app.domain.freelancer.repositories:IPortfolioItemRepository",
    "category_repo": "app.domain.category.repositories:ICategoryRepository",
    "category_supervisor_repo": "app.domain.category.repositories:ICategorySupervisorRepository",
    "template_repo": "app.domain.form.repositories:IFormTemplateRepository",
    "form_template_repo": "app.domain.form.repositories:IFormTemplateRepository",
    "project_repo": "app.domain.project.repositories:IProjectRepository",
    "application_repo": "app.domain.project.repositories:IProjectApplicationRepository",
    "delivery_repo": "app.domain.project.repositories:IProjectDeliveryRepository",
    "revision_repo": "app.domain.project.repositories:IProjectRevisionRequestRepository",
    "status_history_repo": "app.domain.project.repositories:IProjectStatusHistoryRepository",
    "review_repo": "app.domain.review.repositories:ISupervisorReviewRepository",
    "customer_review_repo": "app.domain.feedback.repositories:ICustomerReviewRepository",
    "rating_repo": "app.domain.feedback.repositories:IRatingRepository",
    "ticket_repo": "app.domain.ticketing.repositories:ITicketRepository",
    "message_repo": "app.domain.ticketing.repositories:ITicketMessageRepository",
    "participant_repo": "app.domain.ticketing.repositories:ITicketParticipantRepository",
    "reporting_read_repo": "app.domain.reporting.repositories:IReportingReadRepository",
    "password_hasher": "app.application.shared.ports:IPasswordHasher",
    "token_service": "app.application.shared.ports:ITokenService",
    "id_generator": "app.application.shared.ports:IIdGenerator",
    "clock": "app.application.shared.ports:IClock",
    "uow": "app.application.shared.ports:IUnitOfWork",
    "notification_service": "app.application.shared.ports:INotificationService",
    "file_storage": "app.application.shared.ports:IFileStorageService",
    "project_code_generator": "app.application.shared.ports:IProjectCodeGenerator",
    "ticket_code_generator": "app.application.shared.ports:ITicketCodeGenerator",
}

use_cases = {}
for mod in pkgutil.walk_packages(app_app.__path__, app_app.__name__ + "."):
    try:
        m = importlib.import_module(mod.name)
    except Exception:
        continue
    for _name, obj in vars(m).items():
        if inspect.isclass(obj) and issubclass(obj, UseCase) and obj is not UseCase:
            annotations = obj.__init__.__annotations__
            sig = inspect.signature(obj.__init__)
            params = [
                (p, annotations.get(p, "Any")) for p in sig.parameters if p not in ("self",)
            ]
            use_cases[obj.__name__] = (mod.name, params)

# helper to snake_case a class name
def snake(name):
    out = []
    for ch in name:
        if ch.isupper():
            out.append("_" + ch.lower())
        else:
            out.append(ch)
    return "".join(out).lstrip("_")

lines = []
lines.append('# ruff: noqa: B008  (Depends() in defaults is the FastAPI DI idiom, not an "in-band arg")')
lines.append('"""Provider stubs for the Presentation layer.')
lines.append("")
lines.append("Every signature here is the contract between ``presentation`` and the")
lines.append("``bootstrap`` Composition Root. The stubs raise ``NotImplementedError`` by")
lines.append("default; ``bootstrap/container.py`` overrides each one with a real")
lines.append("infrastructure implementation via ``app.dependency_overrides``.")
lines.append("")
lines.append("This file must never import from ``app.infrastructure``.")
lines.append('"""')
lines.append("")
lines.append("from typing import Any")
lines.append("")
lines.append("from fastapi import Depends")
lines.append("")

# imports
imports = {}
for _stub_name, iface in INTERFACE_TYPE.items():
    mod, cls = iface.split(":")
    imports.setdefault(mod, set()).add(cls)
use_case_imports = {}
for uc_name, (_mod, _params) in use_cases.items():
    use_case_imports.setdefault(_mod, set()).add(uc_name)

for mod in sorted(set(imports) | set(use_case_imports)):
    names = sorted(imports.get(mod, set()) | use_case_imports.get(mod, set()))
    lines.append(f"from {mod} import {', '.join(names)}")
lines.append("")

# port / repo stubs
stub_to_interface = {}
for param_key, iface in INTERFACE_TYPE.items():
    stub_to_interface[PARAM_TO_STUB[param_key]] = iface

for stub_name in sorted(stub_to_interface):
    mod, cls = stub_to_interface[stub_name].split(":")
    lines.append(f"def {stub_name}() -> {cls}:")
    lines.append('    raise NotImplementedError("must be overridden by bootstrap.container")')
    lines.append("")

lines.append("")
# use case providers
for uc_name in sorted(use_cases):
    mod, params = use_cases[uc_name]
    stub_name = f"get_{snake(uc_name.removesuffix('UseCase'))}_use_case"
    lines.append(f"def {stub_name}(")
    for i, (pname, _) in enumerate(params):
        iface_mod, iface_cls = INTERFACE_TYPE[pname].split(":")
        getter = PARAM_TO_STUB[pname]
        comma = "," if i < len(params) - 1 else ","
        lines.append(f"    {pname}: {iface_cls} = Depends({getter}){comma}")
    lines.append(f") -> {uc_name}:")
    argnames = ", ".join(p[0] for p in params)
    if len(f"    return {uc_name}({argnames})") > 100:
        lines.append(f"    return {uc_name}(")
        for p in params:
            lines.append(f"        {p[0]},")
        lines.append("    )")
    else:
        lines.append(f"    return {uc_name}({argnames})")
    lines.append("")

with open("src/app/presentation/core/providers.py", "w") as f:
    f.write("\n".join(lines))
print(f"wrote providers.py with {len(use_cases)} use cases")
