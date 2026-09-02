# Frontend Build Guide

This document is generated from the live OpenAPI contract captured from `http://127.0.0.1:8000/openapi.json`. The captured contract contains **90 paths, 123 HTTP operations, and 265 component schemas**. Paths, fields, requiredness, nullability, formats, and enum values below come from that contract.

## 1. Role model overview

| Role | How obtained | Frontend purpose |
|---|---|---|
| `customer` | Selected during public registration or assigned by an admin | Create and manage projects, select freelancers, review deliveries, submit final reviews and ratings, and communicate through tickets. |
| `freelancer` | Selected during public registration or assigned by an admin | Complete profile onboarding, manage resume/portfolio, browse eligible projects, apply, deliver work, handle revisions, and view ratings. |
| `supervisor` | Admin-provisioned account and role assignment only | Review deliveries for supervised categories, inspect supervised projects, and communicate with eligible stakeholders. |
| `admin` | Seeded bootstrap account or admin-created account with the existing admin role | Manage users/RBAC links, categories, templates, freelancer approvals and levels, on-behalf actions, reports, and all operational oversight. |

Public registration accepts only `customer` and `freelancer`. Treat `roles` and `permissions` from `/api/v1/auth/me` as authoritative for navigation and action visibility.

## 2. Authentication and session

### Session endpoints
- **POST `/api/v1/auth/change-password`** (`change_password`): Change Password. `application/json`: `ChangePasswordRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/forgot-password`** (`forgot_password`): Forgot Password. `application/json`: `ForgotPasswordRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/login`** (`login_user`): Login User. `application/json`: `LoginRequest`. Required. Responses: `200` application/json `SuccessEnvelope_LoginResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/logout`** (`logout`): Logout. `application/json`: `LogoutRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/auth/me`** (`get_me`): Get Me. No request body. Responses: `200` application/json `SuccessEnvelope_UserMeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/refresh`** (`refresh_token`): Refresh Token. `application/json`: `RefreshRequest`. Required. Responses: `200` application/json `SuccessEnvelope_RefreshResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/register`** (`register_user`): Register User. `application/json`: `RegisterRequest`. Required. Responses: `201` application/json `SuccessEnvelope_RegisterResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

### Client token mechanics

1. Store the access token in memory. Store the refresh token only in the application session store chosen by the frontend security model; never use `refresh_token_jti` as the refresh or logout credential.
2. Send `Authorization: Bearer <access_token>` on authenticated operations.
3. On the first authenticated 401, pause subsequent failed requests behind one shared refresh promise. Call `POST /api/v1/auth/refresh` once with `{ "refresh_token": "..." }`.
4. Replace both stored tokens atomically from the refresh response, then replay queued requests with the new access token. A rotated refresh token invalidates the prior token immediately.
5. If refresh fails, clear session state and route to login. Do not start multiple refresh calls concurrently.
6. Logout calls `POST /api/v1/auth/logout` with the current raw refresh token, then clears local state regardless of the network result.
7. After login/refresh, call `GET /api/v1/auth/me`. For freelancers, route to onboarding when `freelancer_onboarding_needed` is true; otherwise retain `freelancer_profile_id`, `freelancer_approval_status`, and `freelancer_level` in session state.

## 3. Per-role page inventory

### Customer pages

#### Category browser

Purpose: Provides the category browser workflow for the applicable user.

- **GET `/api/v1/categories`** (`get_categories`): Get Categories. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_CategoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}`** (`get_category`): Get Category. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/projects`** (`get_category_projects`): Get Category Projects. Parameters: `category_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/supervisors`** (`list_category_supervisors`): List Category Supervisors. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListCategorySupervisorsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Customer application review

Purpose: Provides the customer application review workflow for the applicable user.

- **GET `/api/v1/projects/{project_id}/applications`** (`view_applications`): View Applications. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ApplicationResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/applications/{application_id}/accept`** (`accept_freelancer`): Accept Freelancer. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_AcceptFreelancerResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/applications/{application_id}/reject`** (`reject_freelancer_application`): Reject Freelancer Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: `application/json`: `app__presentation__api__v1__project__schemas__RejectFreelancerRequest`. Required. Responses: `200` application/json `app__presentation__core__envelope__SuccessEnvelope_RejectFreelancerResponse___2`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Customer final review and rating

Purpose: Provides the customer final review and rating workflow for the applicable user.

- **GET `/api/v1/feedback/projects/{project_id}/rating`** (`get_project_rating`): Get Project Rating. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRatingResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/feedback/projects/{project_id}/reviews`** (`list_customer_reviews`): List Customer Reviews. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CustomerReviewsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/feedback/ratings`** (`submit_rating`): Submit Rating. Parameters: none. Request: `application/json`: `SubmitRatingRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SubmitRatingResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/feedback/ratings/{rating_id}`** (`delete_rating`): Delete Rating. Parameters: `rating_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/feedback/ratings/{rating_id}`** (`update_rating`): Update Rating. Parameters: `rating_id` (path, required). Request: `application/json`: `UpdateRatingRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/feedback/reviews`** (`submit_review`): Submit Review. Parameters: none. Request: `application/json`: `SubmitReviewRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SubmitReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/feedback/reviews/{review_id}`** (`delete_customer_review`): Delete Customer Review. Parameters: `review_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/feedback/reviews/{review_id}`** (`get_customer_review`): Get Customer Review. Parameters: `review_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CustomerReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/feedback/reviews/{review_id}`** (`update_customer_review`): Update Customer Review. Parameters: `review_id` (path, required). Request: `application/json`: `UpdateCustomerReviewRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Customer project editor and lifecycle

Purpose: Provides the customer project editor and lifecycle workflow for the applicable user.

- **POST `/api/v1/projects`** (`create_project`): Create Project. Parameters: none. Request: `application/json`: `CreateProjectRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/projects/{project_id}`** (`delete_project`): Delete Project. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeleteProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/projects/{project_id}`** (`update_project`): Update Project. Parameters: `project_id` (path, required). Request: `application/json`: `UpdateProjectRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdateProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/cancel`** (`cancel_project`): Cancel Project. Parameters: `project_id` (path, required). Request: `application/json`: `CancelProjectRequest`. Required. Responses: `200` application/json `SuccessEnvelope_CancelProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/publish`** (`publish_project`): Publish Project. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_PublishProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/start`** (`start_project`): Start Project. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_StartProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Form-template browser and renderer

Purpose: Provides the form-template browser and renderer workflow for the applicable user.

- **GET `/api/v1/form-templates`** (`list_form_templates`): List Form Templates. Parameters: `category_id` (query), `status` (query), `search` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListFormTemplatesResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/form-templates/{template_id}`** (`get_form_template`): Get Form Template. Parameters: `template_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_FormTemplateResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/form-templates/{template_id}/versions`** (`list_form_template_versions`): List Form Template Versions. Parameters: `template_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListFormTemplateVersionsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### New ticket recipient picker

Purpose: Provides the new ticket recipient picker workflow for the applicable user.

- **GET `/api/v1/users/related`** (`list_related_users`): List Related Users. Parameters: `search` (query), `role` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_RelatedUserResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Project detail and activity

Purpose: Provides the project detail and activity workflow for the applicable user.

- **GET `/api/v1/deliveries/{delivery_id}`** (`get_project_delivery`): Get Project Delivery. Parameters: `delivery_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeliveryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects`** (`list_visible_projects`): List Visible Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/my`** (`get_my_projects`): Get My Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}`** (`get_project_details`): Get Project Details. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectDetailsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/applications/{application_id}`** (`get_project_application`): Get Project Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ApplicationResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/deliveries`** (`list_project_deliveries`): List Project Deliveries. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_DeliveryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/revisions`** (`list_project_revision_requests`): List Project Revision Requests. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectRevisionRequestResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/status-history`** (`list_project_status_history`): List Project Status History. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectStatusHistoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Revision request detail

Purpose: Provides the revision request detail workflow for the applicable user.

- **GET `/api/v1/revisions/{revision_id}`** (`get_project_revision_request`): Get Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/revisions/{revision_id}/close`** (`close_project_revision_request`): Close Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket inbox

Purpose: Provides the ticket inbox workflow for the applicable user.

- **GET `/api/v1/tickets`** (`get_user_tickets`): Get User Tickets. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket thread and composer

Purpose: Provides the ticket thread and composer workflow for the applicable user.

- **POST `/api/v1/tickets`** (`create_ticket`): Create Ticket. Parameters: none. Request: `application/json`: `CreateTicketRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}`** (`get_ticket`): Get Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}`** (`update_ticket`): Update Ticket. Parameters: `ticket_id` (path, required). Request: `application/json`: `UpdateTicketRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/close`** (`close_ticket`): Close Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CloseTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}/messages`** (`get_ticket_messages`): Get Ticket Messages. Parameters: `ticket_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketMessageResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/messages`** (`send_message`): Send Message. Parameters: `ticket_id` (path, required). Request: `application/json`: `SendMessageRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SendMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`delete_ticket_message`): Delete Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`update_ticket_message`): Update Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: `application/json`: `UpdateTicketMessageRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

### Freelancer pages

#### Category browser

Purpose: Provides the category browser workflow for the applicable user.

- **GET `/api/v1/categories`** (`get_categories`): Get Categories. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_CategoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}`** (`get_category`): Get Category. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/projects`** (`get_category_projects`): Get Category Projects. Parameters: `category_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/supervisors`** (`list_category_supervisors`): List Category Supervisors. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListCategorySupervisorsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Freelancer profile and onboarding

Purpose: Provides the freelancer profile and onboarding workflow for the applicable user.

- **POST `/api/v1/freelancers`** (`create_freelancer_profile`): Create Freelancer Profile. Parameters: none. Request: `application/json`: `CreateFreelancerProfileRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateFreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/freelancers/{profile_id}`** (`get_freelancer_profile`): Get Freelancer Profile. Parameters: `profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_FreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/freelancers/{profile_id}`** (`update_freelancer_profile`): Update Freelancer Profile. Parameters: `profile_id` (path, required). Request: `application/json`: `UpdateFreelancerProfileRequest`. Required. Responses: `200` application/json `SuccessEnvelope_FreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/submit-approval`** (`submit_freelancer_approval`): Submit Freelancer Approval. Parameters: `profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_SubmitFreelancerApprovalResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Freelancer project marketplace and workbench

Purpose: Provides the freelancer project marketplace and workbench workflow for the applicable user.

- **GET `/api/v1/projects/available`** (`get_available_projects`): Get Available Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/applications`** (`apply_for_project`): Apply For Project. Parameters: `project_id` (path, required). Request: `application/json`: `ApplyForProjectRequest`. Required. Responses: `201` application/json `SuccessEnvelope_ApplyForProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/applications/{application_id}/withdraw`** (`withdraw_application`): Withdraw Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_WithdrawApplicationResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/deliveries`** (`submit_delivery`): Submit Delivery. Parameters: `project_id` (path, required). Request: `application/json`: `SubmitDeliveryRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SubmitDeliveryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### My ratings

Purpose: Provides the my ratings workflow for the applicable user.

- **GET `/api/v1/feedback/freelancers/{freelancer_profile_id}/ratings`** (`get_freelancer_ratings`): Get Freelancer Ratings. Parameters: `freelancer_profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_FreelancerRatingsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### New ticket recipient picker

Purpose: Provides the new ticket recipient picker workflow for the applicable user.

- **GET `/api/v1/users/related`** (`list_related_users`): List Related Users. Parameters: `search` (query), `role` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_RelatedUserResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Portfolio manager

Purpose: Provides the portfolio manager workflow for the applicable user.

- **GET `/api/v1/freelancers/{profile_id}/portfolio`** (`list_portfolio_items`): List Portfolio Items. Parameters: `profile_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_PortfolioItemResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/portfolio`** (`add_portfolio_item`): Add Portfolio Item. Parameters: `profile_id` (path, required). Request: `application/json`: `AddPortfolioItemRequest`. Required. Responses: `201` application/json `SuccessEnvelope_AddPortfolioItemResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/freelancers/{profile_id}/portfolio/{item_id}`** (`delete_portfolio_item`): Delete Portfolio Item. Parameters: `profile_id` (path, required), `item_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeletePortfolioItemResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/freelancers/{profile_id}/portfolio/{item_id}`** (`get_portfolio_item`): Get Portfolio Item. Parameters: `profile_id` (path, required), `item_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_PortfolioItemResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/freelancers/{profile_id}/portfolio/{item_id}`** (`update_portfolio_item`): Update Portfolio Item. Parameters: `profile_id` (path, required), `item_id` (path, required). Request: `application/json`: `UpdatePortfolioItemRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdatePortfolioItemResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Project detail and activity

Purpose: Provides the project detail and activity workflow for the applicable user.

- **GET `/api/v1/deliveries/{delivery_id}`** (`get_project_delivery`): Get Project Delivery. Parameters: `delivery_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeliveryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects`** (`list_visible_projects`): List Visible Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/my`** (`get_my_projects`): Get My Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}`** (`get_project_details`): Get Project Details. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectDetailsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/applications/{application_id}`** (`get_project_application`): Get Project Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ApplicationResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/deliveries`** (`list_project_deliveries`): List Project Deliveries. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_DeliveryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/revisions`** (`list_project_revision_requests`): List Project Revision Requests. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectRevisionRequestResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/status-history`** (`list_project_status_history`): List Project Status History. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectStatusHistoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Resume manager

Purpose: Provides the resume manager workflow for the applicable user.

- **GET `/api/v1/freelancers/{profile_id}/resume`** (`get_current_resume`): Get Current Resume. Parameters: `profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ResumeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/freelancers/{profile_id}/resume`** (`update_resume`): Update Resume. Parameters: `profile_id` (path, required). Request: `application/json`: `UpdateResumeRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdateResumeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/resume`** (`upload_resume`): Upload Resume. Parameters: `profile_id` (path, required). Request: `application/json`: `UploadResumeRequest`. Required. Responses: `201` application/json `SuccessEnvelope_UploadResumeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/freelancers/{profile_id}/resume/versions`** (`list_resume_versions`): List Resume Versions. Parameters: `profile_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ResumeResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/freelancers/{profile_id}/resume/versions/{resume_id}`** (`delete_resume`): Delete Resume. Parameters: `profile_id` (path, required), `resume_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ResumeChangeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/freelancers/{profile_id}/resume/versions/{resume_id}`** (`get_resume`): Get Resume. Parameters: `profile_id` (path, required), `resume_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ResumeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/resume/versions/{resume_id}/set-current`** (`set_current_resume`): Set Current Resume. Parameters: `profile_id` (path, required), `resume_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ResumeChangeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Revision request detail

Purpose: Provides the revision request detail workflow for the applicable user.

- **GET `/api/v1/revisions/{revision_id}`** (`get_project_revision_request`): Get Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/revisions/{revision_id}/close`** (`close_project_revision_request`): Close Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket inbox

Purpose: Provides the ticket inbox workflow for the applicable user.

- **GET `/api/v1/tickets`** (`get_user_tickets`): Get User Tickets. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket thread and composer

Purpose: Provides the ticket thread and composer workflow for the applicable user.

- **POST `/api/v1/tickets`** (`create_ticket`): Create Ticket. Parameters: none. Request: `application/json`: `CreateTicketRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}`** (`get_ticket`): Get Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}`** (`update_ticket`): Update Ticket. Parameters: `ticket_id` (path, required). Request: `application/json`: `UpdateTicketRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/close`** (`close_ticket`): Close Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CloseTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}/messages`** (`get_ticket_messages`): Get Ticket Messages. Parameters: `ticket_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketMessageResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/messages`** (`send_message`): Send Message. Parameters: `ticket_id` (path, required). Request: `application/json`: `SendMessageRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SendMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`delete_ticket_message`): Delete Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`update_ticket_message`): Update Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: `application/json`: `UpdateTicketMessageRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

### Supervisor pages

#### Category browser

Purpose: Provides the category browser workflow for the applicable user.

- **GET `/api/v1/categories`** (`get_categories`): Get Categories. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_CategoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}`** (`get_category`): Get Category. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/projects`** (`get_category_projects`): Get Category Projects. Parameters: `category_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/supervisors`** (`list_category_supervisors`): List Category Supervisors. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListCategorySupervisorsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### New ticket recipient picker

Purpose: Provides the new ticket recipient picker workflow for the applicable user.

- **GET `/api/v1/users/related`** (`list_related_users`): List Related Users. Parameters: `search` (query), `role` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_RelatedUserResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Project detail and activity

Purpose: Provides the project detail and activity workflow for the applicable user.

- **GET `/api/v1/deliveries/{delivery_id}`** (`get_project_delivery`): Get Project Delivery. Parameters: `delivery_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeliveryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects`** (`list_visible_projects`): List Visible Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/my`** (`get_my_projects`): Get My Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}`** (`get_project_details`): Get Project Details. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectDetailsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/applications/{application_id}`** (`get_project_application`): Get Project Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ApplicationResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/deliveries`** (`list_project_deliveries`): List Project Deliveries. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_DeliveryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/revisions`** (`list_project_revision_requests`): List Project Revision Requests. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectRevisionRequestResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/status-history`** (`list_project_status_history`): List Project Status History. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectStatusHistoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Revision request detail

Purpose: Provides the revision request detail workflow for the applicable user.

- **GET `/api/v1/revisions/{revision_id}`** (`get_project_revision_request`): Get Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/revisions/{revision_id}/close`** (`close_project_revision_request`): Close Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Supervisor review queue and decision

Purpose: Provides the supervisor review queue and decision workflow for the applicable user.

- **GET `/api/v1/deliveries/{delivery_id}/review`** (`get_supervisor_review`): Get Supervisor Review. Parameters: `delivery_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/deliveries/{delivery_id}/review`** (`review_delivery`): Review Delivery. Parameters: `delivery_id` (path, required). Request: `application/json`: `ReviewDeliveryRequest`. Required. Responses: `200` application/json `SuccessEnvelope_DeliveryReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reviews/pending`** (`get_pending_reviews`): Get Pending Reviews. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ReviewResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reviews/supervisor/projects`** (`get_supervisor_projects`): Get Supervisor Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket inbox

Purpose: Provides the ticket inbox workflow for the applicable user.

- **GET `/api/v1/tickets`** (`get_user_tickets`): Get User Tickets. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket thread and composer

Purpose: Provides the ticket thread and composer workflow for the applicable user.

- **POST `/api/v1/tickets`** (`create_ticket`): Create Ticket. Parameters: none. Request: `application/json`: `CreateTicketRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}`** (`get_ticket`): Get Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}`** (`update_ticket`): Update Ticket. Parameters: `ticket_id` (path, required). Request: `application/json`: `UpdateTicketRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/close`** (`close_ticket`): Close Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CloseTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}/messages`** (`get_ticket_messages`): Get Ticket Messages. Parameters: `ticket_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketMessageResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/messages`** (`send_message`): Send Message. Parameters: `ticket_id` (path, required). Request: `application/json`: `SendMessageRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SendMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`delete_ticket_message`): Delete Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`update_ticket_message`): Update Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: `application/json`: `UpdateTicketMessageRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

### Admin pages

#### Admin project actions

Purpose: Provides the admin project actions workflow for the applicable user.

- **POST `/api/v1/admin/projects`** (`admin_create_project`): Admin Create Project. Parameters: none. Request: `application/json`: `AdminCreateProjectRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/admin/projects/{project_id}/applications`** (`admin_apply_for_project`): Admin Apply For Project. Parameters: `project_id` (path, required). Request: `application/json`: `AdminApplyForProjectRequest`. Required. Responses: `201` application/json `SuccessEnvelope_ApplyForProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Category administration

Purpose: Provides the category administration workflow for the applicable user.

- **POST `/api/v1/categories`** (`create_category`): Create Category. Parameters: none. Request: `application/json`: `CreateCategoryRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/categories/{category_id}`** (`delete_category`): Delete Category. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeleteCategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/categories/{category_id}`** (`update_category`): Update Category. Parameters: `category_id` (path, required). Request: `application/json`: `UpdateCategoryRequest`. Required. Responses: `200` application/json `SuccessEnvelope_CategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/categories/{category_id}/supervisors`** (`assign_supervisor`): Assign Supervisor. Parameters: `category_id` (path, required). Request: `application/json`: `AssignSupervisorRequest`. Required. Responses: `200` application/json `SuccessEnvelope_AssignSupervisorResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/categories/{category_id}/supervisors/{supervisor_user_id}`** (`remove_supervisor`): Remove Supervisor. Parameters: `category_id` (path, required), `supervisor_user_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_RemoveSupervisorResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Category browser

Purpose: Provides the category browser workflow for the applicable user.

- **GET `/api/v1/categories`** (`get_categories`): Get Categories. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_CategoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}`** (`get_category`): Get Category. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CategoryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/projects`** (`get_category_projects`): Get Category Projects. Parameters: `category_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/categories/{category_id}/supervisors`** (`list_category_supervisors`): List Category Supervisors. Parameters: `category_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListCategorySupervisorsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Customer application review

Purpose: Provides the customer application review workflow for the applicable user.

- **GET `/api/v1/projects/{project_id}/applications`** (`view_applications`): View Applications. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ApplicationResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/applications/{application_id}/accept`** (`accept_freelancer`): Accept Freelancer. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_AcceptFreelancerResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/applications/{application_id}/reject`** (`reject_freelancer_application`): Reject Freelancer Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: `application/json`: `app__presentation__api__v1__project__schemas__RejectFreelancerRequest`. Required. Responses: `200` application/json `app__presentation__core__envelope__SuccessEnvelope_RejectFreelancerResponse___2`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Customer final review and rating

Purpose: Provides the customer final review and rating workflow for the applicable user.

- **GET `/api/v1/feedback/projects/{project_id}/rating`** (`get_project_rating`): Get Project Rating. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRatingResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/feedback/projects/{project_id}/reviews`** (`list_customer_reviews`): List Customer Reviews. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CustomerReviewsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/feedback/ratings`** (`submit_rating`): Submit Rating. Parameters: none. Request: `application/json`: `SubmitRatingRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SubmitRatingResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/feedback/ratings/{rating_id}`** (`delete_rating`): Delete Rating. Parameters: `rating_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/feedback/ratings/{rating_id}`** (`update_rating`): Update Rating. Parameters: `rating_id` (path, required). Request: `application/json`: `UpdateRatingRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/feedback/reviews`** (`submit_review`): Submit Review. Parameters: none. Request: `application/json`: `SubmitReviewRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SubmitReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/feedback/reviews/{review_id}`** (`delete_customer_review`): Delete Customer Review. Parameters: `review_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/feedback/reviews/{review_id}`** (`get_customer_review`): Get Customer Review. Parameters: `review_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CustomerReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/feedback/reviews/{review_id}`** (`update_customer_review`): Update Customer Review. Parameters: `review_id` (path, required). Request: `application/json`: `UpdateCustomerReviewRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Customer project editor and lifecycle

Purpose: Provides the customer project editor and lifecycle workflow for the applicable user.

- **POST `/api/v1/projects`** (`create_project`): Create Project. Parameters: none. Request: `application/json`: `CreateProjectRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/projects/{project_id}`** (`delete_project`): Delete Project. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeleteProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/projects/{project_id}`** (`update_project`): Update Project. Parameters: `project_id` (path, required). Request: `application/json`: `UpdateProjectRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdateProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/cancel`** (`cancel_project`): Cancel Project. Parameters: `project_id` (path, required). Request: `application/json`: `CancelProjectRequest`. Required. Responses: `200` application/json `SuccessEnvelope_CancelProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/publish`** (`publish_project`): Publish Project. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_PublishProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/projects/{project_id}/start`** (`start_project`): Start Project. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_StartProjectResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Form-template administration

Purpose: Provides the form-template administration workflow for the applicable user.

- **POST `/api/v1/form-templates`** (`create_form_template`): Create Form Template. Parameters: none. Request: `application/json`: `CreateFormTemplateRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateFormTemplateResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/form-templates/{template_id}`** (`delete_form_template`): Delete Form Template. Parameters: `template_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeleteFormTemplateResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/form-templates/{template_id}`** (`update_form_template`): Update Form Template. Parameters: `template_id` (path, required). Request: `application/json`: `UpdateFormTemplateRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdateFormTemplateResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/form-templates/{template_id}/fields`** (`add_field`): Add Field. Parameters: `template_id` (path, required). Request: `application/json`: `AddFieldRequest`. Required. Responses: `201` application/json `SuccessEnvelope_AddFieldResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/form-templates/{template_id}/fields/{field_id}`** (`remove_field`): Remove Field. Parameters: `template_id` (path, required), `field_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_RemoveFieldResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/form-templates/{template_id}/fields/{field_id}`** (`update_field`): Update Field. Parameters: `template_id` (path, required), `field_id` (path, required). Request: `application/json`: `UpdateFieldRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdateFieldResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/form-templates/{template_id}/fields/{field_id}/options`** (`add_field_option`): Add Field Option. Parameters: `template_id` (path, required), `field_id` (path, required). Request: `application/json`: `AddFieldOptionRequest`. Required. Responses: `201` application/json `SuccessEnvelope_AddFieldOptionResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/form-templates/{template_id}/fields/{field_id}/options/{option_id}`** (`remove_field_option`): Remove Field Option. Parameters: `template_id` (path, required), `field_id` (path, required), `option_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_RemoveFieldOptionResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/form-templates/{template_id}/fields/{field_id}/options/{option_id}`** (`update_field_option`): Update Field Option. Parameters: `template_id` (path, required), `field_id` (path, required), `option_id` (path, required). Request: `application/json`: `UpdateFieldOptionRequest`. Required. Responses: `200` application/json `SuccessEnvelope_UpdateFieldOptionResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/form-templates/{template_id}/publish`** (`publish_form_template`): Publish Form Template. Parameters: `template_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_PublishFormTemplateResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Form-template browser and renderer

Purpose: Provides the form-template browser and renderer workflow for the applicable user.

- **GET `/api/v1/form-templates`** (`list_form_templates`): List Form Templates. Parameters: `category_id` (query), `status` (query), `search` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListFormTemplatesResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/form-templates/{template_id}`** (`get_form_template`): Get Form Template. Parameters: `template_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_FormTemplateResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/form-templates/{template_id}/versions`** (`list_form_template_versions`): List Form Template Versions. Parameters: `template_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListFormTemplateVersionsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Freelancer approval and levels

Purpose: Provides the freelancer approval and levels workflow for the applicable user.

- **GET `/api/v1/admin/freelancers`** (`list_freelancer_profiles_by_approval_status`): List Freelancer Profiles By Approval Status. Parameters: `status` (query, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_FreelancerProfileResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/admin/freelancers`** (`admin_create_freelancer_profile`): Admin Create Freelancer Profile. Parameters: none. Request: `application/json`: `AdminCreateFreelancerProfileRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateFreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/admin/freelancers/{profile_id}`** (`soft_delete_freelancer_profile`): Soft Delete Freelancer Profile. Parameters: `profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/approve`** (`approve_freelancer`): Approve Freelancer. Parameters: `profile_id` (path, required). Request: `application/json`: `ApproveFreelancerRequest`. Required. Responses: `200` application/json `SuccessEnvelope_ApproveFreelancerResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/level`** (`assign_freelancer_level`): Assign Freelancer Level. Parameters: `profile_id` (path, required). Request: `application/json`: `AssignFreelancerLevelRequest`. Required. Responses: `200` application/json `SuccessEnvelope_AssignFreelancerLevelResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/freelancers/{profile_id}/level-history`** (`list_freelancer_level_history`): List Freelancer Level History. Parameters: `profile_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_FreelancerLevelHistoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/reject`** (`reject_freelancer`): Reject Freelancer. Parameters: `profile_id` (path, required). Request: `application/json`: `app__presentation__api__v1__freelancer__schemas__RejectFreelancerRequest`. Required. Responses: `200` application/json `app__presentation__core__envelope__SuccessEnvelope_RejectFreelancerResponse___1`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Freelancer profile and onboarding

Purpose: Provides the freelancer profile and onboarding workflow for the applicable user.

- **POST `/api/v1/freelancers`** (`create_freelancer_profile`): Create Freelancer Profile. Parameters: none. Request: `application/json`: `CreateFreelancerProfileRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateFreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/freelancers/{profile_id}`** (`get_freelancer_profile`): Get Freelancer Profile. Parameters: `profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_FreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/freelancers/{profile_id}`** (`update_freelancer_profile`): Update Freelancer Profile. Parameters: `profile_id` (path, required). Request: `application/json`: `UpdateFreelancerProfileRequest`. Required. Responses: `200` application/json `SuccessEnvelope_FreelancerProfileResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/freelancers/{profile_id}/submit-approval`** (`submit_freelancer_approval`): Submit Freelancer Approval. Parameters: `profile_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_SubmitFreelancerApprovalResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### New ticket recipient picker

Purpose: Provides the new ticket recipient picker workflow for the applicable user.

- **GET `/api/v1/users/related`** (`list_related_users`): List Related Users. Parameters: `search` (query), `role` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_RelatedUserResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Project detail and activity

Purpose: Provides the project detail and activity workflow for the applicable user.

- **GET `/api/v1/deliveries/{delivery_id}`** (`get_project_delivery`): Get Project Delivery. Parameters: `delivery_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_DeliveryResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects`** (`list_visible_projects`): List Visible Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/my`** (`get_my_projects`): Get My Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}`** (`get_project_details`): Get Project Details. Parameters: `project_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectDetailsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/applications/{application_id}`** (`get_project_application`): Get Project Application. Parameters: `project_id` (path, required), `application_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ApplicationResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/deliveries`** (`list_project_deliveries`): List Project Deliveries. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_DeliveryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/revisions`** (`list_project_revision_requests`): List Project Revision Requests. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectRevisionRequestResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/projects/{project_id}/status-history`** (`list_project_status_history`): List Project Status History. Parameters: `project_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectStatusHistoryResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Reporting and system analytics

Purpose: Provides the reporting and system analytics workflow for the applicable user.

- **GET `/api/v1/reporting/customers`** (`get_customer_statistics`): Get Customer Statistics. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_CustomerStatisticsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reporting/dashboard`** (`get_dashboard_statistics`): Get Dashboard Statistics. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_DashboardStatisticsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reporting/freelancers`** (`get_freelancer_statistics`): Get Freelancer Statistics. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_FreelancerStatisticsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reporting/projects`** (`get_project_statistics`): Get Project Statistics. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectStatisticsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reporting/system-analytics`** (`get_system_analytics`): Get System Analytics. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_SystemAnalyticsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reporting/users`** (`get_user_statistics`): Get User Statistics. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_UserStatisticsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Revision request detail

Purpose: Provides the revision request detail workflow for the applicable user.

- **GET `/api/v1/revisions/{revision_id}`** (`get_project_revision_request`): Get Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/revisions/{revision_id}/close`** (`close_project_revision_request`): Close Project Revision Request. Parameters: `revision_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ProjectRevisionRequestResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Supervisor review queue and decision

Purpose: Provides the supervisor review queue and decision workflow for the applicable user.

- **GET `/api/v1/deliveries/{delivery_id}/review`** (`get_supervisor_review`): Get Supervisor Review. Parameters: `delivery_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/deliveries/{delivery_id}/review`** (`review_delivery`): Review Delivery. Parameters: `delivery_id` (path, required). Request: `application/json`: `ReviewDeliveryRequest`. Required. Responses: `200` application/json `SuccessEnvelope_DeliveryReviewResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reviews/pending`** (`get_pending_reviews`): Get Pending Reviews. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ReviewResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/reviews/supervisor/projects`** (`get_supervisor_projects`): Get Supervisor Projects. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_ProjectResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket inbox

Purpose: Provides the ticket inbox workflow for the applicable user.

- **GET `/api/v1/tickets`** (`get_user_tickets`): Get User Tickets. Parameters: `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### Ticket thread and composer

Purpose: Provides the ticket thread and composer workflow for the applicable user.

- **POST `/api/v1/admin/tickets`** (`admin_create_ticket`): Admin Create Ticket. Parameters: none. Request: `application/json`: `AdminCreateTicketRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets`** (`create_ticket`): Create Ticket. Parameters: none. Request: `application/json`: `CreateTicketRequest`. Required. Responses: `201` application/json `SuccessEnvelope_CreateTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}`** (`get_ticket`): Get Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}`** (`update_ticket`): Update Ticket. Parameters: `ticket_id` (path, required). Request: `application/json`: `UpdateTicketRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/close`** (`close_ticket`): Close Ticket. Parameters: `ticket_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_CloseTicketResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/tickets/{ticket_id}/messages`** (`get_ticket_messages`): Get Ticket Messages. Parameters: `ticket_id` (path, required), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_list_TicketMessageResponse__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/tickets/{ticket_id}/messages`** (`send_message`): Send Message. Parameters: `ticket_id` (path, required). Request: `application/json`: `SendMessageRequest`. Required. Responses: `201` application/json `SuccessEnvelope_SendMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`delete_ticket_message`): Delete Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_dict_str__str__`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/tickets/{ticket_id}/messages/{message_id}`** (`update_ticket_message`): Update Ticket Message. Parameters: `ticket_id` (path, required), `message_id` (path, required). Request: `application/json`: `UpdateTicketMessageRequest`. Required. Responses: `200` application/json `SuccessEnvelope_TicketMessageResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### User and access management

Purpose: Provides the user and access management workflow for the applicable user.

- **GET `/api/v1/permissions`** (`list_permissions`): List Permissions. Parameters: `module` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListPermissionsResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/roles`** (`list_roles`): List Roles. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_ListRolesResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/users`** (`admin_list_users`): Admin List Users. Parameters: `status` (query), `role` (query), `search` (query), `page` (query), `page_size` (query). Request: No request body. Responses: `200` application/json `SuccessEnvelope_AdminListUsersResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/users`** (`admin_create_user`): Admin Create User. Parameters: none. Request: `application/json`: `AdminCreateUserRequest`. Required. Responses: `201` application/json `SuccessEnvelope_AdminCreateUserResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/users/roles/{role_id}/permissions`** (`grant_permission`): Grant Permission. Parameters: `role_id` (path, required). Request: `application/json`: `GrantPermissionRequest`. Required. Responses: `200` application/json `SuccessEnvelope_GrantPermissionResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/users/roles/{role_id}/permissions/{permission_id}`** (`revoke_permission`): Revoke Permission. Parameters: `role_id` (path, required), `permission_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_RevokePermissionResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/users/{user_id}`** (`admin_delete_user`): Admin Delete User. Parameters: `user_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_AdminDeleteUserResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/users/{user_id}`** (`admin_get_user`): Admin Get User. Parameters: `user_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_AdminGetUserResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **PATCH `/api/v1/users/{user_id}`** (`admin_update_user`): Admin Update User. Parameters: `user_id` (path, required). Request: `application/json`: `AdminUpdateUserRequest`. Required. Responses: `200` application/json `SuccessEnvelope_AdminUpdateUserResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/users/{user_id}/activate`** (`activate_user`): Activate User. Parameters: `user_id` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_ActivateUserResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/users/{user_id}/block`** (`block_user`): Block User. Parameters: `user_id` (path, required). Request: `application/json`: `BlockUserRequest`. Required. Responses: `200` application/json `SuccessEnvelope_BlockUserResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/users/{user_id}/roles`** (`assign_role`): Assign Role. Parameters: `user_id` (path, required). Request: `application/json`: `AssignRoleRequest`. Required. Responses: `200` application/json `SuccessEnvelope_AssignRoleResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **DELETE `/api/v1/users/{user_id}/roles/{role_key}`** (`remove_role`): Remove Role. Parameters: `user_id` (path, required), `role_key` (path, required). Request: No request body. Responses: `200` application/json `SuccessEnvelope_RemoveRoleResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

### Shared authenticated/public pages

#### Authentication and account

Purpose: Provides the authentication and account workflow for the applicable user.

- **POST `/api/v1/auth/change-password`** (`change_password`): Change Password. Parameters: none. Request: `application/json`: `ChangePasswordRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/forgot-password`** (`forgot_password`): Forgot Password. Parameters: none. Request: `application/json`: `ForgotPasswordRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/login`** (`login_user`): Login User. Parameters: none. Request: `application/json`: `LoginRequest`. Required. Responses: `200` application/json `SuccessEnvelope_LoginResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/logout`** (`logout`): Logout. Parameters: none. Request: `application/json`: `LogoutRequest`. Required. Responses: `200` application/json `SuccessEnvelope_dict_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/auth/me`** (`get_me`): Get Me. Parameters: none. Request: No request body. Responses: `200` application/json `SuccessEnvelope_UserMeResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/refresh`** (`refresh_token`): Refresh Token. Parameters: none. Request: `application/json`: `RefreshRequest`. Required. Responses: `200` application/json `SuccessEnvelope_RefreshResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **POST `/api/v1/auth/register`** (`register_user`): Register User. Parameters: none. Request: `application/json`: `RegisterRequest`. Required. Responses: `201` application/json `SuccessEnvelope_RegisterResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

#### File upload and download

Purpose: Provides the file upload and download workflow for the applicable user.

- **POST `/api/v1/files`** (`upload_file`): Upload File. Parameters: none. Request: `multipart/form-data`: `Body_upload_file`. Required. Responses: `201` application/json `SuccessEnvelope_FileAssetResponse_`; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`
- **GET `/api/v1/files/{file_asset_id}`** (`get_file_asset`): Get File Asset. Parameters: `file_asset_id` (path, required). Request: No request body. Responses: `200` application/json none; `400` application/json `ErrorEnvelope`; `401` application/json `ErrorEnvelope`; `403` application/json `ErrorEnvelope`; `404` application/json `ErrorEnvelope`; `409` application/json `ErrorEnvelope`; `422` application/json `ErrorEnvelope`; `500` application/json `ErrorEnvelope`

### Required conditional UI rules

- Freelancer navigation: show onboarding when `freelancer_onboarding_needed`; approval submission while pending/rejected; level as read-only for freelancers; resume/portfolio after profile creation.
- Project editor actions: update/delete only while `draft`; publish while `draft`; application review while accepting applications; start after assignment; cancel while non-terminal.
- Freelancer marketplace: use `/projects/available`; never infer level eligibility locally. Disable application actions for unapproved users and surface API eligibility errors.
- Delivery flow: show submit/resubmit only to the selected freelancer in `in_progress` or revision state. A supervisor-assigned delivery enters supervisor review; otherwise customer review.
- Revision actions: the backend owns the three-round cap. Hide additional revision actions after round 3 and still handle the conflict response.
- Final feedback: review approval completes the project; review rejection opens a revision. Rating is available only after an approved final review and uses score 1–5.
- Form templates: mutate fields/options only on `draft`; published templates are read-only and are versioned rather than edited.
- Tickets: available recipients come only from `/users/related`; creator and target are the only users who may view, message, edit/delete messages, or close the ticket.

## 4. Shared and cross-role components

- **API client and envelope parser:** success responses use `success`, `message`, `data`, and nullable `meta`; errors use the documented `ErrorEnvelope` schemas in the catalog.
- **Pagination controls:** send `page` and `page_size` wherever declared. Read `meta.page`, `meta.page_size`, `meta.total_items`, and `meta.total_pages`.
- **File picker/uploader:** send multipart field `file` plus `context` to `POST /api/v1/files`, retain returned `file_asset_id`, and pass IDs to resume, portfolio, delivery, or ticket-message requests. Download through authenticated `GET /api/v1/files/{file_asset_id}`.
- **Dynamic form renderer:** render fields/options from form-template responses. Supported `FormFieldType` values are listed in the schema catalog; submit values using the exact project request schema.
- **Ticket thread:** recipient picker uses `/users/related?search=&role=`; thread uses ticket/message operations and attachment asset IDs.
- **Permission-aware actions:** permissions control visibility, but the API remains authoritative. A hidden action must still handle 403/422/409 when state changes concurrently.
- **WebSocket notifications:** `/ws/notifications` is not represented in OpenAPI, so its message contract is not specified here. Do not invent event payload types from this HTTP contract.

## 5. Endpoint-to-page cross-reference

| Method | Path | Operation ID | Page | Roles |
|---|---|---|---|---|
| GET | `/api/v1/admin/freelancers` | `list_freelancer_profiles_by_approval_status` | Freelancer approval and levels | admin |
| POST | `/api/v1/admin/freelancers` | `admin_create_freelancer_profile` | Freelancer approval and levels | admin |
| DELETE | `/api/v1/admin/freelancers/{profile_id}` | `soft_delete_freelancer_profile` | Freelancer approval and levels | admin |
| POST | `/api/v1/admin/projects` | `admin_create_project` | Admin project actions | admin |
| POST | `/api/v1/admin/projects/{project_id}/applications` | `admin_apply_for_project` | Admin project actions | admin |
| POST | `/api/v1/admin/tickets` | `admin_create_ticket` | Ticket thread and composer | admin |
| POST | `/api/v1/auth/change-password` | `change_password` | Authentication and account | shared |
| POST | `/api/v1/auth/forgot-password` | `forgot_password` | Authentication and account | shared |
| POST | `/api/v1/auth/login` | `login_user` | Authentication and account | shared |
| POST | `/api/v1/auth/logout` | `logout` | Authentication and account | shared |
| GET | `/api/v1/auth/me` | `get_me` | Authentication and account | shared |
| POST | `/api/v1/auth/refresh` | `refresh_token` | Authentication and account | shared |
| POST | `/api/v1/auth/register` | `register_user` | Authentication and account | shared |
| GET | `/api/v1/categories` | `get_categories` | Category browser | customer, freelancer, supervisor, admin |
| POST | `/api/v1/categories` | `create_category` | Category administration | admin |
| GET | `/api/v1/categories/{category_id}` | `get_category` | Category browser | customer, freelancer, supervisor, admin |
| PATCH | `/api/v1/categories/{category_id}` | `update_category` | Category administration | admin |
| DELETE | `/api/v1/categories/{category_id}` | `delete_category` | Category administration | admin |
| GET | `/api/v1/categories/{category_id}/projects` | `get_category_projects` | Category browser | customer, freelancer, supervisor, admin |
| GET | `/api/v1/categories/{category_id}/supervisors` | `list_category_supervisors` | Category browser | customer, freelancer, supervisor, admin |
| POST | `/api/v1/categories/{category_id}/supervisors` | `assign_supervisor` | Category administration | admin |
| DELETE | `/api/v1/categories/{category_id}/supervisors/{supervisor_user_id}` | `remove_supervisor` | Category administration | admin |
| GET | `/api/v1/deliveries/{delivery_id}` | `get_project_delivery` | Project detail and activity | customer, freelancer, supervisor, admin |
| GET | `/api/v1/deliveries/{delivery_id}/review` | `get_supervisor_review` | Supervisor review queue and decision | supervisor, admin |
| POST | `/api/v1/deliveries/{delivery_id}/review` | `review_delivery` | Supervisor review queue and decision | supervisor, admin |
| GET | `/api/v1/feedback/freelancers/{freelancer_profile_id}/ratings` | `get_freelancer_ratings` | My ratings | freelancer |
| GET | `/api/v1/feedback/projects/{project_id}/rating` | `get_project_rating` | Customer final review and rating | customer, admin |
| GET | `/api/v1/feedback/projects/{project_id}/reviews` | `list_customer_reviews` | Customer final review and rating | customer, admin |
| POST | `/api/v1/feedback/ratings` | `submit_rating` | Customer final review and rating | customer, admin |
| PATCH | `/api/v1/feedback/ratings/{rating_id}` | `update_rating` | Customer final review and rating | customer, admin |
| DELETE | `/api/v1/feedback/ratings/{rating_id}` | `delete_rating` | Customer final review and rating | customer, admin |
| POST | `/api/v1/feedback/reviews` | `submit_review` | Customer final review and rating | customer, admin |
| GET | `/api/v1/feedback/reviews/{review_id}` | `get_customer_review` | Customer final review and rating | customer, admin |
| PATCH | `/api/v1/feedback/reviews/{review_id}` | `update_customer_review` | Customer final review and rating | customer, admin |
| DELETE | `/api/v1/feedback/reviews/{review_id}` | `delete_customer_review` | Customer final review and rating | customer, admin |
| POST | `/api/v1/files` | `upload_file` | File upload and download | shared |
| GET | `/api/v1/files/{file_asset_id}` | `get_file_asset` | File upload and download | shared |
| GET | `/api/v1/form-templates` | `list_form_templates` | Form-template browser and renderer | customer, admin |
| POST | `/api/v1/form-templates` | `create_form_template` | Form-template administration | admin |
| GET | `/api/v1/form-templates/{template_id}` | `get_form_template` | Form-template browser and renderer | customer, admin |
| PATCH | `/api/v1/form-templates/{template_id}` | `update_form_template` | Form-template administration | admin |
| DELETE | `/api/v1/form-templates/{template_id}` | `delete_form_template` | Form-template administration | admin |
| POST | `/api/v1/form-templates/{template_id}/fields` | `add_field` | Form-template administration | admin |
| PATCH | `/api/v1/form-templates/{template_id}/fields/{field_id}` | `update_field` | Form-template administration | admin |
| DELETE | `/api/v1/form-templates/{template_id}/fields/{field_id}` | `remove_field` | Form-template administration | admin |
| POST | `/api/v1/form-templates/{template_id}/fields/{field_id}/options` | `add_field_option` | Form-template administration | admin |
| PATCH | `/api/v1/form-templates/{template_id}/fields/{field_id}/options/{option_id}` | `update_field_option` | Form-template administration | admin |
| DELETE | `/api/v1/form-templates/{template_id}/fields/{field_id}/options/{option_id}` | `remove_field_option` | Form-template administration | admin |
| POST | `/api/v1/form-templates/{template_id}/publish` | `publish_form_template` | Form-template administration | admin |
| GET | `/api/v1/form-templates/{template_id}/versions` | `list_form_template_versions` | Form-template browser and renderer | customer, admin |
| POST | `/api/v1/freelancers` | `create_freelancer_profile` | Freelancer profile and onboarding | freelancer, admin |
| GET | `/api/v1/freelancers/{profile_id}` | `get_freelancer_profile` | Freelancer profile and onboarding | freelancer, admin |
| PATCH | `/api/v1/freelancers/{profile_id}` | `update_freelancer_profile` | Freelancer profile and onboarding | freelancer, admin |
| POST | `/api/v1/freelancers/{profile_id}/approve` | `approve_freelancer` | Freelancer approval and levels | admin |
| POST | `/api/v1/freelancers/{profile_id}/level` | `assign_freelancer_level` | Freelancer approval and levels | admin |
| GET | `/api/v1/freelancers/{profile_id}/level-history` | `list_freelancer_level_history` | Freelancer approval and levels | admin |
| GET | `/api/v1/freelancers/{profile_id}/portfolio` | `list_portfolio_items` | Portfolio manager | freelancer |
| POST | `/api/v1/freelancers/{profile_id}/portfolio` | `add_portfolio_item` | Portfolio manager | freelancer |
| GET | `/api/v1/freelancers/{profile_id}/portfolio/{item_id}` | `get_portfolio_item` | Portfolio manager | freelancer |
| PATCH | `/api/v1/freelancers/{profile_id}/portfolio/{item_id}` | `update_portfolio_item` | Portfolio manager | freelancer |
| DELETE | `/api/v1/freelancers/{profile_id}/portfolio/{item_id}` | `delete_portfolio_item` | Portfolio manager | freelancer |
| POST | `/api/v1/freelancers/{profile_id}/reject` | `reject_freelancer` | Freelancer approval and levels | admin |
| GET | `/api/v1/freelancers/{profile_id}/resume` | `get_current_resume` | Resume manager | freelancer |
| POST | `/api/v1/freelancers/{profile_id}/resume` | `upload_resume` | Resume manager | freelancer |
| PATCH | `/api/v1/freelancers/{profile_id}/resume` | `update_resume` | Resume manager | freelancer |
| GET | `/api/v1/freelancers/{profile_id}/resume/versions` | `list_resume_versions` | Resume manager | freelancer |
| GET | `/api/v1/freelancers/{profile_id}/resume/versions/{resume_id}` | `get_resume` | Resume manager | freelancer |
| DELETE | `/api/v1/freelancers/{profile_id}/resume/versions/{resume_id}` | `delete_resume` | Resume manager | freelancer |
| POST | `/api/v1/freelancers/{profile_id}/resume/versions/{resume_id}/set-current` | `set_current_resume` | Resume manager | freelancer |
| POST | `/api/v1/freelancers/{profile_id}/submit-approval` | `submit_freelancer_approval` | Freelancer profile and onboarding | freelancer, admin |
| GET | `/api/v1/permissions` | `list_permissions` | User and access management | admin |
| GET | `/api/v1/projects` | `list_visible_projects` | Project detail and activity | customer, freelancer, supervisor, admin |
| POST | `/api/v1/projects` | `create_project` | Customer project editor and lifecycle | customer, admin |
| GET | `/api/v1/projects/available` | `get_available_projects` | Freelancer project marketplace and workbench | freelancer |
| GET | `/api/v1/projects/my` | `get_my_projects` | Project detail and activity | customer, freelancer, supervisor, admin |
| GET | `/api/v1/projects/{project_id}` | `get_project_details` | Project detail and activity | customer, freelancer, supervisor, admin |
| PATCH | `/api/v1/projects/{project_id}` | `update_project` | Customer project editor and lifecycle | customer, admin |
| DELETE | `/api/v1/projects/{project_id}` | `delete_project` | Customer project editor and lifecycle | customer, admin |
| GET | `/api/v1/projects/{project_id}/applications` | `view_applications` | Customer application review | customer, admin |
| POST | `/api/v1/projects/{project_id}/applications` | `apply_for_project` | Freelancer project marketplace and workbench | freelancer |
| GET | `/api/v1/projects/{project_id}/applications/{application_id}` | `get_project_application` | Project detail and activity | customer, freelancer, supervisor, admin |
| POST | `/api/v1/projects/{project_id}/applications/{application_id}/accept` | `accept_freelancer` | Customer application review | customer, admin |
| POST | `/api/v1/projects/{project_id}/applications/{application_id}/reject` | `reject_freelancer_application` | Customer application review | customer, admin |
| POST | `/api/v1/projects/{project_id}/applications/{application_id}/withdraw` | `withdraw_application` | Freelancer project marketplace and workbench | freelancer |
| POST | `/api/v1/projects/{project_id}/cancel` | `cancel_project` | Customer project editor and lifecycle | customer, admin |
| GET | `/api/v1/projects/{project_id}/deliveries` | `list_project_deliveries` | Project detail and activity | customer, freelancer, supervisor, admin |
| POST | `/api/v1/projects/{project_id}/deliveries` | `submit_delivery` | Freelancer project marketplace and workbench | freelancer |
| POST | `/api/v1/projects/{project_id}/publish` | `publish_project` | Customer project editor and lifecycle | customer, admin |
| GET | `/api/v1/projects/{project_id}/revisions` | `list_project_revision_requests` | Project detail and activity | customer, freelancer, supervisor, admin |
| POST | `/api/v1/projects/{project_id}/start` | `start_project` | Customer project editor and lifecycle | customer, admin |
| GET | `/api/v1/projects/{project_id}/status-history` | `list_project_status_history` | Project detail and activity | customer, freelancer, supervisor, admin |
| GET | `/api/v1/reporting/customers` | `get_customer_statistics` | Reporting and system analytics | admin |
| GET | `/api/v1/reporting/dashboard` | `get_dashboard_statistics` | Reporting and system analytics | admin |
| GET | `/api/v1/reporting/freelancers` | `get_freelancer_statistics` | Reporting and system analytics | admin |
| GET | `/api/v1/reporting/projects` | `get_project_statistics` | Reporting and system analytics | admin |
| GET | `/api/v1/reporting/system-analytics` | `get_system_analytics` | Reporting and system analytics | admin |
| GET | `/api/v1/reporting/users` | `get_user_statistics` | Reporting and system analytics | admin |
| GET | `/api/v1/reviews/pending` | `get_pending_reviews` | Supervisor review queue and decision | supervisor, admin |
| GET | `/api/v1/reviews/supervisor/projects` | `get_supervisor_projects` | Supervisor review queue and decision | supervisor, admin |
| GET | `/api/v1/revisions/{revision_id}` | `get_project_revision_request` | Revision request detail | customer, freelancer, supervisor, admin |
| POST | `/api/v1/revisions/{revision_id}/close` | `close_project_revision_request` | Revision request detail | customer, freelancer, supervisor, admin |
| GET | `/api/v1/roles` | `list_roles` | User and access management | admin |
| GET | `/api/v1/tickets` | `get_user_tickets` | Ticket inbox | customer, freelancer, supervisor, admin |
| POST | `/api/v1/tickets` | `create_ticket` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| GET | `/api/v1/tickets/{ticket_id}` | `get_ticket` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| PATCH | `/api/v1/tickets/{ticket_id}` | `update_ticket` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| POST | `/api/v1/tickets/{ticket_id}/close` | `close_ticket` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| GET | `/api/v1/tickets/{ticket_id}/messages` | `get_ticket_messages` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| POST | `/api/v1/tickets/{ticket_id}/messages` | `send_message` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| PATCH | `/api/v1/tickets/{ticket_id}/messages/{message_id}` | `update_ticket_message` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| DELETE | `/api/v1/tickets/{ticket_id}/messages/{message_id}` | `delete_ticket_message` | Ticket thread and composer | customer, freelancer, supervisor, admin |
| GET | `/api/v1/users` | `admin_list_users` | User and access management | admin |
| POST | `/api/v1/users` | `admin_create_user` | User and access management | admin |
| GET | `/api/v1/users/related` | `list_related_users` | New ticket recipient picker | customer, freelancer, supervisor, admin |
| POST | `/api/v1/users/roles/{role_id}/permissions` | `grant_permission` | User and access management | admin |
| DELETE | `/api/v1/users/roles/{role_id}/permissions/{permission_id}` | `revoke_permission` | User and access management | admin |
| GET | `/api/v1/users/{user_id}` | `admin_get_user` | User and access management | admin |
| PATCH | `/api/v1/users/{user_id}` | `admin_update_user` | User and access management | admin |
| DELETE | `/api/v1/users/{user_id}` | `admin_delete_user` | User and access management | admin |
| POST | `/api/v1/users/{user_id}/activate` | `activate_user` | User and access management | admin |
| POST | `/api/v1/users/{user_id}/block` | `block_user` | User and access management | admin |
| POST | `/api/v1/users/{user_id}/roles` | `assign_role` | User and access management | admin |
| DELETE | `/api/v1/users/{user_id}/roles/{role_key}` | `remove_role` | User and access management | admin |

Coverage confirmation: **123 of 123 live HTTP operations are mapped**. No OpenAPI operation is unused or marked backend-only.

## 6. Exact component schema catalog

Use this catalog with the endpoint request/response references above. A field is required only when marked **required**. `A or null` is nullable; absence from the required list means optional.

### `AcceptFreelancerResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `selected_application_id` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |

### `ActivateUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `status` | `string` | yes | - |

### `AddFieldOptionRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `option_key` | `string` | yes | minLength=1 |
| `label` | `string` | yes | minLength=1 |
| `value` | `string` | yes | minLength=1 |
| `sort_order` | `integer` | no | default=`0` |
| `is_active` | `boolean` | no | default=`True` |

### `AddFieldOptionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `option_id` | `string` | yes | - |

### `AddFieldRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `field_key` | `string` | yes | minLength=1 |
| `label` | `string` | yes | minLength=1 |
| `field_type` | `FormFieldType` | yes | - |
| `description` | `string` or `null` | no | - |
| `is_required` | `boolean` | no | default=`False` |
| `is_repeatable` | `boolean` | no | default=`False` |
| `is_unique` | `boolean` | no | default=`False` |
| `sort_order` | `integer` | no | default=`0` |
| `validation_rules` | object/map or `null` | no | - |

### `AddFieldResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `field_id` | `string` | yes | - |

### `AddPortfolioItemRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `title` | `string` | yes | - |
| `description` | `string` or `null` | no | - |
| `external_url` | `string` or `null` | no | - |
| `file_asset_id` | `string` or `null` | no | - |
| `display_order` | `integer` | no | default=`0` |
| `is_featured` | `boolean` | no | default=`False` |

### `AddPortfolioItemResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `item_id` | `string` | yes | - |

### `AdminApplyForProjectRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `target_freelancer_profile_id` | `string` | yes | - |
| `cover_letter` | `string` or `null` | no | - |
| `proposed_amount` | `number` or `string` or `null` | no | - |
| `proposed_days` | `integer` or `null` | no | - |

### `AdminCreateFreelancerProfileRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `target_user_id` | `string` | yes | - |
| `display_name` | `string` | yes | minLength=1 |
| `headline` | `string` or `null` | no | - |
| `bio` | `string` or `null` | no | - |
| `country_code` | `string` or `null` | no | - |
| `city` | `string` or `null` | no | - |
| `timezone` | `string` or `null` | no | - |

### `AdminCreateProjectRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `target_customer_user_id` | `string` | yes | - |
| `form_template_id` | `string` | yes | - |
| `title` | `string` | yes | - |
| `description` | `string` | yes | - |
| `visibility` | `ProjectVisibility` | yes | - |
| `budget_type` | `BudgetType` | yes | - |
| `currency_code` | `string` | yes | - |
| `required_level` | `FreelancerLevelEnum` or `null` | no | - |
| `fixed_budget` | `number` or `string` or `null` | no | - |
| `budget_min` | `number` or `string` or `null` | no | - |
| `budget_max` | `number` or `string` or `null` | no | - |
| `priority` | `ProjectPriority` | no | default=`normal` |
| `application_deadline` | `string` (`date-time`) or `null` | no | - |
| `form_values` | array of `FormValueInputRequest` | no | - |

### `AdminCreateTicketRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `requester_user_id` | `string` | yes | - |
| `target_user_id` | `string` | yes | - |
| `subject` | `string` | yes | minLength=1 |
| `priority` | `TicketPriority` | no | default=`normal` |

### `AdminCreateUserRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `email` | `string` | yes | - |
| `password` | `string` | yes | minLength=8 |
| `first_name` | `string` | yes | - |
| `last_name` | `string` | yes | - |

### `AdminCreateUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `status` | `string` | yes | - |
| `created_at` | `string` | yes | - |

### `AdminDeleteUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `deleted_at` | `string` | yes | - |

### `AdminGetUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `first_name` | `string` | yes | - |
| `last_name` | `string` | yes | - |
| `phone` | `string` or `null` | no | - |
| `status` | `string` | yes | - |
| `email_verified_at` | `string` or `null` | no | - |
| `phone_verified_at` | `string` or `null` | no | - |
| `last_login_at` | `string` or `null` | no | - |
| `roles` | array of `string` | yes | - |

### `AdminListUsersResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `users` | array of `AdminUserSummaryResponse` | yes | - |

### `AdminUpdateUserRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `first_name` | `string` or `null` | no | - |
| `last_name` | `string` or `null` | no | - |
| `phone` | `string` or `null` | no | - |

### `AdminUpdateUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `first_name` | `string` | yes | - |
| `last_name` | `string` | yes | - |

### `AdminUserSummaryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `first_name` | `string` | yes | - |
| `last_name` | `string` | yes | - |
| `status` | `string` | yes | - |
| `created_at` | `string` | yes | - |

### `ApplicationResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `application_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `freelancer_profile_id` | `string` | yes | - |
| `status` | `ProjectApplicationStatus` | yes | - |
| `cover_letter` | `string` or `null` | yes | - |
| `proposed_amount` | `string` or `null` | yes | - |
| `proposed_days` | `integer` or `null` | yes | - |
| `applied_at` | `string` (`date-time`) | yes | - |
| `submitted_by_user_id` | `string` or `null` | yes | - |
| `decided_at` | `string` (`date-time`) or `null` | yes | - |
| `decision_note` | `string` or `null` | yes | - |

### `ApplyForProjectRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `cover_letter` | `string` or `null` | no | - |
| `proposed_amount` | `number` or `string` or `null` | no | - |
| `proposed_days` | `integer` or `null` | no | - |

### `ApplyForProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `application_id` | `string` | yes | - |
| `status` | `ProjectApplicationStatus` | yes | - |

### `ApproveFreelancerRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `note` | `string` or `null` | no | - |

### `ApproveFreelancerResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `profile_id` | `string` | yes | - |
| `approval_status` | `string` | yes | - |
| `current_level` | `FreelancerLevelEnum` or `null` | yes | - |

### `AssignFreelancerLevelRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `new_level` | `FreelancerLevelEnum` | yes | - |
| `reason` | `string` or `null` | no | - |

### `AssignFreelancerLevelResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `profile_id` | `string` | yes | - |
| `old_level` | `FreelancerLevelEnum` or `null` | yes | - |
| `new_level` | `FreelancerLevelEnum` | yes | - |

### `AssignRoleRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `role_key` | `string` | yes | - |

### `AssignRoleResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_role_id` | `string` | yes | - |
| `user_id` | `string` | yes | - |
| `role_id` | `string` | yes | - |

### `AssignSupervisorRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `supervisor_user_id` | `string` | yes | - |

### `AssignSupervisorResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `link_id` | `string` | yes | - |
| `category_id` | `string` | yes | - |
| `supervisor_user_id` | `string` | yes | - |

### `BlockUserRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `reason` | `string` | yes | - |

### `BlockUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `status` | `string` | yes | - |

### `Body_upload_file`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `file` | `string` | yes | - |
| `context` | `FileAssetContext` | yes | - |

### `BudgetResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `budget_type` | `BudgetType` | yes | - |
| `fixed_amount` | `string` or `null` | yes | - |
| `min_amount` | `string` or `null` | yes | - |
| `max_amount` | `string` or `null` | yes | - |
| `currency_code` | `string` | yes | - |

### `BudgetType`

Enum values: `fixed`, `range`, `hourly`, `negotiable`.

### `CancelProjectRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `reason` | `string` | yes | - |

### `CancelProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |

### `CategoryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `category_id` | `string` | yes | - |
| `category_key` | `string` | yes | - |
| `name` | `string` | yes | - |
| `slug` | `string` | yes | - |
| `description` | `string` or `null` | yes | - |
| `is_active` | `boolean` | yes | - |
| `sort_order` | `integer` | yes | - |
| `parent_category_id` | `string` or `null` | yes | - |

### `CategorySupervisorResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `link_id` | `string` | yes | - |
| `category_id` | `string` | yes | - |
| `supervisor_user_id` | `string` | yes | - |
| `is_primary` | `boolean` | yes | - |
| `assigned_at` | `string` | yes | - |

### `ChangePasswordRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `old_password` | `string` | yes | - |
| `new_password` | `string` | yes | minLength=8 |

### `CloseTicketResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `ticket_id` | `string` | yes | - |
| `status` | `TicketStatus` | yes | - |

### `CreateCategoryRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `name` | `string` | yes | minLength=1 |
| `slug` | `string` | yes | minLength=1 |
| `category_key` | `string` | yes | minLength=1 |
| `description` | `string` or `null` | no | - |
| `parent_category_id` | `string` or `null` | no | - |
| `sort_order` | `integer` | no | default=`0` |

### `CreateFormTemplateRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `category_id` | `string` | yes | minLength=1 |
| `name` | `string` | yes | minLength=1 |
| `template_key` | `string` | yes | minLength=1 |

### `CreateFormTemplateResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `template_id` | `string` | yes | - |
| `version_no` | `integer` | yes | - |
| `status` | `FormTemplateStatus` | yes | - |

### `CreateFreelancerProfileRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `display_name` | `string` | yes | minLength=1 |
| `headline` | `string` or `null` | no | - |
| `bio` | `string` or `null` | no | - |
| `country_code` | `string` or `null` | no | - |
| `city` | `string` or `null` | no | - |
| `timezone` | `string` or `null` | no | - |

### `CreateFreelancerProfileResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `profile_id` | `string` | yes | - |

### `CreateProjectRequest`

``category_id`` is derived server-side from the template, so it is not accepted here.

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `form_template_id` | `string` | yes | - |
| `title` | `string` | yes | - |
| `description` | `string` | yes | - |
| `visibility` | `ProjectVisibility` | yes | - |
| `budget_type` | `BudgetType` | yes | - |
| `currency_code` | `string` | yes | - |
| `required_level` | `FreelancerLevelEnum` or `null` | no | - |
| `fixed_budget` | `number` or `string` or `null` | no | - |
| `budget_min` | `number` or `string` or `null` | no | - |
| `budget_max` | `number` or `string` or `null` | no | - |
| `priority` | `ProjectPriority` | no | default=`normal` |
| `application_deadline` | `string` (`date-time`) or `null` | no | - |
| `form_values` | array of `FormValueInputRequest` | no | - |

### `CreateProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `project_code` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |

### `CreateTicketRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `target_user_id` | `string` | yes | - |
| `subject` | `string` | yes | minLength=1 |
| `priority` | `TicketPriority` | no | default=`normal` |

### `CreateTicketResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `ticket_id` | `string` | yes | - |
| `ticket_code` | `string` | yes | - |
| `status` | `TicketStatus` | yes | - |

### `CustomerReviewResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `review_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `project_delivery_id` | `string` | yes | - |
| `customer_user_id` | `string` | yes | - |
| `decision` | `ReviewStatus` | yes | - |
| `comment` | `string` or `null` | yes | - |
| `reviewed_at` | `string` (`date-time`) | yes | - |

### `CustomerReviewsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `reviews` | array of `CustomerReviewResponse` | yes | - |

### `CustomerStatisticsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `total_customers` | `integer` | yes | - |
| `active_projects` | `integer` | yes | - |
| `completed_projects` | `integer` | yes | - |

### `DashboardStatisticsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `total_users` | `integer` | yes | - |
| `active_projects` | `integer` | yes | - |
| `total_freelancers` | `integer` | yes | - |
| `total_revenue` | `string` | yes | pattern=^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$ |

### `DeleteCategoryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `category_id` | `string` | yes | - |

### `DeleteFormTemplateResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `template_id` | `string` | yes | - |

### `DeletePortfolioItemResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `item_id` | `string` | yes | - |

### `DeleteProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `deleted_at` | `string` (`date-time`) | yes | - |

### `DeliveryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `delivery_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `version_no` | `integer` | yes | - |
| `status` | `DeliveryStatus` | yes | - |
| `delivery_note` | `string` or `null` | yes | - |
| `submitted_at` | `string` (`date-time`) | yes | - |
| `reviewed_at` | `string` (`date-time`) or `null` | yes | - |
| `reviewer_user_id` | `string` or `null` | yes | - |
| `file_asset_ids` | array of `string` | yes | - |

### `DeliveryReviewResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `delivery_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `decision` | `ReviewStatus` | yes | - |
| `project_status` | `ProjectStatus` | yes | - |

### `DeliveryStatus`

Enum values: `submitted`, `under_review`, `approved`, `rejected`, `revised`, `superseded`.

### `ErrorDetail`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `code` | `string` | yes | - |
| `message` | `string` | yes | - |
| `details` | object/map or array of none or `null` | no | - |

### `ErrorEnvelope`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`False` |
| `error` | `ErrorDetail` | yes | - |

### `FileAssetContext`

Enum values: `resume`, `portfolio`, `delivery`, `ticket_attachment`, `generic`.

### `FileAssetResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `file_asset_id` | `string` | yes | - |
| `file_name` | `string` | yes | - |
| `size_bytes` | `integer` | yes | - |
| `mime_type` | `string` | yes | - |
| `uploaded_at` | `string` (`date-time`) | yes | - |
| `context` | `FileAssetContext` | yes | - |

### `ForgotPasswordRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `email` | `string` | yes | - |

### `FormFieldOptionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `option_id` | `string` | yes | - |
| `option_key` | `string` | yes | - |
| `label` | `string` | yes | - |
| `value` | `string` | yes | - |
| `sort_order` | `integer` | yes | - |
| `is_active` | `boolean` | yes | - |

### `FormFieldResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `field_id` | `string` | yes | - |
| `field_key` | `string` | yes | - |
| `label` | `string` | yes | - |
| `description` | `string` or `null` | yes | - |
| `field_type` | `FormFieldType` | yes | - |
| `is_required` | `boolean` | yes | - |
| `is_repeatable` | `boolean` | yes | - |
| `is_unique` | `boolean` | yes | - |
| `sort_order` | `integer` | yes | - |
| `validation_rules` | object/map or `null` | yes | - |
| `is_active` | `boolean` | yes | - |
| `options` | array of `FormFieldOptionResponse` | yes | - |

### `FormFieldType`

Enum values: `text`, `textarea`, `number`, `decimal`, `boolean`, `date`, `datetime`, `email`, `phone`, `url`, `select`, `multi_select`, `file`, `json`.

### `FormTemplateResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `template_id` | `string` | yes | - |
| `category_id` | `string` | yes | - |
| `template_key` | `string` | yes | - |
| `name` | `string` | yes | - |
| `version_no` | `integer` | yes | - |
| `status` | `FormTemplateStatus` | yes | - |
| `is_active` | `boolean` | yes | - |
| `published_at` | `string` or `null` | yes | - |
| `fields` | array of `FormFieldResponse` | yes | - |

### `FormTemplateStatus`

Enum values: `draft`, `published`, `archived`.

### `FormValueInputRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `field_id` | `string` | yes | - |
| `value` | `string` | yes | - |

### `FreelancerApprovalStatus`

Enum values: `pending`, `approved`, `rejected`, `suspended`.

### `FreelancerLevelEnum`

Closed ladder of freelancer levels, in ascending order.  Eligibility is hierarchical: a freelancer may apply to any project whose ``required_level`` is at or below their own level. There is no per-level configuration table — these three values are the whole model.

Enum values: `junior`, `mid_level`, `senior`.

### `FreelancerLevelHistoryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `history_id` | `string` | yes | - |
| `freelancer_profile_id` | `string` | yes | - |
| `old_level` | `FreelancerLevelEnum` or `null` | yes | - |
| `new_level` | `FreelancerLevelEnum` | yes | - |
| `assigned_by_user_id` | `string` | yes | - |
| `reason` | `string` or `null` | yes | - |
| `assigned_at` | `string` | yes | - |

### `FreelancerProfileResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `profile_id` | `string` | yes | - |
| `user_id` | `string` | yes | - |
| `display_name` | `string` | yes | - |
| `headline` | `string` or `null` | yes | - |
| `bio` | `string` or `null` | yes | - |
| `country_code` | `string` or `null` | yes | - |
| `city` | `string` or `null` | yes | - |
| `timezone` | `string` or `null` | yes | - |
| `hourly_rate_min` | `string` or `null` | yes | - |
| `hourly_rate_max` | `string` or `null` | yes | - |
| `is_available` | `boolean` | yes | - |
| `current_level` | `FreelancerLevelEnum` or `null` | yes | - |
| `approval_status` | `string` | yes | - |
| `approved_at` | `string` or `null` | yes | - |

### `FreelancerRatingsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `ratings` | array of `RatingResponse` | yes | - |
| `average_score` | `string` or `null` | yes | - |

### `FreelancerStatisticsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `total_freelancers` | `integer` | yes | - |
| `approved_freelancers` | `integer` | yes | - |
| `pending_freelancers` | `integer` | yes | - |
| `average_rating` | `string` or `null` | yes | - |

### `GrantPermissionRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `permission_id` | `string` | yes | - |

### `GrantPermissionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `role_id` | `string` | yes | - |
| `permission_id` | `string` | yes | - |

### `ListCategorySupervisorsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `supervisors` | array of `CategorySupervisorResponse` | yes | - |

### `ListFormTemplateVersionsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `versions` | array of `FormTemplateResponse` | yes | - |

### `ListFormTemplatesResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `templates` | array of `FormTemplateResponse` | yes | - |

### `ListPermissionsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `permissions` | array of `PermissionResponse` | yes | - |

### `ListRolesResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `roles` | array of `RoleResponse` | yes | - |

### `LoginRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `email` | `string` | yes | - |
| `password` | `string` | yes | - |

### `LoginResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `access_token` | `string` | yes | - |
| `refresh_token` | `string` | yes | - |
| `refresh_token_jti` | `string` | yes | - |

### `LogoutRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `refresh_token` | `string` | yes | - |

### `PaginationMeta`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `page` | `integer` | yes | - |
| `page_size` | `integer` | yes | - |
| `total_items` | `integer` | yes | - |
| `total_pages` | `integer` | yes | - |

### `PermissionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `permission_id` | `string` | yes | - |
| `permission_key` | `string` | yes | - |
| `module` | `string` | yes | - |
| `action` | `string` | yes | - |
| `description` | `string` or `null` | no | - |
| `is_system` | `boolean` | yes | - |

### `PortfolioItemResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `item_id` | `string` | yes | - |
| `freelancer_profile_id` | `string` | yes | - |
| `title` | `string` | yes | - |
| `description` | `string` or `null` | yes | - |
| `external_url` | `string` or `null` | yes | - |
| `file_asset_id` | `string` or `null` | yes | - |
| `display_order` | `integer` | yes | - |
| `is_featured` | `boolean` | yes | - |

### `ProjectApplicationStatus`

Enum values: `applied`, `shortlisted`, `accepted`, `rejected`, `withdrawn`, `expired`.

### `ProjectDetailsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project` | `ProjectResponse` | yes | - |
| `applications` | array of `ApplicationResponse` | yes | - |
| `deliveries` | array of `DeliveryResponse` | yes | - |

### `ProjectPriority`

Enum values: `low`, `normal`, `high`, `urgent`.

### `ProjectRatingResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `rating` | `RatingResponse` or `null` | yes | - |

### `ProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `project_code` | `string` | yes | - |
| `customer_user_id` | `string` | yes | - |
| `category_id` | `string` | yes | - |
| `required_level` | `FreelancerLevelEnum` or `null` | yes | - |
| `title` | `string` | yes | - |
| `description` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |
| `visibility` | `ProjectVisibility` | yes | - |
| `priority` | `ProjectPriority` | yes | - |
| `budget` | `BudgetResponse` | yes | - |
| `assigned_supervisor_user_id` | `string` or `null` | yes | - |
| `selected_application_id` | `string` or `null` | yes | - |
| `application_deadline` | `string` (`date-time`) or `null` | yes | - |
| `created_by_user_id` | `string` or `null` | yes | - |
| `created_at` | `string` (`date-time`) | yes | - |

### `ProjectRevisionRequestResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `revision_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `project_delivery_id` | `string` or `null` | yes | - |
| `requested_by_user_id` | `string` | yes | - |
| `requested_to_user_id` | `string` or `null` | yes | - |
| `round_no` | `integer` | yes | - |
| `status` | `string` | yes | - |
| `reason` | `string` | yes | - |
| `resolved_by_user_id` | `string` or `null` | yes | - |
| `requested_at` | `string` (`date-time`) | yes | - |
| `resolved_at` | `string` (`date-time`) or `null` | yes | - |

### `ProjectStatisticsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `created` | `integer` | yes | - |
| `completed` | `integer` | yes | - |
| `cancelled` | `integer` | yes | - |

### `ProjectStatus`

Enum values: `draft`, `published`, `collecting_applications`, `assigned`, `in_progress`, `delivery_submitted`, `under_supervisor_review`, `revision_requested`, `awaiting_customer_review`, `completed`, `cancelled`, `archived`.

### `ProjectStatusHistoryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `history_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `from_status` | `string` or `null` | yes | - |
| `to_status` | `string` | yes | - |
| `changed_by_user_id` | `string` | yes | - |
| `reason` | `string` or `null` | yes | - |
| `changed_at` | `string` (`date-time`) | yes | - |

### `ProjectVisibility`

Enum values: `public`, `private`, `invite_only`.

### `PublishFormTemplateResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `template_id` | `string` | yes | - |
| `status` | `FormTemplateStatus` | yes | - |
| `published_at` | `string` | yes | - |

### `PublishProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |

### `RatingResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `rating_id` | `string` | yes | - |
| `customer_review_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `customer_user_id` | `string` | yes | - |
| `freelancer_profile_id` | `string` | yes | - |
| `score` | `integer` | yes | - |
| `comment` | `string` or `null` | yes | - |
| `is_public` | `boolean` | yes | - |

### `RefreshRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `refresh_token` | `string` | yes | - |

### `RefreshResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `access_token` | `string` | yes | - |
| `refresh_token` | `string` | yes | - |
| `refresh_token_jti` | `string` | yes | - |

### `RegisterRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `email` | `string` | yes | - |
| `password` | `string` | yes | minLength=8 |
| `first_name` | `string` | yes | - |
| `last_name` | `string` | yes | - |
| `role` | `string` | yes | - |

### `RegisterResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `role` | `string` | yes | - |
| `status` | `string` | yes | - |
| `created_at` | `string` | yes | - |

### `RelatedUserResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `first_name` | `string` | yes | - |
| `last_name` | `string` | yes | - |

### `RemoveFieldOptionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `option_id` | `string` | yes | - |

### `RemoveFieldResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `field_id` | `string` | yes | - |

### `RemoveRoleResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `role_id` | `string` | yes | - |
| `revoked_at` | `string` | yes | - |

### `RemoveSupervisorResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `category_id` | `string` | yes | - |
| `supervisor_user_id` | `string` | yes | - |
| `revoked_at` | `string` | yes | - |

### `ResumeChangeResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `resume_id` | `string` | yes | - |

### `ResumeResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `resume_id` | `string` | yes | - |
| `freelancer_profile_id` | `string` | yes | - |
| `file_asset_id` | `string` | yes | - |
| `version_no` | `integer` | yes | - |
| `summary` | `string` or `null` | yes | - |
| `is_current` | `boolean` | yes | - |

### `ReviewDeliveryRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `decision` | `ReviewStatus` | yes | - |
| `notes` | `string` or `null` | no | - |
| `reject_reason` | `string` or `null` | no | - |

### `ReviewResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `review_id` | `string` | yes | - |
| `project_delivery_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `supervisor_user_id` | `string` | yes | - |
| `decision` | `ReviewStatus` | yes | - |
| `reject_reason` | `string` or `null` | yes | - |
| `notes` | `string` or `null` | yes | - |
| `reviewed_at` | `string` (`date-time`) or `null` | yes | - |

### `ReviewStatus`

Enum values: `pending`, `approved`, `rejected`.

### `RevokePermissionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `role_id` | `string` | yes | - |
| `permission_id` | `string` | yes | - |

### `RoleResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `role_id` | `string` | yes | - |
| `role_key` | `string` | yes | - |
| `name` | `string` | yes | - |
| `description` | `string` or `null` | no | - |
| `is_system` | `boolean` | yes | - |

### `SendMessageRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `body` | `string` | yes | minLength=1 |
| `attachment_file_asset_ids` | array of `string` | no | - |

### `SendMessageResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `message_id` | `string` | yes | - |
| `ticket_id` | `string` | yes | - |
| `last_message_at` | `string` (`date-time`) | yes | - |

### `StartProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |

### `SubmitDeliveryRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `delivery_note` | `string` or `null` | no | - |
| `file_asset_ids` | array of `string` | no | - |

### `SubmitDeliveryResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `delivery_id` | `string` | yes | - |
| `version_no` | `integer` | yes | - |
| `project_status` | `ProjectStatus` | yes | - |

### `SubmitFreelancerApprovalResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `profile_id` | `string` | yes | - |
| `approval_status` | `string` | yes | - |

### `SubmitRatingRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `score` | `integer` | yes | minimum=1.0; maximum=5.0 |
| `comment` | `string` or `null` | no | - |
| `is_public` | `boolean` | no | default=`False` |

### `SubmitRatingResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `rating_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `score` | `integer` | yes | - |

### `SubmitReviewRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `decision` | `ReviewStatus` | yes | - |
| `comment` | `string` or `null` | no | - |

### `SubmitReviewResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `review_id` | `string` | yes | - |
| `project_id` | `string` | yes | - |
| `decision` | `ReviewStatus` | yes | - |
| `project_status` | `ProjectStatus` | yes | - |

### `SuccessEnvelope_AcceptFreelancerResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AcceptFreelancerResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ActivateUserResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ActivateUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AddFieldOptionResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AddFieldOptionResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AddFieldResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AddFieldResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AddPortfolioItemResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AddPortfolioItemResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AdminCreateUserResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AdminCreateUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AdminDeleteUserResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AdminDeleteUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AdminGetUserResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AdminGetUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AdminListUsersResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AdminListUsersResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AdminUpdateUserResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AdminUpdateUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ApplicationResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ApplicationResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ApplyForProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ApplyForProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ApproveFreelancerResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ApproveFreelancerResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AssignFreelancerLevelResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AssignFreelancerLevelResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AssignRoleResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AssignRoleResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_AssignSupervisorResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `AssignSupervisorResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_BlockUserResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `BlockUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CancelProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CancelProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CategoryResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CategoryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CloseTicketResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CloseTicketResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CreateFormTemplateResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CreateFormTemplateResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CreateFreelancerProfileResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CreateFreelancerProfileResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CreateProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CreateProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CreateTicketResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CreateTicketResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CustomerReviewResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CustomerReviewResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CustomerReviewsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CustomerReviewsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_CustomerStatisticsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `CustomerStatisticsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DashboardStatisticsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DashboardStatisticsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DeleteCategoryResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DeleteCategoryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DeleteFormTemplateResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DeleteFormTemplateResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DeletePortfolioItemResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DeletePortfolioItemResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DeleteProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DeleteProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DeliveryResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DeliveryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_DeliveryReviewResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `DeliveryReviewResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_FileAssetResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `FileAssetResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_FormTemplateResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `FormTemplateResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_FreelancerProfileResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `FreelancerProfileResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_FreelancerRatingsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `FreelancerRatingsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_FreelancerStatisticsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `FreelancerStatisticsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_GrantPermissionResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `GrantPermissionResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ListCategorySupervisorsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ListCategorySupervisorsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ListFormTemplateVersionsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ListFormTemplateVersionsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ListFormTemplatesResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ListFormTemplatesResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ListPermissionsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ListPermissionsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ListRolesResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ListRolesResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_LoginResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `LoginResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_PortfolioItemResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `PortfolioItemResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ProjectDetailsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ProjectDetailsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ProjectRatingResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ProjectRatingResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ProjectRevisionRequestResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ProjectRevisionRequestResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ProjectStatisticsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ProjectStatisticsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_PublishFormTemplateResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `PublishFormTemplateResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_PublishProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `PublishProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RefreshResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RefreshResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RegisterResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RegisterResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RemoveFieldOptionResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RemoveFieldOptionResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RemoveFieldResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RemoveFieldResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RemoveRoleResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RemoveRoleResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RemoveSupervisorResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RemoveSupervisorResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ResumeChangeResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ResumeChangeResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ResumeResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ResumeResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_ReviewResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `ReviewResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_RevokePermissionResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `RevokePermissionResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_SendMessageResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `SendMessageResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_StartProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `StartProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_SubmitDeliveryResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `SubmitDeliveryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_SubmitFreelancerApprovalResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `SubmitFreelancerApprovalResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_SubmitRatingResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `SubmitRatingResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_SubmitReviewResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `SubmitReviewResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_SystemAnalyticsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `SystemAnalyticsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_TicketMessageResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `TicketMessageResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_TicketResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `TicketResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UpdateFieldOptionResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UpdateFieldOptionResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UpdateFieldResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UpdateFieldResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UpdateFormTemplateResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UpdateFormTemplateResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UpdatePortfolioItemResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UpdatePortfolioItemResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UpdateProjectResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UpdateProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UpdateResumeResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UpdateResumeResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UploadResumeResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UploadResumeResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UserMeResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UserMeResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_UserStatisticsResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `UserStatisticsResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_WithdrawApplicationResponse_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `WithdrawApplicationResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_dict_`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | object/map | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_dict_str__str__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | object/map | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_ApplicationResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `ApplicationResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_CategoryResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `CategoryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_DeliveryResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `DeliveryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_FreelancerLevelHistoryResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `FreelancerLevelHistoryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_FreelancerProfileResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `FreelancerProfileResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_PortfolioItemResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `PortfolioItemResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_ProjectResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `ProjectResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_ProjectRevisionRequestResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `ProjectRevisionRequestResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_ProjectStatusHistoryResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `ProjectStatusHistoryResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_RelatedUserResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `RelatedUserResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_ResumeResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `ResumeResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_ReviewResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `ReviewResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_TicketMessageResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `TicketMessageResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SuccessEnvelope_list_TicketResponse__`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | array of `TicketResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `SystemAnalyticsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `dashboard` | `DashboardStatisticsResponse` | yes | - |
| `users` | `UserStatisticsResponse` | yes | - |
| `projects` | `ProjectStatisticsResponse` | yes | - |
| `freelancers` | `FreelancerStatisticsResponse` | yes | - |
| `customers` | `CustomerStatisticsResponse` | yes | - |

### `TicketMessageResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `message_id` | `string` | yes | - |
| `ticket_id` | `string` | yes | - |
| `sender_user_id` | `string` | yes | - |
| `message_type` | `TicketMessageType` | yes | - |
| `body` | `string` or `null` | yes | - |
| `is_internal` | `boolean` | yes | - |
| `sent_at` | `string` (`date-time`) | yes | - |
| `attachment_file_asset_ids` | array of `string` | yes | - |

### `TicketMessageType`

Enum values: `text`, `file`, `system`.

### `TicketPriority`

Enum values: `low`, `normal`, `high`, `urgent`.

### `TicketResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `ticket_id` | `string` | yes | - |
| `ticket_code` | `string` | yes | - |
| `created_by_user_id` | `string` | yes | - |
| `target_user_id` | `string` | yes | - |
| `subject` | `string` | yes | - |
| `status` | `TicketStatus` | yes | - |
| `priority` | `TicketPriority` | yes | - |
| `closed_at` | `string` (`date-time`) or `null` | yes | - |
| `last_message_at` | `string` (`date-time`) or `null` | yes | - |

### `TicketStatus`

Enum values: `open`, `closed`, `archived`.

### `UpdateCategoryRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `name` | `string` | yes | minLength=1 |
| `slug` | `string` | yes | minLength=1 |
| `description` | `string` or `null` | no | - |
| `sort_order` | `integer` | no | default=`0` |

### `UpdateCustomerReviewRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `comment` | `string` or `null` | no | - |

### `UpdateFieldOptionRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `label` | `string` or `null` | no | - |
| `value` | `string` or `null` | no | - |
| `sort_order` | `integer` or `null` | no | - |
| `is_active` | `boolean` or `null` | no | - |

### `UpdateFieldOptionResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `option_id` | `string` | yes | - |

### `UpdateFieldRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `label` | `string` or `null` | no | - |
| `description` | `string` or `null` | no | - |
| `field_type` | `FormFieldType` or `null` | no | - |
| `is_required` | `boolean` or `null` | no | - |
| `is_repeatable` | `boolean` or `null` | no | - |
| `is_unique` | `boolean` or `null` | no | - |
| `sort_order` | `integer` or `null` | no | - |
| `validation_rules` | object/map or `null` | no | - |
| `is_active` | `boolean` or `null` | no | - |

### `UpdateFieldResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `field_id` | `string` | yes | - |

### `UpdateFormTemplateRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `name` | `string` | yes | minLength=1 |

### `UpdateFormTemplateResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `template_id` | `string` | yes | - |
| `name` | `string` | yes | - |

### `UpdateFreelancerProfileRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `display_name` | `string` or `null` | no | - |
| `headline` | `string` or `null` | no | - |
| `bio` | `string` or `null` | no | - |
| `country_code` | `string` or `null` | no | - |
| `city` | `string` or `null` | no | - |
| `timezone` | `string` or `null` | no | - |
| `hourly_rate_min` | `number` or `string` or `null` | no | - |
| `hourly_rate_max` | `number` or `string` or `null` | no | - |

### `UpdatePortfolioItemRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `title` | `string` | yes | - |
| `description` | `string` or `null` | no | - |
| `external_url` | `string` or `null` | no | - |
| `file_asset_id` | `string` or `null` | no | - |
| `display_order` | `integer` | no | default=`0` |
| `is_featured` | `boolean` | no | default=`False` |

### `UpdatePortfolioItemResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `item_id` | `string` | yes | - |

### `UpdateProjectRequest`

DRAFT-only edit; every field is replaced, so send the full desired state.  ``category_id`` is derived from ``form_template_id`` and is not accepted here.

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `form_template_id` | `string` | yes | - |
| `title` | `string` | yes | - |
| `description` | `string` | yes | - |
| `visibility` | `ProjectVisibility` | yes | - |
| `budget_type` | `BudgetType` | yes | - |
| `currency_code` | `string` | yes | - |
| `required_level` | `FreelancerLevelEnum` or `null` | no | - |
| `fixed_budget` | `number` or `string` or `null` | no | - |
| `budget_min` | `number` or `string` or `null` | no | - |
| `budget_max` | `number` or `string` or `null` | no | - |
| `priority` | `ProjectPriority` | no | default=`normal` |
| `application_deadline` | `string` (`date-time`) or `null` | no | - |
| `form_values` | array of `FormValueInputRequest` | no | - |

### `UpdateProjectResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `project_id` | `string` | yes | - |
| `status` | `ProjectStatus` | yes | - |

### `UpdateRatingRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `score` | `integer` | yes | minimum=1.0; maximum=5.0 |
| `comment` | `string` or `null` | no | - |
| `is_public` | `boolean` | no | default=`False` |

### `UpdateResumeRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `summary` | `string` or `null` | no | - |

### `UpdateResumeResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `resume_id` | `string` | yes | - |
| `summary` | `string` or `null` | yes | - |

### `UpdateTicketMessageRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `body` | `string` | yes | minLength=1 |

### `UpdateTicketRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `subject` | `string` or `null` | no | - |
| `priority` | `TicketPriority` or `null` | no | - |
| `status` | `TicketStatus` or `null` | no | - |

### `UploadResumeRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `file_asset_id` | `string` | yes | - |
| `summary` | `string` or `null` | no | - |

### `UploadResumeResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `resume_id` | `string` | yes | - |
| `version_no` | `integer` | yes | - |

### `UserMeResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `user_id` | `string` | yes | - |
| `email` | `string` | yes | - |
| `roles` | array of `string` | yes | - |
| `permissions` | array of `string` | yes | - |
| `freelancer_profile_id` | `string` or `null` | no | - |
| `freelancer_onboarding_needed` | `boolean` | no | default=`False` |
| `freelancer_approval_status` | `string` or `null` | no | - |
| `freelancer_level` | `string` or `null` | no | - |

### `UserStatisticsResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `total_users` | `integer` | yes | - |
| `verified_users` | `integer` | yes | - |
| `active_users` | `integer` | yes | - |

### `UserStatus`

Enum values: `pending`, `active`, `blocked`, `archived`.

### `WithdrawApplicationResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `application_id` | `string` | yes | - |
| `status` | `ProjectApplicationStatus` | yes | - |

### `app__presentation__api__v1__freelancer__schemas__RejectFreelancerRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `note` | `string` | yes | - |

### `app__presentation__api__v1__freelancer__schemas__RejectFreelancerResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `profile_id` | `string` | yes | - |
| `approval_status` | `string` | yes | - |

### `app__presentation__api__v1__project__schemas__RejectFreelancerRequest`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `note` | `string` or `null` | no | - |

### `app__presentation__api__v1__project__schemas__RejectFreelancerResponse`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `application_id` | `string` | yes | - |
| `status` | `ProjectApplicationStatus` | yes | - |

### `app__presentation__core__envelope__SuccessEnvelope_RejectFreelancerResponse___1`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `app__presentation__api__v1__freelancer__schemas__RejectFreelancerResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |

### `app__presentation__core__envelope__SuccessEnvelope_RejectFreelancerResponse___2`

| Field | Type | Required | Constraints/default |
|---|---|---|---|
| `success` | `boolean` | no | default=`True` |
| `message` | `string` | yes | - |
| `data` | `app__presentation__api__v1__project__schemas__RejectFreelancerResponse` | yes | - |
| `meta` | `PaginationMeta` or `null` | no | - |
