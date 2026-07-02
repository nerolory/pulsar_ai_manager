<template>
  <div class="chat-input">
    <div v-if="attachedImages.length" class="chat-input__previews">
      <div v-for="(img, index) in attachedImages" :key="index" class="chat-input__preview">
        <img :src="img.dataUrl" />
        <button class="chat-input__preview-remove" @click="removeImage(index)" :title="t('chat.delete_chat')">✕</button>
      </div>
    </div>
    <div class="chat-input__wrapper">
      <textarea
        ref="ta"
        v-model="text"
        class="chat-input__textarea"
        :placeholder="t('chat.input_placeholder')"
        rows="1"
        @keydown.enter.exact.prevent="submit"
        @keydown.enter.shift.exact.prevent="newline"
        @input="autoResize"
        @paste="onPaste"
        @contextmenu="onContextMenu"
      />
      <div class="chat-input__actions">
        <button
          v-if="voiceSupported"
          class="chat-input__action-btn chat-input__action-btn--mic"
          :class="{ 'chat-input__action-btn--recording': voiceState === 'recording', 'chat-input__action-btn--processing': voiceState === 'processing' }"
          :title="voiceState === 'recording' ? t('input.recording') : voiceState === 'processing' ? t('input.processing') : t('input.voice_input')"
          :disabled="voiceState === 'processing'"
          @click="onVoiceToggle"
        >
          <svg v-if="voiceState === 'idle'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
          <span v-else-if="voiceState === 'recording'" class="chat-input__mic-pulse">●</span>
          <span v-else class="chat-input__mic-spin">⟳</span>
        </button>
        <button class="chat-input__action-btn" :title="t('input.attach_image')" @click="openFilePicker">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8B7355" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" fill="#E8E8E8"></path>
            <circle cx="12" cy="13" r="4" fill="#A0A0A0"></circle>
          </svg>
        </button>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          multiple
          class="chat-input__file-input"
          @change="onFileChange"
        />
        <button
          class="chat-input__tune-btn"
          :class="{ 'chat-input__tune-btn--active': tuneOpen }"
          :data-tip="t('input.fine_tune')"
          title=""
          @click="emit('toggleTune')"
        >⚙</button>
        <button
          class="chat-input__send-btn"
          :class="{ 'chat-input__send-btn--stop': streaming }"
          :title="streaming ? t('chat.stop') : uploadingImages ? t('input.uploading') : t('chat.send')"
          :disabled="uploadingImages && !streaming"
          @click="streaming ? emit('stop') : submit()"
        >
          {{ streaming ? '■' : '↑' }}
        </button>
      </div>
    </div>
    <div class="chat-input__hint">{{ t('input.hint') }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { ContentPart } from '@/types'
import { useVoice } from '@/composables/useVoice'
import { useToast } from '@/composables/useToast'
import { useI18n } from '@/composables/useI18n'
import { useContextMenuProvider } from '@/composables/useContextMenu'
import { uploadImage } from '@/api/uploads'

defineProps<{ streaming: boolean; tuneOpen: boolean }>()
const emit = defineEmits<{
  send: [text: string, images?: ContentPart[]]
  stop: []
  toggleTune: []
}>()

const text = ref('')
const ta = ref<HTMLTextAreaElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const { t } = useI18n()

const { state: voiceState, isSupported: voiceSupported, toggle: toggleVoice } = useVoice()
const { show: showToast } = useToast()
const contextMenu = useContextMenuProvider()

function onContextMenu(event: MouseEvent) {
  if (ta.value) contextMenu.handleContextMenuEvent(event, 'editable', ta.value)
}

function onVoiceToggle() {
  toggleVoice(
    (transcript) => {
      text.value = text.value ? text.value + ' ' + transcript : transcript
      nextTick(() => autoResize())
    },
    (err) => {
      showToast('🎤', t('voice.title'), t('voice.error', { message: err }), 3000)
    }
  )
}

interface AttachedImage { dataUrl: string; file: File }
const attachedImages = ref<AttachedImage[]>([])
const uploadingImages = ref(false)

function openFilePicker() {
  fileInput.value?.click()
}

function removeImage(i: number) {
  attachedImages.value.splice(i, 1)
}

async function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  for (const file of Array.from(files)) {
    await addImageFile(file)
  }
  if (fileInput.value) fileInput.value.value = ''
}

async function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of Array.from(items)) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      if (file) await addImageFile(file)
    }
  }
}

function addImageFile(file: File): Promise<void> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (ev) => {
      attachedImages.value.push({ dataUrl: ev.target!.result as string, file })
      resolve()
    }
    reader.readAsDataURL(file)
  })
}

async function submit() {
  const messageText = text.value.trim()
  if (!messageText && attachedImages.value.length === 0) return
  if (uploadingImages.value) return

  if (attachedImages.value.length > 0) {
    uploadingImages.value = true
    try {
      const parts: ContentPart[] = []
      if (messageText) parts.push({ type: 'text', text: messageText })
      for (const img of attachedImages.value) {
        const uploaded = await uploadImage(img.file)
        parts.push({ type: 'image_url', image_url: { url: uploaded.url } })
      }
      emit('send', messageText, parts)
      attachedImages.value = []
    } catch (error) {
      console.error('Image upload failed:', error)
      showToast('❌', t('app.brand'), t('input.upload_failed'), 4000)
      return
    } finally {
      uploadingImages.value = false
    }
  } else {
    emit('send', messageText)
  }

  text.value = ''
  if (ta.value) { ta.value.style.height = 'auto' }
}

function newline() {
  const el = ta.value
  if (!el) return
  const start = el.selectionStart ?? text.value.length
  const end = el.selectionEnd ?? text.value.length
  text.value = text.value.slice(0, start) + '\n' + text.value.slice(end)
  nextTick(() => {
    el.selectionStart = el.selectionEnd = start + 1
    autoResize()
  })
}

function autoResize() {
  if (!ta.value) return
  ta.value.style.height = 'auto'
  ta.value.style.height = Math.min(ta.value.scrollHeight, 200) + 'px'
}
</script>

<style scoped>
.chat-input {
  padding: 12px 16px 14px; border-top: 1px solid var(--brd);
  background: var(--topbar-bg); flex-shrink: 0;
}
.chat-input__wrapper {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-g); border: 1px solid var(--brd);
  border-radius: var(--r); padding: 8px 10px;
  transition: border-color .15s;
}
.chat-input__wrapper:focus-within { border-color: var(--brd-a); }

.chat-input__textarea {
  flex: 1; background: none; border: none; outline: none; resize: none;
  font-family: inherit; font-size: 13.5px; color: var(--t1);
  line-height: 2; min-height: 24px; max-height: 200px;
  scrollbar-width: thin;
}
.chat-input__textarea::placeholder { color: var(--t3); }

.chat-input__actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.chat-input__action-btn {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 16px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .14s;
  flex-shrink: 0;
}
.chat-input__action-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }

.chat-input__tune-btn {
  position: relative; width: 32px; height: 32px; border-radius: 8px;
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 16px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all .14s; flex-shrink: 0;
}
.chat-input__tune-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }
.chat-input__tune-btn--active { color: var(--accent-l); border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.1); }
.chat-input__tune-btn::after {
  content: attr(data-tip);
  position: absolute; bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%);
  background: var(--bg-panel); border: 1px solid var(--brd); border-radius: 6px;
  padding: 4px 9px; font-size: 11px; color: var(--t1); white-space: nowrap;
  pointer-events: none; opacity: 0; transition: opacity .15s;
}
.chat-input__tune-btn:hover::after { opacity: 1; }

.chat-input__send-btn {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--accent); border: none;
  color: var(--on-accent); font-size: 16px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s; flex-shrink: 0;
}
.chat-input__send-btn:hover { background: var(--accent-l); }
.chat-input__send-btn--stop { background: var(--error); opacity: 0.85; }
.chat-input__send-btn--stop:hover { background: var(--error); opacity: 1; }

.chat-input__hint { font-size: 10px; color: var(--t3); margin-top: 6px; text-align: center; }

.chat-input__previews {
  display: flex; gap: 8px; flex-wrap: wrap;
  padding: 6px 0 4px;
}
.chat-input__preview {
  position: relative; flex-shrink: 0;
}
.chat-input__preview img {
  width: 72px; height: 72px; object-fit: cover;
  border-radius: 8px; border: 1px solid var(--brd); display: block;
}
.chat-input__preview-remove {
  position: absolute; top: -6px; right: -6px;
  width: 18px; height: 18px; border-radius: 50%;
  background: rgba(239,68,68,0.85); border: none;
  color: var(--on-accent); font-size: 9px; font-weight: 700;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  line-height: 1;
}
.chat-input__preview-remove:hover { background: var(--error); }
.chat-input__file-input { display: none; }

.chat-input__action-btn--recording {
  color: var(--error);
  border-color: var(--error-dim);
  background: var(--error-bg);
}
.chat-input__action-btn--processing {
  color: var(--accent-l);
  border-color: rgba(99,102,241,0.5);
  background: rgba(99,102,241,0.1);
  cursor: wait;
}
.chat-input__mic-pulse {
  font-size: 14px;
  animation: pulse 1s ease-in-out infinite;
}
.chat-input__mic-spin {
  font-size: 16px;
  display: inline-block;
  animation: spin 1s linear infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ── Responsive styles ──────────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  .chat-input { padding: 10px; }
  .chat-input__wrapper { border-radius: 10px; }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  .chat-input { padding: 8px; }
  .chat-input__actions { padding: 0 6px; }
  .chat-input__send-btn { width: 32px; height: 32px; }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .chat-input {
    padding: 8px;
    border-top: 1px solid var(--brd);
  }

  .chat-input__wrapper {
    border-radius: 8px;
  }

  .chat-input__textarea {
    min-height: 44px;
    max-height: 120px;
    padding: 10px 12px;
    font-size: 16px; /* Prevents zoom on iOS */
  }

  .chat-input__actions {
    padding: 0 8px;
    height: 44px;
  }

  .chat-input__preview img {
    width: 60px;
    height: 60px;
  }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .chat-input { padding: 6px; }
  .chat-input__textarea { padding: 8px 10px; font-size: 15px; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .chat-input__textarea { max-height: 80px; }
  .chat-input__previews { max-height: 70px; overflow-x: auto; flex-wrap: nowrap; }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
  .chat-input__textarea { min-height: 44px; }
}
</style>
