<template>
  <div class="inp-zone">
    <div v-if="attachedImages.length" class="img-previews">
      <div v-for="(img, index) in attachedImages" :key="index" class="img-preview">
        <img :src="img.dataUrl" />
        <button class="img-rm" @click="removeImage(index)" title="Удалить">✕</button>
      </div>
    </div>
    <div class="inp-wrap">
      <textarea
        ref="ta"
        v-model="text"
        class="inp-ta"
        placeholder="Напишите сообщение..."
        rows="1"
        @keydown.enter.exact.prevent="submit"
        @keydown.enter.shift.exact.prevent="newline"
        @input="autoResize"
        @paste="onPaste"
      />
      <div class="inp-acts">
        <button class="ia-btn" title="Прикрепить изображение" @click="openFilePicker">
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
          class="file-input-hidden"
          @change="onFileChange"
        />
        <button
          class="tune-btn"
          :class="{ on: tuneOpen }"
          data-tip="Тонкая настройка"
          title=""
          @click="emit('toggleTune')"
        >⚙</button>
        <button
          class="snd"
          :class="{ stop: streaming }"
          :title="streaming ? 'Остановить' : 'Отправить'"
          @click="streaming ? emit('stop') : submit()"
        >
          {{ streaming ? '■' : '↑' }}
        </button>
      </div>
    </div>
    <div class="inp-hint">Enter — отправить · Shift+Enter — перенос строки</div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { ContentPart } from '@/types'

defineProps<{ streaming: boolean; tuneOpen: boolean }>()
const emit = defineEmits<{
  send: [text: string, images?: ContentPart[]]
  stop: []
  toggleTune: []
}>()

const text = ref('')
const ta = ref<HTMLTextAreaElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

interface AttachedImage { dataUrl: string; file: File }
const attachedImages = ref<AttachedImage[]>([])

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

function submit() {
  const t = text.value.trim()
  if (!t && attachedImages.value.length === 0) return

  if (attachedImages.value.length > 0) {
    const parts: ContentPart[] = []
    if (t) parts.push({ type: 'text', text: t })
    for (const img of attachedImages.value) {
      parts.push({ type: 'image_url', image_url: { url: img.dataUrl } })
    }
    emit('send', t, parts)
    attachedImages.value = []
  } else {
    emit('send', t)
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
.inp-zone {
  padding: 12px 16px 14px; border-top: 1px solid var(--brd);
  background: rgba(255,255,255,0.02); flex-shrink: 0;
}
.inp-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-g); border: 1px solid var(--brd);
  border-radius: var(--r); padding: 8px 10px;
  transition: border-color .15s;
}
.inp-wrap:focus-within { border-color: var(--brd-a); }

.inp-ta {
  flex: 1; background: none; border: none; outline: none; resize: none;
  font-family: inherit; font-size: 13.5px; color: var(--t1);
  line-height: 2; min-height: 24px; max-height: 200px;
  scrollbar-width: thin;
}
.inp-ta::placeholder { color: var(--t3); }

.inp-acts { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.ia-btn {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 16px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .14s;
  flex-shrink: 0;
}
.ia-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }

.tune-btn {
  position: relative; width: 32px; height: 32px; border-radius: 8px;
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 16px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all .14s; flex-shrink: 0;
}
.tune-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }
.tune-btn.on { color: var(--accent-l); border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.1); }
.tune-btn::after {
  content: attr(data-tip);
  position: absolute; bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%);
  background: var(--bg-panel); border: 1px solid var(--brd); border-radius: 6px;
  padding: 4px 9px; font-size: 11px; color: var(--t1); white-space: nowrap;
  pointer-events: none; opacity: 0; transition: opacity .15s;
}
.tune-btn:hover::after { opacity: 1; }

.snd {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--accent); border: none;
  color: #fff; font-size: 16px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s; flex-shrink: 0;
}
.snd:hover { background: var(--accent-l); }
.snd.stop { background: rgba(239,68,68,0.8); }
.snd.stop:hover { background: #ef4444; }

.inp-hint { font-size: 10px; color: var(--t3); margin-top: 6px; text-align: center; }

.img-previews {
  display: flex; gap: 8px; flex-wrap: wrap;
  padding: 6px 0 4px;
}
.img-preview {
  position: relative; flex-shrink: 0;
}
.img-preview img {
  width: 72px; height: 72px; object-fit: cover;
  border-radius: 8px; border: 1px solid var(--brd); display: block;
}
.img-rm {
  position: absolute; top: -6px; right: -6px;
  width: 18px; height: 18px; border-radius: 50%;
  background: rgba(239,68,68,0.85); border: none;
  color: #fff; font-size: 9px; font-weight: 700;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  line-height: 1;
}
.img-rm:hover { background: #ef4444; }
.file-input-hidden { display: none; }

/* ── Responsive styles ──────────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  .chat-input { padding: 10px; }
  .inp-box { border-radius: 10px; }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  .chat-input { padding: 8px; }
  .inp-acts { padding: 0 6px; }
  .send-btn { width: 32px; height: 32px; }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .chat-input {
    padding: 8px;
    border-top: 1px solid var(--brd);
  }

  .inp-box {
    border-radius: 8px;
  }

  .ta {
    min-height: 44px;
    max-height: 120px;
    padding: 10px 12px;
    font-size: 16px; /* Prevents zoom on iOS */
  }

  .inp-acts {
    padding: 0 8px;
    height: 44px;
  }

  .img-preview img {
    width: 60px;
    height: 60px;
  }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .chat-input { padding: 6px; }
  .ta { padding: 8px 10px; font-size: 15px; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .ta { max-height: 80px; }
  .img-previews { max-height: 70px; overflow-x: auto; flex-wrap: nowrap; }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
  .ta { min-height: 44px; }
}
</style>
