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

## Task 10: Iteration - Department Dimension (Owning Department + Admin Department Isolation + User Management)
- [x] ID: 10.1: Backend Models & Migration 0007 - Add `CustomUser.department` (choices: it/rnd, null=True blank=True for regular users) and `RequirementRequest.owning_department` (choices: it/rnd, default='it'). Data migration: set department='it' for all existing role='admin' users; existing requirements get 'it' via model default. (Depends on: None)
- [x] ID: 10.2: Backend Serializers - (a) `CustomTokenObtainPairSerializer` adds `department` JWT claim. (b) `RequirementRequestSerializer` adds `owning_department` as explicit `ChoiceField(required=True)` (overrides model default; 400 if missing/invalid on create AND update). (c) `AdminRequirementSerializer` adds `owning_department` to fields + read_only_fields. (d) New `UserCreateSerializer`: username (unique, 400 on duplicate), password (validate_password + set_password), role (admin/user), department (required when role=admin and must be it/rnd; forced to None when role=user). (Depends on: 10.1)
- [x] ID: 10.3: Backend Views & URLs - (a) `AdminRequirementViewSet.get_queryset` filters `.filter(owning_department=self.request.user.department)`; defensive: empty queryset if admin.department is falsy. (retrieve/update/destroy auto-404 cross-department via same queryset). (b) `AttachmentDownloadView`: admin downloads require `requirement.owning_department == user.department`, else 403; submitter rule unchanged. (c) New `UserCreateView(APIView)` at POST `/api/admin/users/` with IsAdminUser permission, returns 201 + {id, username, role, department}. (d) Register URL. (Depends on: 10.2)
- [x] ID: 10.4: Backend pytest - New tests: IT admin list sees only IT requests; R&D admin sees only R&D; cross-department retrieve → 404; cross-department assess (PATCH) → 404; cross-department attachment download → 403; regular user still sees all; create requirement without owning_department → 400; invalid owning_department value → 400; owner can change owning_department in pending_review/rejected, cannot when locked (other statuses keep DB value); admin creates Regular User (department forced None) and Admin (department required → 400 if missing; invalid → 400); duplicate username → 400; regular user calling POST /api/admin/users/ → 403; JWT contains department claim; admin with null department sees empty list. Update existing API-POST creation tests to include owning_department. Full pytest suite green. (Depends on: 10.3)
- [x] ID: 10.5: Frontend API & Store - (a) `RequirementPayload` adds `owning_department: string`; `buildFormData` appends it. (b) New `api/users.ts` with `createUserAccount(token, {username, password, role, department?})` → POST /api/admin/users/. (c) `stores/auth.ts` parses `department` from JWT payload into `user_department` localStorage key, exposes it, clears on logout. (Depends on: 10.4)
- [x] ID: 10.6: Frontend RequirementForm.vue - Add "Owning Department" el-select (IT / R&D) as the FIRST field in Basic Information section, required validation rule, participates in disabled/locked state automatically. (Depends on: 10.5)
- [x] ID: 10.7: Frontend UserDashboard.vue - Create-form initial data / edit-form prefill / submit payload include owning_department; table adds "Department" column (el-tag IT/R&D); filter bar adds Department select (clearable) wired into filteredRequests computed. (Depends on: 10.6)
- [x] ID: 10.8: Frontend AdminDashboard.vue - Header adds "User Management" button opening create-account el-dialog (username/password/role select; department select visible+required only when role=Admin; success → ElMessage + close; 400 → show backend error). Header shows current admin's department badge. Assess dialog shows Owning Department read-only. No department column in admin table (single-department data). (Depends on: 10.5)
- [x] ID: 10.9: Frontend verification - `npm run build` (incl. vue-tsc type check) passes. (Depends on: 10.7, 10.8)
