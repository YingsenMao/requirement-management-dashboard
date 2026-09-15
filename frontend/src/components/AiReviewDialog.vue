<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="680"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="ai-review-dialog">
      <div v-if="!finished" class="chat-section">
        <div class="message-list">
          <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
            <div class="message-content" v-html="msg.content"></div>
          </div>
          <div v-if="loading" class="message ai">
            <div class="message-content">
              <el-icon class="is-loading"><Loading /></el-icon> AI is thinking...
            </div>
          </div>
        </div>
        <div class="input-section">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            placeholder="Type your answer here..."
            :disabled="loading"
            @keydown.enter.ctrl="handleSend"
          />
          <el-button
            type="primary"
            @click="handleSend"
            :loading="loading"
            :disabled="!userInput.trim()"
            style="margin-top: 10px"
          >
            Send
          </el-button>
        </div>
      </div>

      <div v-else class="result-section">
        <div class="result-preview">
          <div class="preview-section">
            <h4>Refined Description:</h4>
            <div class="preview-content" v-html="generatedDescription"></div>
          </div>
          <div class="preview-section">
            <h4>Acceptance Criteria:</h4>
            <div class="preview-content" v-html="generatedAcceptance"></div>
          </div>
        </div>
        <div class="result-actions">
          <el-button @click="handleDiscard">Discard</el-button>
          <el-button type="primary" @click="handleApply">Apply to Description</el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { createReviewSession, sendReviewMessage, confirmReviewSession, discardReviewSession } from '../api/aiReview'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  modelValue: boolean
  mode: 'create' | 'edit'
  requirementId?: number
  formContext: {
    name: string
    summary: string
    requirement_type?: string
    [key: string]: any
  }
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'apply': [description: string, acceptance: string]
}>()

const authStore = useAuthStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const title = computed(() => {
  return props.mode === 'create' ? 'AI Requirement Review' : 'AI Requirement Review (Edit)'
})

const messages = ref<Array<{role: 'ai' | 'user', content: string}>>([])
const userInput = ref('')
const loading = ref(false)
const finished = ref(false)
const sessionId = ref<number | null>(null)
const generatedDescription = ref('')
const generatedAcceptance = ref('')

watch(() => props.modelValue, async (val) => {
  if (val) {
    messages.value = []
    userInput.value = ''
    loading.value = false
    finished.value = false
    sessionId.value = null
    generatedDescription.value = ''
    generatedAcceptance.value = ''
    await startSession()
  }
})

const startSession = async () => {
  loading.value = true
  try {
    const payload: any = {
      mode: props.mode,
      form_context: props.formContext
    }
    if (props.mode === 'edit' && props.requirementId) {
      payload.requirement_id = props.requirementId
    }
    const response = await createReviewSession(authStore.token || '', payload)
    sessionId.value = response.data.session_id
    if (response.data.finished) {
      finished.value = true
      generatedDescription.value = response.data.description_html
      generatedAcceptance.value = response.data.acceptance_criteria_html
    } else {
      messages.value.push({ role: 'ai', content: response.data.question })
    }
  } catch (error: any) {
    console.error('Failed to start review session', error)
    const msg = error?.response?.data?.detail || 'Failed to start AI review'
    ElMessage.error(msg)
    visible.value = false
  } finally {
    loading.value = false
  }
}

const handleSend = async () => {
  if (!userInput.value.trim() || loading.value || !sessionId.value) return

  const answer = userInput.value.trim()
  messages.value.push({ role: 'user', content: answer })
  userInput.value = ''
  loading.value = true

  try {
    const response = await sendReviewMessage(authStore.token || '', sessionId.value, { answer })
    if (response.data.finished) {
      finished.value = true
      generatedDescription.value = response.data.description_html
      generatedAcceptance.value = response.data.acceptance_criteria_html
    } else {
      messages.value.push({ role: 'ai', content: response.data.question })
    }
  } catch (error: any) {
    console.error('Failed to send message', error)
    ElMessage.error('Failed to get AI response')
  } finally {
    loading.value = false
  }
}

const handleApply = async () => {
  if (!sessionId.value) return
  try {
    await confirmReviewSession(authStore.token || '', sessionId.value)
    emit('apply', generatedDescription.value, generatedAcceptance.value)
    visible.value = false
  } catch (error) {
    console.error('Failed to confirm session', error)
    ElMessage.error('Failed to confirm')
  }
}

const handleDiscard = async () => {
  if (!sessionId.value) return
  try {
    await discardReviewSession(authStore.token || '', sessionId.value)
    visible.value = false
  } catch (error) {
    console.error('Failed to discard session', error)
  }
}

const handleClose = async () => {
  if (sessionId.value && !finished.value) {
    try {
      await discardReviewSession(authStore.token || '', sessionId.value)
    } catch (error) {
      console.error('Failed to discard session on close', error)
    }
  }
  visible.value = false
}
</script>

<style scoped>
.ai-review-dialog {
  min-height: 400px;
}

.chat-section {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--color-surface-form, #f5f7fa);
  border-radius: 8px;
  margin-bottom: 16px;
}

.message {
  margin-bottom: 12px;
  display: flex;
}

.message.ai {
  justify-content: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.5;
}

.message.ai .message-content {
  background: white;
  border: 1px solid var(--color-border-default, #dcdfe6);
}

.message.user .message-content {
  background: var(--color-accent, #409eff);
  color: white;
}

.input-section {
  display: flex;
  flex-direction: column;
}

.result-section {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.result-preview {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--color-surface-form, #f5f7fa);
  border-radius: 8px;
  margin-bottom: 16px;
}

.preview-section {
  margin-bottom: 20px;
}

.preview-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary, #303133);
}

.preview-content {
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid var(--color-border-default, #dcdfe6);
  line-height: 1.6;
}

.preview-content :deep(p) {
  margin: 0 0 10px 0;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  padding-left: 20px;
  margin: 0;
}

.preview-content :deep(li) {
  margin-bottom: 6px;
}

.result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
