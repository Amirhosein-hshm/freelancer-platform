# Project Workflow Remediation

The project detail, delivery, and review reads are stakeholder-scoped. A customer, the
selected freelancer, and the assigned supervisor may read the project workflow; admins
use the corresponding `*_any` permission. Applicants may read the application they own.

`GetProjectDetailsQuery` now carries the authenticated actor and rejects unrelated users.
Delivery listing accepts the customer, admin, or selected freelancer. Supervisor pending
review and assigned-project queries require `review.decide_own`.

When a selected freelancer submits a replacement delivery from `REVISION_REQUESTED`, the
project transitions back through `DELIVERY_SUBMITTED`, the open revision request is closed
with the freelancer as resolver, and the normal supervisor/customer review path resumes.

The canonical state path is:

```text
DRAFT -> PUBLISHED -> COLLECTING_APPLICATIONS -> ASSIGNED -> IN_PROGRESS
-> DELIVERY_SUBMITTED -> UNDER_SUPERVISOR_REVIEW -> AWAITING_CUSTOMER_REVIEW -> COMPLETED
```

Both supervisor and customer rejection return the project to `REVISION_REQUESTED`, after
which a replacement delivery re-enters the delivery review path. Duplicate route cleanup
and notification event wiring remain tracked as follow-up presentation/infrastructure work.
