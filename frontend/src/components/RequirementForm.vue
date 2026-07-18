<template>
  <el-form
    :model="modelValue"
    :rules="rules"
    ref="internalFormRef"
    :disabled="disabled"
    label-position="top"
    class="requirement-form"
  >
    <div class="form-section">
      <div class="section-header">
        <span class="section-title">Basic Information</span>
      </div>
      <el-form-item label="Name" prop="name">
        <el-input
          :model-value="modelValue.name"
          @update:model-value="updateField('name', $event)"
          placeholder="Enter a concise requirement name"
          maxlength="255"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="Summary" prop="summary">
        <el-input
          :model-value="modelValue.summary"
          @update:model-value="updateField('summary', $event)"
          type="textarea"
          :rows="4"
          placeholder="Describe the requirement in detail"
          maxlength="2000"
          show-word-limit
        />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Country" prop="country">
            <el-select
              :model-value="modelValue.country"
              @update:model-value="updateField('country', $event)"
              placeholder="Select country"
              class="field-block"
              filterable
            >
              <el-option v-for="c in COUNTRIES" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Urgency">
            <el-select
              :model-value="modelValue.urgency"
              @update:model-value="updateField('urgency', $event)"
              placeholder="Select urgency"
              class="field-block"
            >
              <el-option label="High" value="high" />
              <el-option label="Medium" value="medium" />
              <el-option label="Low" value="low" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </div>

    <div class="form-section">
      <div class="section-header">
        <span class="section-title">Business Details</span>
      </div>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Requirement Type" prop="requirement_type">
            <el-tooltip content="The primary category this requirement falls under" placement="top" :show-after="300">
              <el-select
                :model-value="modelValue.requirement_type"
                @update:model-value="updateField('requirement_type', $event)"
                placeholder="Select type"
                class="field-block"
              >
                <el-option label="Regulatory Compliance" value="regulatory" />
                <el-option label="Security Vulnerability" value="security" />
                <el-option label="Revenue Growth" value="revenue" />
                <el-option label="Cost Reduction" value="cost" />
                <el-option label="Bug" value="bug" />
                <el-option label="Feature Optimization" value="optimization" />
              </el-select>
            </el-tooltip>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Impacted Users">
            <el-tooltip content="Estimated number of users affected by this requirement" placement="top" :show-after="300">
              <el-select
                :model-value="modelValue.impacted_users"
                @update:model-value="updateField('impacted_users', $event)"
                placeholder="Select impacted users"
                class="field-block"
                clearable
              >
                <el-option label="<100" value="<100" />
                <el-option label="100-500" value="100-500" />
                <el-option label="500-1000" value="500-1000" />
                <el-option label=">1000" value=">1000" />
              </el-select>
            </el-tooltip>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Revenue Impact">
            <el-tooltip content="Estimated annual revenue impact in USD" placement="top" :show-after="300">
              <el-select
                :model-value="modelValue.revenue_impact"
                @update:model-value="updateField('revenue_impact', $event)"
                placeholder="Select revenue impact"
                class="field-block"
                clearable
              >
                <el-option label="<50k" value="<50k" />
                <el-option label="50k-300k" value="50k-300k" />
                <el-option label="300k-1M" value="300k-1M" />
                <el-option label=">1M" value=">1M" />
              </el-select>
            </el-tooltip>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Deadline">
            <el-date-picker
              :model-value="modelValue.deadline"
              @update:model-value="updateField('deadline', $event)"
              type="date"
              placeholder="Select deadline"
              class="field-block"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Supplementary Materials">
        <el-select
          :model-value="modelValue.supplementary_materials"
          @update:model-value="updateField('supplementary_materials', $event)"
          multiple
          placeholder="Select supporting materials"
          class="field-block"
        >
          <el-option label="User Research" value="user_research" />
          <el-option label="Data Report" value="data_report" />
          <el-option label="Competitor Analysis" value="competitor_analysis" />
          <el-option label="Technical Solution" value="technical_solution" />
        </el-select>
      </el-form-item>
    </div>

    <div class="form-section">
      <div class="section-header">
        <span class="section-title">Attachments</span>
      </div>
      <el-form-item>
        <template v-if="disabled">
          <div v-if="modelValue.attachments_list && modelValue.attachments_list.length" class="existing-attachments">
            <div v-for="att in modelValue.attachments_list" :key="att.id" class="attachment-item">
              <el-link type="primary" @click="$emit('download', att.id, getFileName(att.file))" :underline="false">
                {{ getFileName(att.file) }}
              </el-link>
            </div>
          </div>
          <span v-else class="text-muted">No attachments</span>
        </template>
        <template v-else>
          <el-upload
            :file-list="uploadFileList"
            @update:file-list="(val: UploadUserFile[]) => emit('update:uploadFileList', val)"
            :auto-upload="false"
            :on-change="onUploadChange"
            :on-remove="onUploadRemove"
            :on-exceed="onUploadExceed"
            :on-preview="onUploadPreview"
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
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance, FormRules, UploadProps, UploadUserFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import { COUNTRIES } from '../constants/countries'

const props = defineProps<{
  modelValue: any
  disabled?: boolean
  uploadFileList?: UploadUserFile[]
}>()

const internalFormRef = ref<FormInstance>()

defineExpose({
  formRef: internalFormRef
})

const emit = defineEmits<{
  'update:modelValue': [value: any]
  'update:uploadFileList': [value: UploadUserFile[]]
  'uploadChange': [file: UploadUserFile, uploadFiles: UploadUserFile[]]
  'uploadRemove': [file: UploadUserFile, uploadFiles: UploadUserFile[]]
  'uploadExceed': []
  'uploadPreview': [file: UploadUserFile]
  'download': [id: number, fileName: string]
}>()

const rules: FormRules = {
  name: [{ required: true, message: 'Please enter requirement name', trigger: 'blur' }],
  summary: [{ required: true, message: 'Please enter summary', trigger: 'blur' }],
  country: [{ required: true, message: 'Please select country', trigger: 'change' }],
  requirement_type: [{ required: true, message: 'Please select type', trigger: 'change' }]
}

const updateField = (field: string, value: any) => {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

const getFileName = (filePath: string) => {
  if (!filePath) return 'attachment'
  return filePath.split('/').pop() || 'attachment'
}

const validateUpload = (file: UploadUserFile) => {
  const allowedExtensions = ['.pdf', '.docx', '.xlsx', '.png', '.jpg']
  const fileName = file.name.toLowerCase()
  const isValidExt = allowedExtensions.some(ext => fileName.endsWith(ext))

  if (!isValidExt) {
    ElMessage.error('Only .pdf, .docx, .xlsx, .png, .jpg files are allowed.')
    return false
  }

  const fileSizeMB = (file.raw?.size || 0) / 1024 / 1024
  if (fileSizeMB > 5) {
    ElMessage.error(`File "${file.name}" exceeds the 5MB limit.`)
    return false
  }

  return true
}

const onUploadChange: UploadProps['onChange'] = (file, uploadFiles) => {
  if (!validateUpload(file)) {
    const newList = uploadFiles.filter(f => f.uid !== file.uid)
    emit('update:uploadFileList', newList)
    return
  }
  emit('uploadChange', file, uploadFiles)
}

const onUploadRemove: UploadProps['onRemove'] = (file, uploadFiles) => {
  emit('uploadRemove', file, uploadFiles)
}

const onUploadExceed: UploadProps['onExceed'] = () => {
  ElMessage.error('Maximum 3 files allowed.')
  emit('uploadExceed')
}

const onUploadPreview = (file: UploadUserFile) => {
  emit('uploadPreview', file)
}
</script>

<style scoped>
.requirement-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-section {
  background: var(--color-surface-form);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  border: 1px solid var(--color-border-subtle);
}

.section-header {
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border-default);
}

.section-title {
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: 0.3px;
}

.field-block {
  width: 100%;
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
  font-size: 13px;
}
</style>
