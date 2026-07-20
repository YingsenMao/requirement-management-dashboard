<template>
  <div class="user-dashboard">
    <div class="header-actions">
      <h2 class="page-title">{{ isAdmin ? 'Admin Dashboard' : 'Requirements List' }}</h2>
      <div>
        <el-button v-if="!isAdmin" type="primary" @click="openCreateDialog">New Request</el-button>
      </div>
    </div>

    <div v-if="!isAdmin" class="filter-bar">
      <div class="filter-switch">
        <el-switch v-model="filterMyRequirements" active-text="My Requirements" />
      </div>
      <el-input
        v-model="filterSearch"
        placeholder="Search by name..."
        clearable
        class="filter-search"
        :prefix-icon="Search"
      />
      <el-select v-model="filterCountry" placeholder="Country" clearable filterable class="filter-select">
        <el-option v-for="c in COUNTRIES" :key="c" :label="c" :value="c" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="Status" clearable class="filter-select">
        <el-option label="Pending Review" value="pending_review" />
        <el-option label="Under Review" value="under_review" />
        <el-option label="Confirmed" value="confirmed" />
        <el-option label="In Development" value="in_development" />
        <el-option label="Completed" value="completed" />
        <el-option label="Rejected" value="rejected" />
      </el-select>
      <el-select v-model="filterSubmitter" placeholder="Submitter" clearable filterable class="filter-select">
        <el-option 
          v-for="user in submitters" 
          :key="user.id" 
          :label="user.username" 
          :value="user.username" 
        />
      </el-select>
    </div>
    
    <el-card class="table-card" shadow="never">
      <el-skeleton :loading="loading" animated :count="5">
        <template #template>
          <el-skeleton-item variant="h3" style="width: 100%; height: 40px; margin-bottom: 12px;" />
        </template>
        <template #default>
          <el-table :data="paginatedRequests" stripe border class="table-fill" @sort-change="handleSortChange">
            <template #empty>
              <div class="empty-state">
                <el-icon :size="48" color="var(--color-text-muted)"><Document /></el-icon>
                <p class="empty-text">No requirements found</p>
                <p class="empty-hint" v-if="!isAdmin">Click "New Request" to create your first requirement.</p>
              </div>
            </template>
      <el-table-column prop="name" label="Name" min-width="150" />
      <el-table-column prop="submitter_username" label="Submitter" width="120" />
      <el-table-column prop="country" label="Country" width="130" show-overflow-tooltip />
      <el-table-column prop="status" label="Status" width="140">
        <template #default="scope">
          <el-tooltip
            v-if="scope.row.status === 'rejected' && scope.row.reject_reason"
            :content="scope.row.reject_reason"
            placement="top"
            :show-after="200"
          >
            <el-tag :type="getStatusType(scope.row.status)" class="rejected-tag">
              {{ formatStatus(scope.row.status) }}
              <el-icon class="reject-icon"><Warning /></el-icon>
            </el-tag>
          </el-tooltip>
          <el-tag v-else :type="getStatusType(scope.row.status)">{{ formatStatus(scope.row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="workload" label="Workload" width="120">
        <template #default="scope">
          {{ formatWorkload(scope.row.workload) }}
        </template>
      </el-table-column>
      <el-table-column prop="priority_score" label="Priority Score" width="130" sortable="custom">
        <template #default="scope">
          {{ scope.row.priority_score !== null ? scope.row.priority_score : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column prop="submission_date" label="Submission Date" width="150" sortable="custom">
        <template #default="scope">
          {{ formatDate(scope.row.submission_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="estimated_completion_date" label="Est. Completion" width="140" sortable="custom">
        <template #default="scope">
          {{ scope.row.estimated_completion_date || 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="180" fixed="right">
        <template #default="scope">
          <template v-if="isAdmin">
            <el-button size="small" type="warning" plain @click="openAssessDialog(scope.row)">Assess</el-button>
          </template>
          <template v-else>
            <el-button v-if="isOwner(scope.row) && (scope.row.status === 'pending_review' || scope.row.status === 'rejected')" size="small" type="primary" plain @click="handleEdit(scope.row)">Edit</el-button>
            <el-button v-if="isOwner(scope.row) && scope.row.status === 'pending_review'" size="small" type="danger" plain @click="handleDelete(scope.row)">Delete</el-button>
            <el-button v-if="!isOwner(scope.row) || (scope.row.status !== 'pending_review' && scope.row.status !== 'rejected')" size="small" type="info" plain @click="handleView(scope.row)">View</el-button>
          </template>
        </template>
      </el-table-column>
      </el-table>
      <div v-if="filteredRequests.length > pageSize" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredRequests.length"
          layout="total, prev, pager, next"
          background
          small
        />
      </div>
        </template>
      </el-skeleton>
    </el-card>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="Create New Request" width="720">
      <RequirementForm
        ref="createFormComponent"
        v-model="createForm"
        v-model:upload-file-list="uploadFileList"
        @upload-change="handleCreateUploadChange"
        @upload-remove="handleCreateUploadRemove"
        @download="handleDownload"
      />
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Edit / View Dialog -->
    <el-dialog v-model="showEditDialog" :title="isFormLocked ? 'View Request' : 'Edit Request'" width="720">
      <el-alert v-if="isFormLocked" title="This request is locked and cannot be edited." type="warning" show-icon class="form-alert-bottom" />
      <el-alert v-if="!isFormLocked && editForm.status === 'rejected' && editForm.reject_reason" :title="'Reject Reason: ' + editForm.reject_reason" type="error" show-icon class="form-alert-bottom" />
      <RequirementForm
        ref="editFormComponent"
        v-model="editForm"
        :disabled="isFormLocked"
        v-model:upload-file-list="editUploadFileList"
        @upload-change="handleEditUploadChange"
        @upload-remove="handleEditUploadRemove"
        @upload-preview="handleEditPreview"
        @download="handleDownload"
      />
      <template #footer>
        <el-button @click="showEditDialog = false">Cancel</el-button>
        <el-button v-if="!isFormLocked" type="primary" @click="submitEdit" :loading="submitting">Save Changes</el-button>
      </template>
    </el-dialog>

    <!-- Admin Assess Dialog -->
    <el-dialog v-model="showAssessDialog" title="Assess Requirement" width="500">
      <el-form :model="assessForm" label-width="120px">
        <el-form-item label="Name">
          <el-input :model-value="assessForm.name" disabled />
        </el-form-item>
        <el-form-item label="Submitter">
          <el-input :model-value="assessForm.submitter_username" disabled />
        </el-form-item>
        <el-form-item label="Attachments">
          <div v-if="assessForm.attachments_list && assessForm.attachments_list.length" class="existing-attachments">
            <div v-for="att in assessForm.attachments_list" :key="att.id" class="attachment-item">
              <el-link type="primary" @click="handleDownload(att.id, getFileName(att.file))" :underline="false">
                {{ getFileName(att.file) }}
              </el-link>
            </div>
          </div>
          <span v-else class="text-muted">No attachments</span>
        </el-form-item>
        <el-form-item label="Workload" required>
          <el-select v-model="assessForm.workload" placeholder="Select workload" class="field-block">
            <el-option label="Small" value="small" />
            <el-option label="Medium" value="medium" />
            <el-option label="Large" value="large" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status" required>
          <el-select v-model="assessForm.status" placeholder="Select status" class="field-block">
            <el-option label="Pending Review" value="pending_review" />
            <el-option label="Under Review" value="under_review" />
            <el-option label="Confirmed" value="confirmed" />
            <el-option label="In Development" value="in_development" />
            <el-option label="Completed" value="completed" />
            <el-option label="Rejected" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="assessForm.status === 'rejected'" label="Reject Reason" required>
          <el-input v-model="assessForm.reject_reason" type="textarea" :rows="3" placeholder="Please provide a reason for rejection" />
        </el-form-item>
        <el-form-item label="Est. Completion">
          <el-date-picker v-model="assessForm.estimated_completion_date" type="date" placeholder="Select date" class="field-block" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssessDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitAssess" :loading="submitting">Save Assessment</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadUserFile } from 'element-plus'
import { createRequirementRequest, updateRequirementRequest, assessRequirementRequest } from '../api/requests'
import { Warning, Search, Document } from '@element-plus/icons-vue'
import { COUNTRIES } from '../constants/countries'
import RequirementForm from '../components/RequirementForm.vue'

const authStore = useAuthStore()

const requests = ref<any[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showAssessDialog = ref(false)
const submitting = ref(false)
const createFormComponent = ref()
const editFormComponent = ref()
const editingId = ref<number | null>(null)

const uploadFileList = ref<UploadUserFile[]>([])
const stagedFiles = ref<File[]>([])

const editUploadFileList = ref<UploadUserFile[]>([])
const editStagedFiles = ref<File[]>([])
const deletedAttachmentIds = ref<number[]>([])

const assessForm = ref<any>({})

// Filter states
const submitters = ref<{id: number, username: string}[]>([])
const filterMyRequirements = ref(false)
const filterSearch = ref('')
const filterCountry = ref('')
const filterStatus = ref('')
const filterSubmitter = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = 10

// Sorting
const sortProp = ref<string | null>(null)
const sortOrder = ref<string | null>(null)

const isAdmin = computed(() => {
  return authStore.role === 'admin'
})

const isOwner = (row: any) => {
  if (!row) return false
  const username = authStore.username
  return row.submitter_username === username
}

const filteredRequests = computed(() => {
  let result = requests.value
  if (!isAdmin.value) {
    if (filterMyRequirements.value) {
      result = result.filter(r => r.submitter_username === authStore.username)
    }
    if (filterSearch.value) {
      const query = filterSearch.value.toLowerCase()
      result = result.filter(r => r.name.toLowerCase().includes(query))
    }
    if (filterCountry.value) {
      result = result.filter(r => r.country === filterCountry.value)
    }
    if (filterStatus.value) {
      result = result.filter(r => r.status === filterStatus.value)
    }
    if (filterSubmitter.value) {
      result = result.filter(r => r.submitter_username === filterSubmitter.value)
    }
  }
  return result
})

const sortedRequests = computed(() => {
  if (!sortProp.value || !sortOrder.value) return filteredRequests.value
  const prop = sortProp.value
  const asc = sortOrder.value === 'ascending' ? 1 : -1
  return [...filteredRequests.value].sort((a: any, b: any) => {
    const va = a[prop]
    const vb = b[prop]
    if (va === null || va === undefined) return 1
    if (vb === null || vb === undefined) return -1
    if (va < vb) return -1 * asc
    if (va > vb) return 1 * asc
    return 0
  })
})

const paginatedRequests = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedRequests.value.slice(start, start + pageSize)
})

const createForm = ref({
  name: '',
  summary: '',
    country: '',
  requirement_type: '',
  impacted_users: '',
  supplementary_materials: [] as string[],
  revenue_impact: '',
  deadline: '',
  urgency: 'medium'
})

const editForm = ref<any>({})

const isFormLocked = computed(() => {
  if (!editForm.value || !editForm.value.status) return true
  if (editForm.value.status !== 'pending_review' && editForm.value.status !== 'rejected') return true
  if (!isOwner(editForm.value)) return true
  return false
})

const handleCreateUploadChange = (_file: UploadUserFile, uploadFiles: UploadUserFile[]) => {
  stagedFiles.value = uploadFiles.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
}

const handleCreateUploadRemove = (_file: UploadUserFile, uploadFiles: UploadUserFile[]) => {
  stagedFiles.value = uploadFiles.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
}

const handleEditUploadChange = (_file: UploadUserFile, uploadFiles: UploadUserFile[]) => {
  editStagedFiles.value = uploadFiles.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
}

const handleEditUploadRemove = (file: UploadUserFile, uploadFiles: UploadUserFile[]) => {
  if ((file as any).id) {
    deletedAttachmentIds.value.push((file as any).id)
  }
  editStagedFiles.value = uploadFiles.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
}

const getFileName = (filePath: string) => {
  if (!filePath) return 'attachment'
  return filePath.split('/').pop() || 'attachment'
}

const handleDownload = async (attachmentId: number, fileName: string) => {
  try {
    const response = await axios.get(`/api/attachments/${attachmentId}/download/`, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed', error)
    ElMessage.error('Failed to download attachment')
  }
}

const handleEditPreview = (file: UploadUserFile) => {
  if ((file as any).id) {
    handleDownload((file as any).id, file.name)
  }
}

const fetchRequests = async () => {
  loading.value = true
  try {
    const url = isAdmin.value ? '/api/admin/requests/' : '/api/requests/'
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    const data = response.data
    
    data.sort((a: any, b: any) => {
      if (a.status === 'completed' && b.status !== 'completed') return 1
      if (a.status !== 'completed' && b.status === 'completed') return -1
      
      if (a.priority_score === null && b.priority_score === null) return 0
      if (a.priority_score === null) return 1
      if (b.priority_score === null) return -1
      return b.priority_score - a.priority_score
    })
    
    requests.value = data
  } catch (error) {
    console.error('Failed to fetch requests', error)
  } finally {
    loading.value = false
  }
}

const fetchSubmitters = async () => {
  try {
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    submitters.value = response.data
  } catch (error) {
    console.error('Failed to fetch submitters', error)
  }
}

const openCreateDialog = () => {
  createForm.value = {
    name: '',
    summary: '',
    country: '',
    requirement_type: '',
    impacted_users: '',
    supplementary_materials: [],
    revenue_impact: '',
    deadline: '',
    urgency: 'medium'
  }
  uploadFileList.value = []
  stagedFiles.value = []
  showCreateDialog.value = true
}

const submitCreate = async () => {
  const formRef = createFormComponent.value?.formRef as FormInstance | undefined
  if (!formRef) return
  await formRef.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          ...createForm.value,
          attachments: stagedFiles.value
        }
        await createRequirementRequest(authStore.token || '', payload)
        showCreateDialog.value = false
        fetchRequests()
      } catch (error) {
        console.error('Failed to create request', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleEdit = (row: any) => {
  editingId.value = row.id
  editForm.value = { ...row }
  
  // Map existing attachments to el-upload file list format so they are visible and downloadable
  const existingFiles = (row.attachments_list || []).map((att: any) => ({
    name: getFileName(att.file),
    // Do not set url to prevent default browser navigation
    id: att.id,
    status: 'success'
  }))
  
  editUploadFileList.value = [...existingFiles]
  editStagedFiles.value = []
  deletedAttachmentIds.value = []
  showEditDialog.value = true
}

const handleView = (row: any) => {
  handleEdit(row)
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this requirement?', 'Warning', {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    })
    await axios.delete(`/api/requests/${row.id}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    ElMessage.success('Deleted successfully')
    fetchRequests()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete', error)
      ElMessage.error('Failed to delete requirement')
    }
  }
}

const openAssessDialog = (row: any) => {
  assessForm.value = { ...row }
  showAssessDialog.value = true
}

const submitAssess = async () => {
  if (!assessForm.value.workload || !assessForm.value.status) {
    ElMessage.warning('Please select both workload and status')
    return
  }
  if (assessForm.value.status === 'rejected' && !assessForm.value.reject_reason?.trim()) {
    ElMessage.warning('Please provide a reject reason')
    return
  }
  submitting.value = true
  try {
    const payload: any = {
      workload: assessForm.value.workload,
      status: assessForm.value.status,
      estimated_completion_date: assessForm.value.estimated_completion_date || null
    }
    if (assessForm.value.status === 'rejected') {
      payload.reject_reason = assessForm.value.reject_reason
    }
    await assessRequirementRequest(authStore.token || '', assessForm.value.id, payload)
    ElMessage.success('Assessment saved')
    showAssessDialog.value = false
    fetchRequests()
  } catch (error) {
    console.error('Failed to assess', error)
    ElMessage.error('Failed to save assessment')
  } finally {
    submitting.value = false
  }
}

const submitEdit = async () => {
  const formRef = editFormComponent.value?.formRef as FormInstance | undefined
  if (!formRef || editingId.value === null) return
  const currentEditingId = editingId.value
  await formRef.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          name: editForm.value.name,
          summary: editForm.value.summary,
          country: editForm.value.country,
          requirement_type: editForm.value.requirement_type,
          impacted_users: editForm.value.impacted_users,
          supplementary_materials: editForm.value.supplementary_materials,
          revenue_impact: editForm.value.revenue_impact,
          deadline: editForm.value.deadline,
          urgency: editForm.value.urgency,
          attachments: editStagedFiles.value,
          deleted_attachment_ids: deletedAttachmentIds.value
        }
        await updateRequirementRequest(authStore.token || '', currentEditingId, payload)
        showEditDialog.value = false
        fetchRequests()
      } catch (error) {
        console.error('Failed to update request', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    pending_review: 'Pending Review',
    under_review: 'Under Review',
    confirmed: 'Confirmed',
    in_development: 'In Development',
    completed: 'Completed',
    rejected: 'Rejected'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending_review: 'info',
    under_review: 'warning',
    confirmed: 'primary',
    in_development: 'warning',
    completed: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

const formatWorkload = (workload: string) => {
  const map: Record<string, string> = {
    pending: 'Pending',
    small: 'Small',
    medium: 'Medium',
    large: 'Large'
  }
  return map[workload] || workload
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-CA')
}

const handleSortChange = ({ prop, order }: { prop: string | null; order: string | null }) => {
  sortProp.value = prop
  sortOrder.value = order
  currentPage.value = 1
}

onMounted(() => {
  fetchRequests()
  fetchSubmitters()
})
</script>

<style scoped>
.table-fill {
  width: 100%;
}

.field-block {
  width: 100%;
}

.form-alert-bottom {
  margin-bottom: var(--space-3);
}

.user-dashboard {
  padding: var(--space-5);
  background-color: var(--color-surface-page);
  min-height: 100%;
  box-sizing: border-box;
}

.page-title {
  margin: 0;
  font-size: var(--font-size-title-page);
  font-weight: var(--font-weight-title);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight-title);
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.filter-bar {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
}

.filter-switch {
  flex-shrink: 0;
}

.filter-search {
  width: 220px;
}

.filter-select {
  width: 180px;
}

.table-card {
  border-radius: var(--radius-md);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-3);
}

.empty-state {
  padding: var(--space-6) 0;
  text-align: center;
}

.empty-text {
  margin: var(--space-2) 0 var(--space-1);
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

.empty-hint {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-muted);
}

.existing-attachments {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.attachment-item {
  display: flex;
  align-items: center;
}

.text-muted {
  color: var(--color-text-muted);
  font-size: 12px;
}

.rejected-tag {
  cursor: pointer;
}

.reject-icon {
  margin-left: 4px;
  vertical-align: middle;
}
</style>
