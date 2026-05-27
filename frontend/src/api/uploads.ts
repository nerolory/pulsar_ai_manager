import { API_BASE_URL } from './apiService'

export async function uploadImage(file: File): Promise<{ id: string; url: string }> {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`${API_BASE_URL}/api/v1/uploads`, { method: 'POST', body: form })
  if (!response.ok) {
    const errorMessage = await response.text()
    throw new Error(errorMessage || 'Upload failed')
  }
  return response.json()
}
