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
      <el-form-item label="Description" prop="summary">
        <div class="rich-editor-wrapper" :class="{ 'is-disabled': disabled }">
          <div v-if="!disabled" class="rich-editor-toolbar">
            <button type="button" :class="{ 'is-active': editor?.isActive('bold') }" @click="editor?.chain().focus().toggleBold().run()">B</button>
            <button type="button" :class="{ 'is-active': editor?.isActive('italic') }" @click="editor?.chain().focus().toggleItalic().run()"><em>I</em></button>
            <button type="button" :class="{ 'is-active': editor?.isActive('underline') }" @click="editor?.chain().focus().toggleUnderline().run()"><u>U</u></button>
            <span class="toolbar-divider"></span>
            <button type="button" :class="{ 'is-active': editor?.isActive('heading', { level: 1 }) }" @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()">H1</button>
            <button type="button" :class="{ 'is-active': editor?.isActive('heading', { level: 2 }) }" @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()">H2</button>
            <span class="toolbar-divider"></span>
            <button type="button" :class="{ 'is-active': editor?.isActive('bulletList') }" @click="editor?.chain().focus().toggleBulletList().run()">&#8226; List</button>
            <button type="button" :class="{ 'is-active': editor?.isActive('orderedList') }" @click="editor?.chain().focus().toggleOrderedList().run()">1. List</button>
            <span class="toolbar-divider"></span>
            <button type="button" :class="{ 'is-active': editor?.isActive({ textAlign: 'left' }) }" @click="editor?.chain().focus().setTextAlign('left').run()">&#8676;</button>
            <button type="button" :class="{ 'is-active': editor?.isActive({ textAlign: 'center' }) }" @click="editor?.chain().focus().setTextAlign('center').run()">&#8596;</button>
            <button type="button" :class="{ 'is-active': editor?.isActive({ textAlign: 'right' }) }" @click="editor?.chain().focus().setTextAlign('right').run()">&#8677;</button>
          </div>
          <EditorContent v-if="!disabled" :editor="editor" class="rich-editor-content" />
          <div v-else class="rich-editor-preview" v-html="modelValue.summary || '<span class=\'text-muted\'>No description</span>'"></div>
        </div>
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
import { ref, watch, onBeforeUnmount } from 'vue'
import type { FormInstance, FormRules, UploadProps, UploadUserFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import { COUNTRIES } from '../constants/countries'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Placeholder from '@tiptap/extension-placeholder'

const props = defineProps<{
  modelValue: any
  disabled?: boolean
  uploadFileList?: UploadUserFile[]
}>()

const internalFormRef = ref<FormInstance>()

const editor = useEditor({
  extensions: [
    StarterKit,
    Underline,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Placeholder.configure({ placeholder: 'Describe the requirement in detail...' }),
  ],
  content: props.modelValue.summary || '',
  onUpdate: ({ editor: e }) => {
    updateField('summary', e.getHTML())
  },
})

watch(() => props.modelValue.summary, (newVal) => {
  if (!editor.value) return
  const currentHTML = editor.value.getHTML()
  if (newVal !== currentHTML) {
    editor.value.commands.setContent(newVal || '', { emitUpdate: false })
  }
})

watch(() => props.disabled, (val) => {
  if (editor.value) {
    editor.value.setEditable(!val)
  }
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

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
  summary: [{ required: true, message: 'Please enter description', trigger: 'blur' }],
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

.rich-editor-wrapper {
  width: 100%;
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-surface-card);
}

.rich-editor-wrapper.is-disabled {
  background: var(--color-surface-form);
}

.rich-editor-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 8px;
  border-bottom: 1px solid var(--color-border-default);
  background: var(--color-surface-form);
  flex-wrap: wrap;
}

.rich-editor-toolbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 28px;
  padding: 0 6px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.rich-editor-toolbar button:hover {
  background: var(--color-border-default);
  color: var(--color-text-primary);
}

.rich-editor-toolbar button.is-active {
  background: var(--color-accent);
  color: #fff;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border-default);
  margin: 0 4px;
}

.rich-editor-content {
  min-height: 150px;
}

.rich-editor-content :deep(.tiptap) {
  outline: none;
  padding: 12px;
  min-height: 150px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-primary);
}

.rich-editor-content :deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: var(--color-text-muted);
  pointer-events: none;
  height: 0;
}

.rich-editor-content :deep(.tiptap h1) {
  font-size: 20px;
  font-weight: 600;
  margin: 8px 0;
}

.rich-editor-content :deep(.tiptap h2) {
  font-size: 17px;
  font-weight: 600;
  margin: 6px 0;
}

.rich-editor-content :deep(.tiptap ul),
.rich-editor-content :deep(.tiptap ol) {
  padding-left: 24px;
}

.rich-editor-preview {
  padding: 12px;
  min-height: 80px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-primary);
}

.rich-editor-preview :deep(h1) {
  font-size: 20px;
  font-weight: 600;
  margin: 8px 0;
}

.rich-editor-preview :deep(h2) {
  font-size: 17px;
  font-weight: 600;
  margin: 6px 0;
}

.rich-editor-preview :deep(ul),
.rich-editor-preview :deep(ol) {
  padding-left: 24px;
}
</style>
