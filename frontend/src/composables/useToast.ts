import { ref } from 'vue'

export interface Toast {
  id: number
  icon: string
  title: string
  message: string
}

const toasts = ref<Toast[]>([])
let _id = 0

export function useToast() {
  function show(icon: string, title: string, message: string, duration = 3500) {
    const id = ++_id
    toasts.value.push({ id, icon, title, message })
    setTimeout(() => dismiss(id), duration)
  }

  function dismiss(id: number) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  return { toasts, show, dismiss }
}
