<template>
  <div class="user-dashboard">
    <div class="header-actions">
      <h2>My Requirements</h2>
      <div>
        <el-button type="primary" @click="openCreateDialog">New Request</el-button>
        <el-button type="danger" @click="handleLogout">Logout</el-button>
      </div>
    </div>
    
    <el-table :data="requests" style="width: 100%" v-loading="loading" stripe>
      <el-table-column prop="name" label="Name" min-width="150" />
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
      <el-table-column label="Actions" width="120" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" plain @click="handleEdit(scope.row)" :disabled="scope.row.status !== 'pending_review'">Edit</el-button>
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
          <el-select v-model="createForm.region" placeholder="Select region" style="width: 100%;">
            <el-option label="China" value="china" />
            <el-option label="Europe" value="europe" />
            <el-option label="South America" value="south_america" />
            <el-option label="North America" value="north_america" />
            <el-option label="Asia" value="asia" />
          </el-select>
        </el-form-item>
        <el-form-item label="Requirement Type" prop="requirement_type">
          <el-select v-model="createForm.requirement_type" placeholder="Select type" style="width: 100%;">
            <el-option label="Regulatory Compliance" value="regulatory" />
            <el-option label="Security Vulnerability" value="security" />
            <el-option label="Revenue Growth" value="revenue" />
            <el-option label="Cost Reduction" value="cost" />
            <el-option label="Bug" value="bug" />
            <el-option label="Feature Optimization" value="optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="Impacted Users" prop="impacted_users">
          <el-select v-model="createForm.impacted_users" placeholder="Select impacted users" style="width: 100%;">
            <el-option label="<100" value="<100" />
            <el-option label="100-500" value="100-500" />
            <el-option label="500-1000" value="500-1000" />
            <el-option label=">1000" value=">1000" />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplementary Materials">
          <el-select v-model="createForm.supplementary_materials" multiple placeholder="Select materials" style="width: 100%;">
            <el-option label="User Research" value="user_research" />
            <el-option label="Data Report" value="data_report" />
            <el-option label="Competitor Analysis" value="competitor_analysis" />
            <el-option label="Technical Solution" value="technical_solution" />
          </el-select>
        </el-form-item>
        <el-form-item label="Revenue Impact">
          <el-select v-model="createForm.revenue_impact" placeholder="Select revenue impact" style="width: 100%;" clearable>
            <el-option label="<50k" value="<50k" />
            <el-option label="50k-300k" value="50k-300k" />
            <el-option label="300k-1M" value="300k-1M" />
            <el-option label=">1M" value=">1M" />
          </el-select>
        </el-form-item>
        <el-form-item label="Deadline">
          <el-date-picker v-model="createForm.deadline" type="date" placeholder="Select deadline" style="width: 100%;" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitCreate" :loading="submitting">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="Edit Request" width="600">
      <el-alert v-if="isFormLocked" title="This request is locked and cannot be edited." type="warning" show-icon style="margin-bottom: 15px;" />
      <el-form :model="editForm" :rules="createRules" ref="editFormRef" label-width="160px" :disabled="isFormLocked">
        <el-form-item label="Name" prop="name">
          <el-input v-model="editForm.name" placeholder="Enter requirement name" />
        </el-form-item>
        <el-form-item label="Summary" prop="summary">
          <el-input v-model="editForm.summary" type="textarea" :rows="3" placeholder="Enter summary" />
        </el-form-item>
        <el-form-item label="Region" prop="region">
          <el-select v-model="editForm.region" placeholder="Select region" style="width: 100%;">
            <el-option label="China" value="china" />
            <el-option label="Europe" value="europe" />
            <el-option label="South America" value="south_america" />
            <el-option label="North America" value="north_america" />
            <el-option label="Asia" value="asia" />
          </el-select>
        </el-form-item>
        <el-form-item label="Requirement Type" prop="requirement_type">
          <el-select v-model="editForm.requirement_type" placeholder="Select type" style="width: 100%;">
            <el-option label="Regulatory Compliance" value="regulatory" />
            <el-option label="Security Vulnerability" value="security" />
            <el-option label="Revenue Growth" value="revenue" />
            <el-option label="Cost Reduction" value="cost" />
            <el-option label="Bug" value="bug" />
            <el-option label="Feature Optimization" value="optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="Impacted Users" prop="impacted_users">
          <el-select v-model="editForm.impacted_users" placeholder="Select impacted users" style="width: 100%;">
            <el-option label="<100" value="<100" />
            <el-option label="100-500" value="100-500" />
            <el-option label="500-1000" value="500-1000" />
            <el-option label=">1000" value=">1000" />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplementary Materials">
          <el-select v-model="editForm.supplementary_materials" multiple placeholder="Select materials" style="width: 100%;">
            <el-option label="User Research" value="user_research" />
            <el-option label="Data Report" value="data_report" />
            <el-option label="Competitor Analysis" value="competitor_analysis" />
            <el-option label="Technical Solution" value="technical_solution" />
          </el-select>
        </el-form-item>
        <el-form-item label="Revenue Impact">
          <el-select v-model="editForm.revenue_impact" placeholder="Select revenue impact" style="width: 100%;" clearable>
            <el-option label="<50k" value="<50k" />
            <el-option label="50k-300k" value="50k-300k" />
            <el-option label="300k-1M" value="300k-1M" />
            <el-option label=">1M" value=">1M" />
          </el-select>
        </el-form-item>
        <el-form-item label="Deadline">
          <el-date-picker v-model="editForm.deadline" type="date" placeholder="Select deadline" style="width: 100%;" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitting" :disabled="isFormLocked">Save Changes</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()

const requests = ref<any[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const submitting = ref(false)
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const editingId = ref<number | null>(null)

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

const isFormLocked = computed(() => editForm.value.status !== 'pending_review')

const createRules = ref<FormRules>({
  name: [{ required: true, message: 'Please enter requirement name', trigger: 'blur' }],
  summary: [{ required: true, message: 'Please enter summary', trigger: 'blur' }],
  region: [{ required: true, message: 'Please select region', trigger: 'change' }],
  requirement_type: [{ required: true, message: 'Please select type', trigger: 'change' }],
  impacted_users: [{ required: true, message: 'Please select impacted users', trigger: 'change' }]
})

const fetchRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/requests/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    requests.value = response.data
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
  showCreateDialog.value = true
}

const submitCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await axios.post('/api/requests/', createForm.value, {
          headers: { Authorization: `Bearer ${authStore.token}` }
        })
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
  showEditDialog.value = true
}

const submitEdit = async () => {
  if (!editFormRef.value || editingId.value === null) return
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await axios.patch(`/api/requests/${editingId.value}/`, editForm.value, {
          headers: { Authorization: `Bearer ${authStore.token}` }
        })
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
.user-dashboard {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
