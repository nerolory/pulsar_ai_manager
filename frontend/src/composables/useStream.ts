import { ref } from 'vue'

/**
 * Lightweight composable wrapping AbortController lifecycle.
 * Used by components that need to cancel ongoing fetch streams.
 */
export function useStream() {
  const streaming = ref(false)
  let controller: AbortController | null = null

  function start(): AbortSignal {
    controller = new AbortController()
    streaming.value = true
    return controller.signal
  }

  function stop() {
    controller?.abort()
    streaming.value = false
    controller = null
  }

  function done() {
    streaming.value = false
    controller = null
  }

  return { streaming, start, stop, done }
}
