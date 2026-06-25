import axios from 'axios'

export interface RequirementPayload {
  name: string
  summary: string
  region: string
  requirement_type: string
  impacted_users: string
  supplementary_materials: string[]
  revenue_impact?: string
  deadline?: string
  attachments?: File[]
  deleted_attachment_ids?: number[]
}

const buildFormData = (payload: RequirementPayload): FormData => {
  const formData = new FormData()

  formData.append('name', payload.name)
  formData.append('summary', payload.summary)
  formData.append('region', payload.region)
  formData.append('requirement_type', payload.requirement_type)
  formData.append('impacted_users', payload.impacted_users)
  
  formData.append('supplementary_materials', JSON.stringify(payload.supplementary_materials || []))
  
  if (payload.revenue_impact) {
    formData.append('revenue_impact', payload.revenue_impact)
  }
  
  if (payload.deadline) {
    formData.append('deadline', payload.deadline)
  }

  // Match the renamed serializer field 'uploaded_files'
  if (payload.attachments && payload.attachments.length > 0) {
    payload.attachments.forEach(file => {
      formData.append('uploaded_files', file)
    })
  }

  if (payload.deleted_attachment_ids && payload.deleted_attachment_ids.length > 0) {
    formData.append('deleted_attachment_ids', JSON.stringify(payload.deleted_attachment_ids))
  }

  return formData
}

export const createRequirementRequest = async (token: string, payload: RequirementPayload) => {
  const formData = buildFormData(payload)

  return axios.post('/api/requests/', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const updateRequirementRequest = async (token: string, id: number, payload: RequirementPayload) => {
  const formData = buildFormData(payload)

  return axios.patch(`/api/requests/${id}/`, formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const assessRequirementRequest = async (token: string, id: number, payload: { workload: string, status: string }) => {
  return axios.patch(`/api/admin/requests/${id}/`, payload, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
}
