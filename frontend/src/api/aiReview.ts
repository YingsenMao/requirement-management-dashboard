import axios from 'axios'

export interface ReviewSessionPayload {
  mode: 'create' | 'edit'
  requirement_id?: number
  form_context: {
    name: string
    summary: string
    requirement_type?: string
    [key: string]: any
  }
}

export interface ReviewMessagePayload {
  answer: string
}

export const createReviewSession = async (token: string, payload: ReviewSessionPayload) => {
  return axios.post('/api/ai/review-sessions/', payload, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
}

export const sendReviewMessage = async (token: string, sessionId: number, payload: ReviewMessagePayload) => {
  return axios.post(`/api/ai/review-sessions/${sessionId}/messages/`, payload, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
}

export const confirmReviewSession = async (token: string, sessionId: number) => {
  return axios.post(`/api/ai/review-sessions/${sessionId}/confirm/`, {}, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}

export const discardReviewSession = async (token: string, sessionId: number) => {
  return axios.post(`/api/ai/review-sessions/${sessionId}/discard/`, {}, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}

export const getAdminReviewSessions = async (token: string, requirementId: number) => {
  return axios.get(`/api/admin/requests/${requirementId}/review-sessions/`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}
