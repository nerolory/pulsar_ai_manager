/**
 * Voice API module — transcription via backend Whisper endpoint.
 */

import { API_BASE_URL } from './apiService'

const API_PREFIX = `${API_BASE_URL}/api/v1`

/**
 * Send audio blob to backend for Whisper transcription.
 * @param audioBlob - Recorded audio blob from MediaRecorder.
 * @returns Transcribed text string.
 */
export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const formData = new FormData()
  formData.append('file', audioBlob, 'recording.webm')

  const response = await fetch(`${API_PREFIX}/voice/transcribe`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const text = await response.text()
    let message = `HTTP ${response.status}`
    try {
      const json = JSON.parse(text)
      message = json.detail ?? json.message ?? text
    } catch {
      message = text || message
    }
    throw new Error(message)
  }

  const data = await response.json()
  return data.text
}
