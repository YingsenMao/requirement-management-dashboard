import axios from 'axios'

export interface UserCreatePayload {
  username: string
  password: string
  role: 'admin' | 'user'
  department?: 'it' | 'rnd' | null
}

export const createUserAccount = async (token: string, payload: UserCreatePayload) => {
  return axios.post('/api/admin/users/', payload, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
}
