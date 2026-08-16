"""Static RBAC seed data (roles, permissions, role-permission mapping).

This data is the single source of truth for what the seeded system starts with.
Every ``PERMISSION_*`` constant used across ``application/`` use cases must appear
here so that the real ``IAuthorizationService`` (which resolves permissions through
the ``user_roles -> role_permissions -> permissions`` join) can ever return True.
"""

ROLES = [
    {"role_key": "admin", "name": "Administrator", "is_system": True},
    {"role_key": "customer", "name": "Customer", "is_system": True},
    {"role_key": "freelancer", "name": "Freelancer", "is_system": True},
    {"role_key": "supervisor", "name": "Supervisor", "is_system": True},
]

_PERMISSIONS = [
    # IAM
    ("user.create", "user", "create"),
    ("user.read", "user", "read"),
    ("user.update_any", "user", "update_any"),
    ("user.delete", "user", "delete"),
    ("user.activate", "user", "activate"),
    ("user.block", "user", "block"),
    ("user.assign_role", "user", "assign_role"),
    ("user.remove_role", "user", "remove_role"),
    ("user.grant_permission", "user", "grant_permission"),
    ("user.revoke_permission", "user", "revoke_permission"),
    # Category
    ("category.manage", "category", "manage"),
    ("category.assign_supervisor", "category", "assign_supervisor"),
    ("category.remove_supervisor", "category", "remove_supervisor"),
    # Freelancer
    ("freelancer.create_own", "freelancer", "create_own"),
    ("freelancer.create_on_behalf", "freelancer", "create_on_behalf"),
    ("freelancer.approve", "freelancer", "approve"),
    ("freelancer.assign_level", "freelancer", "assign_level"),
    # Form
    ("form.manage", "form", "manage"),
    # Project
    ("project.create_own", "project", "create_own"),
    ("project.create_on_behalf", "project", "create_on_behalf"),
    ("project.apply", "project", "apply"),
    ("project.apply_on_behalf", "project", "apply_on_behalf"),
    ("project.manage_own", "project", "manage_own"),
    ("project.manage_any", "project", "manage_any"),
    # Review
    ("review.decide_own", "review", "decide_own"),
    ("review.decide_any", "review", "decide_any"),
    # Feedback
    ("feedback.manage_own", "feedback", "manage_own"),
    ("feedback.manage_any", "feedback", "manage_any"),
    # Ticketing
    ("ticket.create_on_behalf", "ticket", "create_on_behalf"),
    ("ticket.assign", "ticket", "assign"),
    ("ticket.read_own", "ticket", "read_own"),
    ("ticket.read_any", "ticket", "read_any"),
    ("ticket.close_own", "ticket", "close_own"),
    ("ticket.close_any", "ticket", "close_any"),
    # Reporting
    ("reporting.read", "reporting", "read"),
    # File
    ("file.upload", "file", "upload"),
    ("file.read_any", "file", "read_any"),
]

PERMISSIONS = [
    {
        "permission_key": key,
        "module": module,
        "action": action,
        "is_system": True,
    }
    for key, module, action in _PERMISSIONS
]

ADMIN_PERMISSION_KEYS = frozenset(p["permission_key"] for p in PERMISSIONS)

ROLE_PERMISSIONS = {
    "customer": [
        "project.create_own",
        "project.manage_own",
        "feedback.manage_own",
        "ticket.read_own",
        "ticket.close_own",
    ],
    "freelancer": [
        "freelancer.create_own",
        "project.apply",
        "project.manage_own",
        "feedback.manage_own",
        "ticket.read_own",
        "ticket.close_own",
    ],
    "supervisor": [
        "review.decide_own",
        "ticket.read_any",
        "ticket.close_any",
    ],
    "admin": ["*"],
}
