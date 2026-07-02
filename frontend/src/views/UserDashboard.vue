<template>
  <div class="user-dashboard">
    <div class="header-actions">
      <h2 class="page-title">{{ isAdmin ? 'Admin Dashboard' : 'Requirements List' }}</h2>
      <div>
        <el-button v-if="!isAdmin" type="primary" @click="openCreateDialog">New Request</el-button>
        <el-button type="danger" @click="handleLogout">Logout</el-button>
      </div>
    </div>
    
    <el-table :data="requests" v-loading="loading" stripe class="table-fill">
      <el-table-column prop="name" label="Name" min-width="150" />
      <el-table-column prop="submitter_username" label="Submitter" width="120" />
      <el-table-column prop="region" label="Region" width="130">
        <template #default="scope">
          {{ formatRegion(scope.row.region) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="Status" width="140">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">{{ formatStatus(scope.row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="workload" label="Workload" width="120">
        <template #default="scope">
          {{ formatWorkload(scope.row.workload) }}
        </template>
      </el-table-column>
      <el-table-column prop="priority_score" label="Priority Score" width="130">
        <template #default="scope">
          {{ scope.row.priority_score !== null ? scope.row.priority_score : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column prop="submission_date" label="Submission Date" width="150">
        <template #default="scope">
          {{ new Date(scope.row.submission_date).toLocaleDateString() }}
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="220" fixed="right">
        <template #default="scope">
          <template v-if="isAdmin">
            <el-button size="small" type="warning" plain @click="openAssessDialog(scope.row)">Assess</el-button>
          </template>
          <template v-else>
            <el-button v-if="isOwner(scope.row) && scope.row.status === 'pending_review'" size="small" type="primary" plain @click="handleEdit(scope.row)">Edit</el-button>
            <el-button v-if="isOwner(scope.row) && scope.row.status === 'pending_review'" size="small" type="danger" plain @click="handleDelete(scope.row)">Delete</el-button>
            <el-button v-if="!isOwner(scope.row) || scope.row.status !== 'pending_review'" size="small" type="info" plain @click="handleView(scope.row)">View</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="Create New Request" width="600">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="160px">
        <el-form-item label="Name" prop="name">
          <el-input v-model="createForm.name" placeholder="Enter requirement name" />
        </el-form-item>
        <el-form-item label="Summary" prop="summary">
          <el-input v-model="createForm.summary" type="textarea" :rows="3" placeholder="Enter summary" />
        </el-form-item>
        <el-form-item label="Region" prop="region">
          <el-select v-model="createForm.region" placeholder="Select region" class="field-block">
            <el-option label="China" value="china" />
            <el-option label="Europe" value="europe" />
            <el-option label="South America" value="south_america" />
            <el-option label="North America" value="north_america" />
            <el-option label="Asia" value="asia" />
          </el-select>
        </el-form-item>
        <el-form-item label="Requirement Type" prop="requirement_type">
          <el-select v-model="createForm.requirement_type" placeholder="Select type" class="field-block">
            <el-option label="Regulatory Compliance" value="regulatory" />
            <el-option label="Security Vulnerability" value="security" />
            <el-option label="Revenue Growth" value="revenue" />
            <el-option label="Cost Reduction" value="cost" />
            <el-option label="Bug" value="bug" />
            <el-option label="Feature Optimization" value="optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="Impacted Users" prop="impacted_users">
          <el-select v-model="createForm.impacted_users" placeholder="Select impacted users" class="field-block">
            <el-option label="<100" value="<100" />
            <el-option label="100-500" value="100-500" />
            <el-option label="500-1000" value="500-1000" />
            <el-option label=">1000" value=">1000" />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplementary Materials">
          <el-select v-model="createForm.supplementary_materials" multiple placeholder="Select materials" class="field-block">
            <el-option label="User Research" value="user_research" />
            <el-option label="Data Report" value="data_report" />
            <el-option label="Competitor Analysis" value="competitor_analysis" />
            <el-option label="Technical Solution" value="technical_solution" />
          </el-select>
        </el-form-item>
        <el-form-item label="Attachments">
          <el-upload
            v-model:file-list="uploadFileList"
            :auto-upload="false"
            :on-change="handleChange"
            :on-remove="handleRemove"
            :on-exceed="handleExceed"
            :limit="3"
            multiple
          >
            <el-button type="primary" plain>Select Files</el-button>
            <template #tip>
              <div class="el-upload__tip">
                Max 3 files, max 5MB per file. Allowed: .pdf, .docx, .xlsx, .png, .jpg
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="Revenue Impact">
          <el-select v-model="createForm.revenue_impact" placeholder="Select revenue impact" class="field-block" clearable>
            <el-option label="<50k" value="<50k" />
            <el-option label="50k-300k" value="50k-300k" />
            <el-option label="300k-1M" value="300k-1M" />
            <el-option label=">1M" value=">1M" />
          </el-select>
        </el-form-item>
        <el-form-item label="Deadline">
          <el-date-picker v-model="createForm.deadline" type="date" placeholder="Select deadline" class="field-block" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Edit / View Dialog -->
    <el-dialog v-model="showEditDialog" :title="isFormLocked ? 'View Request' : 'Edit Request'" width="600">
      <el-alert v-if="isFormLocked" title="This request is locked and cannot be edited." type="warning" show-icon class="form-alert-bottom" />
      <el-form :model="editForm" :rules="createRules" ref="editFormRef" label-width="160px" :disabled="isFormLocked">
        <el-form-item label="Name" prop="name">
          <el-input v-model="editForm.name" placeholder="Enter requirement name" />
        </el-form-item>
        <el-form-item label="Summary" prop="summary">
          <el-input v-model="editForm.summary" type="textarea" :rows="3" placeholder="Enter summary" />
        </el-form-item>
        <el-form-item label="Region" prop="region">
          <el-select v-model="editForm.region" placeholder="Select region" class="field-block">
            <el-option label="China" value="china" />
            <el-option label="Europe" value="europe" />
            <el-option label="South America" value="south_america" />
            <el-option label="North America" value="north_america" />
            <el-option label="Asia" value="asia" />
          </el-select>
        </el-form-item>
        <el-form-item label="Requirement Type" prop="requirement_type">
          <el-select v-model="editForm.requirement_type" placeholder="Select type" class="field-block">
            <el-option label="Regulatory Compliance" value="regulatory" />
            <el-option label="Security Vulnerability" value="security" />
            <el-option label="Revenue Growth" value="revenue" />
            <el-option label="Cost Reduction" value="cost" />
            <el-option label="Bug" value="bug" />
            <el-option label="Feature Optimization" value="optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="Impacted Users" prop="impacted_users">
          <el-select v-model="editForm.impacted_users" placeholder="Select impacted users" class="field-block">
            <el-option label="<100" value="<100" />
            <el-option label="100-500" value="100-500" />
            <el-option label="500-1000" value="500-1000" />
            <el-option label=">1000" value=">1000" />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplementary Materials">
          <el-select v-model="editForm.supplementary_materials" multiple placeholder="Select materials" class="field-block">
            <el-option label="User Research" value="user_research" />
            <el-option label="Data Report" value="data_report" />
            <el-option label="Competitor Analysis" value="competitor_analysis" />
            <el-option label="Technical Solution" value="technical_solution" />
          </el-select>
        </el-form-item>
        <el-form-item label="Attachments">
          <template v-if="isFormLocked">
            <div v-if="editForm.attachments_list && editForm.attachments_list.length" class="existing-attachments">
              <div v-for="att in editForm.attachments_list" :key="att.id" class="attachment-item">
                <el-link type="primary" @click="handleDownload(att.id, getFileName(att.file))" :underline="false">
                  {{ getFileName(att.file) }}
                </el-link>
              </div>
            </div>
            <span v-else class="text-muted">No attachments</span>
          </template>
          <template v-else>
            <el-upload
              v-model:file-list="editUploadFileList"
              :auto-upload="false"
              :on-change="handleEditChange"
              :on-remove="handleEditRemove"
              :on-exceed="handleExceed"
              :limit="3"
              multiple
            >
              <el-button type="primary" plain>Select Files</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  Max 3 files, max 5MB per file. Allowed: .pdf, .docx, .xlsx, .png, .jpg
                </div>
              </template>
            </el-upload>
          </template>
        </el-form-item>
        <el-form-item label="Revenue Impact">
          <el-select v-model="editForm.revenue_impact" placeholder="Select revenue impact" class="field-block" clearable>
            <el-option label="<50k" value="<50k" />
            <el-option label="50k-300k" value="50k-300k" />
            <el-option label="300k-1M" value="300k-1M" />
            <el-option label=">1M" value=">1M" />
          </el-select>
        </el-form-item>
        <el-form-item label="Deadline">
          <el-date-picker v-model="editForm.deadline" type="date" placeholder="Select deadline" class="field-block" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
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
      </el-form>
      <template #footer>
        <el-button @click="showAssessDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitAssess" :loading="submitting">Save Assessment</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'
import { createRequirementRequest, updateRequirementRequest, assessRequirementRequest } from '../api/requests'

const authStore = useAuthStore()
const router = useRouter()

const requests = ref<any[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showAssessDialog = ref(false)
const submitting = ref(false)
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const editingId = ref<number | null>(null)

const uploadFileList = ref<UploadUserFile[]>([])
const stagedFiles = ref<File[]>([])

const editUploadFileList = ref<UploadUserFile[]>([])
const editStagedFiles = ref<File[]>([])
const deletedAttachmentIds = ref<number[]>([])

const assessForm = ref<any>({})

const isAdmin = computed(() => {
  return authStore.role === 'admin'
})

const isOwner = (row: any) => {
  if (!row) return false
  const username = authStore.username
  return row.submitter_username === username
}

const createForm = ref({
  name: '',
  summary: '',
  region: '',
  requirement_type: '',
  impacted_users: '',
  supplementary_materials: [] as string[],
  revenue_impact: '',
  deadline: ''
})

const editForm = ref<any>({})

const isFormLocked = computed(() => {
  if (!editForm.value || !editForm.value.status) return true
  if (editForm.value.status !== 'pending_review') return true
  if (!isOwner(editForm.value)) return true
  return false
})

const createRules = ref<FormRules>({
  name: [{ required: true, message: 'Please enter requirement name', trigger: 'blur' }],
  summary: [{ required: true, message: 'Please enter summary', trigger: 'blur' }],
  region: [{ required: true, message: 'Please select region', trigger: 'change' }],
  requirement_type: [{ required: true, message: 'Please select type', trigger: 'change' }],
  impacted_users: [{ required: true, message: 'Please select impacted users', trigger: 'change' }]
})

const validateUpload = (file: UploadUserFile, uploadFiles: UploadUserFile[], fileListRef: Ref<UploadUserFile[]>, stagedFilesRef: Ref<File[]>) => {
  const allowedExtensions = ['.pdf', '.docx', '.xlsx', '.png', '.jpg']
  const fileName = file.name.toLowerCase()
  const isValidExt = allowedExtensions.some(ext => fileName.endsWith(ext))
  
  if (!isValidExt) {
    ElMessage.error('Only .pdf, .docx, .xlsx, .png, .jpg files are allowed.')
    fileListRef.value = fileListRef.value.filter(f => f.uid !== file.uid)
    stagedFilesRef.value = fileListRef.value.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
    return
  }
  
  const fileSizeMB = (file.raw?.size || 0) / 1024 / 1024
  if (fileSizeMB > 5) {
    ElMessage.error(`File "${file.name}" exceeds the 5MB limit.`)
    fileListRef.value = fileListRef.value.filter(f => f.uid !== file.uid)
    stagedFilesRef.value = fileListRef.value.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
    return
  }
  
  stagedFilesRef.value = uploadFiles.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
}

const handleChange: UploadProps['onChange'] = (file, uploadFiles) => {
  validateUpload(file, uploadFiles, uploadFileList, stagedFiles)
}

const handleEditChange: UploadProps['onChange'] = (file, uploadFiles) => {
  validateUpload(file, uploadFiles, editUploadFileList, editStagedFiles)
}

const handleRemove: UploadProps['onRemove'] = (_file, uploadFiles) => {
  stagedFiles.value = uploadFiles.map(f => f.raw as File).filter(Boolean)
}

const handleEditRemove: UploadProps['onRemove'] = (file, uploadFiles) => {
  // If the removed file is an existing file (has an ID), track it for backend deletion
  if ((file as any).id) {
    deletedAttachmentIds.value.push((file as any).id)
  }
  editStagedFiles.value = uploadFiles.filter(f => !(f as any).id).map(f => f.raw as File).filter(Boolean)
}

const handleExceed: UploadProps['onExceed'] = () => {
  ElMessage.error('Maximum 3 files allowed.')
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

const fetchRequests = async () => {
  loading.value = true
  try {
    const url = isAdmin.value ? '/api/admin/requests/' : '/api/requests/'
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    const data = response.data
    
    // Frontend sort guarantee: Priority Score descending, N/A (null) at the bottom
    data.sort((a: any, b: any) => {
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

const openCreateDialog = () => {
  createForm.value = {
    name: '',
    summary: '',
    region: '',
    requirement_type: '',
    impacted_users: '',
    supplementary_materials: [],
    revenue_impact: '',
    deadline: ''
  }
  uploadFileList.value = []
  stagedFiles.value = []
  showCreateDialog.value = true
}

const submitCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
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
    url: att.file,
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
  submitting.value = true
  try {
    await assessRequirementRequest(authStore.token || '', assessForm.value.id, {
      workload: assessForm.value.workload,
      status: assessForm.value.status
    })
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
  if (!editFormRef.value || editingId.value === null) return
  const currentEditingId = editingId.value
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          name: editForm.value.name,
          summary: editForm.value.summary,
          region: editForm.value.region,
          requirement_type: editForm.value.requirement_type,
          impacted_users: editForm.value.impacted_users,
          supplementary_materials: editForm.value.supplementary_materials,
          revenue_impact: editForm.value.revenue_impact,
          deadline: editForm.value.deadline,
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

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const formatRegion = (region: string) => {
  const map: Record<string, string> = {
    china: 'China',
    europe: 'Europe',
    south_america: 'South America',
    north_america: 'North America',
    asia: 'Asia'
  }
  return map[region] || region
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
    in_development: '',
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

onMounted(fetchRequests)
</script>

<style scoped>
.table-fill {
  width: 100%;
}

.field-block {
  width: 100%;
}

.form-alert-bottom {
  margin-bottom: var(--space-header);
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

.existing-attachments {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
}

.text-muted {
  color: #909399;
  font-size: 12px;
}
</style>
