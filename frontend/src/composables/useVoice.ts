import { ref, computed } from 'vue'
import { transcribeAudio } from '@/api/voice'
import { sanitizeForTTS } from '@/utils/ttsSanitize'
import { useI18n } from '@/composables/useI18n'
import type { SpeechRecognitionInstance } from '@/types/speech-recognition'

export type VoiceState = 'idle' | 'recording' | 'processing'

export function useVoice() {
  const { t } = useI18n()
  const state = ref<VoiceState>('idle')
  const error = ref<string | null>(null)
  const isSupported = computed(() => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  })

  let mediaRecorder: MediaRecorder | null = null
  let chunks: Blob[] = []
  let recognition: SpeechRecognitionInstance | null = null

  // Try Web Speech API first (instant, no backend needed)
  const hasSpeechRecognition = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  function startSpeechRecognition(onResult: (text: string) => void, onError: (e: string) => void) {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognitionAPI) {
      onError(t('voice.transcription_error'))
      return
    }
    recognition = new SpeechRecognitionAPI()
    recognition.lang = 'ru-RU'
    recognition.interimResults = false
    recognition.maxAlternatives = 1
    recognition.continuous = false

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      state.value = 'idle'
      onResult(transcript)
    }

    recognition.onerror = (event) => {
      state.value = 'idle'
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        onError(event.error)
      }
    }

    recognition.onend = () => {
      if (state.value === 'recording') {
        state.value = 'idle'
      }
    }

    recognition.start()
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
          const text = await transcribeAudio(blob)
          state.value = 'idle'
          if (text) onResult(text)
        } catch (e: unknown) {
          state.value = 'idle'
          const message = e instanceof Error ? e.message : t('voice.transcription_error')
          onError(message || t('voice.transcription_error'))
        }
      }

      mediaRecorder.start()
      state.value = 'recording'
    } catch (e: unknown) {
      state.value = 'idle'
      const message = e instanceof Error ? e.message : t('voice.mic_denied')
      onError(message || t('voice.mic_denied'))
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

  function speak(text: string, lang = 'ru-RU', rate = 1, pitch = 1): boolean {
    if (!isSupported) return false
    const sanitized = sanitizeForTTS(text)
    if (!sanitized) return false
    stop()
    const utterance = new SpeechSynthesisUtterance(sanitized)
    utterance.lang = lang
    utterance.rate = rate
    utterance.pitch = pitch
    utterance.onstart = () => { isSpeaking.value = true }
    utterance.onend = () => { isSpeaking.value = false }
    utterance.onerror = () => { isSpeaking.value = false }
    window.speechSynthesis.speak(utterance)
    return true
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
