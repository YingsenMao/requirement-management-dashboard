<template>
  <div class="admin-dashboard">
    <el-card class="dashboard-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <span class="brand-icon">🏥</span>
            <span class="title-text">Yuwell Requirement Management Dashboard</span>
          </div>
          <el-button type="danger" plain @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            Logout
          </el-button>
        </div>
      </template>

      <el-table :data="requests" style="width: 100%" v-loading="loading" stripe border class="data-table">
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
        <el-table-column prop="priority_score" label="Priority Score" width="140" align="center">
          <template #default="scope">
            <span class="priority-score">{{ scope.row.priority_score !== null ? scope.row.priority_score : 'TBD' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="submission_date" label="Submission Date" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.submission_date) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" @click="handleAssess(scope.row)">Assess</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Assessment Dialog -->
    <el-dialog v-model="showAssessDialog" title="Assess Requirement" width="850" destroy-on-close class="assess-dialog">
      <div v-if="selectedRequest" class="dialog-content">
        <div class="section-title">Submitted Request Details</div>
        <el-descriptions :column="2" border size="default" class="request-details">
          <el-descriptions-item label="Name">{{ selectedRequest.name }}</el-descriptions-item>
          <el-descriptions-item label="Region">{{ formatRegion(selectedRequest.region) }}</el-descriptions-item>
          <el-descriptions-item label="Requirement Type">{{ formatType(selectedRequest.requirement_type) }}</el-descriptions-item>
          <el-descriptions-item label="Impacted Users">{{ formatUsers(selectedRequest.impacted_users) }}</el-descriptions-item>
          <el-descriptions-item label="Revenue Impact">{{ formatRevenue(selectedRequest.revenue_impact) }}</el-descriptions-item>
          <el-descriptions-item label="Deadline">{{ selectedRequest.deadline || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Summary" :span="2" class="summary-cell">{{ selectedRequest.summary }}</el-descriptions-item>
          <el-descriptions-item label="Supplementary Materials" :span="2">
            <div v-if="selectedRequest.supplementary_materials && selectedRequest.supplementary_materials.length" class="materials-list">
              <el-tag v-for="(mat, idx) in selectedRequest.supplementary_materials" :key="idx" type="info" effect="plain" class="material-tag">{{ mat }}</el-tag>
            </div>
            <span v-else class="text-muted">None provided</span>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">Admin Assessment</el-divider>
        <el-form :model="assessForm" label-width="120px" class="assess-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Workload">
                <el-select v-model="assessForm.workload" placeholder="Select workload" style="width: 100%;">
                  <el-option label="Pending" value="pending" />
                  <el-option label="Small" value="small" />
                  <el-option label="Medium" value="medium" />
                  <el-option label="Large" value="large" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Status">
                <el-select v-model="assessForm.status" placeholder="Select status" style="width: 100%;">
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { SwitchButton } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()

const requests = ref<any[]>([])
const loading = ref(false)
const showAssessDialog = ref(false)
const assessing = ref(false)
const assessingId = ref<number | null>(null)
const selectedRequest = ref<any>(null)

const assessForm = ref({
  workload: '',
  status: ''
})

const fetchRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/requests/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    requests.value = response.data
  } catch (error) {
    console.error('Failed to fetch requests', error)
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleAssess = (row: any) => {
  assessingId.value = row.id
  selectedRequest.value = row
  assessForm.value = {
    workload: row.workload,
    status: row.status
  }
  showAssessDialog.value = true
}

const submitAssess = async () => {
  if (assessingId.value === null) return
  assessing.value = true
  try {
    await axios.patch(`/api/admin/requests/${assessingId.value}/`, assessForm.value, {
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

const getWorkloadType = (workload: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    small: 'success',
    medium: 'warning',
    large: 'danger'
  }
  return map[workload] || 'info'
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

const formatUsers = (users: string) => {
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

onMounted(fetchRequests)
</script>

<style scoped>
.admin-dashboard {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
  box-sizing: border-box;
}

.dashboard-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  font-size: 24px;
}

.title-text {
  font-size: 20px;
  font-weight: 700;
  color: #1d2129;
  letter-spacing: 0.5px;
}

.data-table {
  border-radius: 8px;
  overflow: hidden;
}

.priority-score {
  font-weight: 700;
  color: #409EFF;
  font-size: 15px;
}

.dialog-content {
  padding: 0 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid #409EFF;
}

.request-details {
  margin-bottom: 24px;
}

.summary-cell {
  line-height: 1.6;
  color: #4e5969;
}

.materials-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.material-tag {
  margin: 0;
}

.text-muted {
  color: #86909c;
  font-style: italic;
}

.assess-form {
  background-color: #f7f8fa;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 12px;
}
</style>

<style>
/* Global reset to eliminate edge whitespace for this view */
html, body {
  margin: 0;
  padding: 0;
  background-color: #f5f7fa;
}
</style>
