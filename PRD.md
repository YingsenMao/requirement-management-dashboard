# Product Requirements Document (PRD)

## Change history
- 2024-05-24: Initial PRD creation based on user requirements and brainstorming phase. (AI)
- 2024-05-24: Added "Under Review" to the Status options. (AI)

## Project overview
This project is a SaaS Requirements Management Platform designed for Product Managers to collect, manage, and prioritize feature requests from global users. The system allows administrators to create user accounts, while regular users can submit and track their requirement requests. The core value of the platform is its automated priority scoring system, which helps PMs objectively rank requests based on ROI and risk factors.

## Core requirements
1. **Role-Based Access Control (RBAC):** Two distinct roles: Admin (Product Manager) and Regular User.
2. **Data Isolation:** Regular users can only view and manage their own submitted requests. Admins can view and manage all requests across the platform.
3. **State Machine & Locking:** Requests have a lifecycle (Status). Once a request moves past the initial "Pending Review" state, it becomes strictly read-only for the regular user to prevent scope creep.
4. **Automated Priority Scoring:** A weighted scoring algorithm calculates the priority of a request. To ensure accuracy, the score is only calculated and displayed after the Admin has assessed and inputted the "Workload".

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
- **View Requests:** Users can view a list of their own requests, including system-generated fields: Submission Date, Workload (Default: Pending), and Status (Default: Pending Review).
- **Edit Requests:** Users can edit their requests *only if* the Status is "Pending Review". They cannot edit Workload, Status, or Priority Score.

### 3. Requirement Management & Prioritization (Admin)
- **Global View:** Admins can view all requests submitted by all users.
- **Sorting:** The request list is sorted by Priority Score in descending order by default.
- **Admin Fields:** Admins can see the Submitter's Username and the Priority Score.
- **Assessment:** Admins can edit the following fields for any request:
  - Workload (Select: Pending, Large, Medium, Small)
  - Status (Select: Pending Review, Under Review, Confirmed, In Development, Completed, Rejected)

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
- **Database:** SQLite (for initial development/MVP) or PostgreSQL.
- **Authentication:** JWT (JSON Web Tokens) or Django Session Auth.

## App/user flow
1. Admin logs in and creates a Regular User account.
2. Regular User logs in and submits a new requirement request.
3. The request appears in the User's dashboard as "Pending Review" with Workload "Pending".
4. Admin logs in, sees the new request in the global list (Priority Score is "N/A").
5. Admin reviews the request and updates the Workload to "Medium".
6. System automatically calculates the Priority Score based on the formula and updates the list sorting.
7. Admin changes the Status to "Confirmed".
8. Regular User views their dashboard; the request is now "Confirmed" and all edit buttons are disabled (locked).

## Implementation plan
- **Task 1:** Initialize project repositories (Django backend, Vue 3 frontend).
- **Task 2:** Implement User Authentication and Role-Based Access Control (RBAC).
- **Task 3:** Create Django models for Requirement Requests with appropriate fields and choices.
- **Task 4:** Develop DRF APIs for CRUD operations, including custom permission classes for Admin vs. Regular User access and locking logic.
- **Task 5:** Implement the Priority Score calculation logic in the backend (triggered on Workload update).
- **Task 6:** Build Frontend UI (Login, Admin Dashboard, User Dashboard, Request Form).
- **Task 7:** Integrate Frontend with Backend APIs and implement UI state locking based on request status.
- **Task 8:** End-to-end testing and bug fixing.
