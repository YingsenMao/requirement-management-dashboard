# Product Requirements Document (PRD)

## Change history
- 2024-05-24: Initial PRD creation based on user requirements and brainstorming phase. (AI)
- 2024-05-24: Added "Under Review" to the Status options. (AI)
- 2024-05-24: Confirmed local storage strategy via Docker volumes on Alibaba Cloud ECS for uploaded files. Configured Nginx to serve media files directly to optimize performance. (AI)
- 2024-05-24: Defined strict file upload constraints: Max 3 files per request, max 5MB per file, whitelist extensions (.pdf, .docx, .xlsx, .png, .jpg). (AI)
- 2024-05-24: Iteration - Updated regular user visibility to allow viewing all requirements (read-only for others'). Added "Submitter" column to the list. Restricted Admin edit rights to only `workload` and `status` fields via an "Assess" action. (AI)
- 2024-05-24: Iteration - Added 'Region' column to the requirement list. Updated sorting logic to strictly order by Priority Score descending with unassessed (N/A) items at the bottom. (AI)

## Project overview
This project is a SaaS Requirements Management Platform designed for Product Managers to collect, manage, and prioritize feature requests from global users. The system allows administrators to create user accounts, while regular users can submit and track their requirement requests. The core value of the platform is its automated priority scoring system, which helps PMs objectively rank requests based on ROI and risk factors.

## Core requirements
1. **Role-Based Access Control (RBAC):** Two distinct roles: Admin (Product Manager) and Regular User.
2. **Data Visibility & Isolation:** Regular users can view all requirements in the system to foster transparency, but they can only edit/delete the requirements they created themselves (and only when in "Pending Review" status). Other users' requirements are strictly read-only for them. Admins can view all requests.
3. **State Machine & Locking:** Requests have a lifecycle (Status). Once a request moves past the initial "Pending Review" state, it becomes strictly read-only for the regular user to prevent scope creep.
4. **Automated Priority Scoring:** A weighted scoring algorithm calculates the priority of a request. To ensure accuracy, the score is only calculated and displayed after the Admin has assessed and inputted the "Workload".
5. **Admin Assessment Restrictions:** Admins are strictly limited to editing only the "Workload" and "Status" fields when assessing a requirement. They cannot modify the original content submitted by the user.
6. **File Storage & Persistence:** Uploaded files (requirement descriptions, market research) will be stored locally on the server using Docker named volumes (`media_volume`) to ensure persistence across container restarts. Nginx will serve these files directly to optimize backend performance.
7. **File Upload Security & Constraints:** To prevent malicious payloads and manage storage, file uploads are strictly limited to a maximum of 3 files per requirement, with a 5MB size limit per file. Only specific whitelisted extensions are allowed: `.pdf`, `.docx`, `.xlsx`, `.png`, and `.jpg`. Validation must occur on both frontend and backend.

## Core features
### 1. User Management
- Admin can create regular user accounts.
- Users can log in to the platform.

### 2. Requirement Submission & Management (Regular User)
- **Submit Request:** Users can submit a new requirement with the following fields:
  - Name (Required, Text)
  - Summary (Required, Text)
  - Region (Required, Select: China, Europe, South America, North America, Asia)
  - Requirement Type (Required, Select: Regulatory Compliance, Security Vulnerability, Revenue Growth, Cost Reduction, Bug, Feature Optimization)
  - Impacted Users (Required, Select: <100, 100-500, 500-1000, >1000)
  - Supplementary Materials (Optional, Multi-select: User Research, Data Report, Competitor Analysis, Technical Solution)
  - Revenue Impact in USD (Optional, Select: <50k, 50k-300k, 300k-1M, >1M)
  - Deadline (Optional, Date)
  - Attachments (Optional, File Upload: Max 3 files, max 5MB each, allowed types: .pdf, .docx, .xlsx, .png, .jpg)
- **View Requests:** Users can view a global list of all requirements. The list includes "Submitter" and "Region" columns. The list is sorted by Priority Score (descending), with unassessed requests (N/A) at the bottom. Users can only edit or delete requirements they created themselves (if Status is "Pending Review"). All other requirements are read-only.
- **Edit Requests:** Users can edit their requests *only if* the Status is "Pending Review". They cannot edit Workload, Status, or Priority Score. They can add or remove attachments within the defined constraints.

### 3. Requirement Management & Prioritization (Admin)
- **Global View:** Admins can view all requests submitted by all users. The list includes the "Region" column and is sorted by Priority Score in descending order, with unassessed requests (N/A) at the bottom.
- **Sorting:** The request list is sorted by Priority Score in descending order by default.
- **Admin Fields:** Admins can see the Submitter's Username and the Priority Score.
- **Assessment:** Admins can assess any requirement by clicking an "Assess" button, which allows them to edit *only* the Workload and Status fields.
- **File Access:** Admins can view and download all attachments associated with any request.

### 4. Priority Scoring Logic
- The Priority Score is displayed as "N/A" until the Admin explicitly sets the Workload to Small, Medium, or Large.
- **Formula (Sum of weights):**
  - **Requirement Type:** Regulatory Compliance (+50), Security Vulnerability (+40), Revenue Growth (+30), Cost Reduction (+20), Bug (+10), Feature Optimization (+0).
  - **Impacted Users:** >1000 (+40), 500-1000 (+30), 100-500 (+20), <100 (+10).
  - **Revenue Impact:** >1M (+40), 300k-1M (+30), 50k-300k (+20), <50k (+10), Not filled (+0).
  - **Supplementary Materials:** +5 for each selected item (Max +20).
  - **Workload:** Small (+30), Medium (+15), Large (+0).

## Core components
- **Frontend:** Vue 3 + Element Plus + TypeScript (Vite build).
- **Backend:** Python + Django + Django REST Framework (DRF).
- **Database:** MySQL 8.0 (via Docker Compose).
- **Authentication:** JWT (JSON Web Tokens) via SimpleJWT.
- **Storage:** Local Docker Volumes (mapped to Alibaba Cloud ECS disk), served directly via Nginx.

## App/user flow
1. Admin logs in and creates a Regular User account.
2. Regular User logs in and submits a new requirement request, optionally uploading up to 3 supporting documents (e.g., PDF, DOCX).
3. The request appears in the global list as "Pending Review" with Workload "Pending". The Submitter's username and Region are visible.
4. Admin logs in, sees the new request in the global list (Priority Score is "N/A" at the bottom), and downloads the attachments for review.
5. Admin clicks "Assess" on the request and updates the Workload to "Medium" and Status to "Confirmed". (Admin cannot edit the user's original text).
6. System automatically calculates the Priority Score based on the formula and updates the list sorting.
7. Regular User views their dashboard; the request is now "Confirmed" and all edit buttons (including file upload/remove) are disabled (locked).

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
