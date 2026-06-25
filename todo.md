# Implementation Todo List

## Task 1: Project Initialization & Base Setup
- [ ] ID: 1.1: Verify Docker Compose setup and ensure all containers (db, backend, frontend) start successfully. (Depends on: None)
- [ ] ID: 1.2: Configure Django `settings.py` for MySQL and local media storage. (Depends on: 1.1)
- [ ] ID: 1.3: Write pytest to verify database connection and media directory writability. (Depends on: 1.2)

## Task 2: User Authentication & RBAC
- [ ] ID: 2.1: Create `CustomUser` model in `requirements_app` with `role` field (Admin/Regular). (Depends on: 1.2)
- [ ] ID: 2.2: Implement JWT authentication endpoints (login, refresh) using SimpleJWT. (Depends on: 2.1)
- [ ] ID: 2.3: Create Admin-only endpoint to create Regular Users. (Depends on: 2.2)
- [ ] ID: 2.4: Write pytest for user creation, login, and role-based access restrictions. (Depends on: 2.3)

## Task 3: Requirement Models & Attachments
- [ ] ID: 3.1: Create `Requirement` model with all PRD fields (Name, Summary, Region, Type, Impacted Users, Supplementary Materials, Revenue Impact, Deadline, Status, Workload, Priority Score). (Depends on: 2.1)
- [ ] ID: 3.2: Create `Attachment` model linked to `Requirement` (ForeignKey) with file field and uploaded_at timestamp. (Depends on: 3.1)
- [ ] ID: 3.3: Write pytest for model creation, field constraints, and relationship integrity. (Depends on: 3.2)

## Task 4: DRF APIs & Business Logic (CRUD, Locking, Validation)
- [ ] ID: 4.1: Create `RequirementSerializer` and `AttachmentSerializer` with strict file validation (max 5MB, whitelist extensions: .pdf, .docx, .xlsx, .png, .jpg). (Depends on: 3.2)
- [ ] ID: 4.2: Implement `RequirementViewSet` with custom permissions (Admin sees all, User sees own). (Depends on: 4.1)
- [ ] ID: 4.3: Implement State Machine Locking: Prevent Regular Users from editing if Status != 'Pending Review'. (Depends on: 4.2)
- [ ] ID: 4.4: Implement Attachment upload/delete endpoints with max 3 files limit enforcement. (Depends on: 4.2)
- [ ] ID: 4.5: Write pytest for API CRUD operations, file validation (size/extension), permission boundaries, and state locking. (Depends on: 4.4)

## Task 5: Priority Scoring Logic
- [ ] ID: 5.1: Implement `calculate_priority_score` utility function based on PRD formula. (Depends on: 3.1)
- [ ] ID: 5.2: Override `RequirementViewSet` update/partial_update to trigger score calculation only when Admin updates 'Workload' to Small/Medium/Large. (Depends on: 5.1, 4.2)
- [ ] ID: 5.3: Write pytest to verify score calculation accuracy across all PRD weight combinations and N/A state. (Depends on: 5.2)

## Task 6: Frontend UI Setup & Auth
- [ ] ID: 6.1: Initialize Vue 3 + Element Plus + TypeScript + Vite project structure and routing. (Depends on: None)
- [ ] ID: 6.2: Setup Pinia store and Axios interceptors for JWT token management. (Depends on: 6.1)
- [ ] ID: 6.3: Build Login Page and Admin User Management Page (Create User). (Depends on: 6.2)

## Task 7: Frontend Requirement Dashboards & File Upload
- [ ] ID: 7.1: Build Regular User Dashboard (List own requests, Submit/Edit Form). (Depends on: 6.3)
- [ ] ID: 7.2: Integrate Element Plus `el-upload` component with frontend validation (max 3 files, 5MB, extensions). (Depends on: 7.1)
- [ ] ID: 7.3: Build Admin Dashboard (Global list, sorted by Priority Score, Edit Workload/Status). (Depends on: 6.3)
- [ ] ID: 7.4: Implement UI State Locking: Disable form inputs and upload components for Regular Users when Status != 'Pending Review'. (Depends on: 7.1, 7.2)
- [ ] ID: 7.5: Implement file download links pointing to Nginx `/media/` path. (Depends on: 7.1, 7.3)

## Task 8: End-to-End Testing & Refinement
- [ ] ID: 8.1: Perform manual E2E testing of the complete User Flow (Submit -> Admin Review -> Score Calc -> Lock). (Depends on: 7.4, 7.5)
- [ ] ID: 8.2: Fix any UI/UX bugs or edge cases discovered during E2E testing. (Depends on: 8.1)

## Task 9: Iteration - Visibility, Submitter Column, and Permission Refinement
- [x] ID: 9.1: Update Backend QuerySets and Permissions: Allow regular users to view all requirements (read-only for others), and restrict edit/delete to owners when status is 'pending_review'. (Depends on: None)
- [x] ID: 9.2: Write pytest for ID 9.1 to verify global read access and owner-only write/delete restrictions. (Depends on: 9.1)
- [x] ID: 9.3: Update Admin Serializer/ViewSet to restrict Admin updates strictly to `workload` and `status` fields. (Depends on: 9.2)
- [x] ID: 9.4: Write pytest for ID 9.3 to verify Admin field-level restrictions. (Depends on: 9.3)
- [x] ID: 9.5: Update Frontend Requirement List page to add "Submitter" column, handle read-only states for non-owners, and add "Assess" button/modal for Admins. (Depends on: 9.4)
