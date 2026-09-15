# Product Requirements Document (PRD)

## Change history
- 2024-05-24: Initial PRD creation based on user requirements and brainstorming phase. (AI)
- 2024-05-24: Added "Under Review" to the Status options. (AI)
- 2024-05-24: Confirmed local storage strategy via Docker volumes on Alibaba Cloud ECS for uploaded files. Configured Nginx to serve media files directly to optimize performance. (AI)
- 2024-05-24: Defined strict file upload constraints: Max 3 files per request, max 5MB per file, whitelist extensions (.pdf, .docx, .xlsx, .png, .jpg). (AI)
- 2024-05-24: Iteration - Updated regular user visibility to allow viewing all requirements (read-only for others'). Added "Submitter" column to the list. Restricted Admin edit rights to only `workload` and `status` fields via an "Assess" action. (AI)
- 2024-05-24: Iteration - Added 'Region' column to the requirement list. Updated sorting logic to strictly order by Priority Score descending with unassessed (N/A) items at the bottom. (AI)
- 2026-07-18: Corrected Priority Scoring formula to match actual implementation: Bug=+30, Revenue Growth=+20, Revenue Impact >1M=+50, Supplementary Materials=+20/item (max +50), Workload Small=+50/Medium=+10/Large=-10. (AI)
- 2026-07-18: Added Reject workflow - Admin must provide reject_reason when rejecting; Users see hoverable reject reason indicator; Rejected requirements can be re-edited by owner (status resets to Pending Review). (AI)
- 2026-07-18: Added Estimated Completion Date - Admin can optionally set an estimated completion date during assessment; visible to all users in the requirement list. (AI)
- 2026-07-18: Changed Region field to Country - replaced fixed region choices with a searchable global country list (195 countries); existing data migrated to "China". (AI)
- 2026-07-18: Added Urgency field (High/Medium/Low) to requirement form - for reference only, not included in priority score calculation; Admin can view it during assessment. (AI)
- 2026-09-13: Added Department dimension - Requirement requests now carry a mandatory "Owning Department" (IT / R&D) selected first at creation time (owner can still change it while Pending Review / Rejected). Admin accounts carry a department (IT / R&D) and can only view/assess/download attachments of requirements matching their own department (cross-department access returns 404/403). Regular users remain department-agnostic and can view all requirements, with a new "Department" column and IT/R&D filter on the user list. Added a User Management dialog (create-account only) in the Admin Dashboard: admins can create Regular User accounts (no department) or Admin accounts (department required); any admin may create admins of either department. Existing admins and existing requirements were migrated to department "IT". (AI)
- 2026-09-13: Added AI Requirement Review for IT department - When creating or editing an IT requirement, users can optionally launch an AI-powered review flow (skippable). The AI acts as a senior product manager, asks up to 5 follow-up questions one at a time based on the user's previous answers, then generates a refined requirement description and acceptance criteria. The user can edit or confirm the result, which is then merged into the Description (summary) field. All review sessions are persisted in the database for auditability; admins can view the full conversation history in the Assess dialog. R&D requirements use the traditional form without AI review. The AI is powered by Alibaba Cloud DashScope Qwen, with the review context based on a platform-provided PRD document (PRD_BCW.md). (AI)
- 2026-09-15: Added Django admin AI Review Audit page - Superusers can access `/admin/` to view aggregate audit statistics (total sessions, total messages, status breakdown, confirmation rate, avg messages/session, unique users) and a per-user usage table (username, role, sessions, messages, confirmed, last activity). Individual sessions can be drilled into to view the full AI/user conversation via read-only inline messages. All review data is read-only (no add/change/delete) for pure audit purposes. (AI)

## Project overview
This project is a SaaS Requirements Management Platform designed for Product Managers to collect, manage, and prioritize feature requests from global users. The system allows administrators to create user accounts, while regular users can submit and track their requirement requests. The core value of the platform is its automated priority scoring system, which helps PMs objectively rank requests based on ROI and risk factors.

## Core requirements
1. **Role-Based Access Control (RBAC):** Two distinct roles: Admin (Product Manager) and Regular User. Admins additionally carry a **Department** (IT or R&D), assigned at account creation and used for data scoping. Regular Users have no department.
2. **Data Visibility & Isolation:** Regular users can view all requirements in the system (department-agnostic) to foster transparency, but they can only edit/delete the requirements they created themselves (and only when in "Pending Review" or "Rejected" status). Other users' requirements are strictly read-only for them. **Admins are department-scoped:** an IT admin can only view/assess requirements whose Owning Department is IT; an R&D admin can only view/assess those whose Owning Department is R&D. Cross-department access returns 404 (list/detail) or 403 (attachment download).
3. **State Machine & Locking:** Requests have a lifecycle (Status). Once a request moves past the initial "Pending Review" state, it becomes strictly read-only for the regular user to prevent scope creep. **Exception:** When status is "Rejected", the owner can re-edit the requirement, which resets status to "Pending Review" and clears the reject reason.
4. **Automated Priority Scoring:** A weighted scoring algorithm calculates the priority of a request. To ensure accuracy, the score is only calculated and displayed after the Admin has assessed and inputted the "Workload".
5. **Admin Assessment Restrictions:** Admins are strictly limited to editing only the "Workload" and "Status" fields when assessing a requirement. They cannot modify the original content submitted by the user.
6. **File Storage & Persistence:** Uploaded files (requirement descriptions, market research) will be stored locally on the server using Docker named volumes (`media_volume`) to ensure persistence across container restarts. Nginx will serve these files directly to optimize backend performance.
7. **File Upload Security & Constraints:** To prevent malicious payloads and manage storage, file uploads are strictly limited to a maximum of 3 files per requirement, with a 5MB size limit per file. Only specific whitelisted extensions are allowed: `.pdf`, `.docx`, `.xlsx`, `.png`, and `.jpg`. Validation must occur on both frontend and backend.

## Core features
### 1. User Management
- Admin can create user accounts via a "User Management" dialog in the Admin Dashboard (create-account only, no edit/delete).
- Two account types: **Regular User** (no department) and **Admin** (department required: IT or R&D).
- Any admin may create admin accounts of either department (including cross-department).
- Users can log in to the platform.

### 2. Requirement Submission & Management (Regular User)
- **Submit Request:** Users can submit a new requirement with the following fields:
  - Owning Department (Required, Select: IT, R&D - the first field selected at creation; determines which admins can see the request)
  - Name (Required, Text)
  - Summary (Required, Text)
  - Country (Required, Select with fuzzy search: global country list)
  - Requirement Type (Required, Select: Regulatory Compliance, Security Vulnerability, Revenue Growth, Cost Reduction, Bug, Feature Optimization)
  - Impacted Users (Required, Select: <100, 100-500, 500-1000, >1000)
  - Supplementary Materials (Optional, Multi-select: User Research, Data Report, Competitor Analysis, Technical Solution)
  - Revenue Impact in USD (Optional, Select: <50k, 50k-300k, 300k-1M, >1M)
  - Deadline (Optional, Date)
  - Urgency (Optional, Select: High, Medium, Low - default Medium; for reference only, not used in priority scoring)
  - Attachments (Optional, File Upload: Max 3 files, max 5MB each, allowed types: .pdf, .docx, .xlsx, .png, .jpg)
- **View Requests:** Users can view a global list of all requirements. The list includes "Submitter", "Country", "Department", and "Est. Completion" columns, plus a Department filter (IT/R&D). The list is sorted by Priority Score (descending), with unassessed requests (N/A) at the bottom. Users can only edit or delete requirements they created themselves (if Status is "Pending Review" or "Rejected"). All other requirements are read-only. When a requirement is "Rejected", the Status column shows a hoverable indicator displaying the reject reason.
- **Edit Requests:** Users can edit their requests *only if* the Status is "Pending Review" or "Rejected". They cannot edit Workload, Status, or Priority Score. They can change the Owning Department while in these states (it locks together with the rest of the form once assessed). They can add or remove attachments within the defined constraints. When editing a "Rejected" requirement, the status automatically resets to "Pending Review" and the reject reason is cleared.

### 3. Requirement Management & Prioritization (Admin)
- **Department-Scoped View:** Admins can only view requests whose Owning Department matches their own department (IT admin → IT requests; R&D admin → R&D requests). The list includes the "Country" and "Est. Completion" columns and is sorted by Priority Score in descending order, with unassessed requests (N/A) at the bottom.
- **Sorting:** The request list is sorted by Priority Score in descending order by default.
- **Admin Fields:** Admins can see the Submitter's Username and the Priority Score. The admin's own department is shown as a badge in the dashboard header.
- **Assessment:** Admins can assess any requirement *within their department* by clicking an "Assess" button, which allows them to edit *only* the Workload, Status, and optionally the Estimated Completion Date fields. The Owning Department is displayed read-only and cannot be changed by admins. When selecting "Rejected" status, a mandatory "Reject Reason" text field appears.
- **File Access:** Admins can view and download attachments only for requests within their own department.

### 4. Priority Scoring Logic
- The Priority Score is displayed as "N/A" until the Admin explicitly sets the Workload to Small, Medium, or Large.
- **Formula (Sum of weights):**
  - **Requirement Type:** Regulatory Compliance (+50), Security Vulnerability (+40), Bug (+30), Revenue Growth (+20), Cost Reduction (+10), Feature Optimization (+0).
  - **Impacted Users:** >1000 (+40), 500-1000 (+30), 100-500 (+20), <100 (+10).
  - **Revenue Impact:** >1M (+50), 300k-1M (+30), 50k-300k (+20), <50k (+10), Not filled (+0).
  - **Supplementary Materials:** +20 for each selected item (Max +50).
  - **Workload:** Small (+50), Medium (+10), Large (-10).

### 5. AI Requirement Review (IT Department Only)
- **Trigger:** When creating or editing a requirement with Owning Department = IT, users see an "AI Review" button below the Description field. R&D requirements do not show this button and use the traditional form.
- **Optional & Skippable:** Users can skip the AI review and submit directly with their manually written description. AI service unavailability does not block submission.
- **Review Flow:**
  1. User clicks "AI Review" → system creates a ReviewSession with form context snapshot (name, summary, requirement_type, etc.)
  2. AI (acting as senior product manager) asks the first follow-up question based on the provided PRD context (PRD_BCW.md)
  3. User answers → AI asks next question (up to 5 questions total, can converge earlier if information is sufficient)
  4. After ≤5 questions, AI generates: (a) refined requirement description, (b) acceptance criteria
  5. User previews the result → can edit in the form or confirm → merged into Description (summary) field as HTML
- **Session Persistence:** All review sessions and messages are stored in the database (ReviewSession/ReviewMessage tables) for auditability. Each user can have at most 3 active (asking/generated) sessions to prevent abuse.
- **Admin Retrospection:** In the Admin Assess dialog, if the requirement has review sessions, a collapsible "AI Review History" panel shows the full conversation (Q&A) and final generated result.
- **Django Admin Audit Page:** Superusers can access `/admin/` → Review Sessions to view aggregate audit statistics (total sessions, total messages, status breakdown, confirmation rate, avg messages/session, unique users) and a per-user usage table (username, role, sessions, messages, confirmed, last activity). Individual sessions can be drilled into to view the full AI/user conversation via read-only inline messages. All review data is read-only (no add/change/delete) for pure audit purposes.
- **LLM Provider:** Alibaba Cloud DashScope Qwen (OpenAI-compatible API), configured via DASHSCOPE_API_KEY environment variable. Model defaults to qwen-plus, configurable via AI_REVIEW_MODEL.
- **Rate Limiting:** 30 requests per hour per user to prevent API abuse.

## Core components
- **Frontend:** Vue 3 + Element Plus + TypeScript (Vite build).
- **Backend:** Python + Django + Django REST Framework (DRF).
- **Database:** MySQL 8.0 (via Docker Compose).
- **Authentication:** JWT (JSON Web Tokens) via SimpleJWT.
- **Storage:** Local Docker Volumes (mapped to Alibaba Cloud ECS disk), served directly via Nginx.
- **LLM:** Alibaba Cloud DashScope Qwen (OpenAI-compatible API) for AI requirement review.

## App/user flow
1. Admin logs in, opens the "User Management" dialog, and creates a Regular User account (or an Admin account with a department).
2. Regular User logs in and submits a new requirement request, first selecting the Owning Department (IT or R&D), then filling in the details and optionally uploading up to 3 supporting documents (e.g., PDF, DOCX).
3. **For IT requirements:** User can optionally click "AI Review" to launch an AI-powered review flow. The AI asks up to 5 follow-up questions, then generates a refined description and acceptance criteria. User confirms or edits, which is merged into the Description field. User can skip this step and submit directly.
4. **For R&D requirements:** User fills in the Description manually and submits directly (no AI review).
5. The request appears in the global list as "Pending Review" with Workload "Pending". The Submitter's username, Country, and Department are visible.
6. An admin whose department matches the request's Owning Department logs in, sees the new request in their department-scoped list (Priority Score is "N/A" at the bottom), and downloads the attachments for review. Admins of the other department cannot see or access it.
7. Admin clicks "Assess" on the request and updates the Workload to "Medium" and Status to "Confirmed". (Admin cannot edit the user's original text or the Owning Department). If the requirement has AI review sessions, the admin can view the full conversation history in the Assess dialog.
8. System automatically calculates the Priority Score based on the formula and updates the list sorting.
9. Regular User views their dashboard; the request is now "Confirmed" and all edit buttons (including file upload/remove and department change) are disabled (locked).

## Implementation plan
- **Task 1:** Initialize project repositories (Django backend, Vue 3 frontend).
- **Task 2:** Implement User Authentication and Role-Based Access Control (RBAC).
- **Task 3:** Create Django models for Requirement Requests with appropriate fields, choices, and a related model for Attachments.
- **Task 4:** Develop DRF APIs for CRUD operations, including custom permission classes, locking logic, and strict file validation (size and extension).
- **Task 5:** Implement the Priority Score calculation logic in the backend (triggered on Workload update).
- **Task 6:** Build Frontend UI (Login, Admin Dashboard, User Dashboard, Request Form with Element Plus Upload component).
- **Task 7:** Integrate Frontend with Backend APIs, implement UI state locking, and handle file upload/download flows.
- **Task 8:** End-to-end testing and bug fixing.
- **Task 9:** Iteration - Visibility, Submitter Column, and Permission Refinement.
- **Task 10:** Iteration - Department Dimension: Owning Department on requirements, Admin department scoping/isolation, User Management dialog (create-account), and department column/filter on the user list.
- **Task 11:** AI Requirement Review (IT Only): ReviewSession/ReviewMessage data model, AI service layer (DashScope Qwen), API endpoints for session lifecycle + admin retrospection, frontend AiReviewDialog component, integration into RequirementForm/UserDashboard/AdminDashboard, deployment configuration (DASHSCOPE_API_KEY env var).
- **Task 12:** AI Review Audit Page (Django Admin): Register ReviewSession/ReviewMessage in Django admin with read-only audit page, aggregate statistics panel (total sessions/messages, status breakdown, confirmation rate, avg messages/session, unique users), per-user usage table, and inline message viewing for individual session drill-down.
