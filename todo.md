# Implementation Plan: SaaS Requirements Management Platform

## Task 1: Project Initialization
- [x] ID: 1.1
  - Description: Initialize Django backend project and core app (`requirements`).
  - Context: Create a standard Django project. Set up `requirements.txt` with Django, djangorestframework, and pytest-django.
  - Depends on: None
- [x] ID: 1.2
  - Description: Initialize Vue 3 frontend project.
  - Context: Use Vite to scaffold a Vue 3 + TypeScript project. Install Element Plus, Vue Router, Pinia, and Axios.
  - Depends on: None

## Task 2: User Authentication & RBAC
- [x] ID: 2.1
  - Description: Configure custom User model and Roles.
  - Context: Extend `AbstractUser` if necessary, or use Django's built-in User and Groups to distinguish between 'Admin' (Product Manager) and 'Regular User'.
  - Depends on: 1.1
- [x] ID: 2.2
  - Description: Setup JWT Authentication.
  - Context: Install and configure `djangorestframework-simplejwt`. Create login endpoints (`/api/token/`).
  - Depends on: 2.1
- [x] ID: 2.3
  - Description: Write pytest for User creation and JWT authentication.
  - Context: Test creating admin and regular users. Test token generation and validation.
  - Depends on: 2.2

## Task 3: Django Models for Requirement Requests
- [x] ID: 3.1
  - Description: Create `RequirementRequest` model.
  - Context: Fields include Name (Char), Summary (Text), Region (Char/Choices), Requirement Type (Char/Choices), Impacted Users (Char/Choices), Supplementary Materials (JSON/Array), Revenue Impact (Char/Choices), Deadline (Date, null=True), Submission Date (DateTime, auto_now_add=True), Workload (Char/Choices, default='Pending'), Status (Char/Choices, default='Pending Review'), Priority Score (Integer, null=True), Submitter (ForeignKey to User).
  - Depends on: 2.1
- [x] ID: 3.2
  - Description: Write pytest for `RequirementRequest` model.
  - Context: Verify model creation, default values (Workload='Pending', Status='Pending Review'), and foreign key constraints.
  - Depends on: 3.1

## Task 4: Priority Score Calculation Logic
- [x] ID: 4.1
  - Description: Implement priority calculation service/function.
  - Context: Input: RequirementRequest instance. Output: Integer score or None. Logic: Sum weights based on PRD formula (Type, Impacted Users, Revenue Impact, Supplementary Materials, Workload). Return None if Workload is 'Pending'.
  - Depends on: 3.1
- [x] ID: 4.2
  - Description: Integrate calculation into model `save()` method.
  - Context: Override `save()` in `RequirementRequest` to automatically call the calculation function and update `priority_score` before saving to the database.
  - Depends on: 4.1
- [x] ID: 4.3
  - Description: Write pytest for priority score calculation.
  - Context: Test all branches of the formula. Specifically test that score is None (N/A) when Workload is 'Pending', and correctly calculated when Workload is Small/Medium/Large.
  - Depends on: 4.2

## Task 5: DRF APIs and Permissions
- [x] ID: 5.1
  - Description: Create serializers for `RequirementRequest`.
  - Context: `RequirementRequestSerializer` for read/write. Ensure read-only fields are properly set (e.g., Priority Score, Submission Date).
  - Depends on: 4.2
- [x] ID: 5.2
  - Description: Implement custom DRF permissions.
  - Context: Create `IsOwnerAndPendingReview` (allows edit only if user is owner AND status is 'Pending Review'). Create `IsAdminUser` for admin-only actions.
  - Depends on: 5.1
- [x] ID: 5.3
  - Description: Create ViewSets for Regular Users.
  - Context: Endpoint `/api/requests/`. Users can POST to create. GET to list only their own requests. PATCH/PUT to update own requests (blocked by permission if status != 'Pending Review'). Users cannot update Workload, Status, or Priority Score.
  - Depends on: 5.2
- [x] ID: 5.4
  - Description: Create ViewSets for Admins.
  - Context: Endpoint `/api/admin/requests/`. GET to list all requests, ordered by `priority_score` descending. PATCH to update Workload and Status.
  - Depends on: 5.3
- [x] ID: 5.5
  - Description: Write pytest for API endpoints, permissions, and locking logic.
  - Context: Test user isolation (cannot see others' requests). Test locking mechanism (user gets 403 when editing a 'Confirmed' request). Test admin sorting and updating capabilities.
  - Depends on: 5.4

## Task 6: Frontend UI - Foundation & Auth
- [x] ID: 6.1
  - Description: Setup Vue Router and Pinia.
  - Context: Configure routing for Login, User Dashboard, and Admin Dashboard. Setup Pinia store for user session and JWT token management.
  - Depends on: 1.2
- [x] ID: 6.2
  - Description: Create Login page and integrate API.
  - Context: UI with username/password. On success, store JWT and redirect to appropriate dashboard based on user role.
  - Depends on: 6.1, 2.2

## Task 7: Frontend UI - Regular User
- [x] ID: 7.1
  - Description: Create User Dashboard.
  - Context: Fetch and display a table of the user's own requests using Element Plus `el-table`. Show Status, Workload, and Submission Date.
  - Depends on: 6.2, 5.3
- [x] ID: 7.2
  - Description: Create Request Submission Form.
  - Context: `el-form` with all required fields (Selects, Inputs, DatePicker). Submit to `/api/requests/`.
  - Depends on: 7.1
- [x] ID: 7.3
  - Description: Create Request Edit Form & UI Locking.
  - Context: Allow opening a request from the dashboard. If Status is 'Pending Review', form is editable. If Status is anything else, disable all form inputs (`disabled=true`) to reflect the read-only state.
  - Depends on: 7.2

## Task 8: Frontend UI - Admin
- [x] ID: 8.1
  - Description: Create Admin Dashboard.
  - Context: Fetch and display all requests. Ensure default sorting is by Priority Score (descending). Display "N/A" if Priority Score is null. Show Submitter username.
  - Depends on: 6.2, 5.4
- [x] ID: 8.2
  - Description: Create Admin Assessment Modal.
  - Context: Allow admin to click a request and open a modal to edit `Workload` and `Status`. Submit PATCH request to `/api/admin/requests/{id}/`.
  - Depends on: 8.1
