import { ref, computed } from 'vue'

export type VoiceState = 'idle' | 'recording' | 'processing'

const API_BASE = '/api/v1'

async function transcribeViaBackend(blob: Blob): Promise<string> {
  const form = new FormData()
  form.append('file', blob, 'audio.webm')
  const res = await fetch(`${API_BASE}/voice/transcribe`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Transcription failed')
  }
  const data = await res.json()
  return data.text || ''
}

export function useVoice() {
  const state = ref<VoiceState>('idle')
  const error = ref<string | null>(null)
  const isSupported = computed(() => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  })

  let mediaRecorder: MediaRecorder | null = null
  let chunks: Blob[] = []
  let recognition: SpeechRecognition | null = null

  // Try Web Speech API first (instant, no backend needed)
  const hasSpeechRecognition = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  function startSpeechRecognition(onResult: (text: string) => void, onError: (e: string) => void) {
    const SpeechRecognitionAPI =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognition = new SpeechRecognitionAPI()
    recognition!.lang = 'ru-RU'
    recognition!.interimResults = false
    recognition!.maxAlternatives = 1
    recognition!.continuous = false

    recognition!.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript
      state.value = 'idle'
      onResult(transcript)
    }

    recognition!.onerror = (event: SpeechRecognitionErrorEvent) => {
      state.value = 'idle'
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        onError(event.error)
      }
    }

    recognition!.onend = () => {
      if (state.value === 'recording') {
        state.value = 'idle'
      }
    }

    recognition!.start()
    state.value = 'recording'
  }

  async function startMediaRecorder(onResult: (text: string) => void, onError: (e: string) => void) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunks = []

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : ''

      mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        state.value = 'processing'
        try {
          const blob = new Blob(chunks, { type: mimeType || 'audio/webm' })
          const text = await transcribeViaBackend(blob)
          state.value = 'idle'
          if (text) onResult(text)
        } catch (e: any) {
          state.value = 'idle'
          onError(e.message || 'Ошибка транскрипции')
        }
      }

      mediaRecorder.start()
      state.value = 'recording'
    } catch (e: any) {
      state.value = 'idle'
      onError(e.message || 'Нет доступа к микрофону')
    }
  }

  function start(onResult: (text: string) => void, onError: (e: string) => void) {
    error.value = null
    if (hasSpeechRecognition) {
      startSpeechRecognition(onResult, onError)
    } else {
      startMediaRecorder(onResult, onError)
    }
  }

  function stop() {
    if (recognition) {
      recognition.stop()
      recognition = null
    }
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop()
    }
  }

  function toggle(onResult: (text: string) => void, onError: (e: string) => void) {
    if (state.value === 'recording') {
      stop()
    } else if (state.value === 'idle') {
      start(onResult, onError)
    }
  }

  return { state, error, isSupported, start, stop, toggle }
}

// ── TTS ─────────────────────────────────────────────────────────────────────

export function useTTS() {
  const isSpeaking = ref(false)
  const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window

  let currentUtterance: SpeechSynthesisUtterance | null = null

  function speak(text: string, lang = 'ru-RU', rate = 1, pitch = 1) {
    if (!isSupported) return
    stop()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = rate
    utterance.pitch = pitch
    utterance.onstart = () => { isSpeaking.value = true }
    utterance.onend = () => { isSpeaking.value = false }
    utterance.onerror = () => { isSpeaking.value = false }
    currentUtterance = utterance
    window.speechSynthesis.speak(utterance)
  }

  function stop() {
    if (!isSupported) return
    window.speechSynthesis.cancel()
    isSpeaking.value = false
  }

  function getVoices(): SpeechSynthesisVoice[] {
    if (!isSupported) return []
    return window.speechSynthesis.getVoices().filter(v => v.lang.startsWith('ru') || v.lang.startsWith('en'))
  }

  return { isSpeaking, isSupported, speak, stop, getVoices }
}
