<template>
  <div class="admin-dashboard">
    <el-card class="dashboard-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <span class="title-text">Requirement Management Dashboard</span>
          </div>
        </div>
      </template>

      <div class="stats-row">
        <div class="stat-card stat-total">
          <div class="stat-icon-wrap">
            <el-icon :size="22"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ requests.length }}</span>
            <span class="stat-label">Total</span>
          </div>
        </div>
        <div class="stat-card stat-pending">
          <div class="stat-icon-wrap">
            <el-icon :size="22"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ countByStatus('pending_review') }}</span>
            <span class="stat-label">Pending Review</span>
          </div>
        </div>
        <div class="stat-card stat-confirmed">
          <div class="stat-icon-wrap">
            <el-icon :size="22"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ countByStatus('confirmed') }}</span>
            <span class="stat-label">Confirmed</span>
          </div>
        </div>
        <div class="stat-card stat-rejected">
          <div class="stat-icon-wrap">
            <el-icon :size="22"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ countByStatus('rejected') }}</span>
            <span class="stat-label">Rejected</span>
          </div>
        </div>
      </div>

      <div class="filter-bar">
        <el-input
          v-model="filterSearch"
          placeholder="Search by name..."
          clearable
          class="filter-search"
          :prefix-icon="Search"
        />
        <el-select v-model="filterStatus" placeholder="Status" clearable class="filter-select">
          <el-option label="Pending Review" value="pending_review" />
          <el-option label="Under Review" value="under_review" />
          <el-option label="Confirmed" value="confirmed" />
          <el-option label="In Development" value="in_development" />
          <el-option label="Completed" value="completed" />
          <el-option label="Rejected" value="rejected" />
        </el-select>
        <el-select v-model="filterCountry" placeholder="Country" clearable filterable class="filter-select">
          <el-option v-for="c in COUNTRIES" :key="c" :label="c" :value="c" />
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

      <el-skeleton :loading="loading" animated :count="5">
        <template #template>
          <el-skeleton-item variant="h3" style="width: 100%; height: 40px; margin-bottom: 12px;" />
        </template>
        <template #default>
          <el-table :data="paginatedRequests" stripe border class="data-table table-fill">
            <template #empty>
              <div class="empty-state">
                <el-icon :size="48" color="var(--color-text-muted)"><Document /></el-icon>
                <p class="empty-text">No requirements found</p>
              </div>
            </template>
        <el-table-column prop="name" label="Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="submitter_username" label="Submitter" width="140" />
        <el-table-column prop="status" label="Status" width="150">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="light" round>{{ formatStatus(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="workload" label="Workload" width="130">
          <template #default="scope">
            <el-tag :type="getWorkloadType(scope.row.workload)" effect="plain" round>{{ formatWorkload(scope.row.workload) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority_score" label="Priority Score" width="140" align="center" sortable :sort-method="sortPriorityScore">
          <template #default="scope">
            <span class="priority-score">{{ scope.row.priority_score !== null ? scope.row.priority_score : 'N/A' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="submission_date" label="Submission Date" width="160" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.submission_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="estimated_completion_date" label="Est. Completion" width="150">
          <template #default="scope">
            {{ scope.row.estimated_completion_date || 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" @click="handleAssess(scope.row)">Assess</el-button>
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

    <!-- Assessment Dialog -->
    <el-dialog v-model="showAssessDialog" title="Assess Requirement" width="780" destroy-on-close class="assess-dialog">
      <div v-if="selectedRequest" class="dialog-content">
        <div class="section-title">Submitted Request Details</div>
        <el-descriptions :column="2" border size="default" class="request-details">
          <el-descriptions-item label="Name">{{ selectedRequest.name }}</el-descriptions-item>
          <el-descriptions-item label="Country">{{ selectedRequest.country }}</el-descriptions-item>
          <el-descriptions-item label="Requirement Type">{{ formatType(selectedRequest.requirement_type) }}</el-descriptions-item>
          <el-descriptions-item label="Impacted Users">{{ formatUsers(selectedRequest.impacted_users) }}</el-descriptions-item>
          <el-descriptions-item label="Revenue Impact">{{ formatRevenue(selectedRequest.revenue_impact) }}</el-descriptions-item>
          <el-descriptions-item label="Deadline">{{ selectedRequest.deadline || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Urgency">
            <el-tag :type="getUrgencyType(selectedRequest.urgency)" effect="light" round>{{ formatUrgency(selectedRequest.urgency) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Summary" :span="2" class="summary-cell">{{ selectedRequest.summary }}</el-descriptions-item>
          <el-descriptions-item label="Supplementary Materials" :span="2">
            <div v-if="selectedRequest.supplementary_materials && selectedRequest.supplementary_materials.length" class="materials-list">
              <el-tag v-for="(mat, idx) in selectedRequest.supplementary_materials" :key="idx" type="info" effect="plain" class="material-tag">{{ mat }}</el-tag>
            </div>
            <span v-else class="text-muted">None provided</span>
          </el-descriptions-item>
          <el-descriptions-item label="Attachments" :span="2">
            <div v-if="selectedRequest.attachments_list && selectedRequest.attachments_list.length" class="materials-list attachments-list">
              <el-link 
                v-for="att in selectedRequest.attachments_list" 
                :key="att.id" 
                type="primary" 
                @click="handleDownload(att.id, getFileName(att.file))" 
                :underline="false"
              >
                {{ getFileName(att.file) }}
              </el-link>
            </div>
            <span v-else class="text-muted">No attachments</span>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">Admin Assessment</el-divider>
        <el-form :model="assessForm" label-width="120px" class="assess-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Workload">
                <el-select v-model="assessForm.workload" placeholder="Select workload" class="field-block">
                  <el-option label="Pending" value="pending" />
                  <el-option label="Small" value="small" />
                  <el-option label="Medium" value="medium" />
                  <el-option label="Large" value="large" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Status">
                <el-select v-model="assessForm.status" placeholder="Select status" class="field-block">
                  <el-option label="Pending Review" value="pending_review" />
                  <el-option label="Under Review" value="under_review" />
                  <el-option label="Confirmed" value="confirmed" />
                  <el-option label="In Development" value="in_development" />
                  <el-option label="Completed" value="completed" />
                  <el-option label="Rejected" value="rejected" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item v-if="assessForm.status === 'rejected'" label="Reject Reason">
            <el-input v-model="assessForm.reject_reason" type="textarea" :rows="3" placeholder="Please provide a reason for rejection" />
          </el-form-item>
          <el-form-item label="Est. Completion">
            <el-date-picker v-model="assessForm.estimated_completion_date" type="date" placeholder="Select date" class="field-block" value-format="YYYY-MM-DD" clearable />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAssessDialog = false">Cancel</el-button>
          <el-button type="primary" @click="submitAssess" :loading="assessing">Save Changes</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { Search, Document, Tickets, Clock, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { COUNTRIES } from '../constants/countries'

const authStore = useAuthStore()

const requests = ref<any[]>([])
const loading = ref(false)
const showAssessDialog = ref(false)
const assessing = ref(false)
const assessingId = ref<number | null>(null)
const selectedRequest = ref<any>(null)

const assessForm = ref({
  workload: '',
  status: '',
  reject_reason: '' as string | null,
  estimated_completion_date: null as string | null
})

// Filter states
const submitters = ref<{id: number, username: string}[]>([])
const filterSearch = ref('')
const filterStatus = ref('')
const filterCountry = ref('')
const filterSubmitter = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = 20

const filteredRequests = computed(() => {
  let result = requests.value
  if (filterSearch.value) {
    const query = filterSearch.value.toLowerCase()
    result = result.filter(r => r.name.toLowerCase().includes(query))
  }
  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }
  if (filterCountry.value) {
    result = result.filter(r => r.country === filterCountry.value)
  }
  if (filterSubmitter.value) {
    result = result.filter(r => r.submitter_username === filterSubmitter.value)
  }
  return result
})

const paginatedRequests = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRequests.value.slice(start, start + pageSize)
})

const countByStatus = (status: string) => {
  return requests.value.filter(r => r.status === status).length
}

const fetchRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/requests/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    requests.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch requests', error)
  } finally {
    loading.value = false
  }
}

const handleAssess = (row: any) => {
  assessingId.value = row.id
  selectedRequest.value = row
  assessForm.value = {
    workload: row.workload,
    status: row.status,
    reject_reason: row.reject_reason || '',
    estimated_completion_date: row.estimated_completion_date || null
  }
  showAssessDialog.value = true
}

const submitAssess = async () => {
  if (assessingId.value === null) return
  if (assessForm.value.status === 'rejected' && !assessForm.value.reject_reason?.trim()) {
    ElMessage.warning('Please provide a reject reason')
    return
  }
  assessing.value = true
  try {
    const payload: any = {
      workload: assessForm.value.workload,
      status: assessForm.value.status,
      estimated_completion_date: assessForm.value.estimated_completion_date || null
    }
    if (assessForm.value.status === 'rejected') {
      payload.reject_reason = assessForm.value.reject_reason
    }
    await axios.patch(`/api/admin/requests/${assessingId.value}/`, payload, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    showAssessDialog.value = false
    fetchRequests()
  } catch (error) {
    console.error('Failed to assess request', error)
  } finally {
    assessing.value = false
  }
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

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-CA')
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

const getWorkloadType = (workload: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    small: 'success',
    medium: 'warning',
    large: 'danger'
  }
  return map[workload] || 'info'
}

const sortPriorityScore = (a: any, b: any) => {
  const scoreA = a.priority_score ?? -1
  const scoreB = b.priority_score ?? -1
  return scoreA - scoreB
}

const formatType = (type: string) => {
  const map: Record<string, string> = {
    regulatory: 'Regulatory Compliance',
    security: 'Security Vulnerability',
    revenue: 'Revenue Growth',
    cost: 'Cost Reduction',
    bug: 'Bug',
    optimization: 'Feature Optimization'
  }
  return map[type] || type
}

const formatUsers = (users: string | null | undefined) => {
  if (!users) return 'N/A'
  const map: Record<string, string> = {
    '<100': '<100',
    '100-500': '100-500',
    '500-1000': '500-1000',
    '>1000': '>1000'
  }
  return map[users] || users
}

const formatRevenue = (rev: string | null) => {
  if (!rev) return 'N/A'
  const map: Record<string, string> = {
    '<50k': '<50k',
    '50k-300k': '50k-300k',
    '300k-1M': '300k-1M',
    '>1M': '>1M'
  }
  return map[rev] || rev
}

const formatUrgency = (urgency: string | null) => {
  if (!urgency) return 'N/A'
  const map: Record<string, string> = {
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return map[urgency] || urgency
}

const getUrgencyType = (urgency: string | null) => {
  const map: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[urgency || ''] || 'info'
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

.admin-dashboard {
  padding: var(--space-5);
  background-color: var(--color-surface-page);
  min-height: 100vh;
  box-sizing: border-box;
}

.dashboard-card {
  border-radius: var(--radius-lg);
  border: var(--border-width-card) solid var(--color-border-default);
  box-shadow: var(--shadow-card);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-1) 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-icon {
  font-size: var(--font-size-brand-icon);
}

.title-text {
  font-size: var(--font-size-title-page);
  font-weight: var(--font-weight-title);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight-title);
}

.data-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.priority-score {
  font-weight: var(--font-weight-title);
  color: var(--color-accent);
  font-size: var(--font-size-accent);
}

.dialog-content {
  padding: 0 var(--space-1);
}

.section-title {
  font-size: var(--font-size-section);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
  padding-left: var(--space-2);
  border-left: var(--section-accent-bar-width) solid var(--color-accent);
}

.request-details {
  margin-bottom: var(--space-5);
}

.summary-cell {
  line-height: var(--line-height-body);
  color: var(--color-text-secondary);
}

.materials-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.attachments-list {
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
}

.material-tag {
  margin: 0;
}

.text-muted {
  color: var(--color-text-muted);
  font-style: italic;
}

.assess-form {
  background-color: var(--color-surface-form);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: var(--border-width-card) solid var(--color-border-subtle);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  padding-top: var(--space-2);
}

.filter-bar {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-default);
  background: var(--color-surface-card);
  transition: box-shadow 0.2s ease;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-total .stat-icon-wrap {
  background: #eff6ff;
  color: #2563eb;
}

.stat-pending .stat-icon-wrap {
  background: #fefce8;
  color: #ca8a04;
}

.stat-confirmed .stat-icon-wrap {
  background: #f0fdf4;
  color: #16a34a;
}

.stat-rejected .stat-icon-wrap {
  background: #fef2f2;
  color: #dc2626;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: var(--font-weight-title);
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.filter-search {
  width: 220px;
}

.filter-select {
  width: 180px;
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
  margin: var(--space-2) 0 0;
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}
</style>
