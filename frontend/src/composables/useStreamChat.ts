/**
 * Composable for streaming chat with automatic retry and abort support.
 *
 * Extracts the complex streaming + retry + error categorization logic
 * from the chat store into a reusable, testable unit.
 */

import { ref } from 'vue'
import { streamChat } from '@/api/chat'
import type { StreamRequest } from '@/api/chat'

export interface StreamResult {
  success: boolean
  content: string
  error: Error | null
  isBalanceError: boolean
  aborted: boolean
}

interface StreamOptions {
  maxRetries?: number
  retryDelayMs?: number
  onToken?: (token: string) => void
  onRetry?: () => void
}

/**
 * Composable providing streaming chat with retry logic.
 *
 * Handles:
 * - AbortController management
 * - Configurable retry with exponential backoff
 * - Balance/credit error detection
 * - Clean abort semantics
 */
export function useStreamChat() {
  const streaming = ref(false)
  let abortController: AbortController | null = null

  /**
   * Execute a streaming chat request with retries.
   *
   * @param request - The StreamRequest payload.
   * @param options - Optional configuration for retries and token callback.
   * @returns StreamResult with final content and error status.
   */
  async function execute(
    request: StreamRequest,
    options: StreamOptions = {},
  ): Promise<StreamResult> {
    const { maxRetries = 3, retryDelayMs = 1000, onToken, onRetry } = options

    abortController = new AbortController()
    streaming.value = true

    let content = ''
    let lastError: Error | null = null
    let aborted = false

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      if (attempt > 1) {
        content = ''
        onRetry?.()
      } else {
        content = ''
      }
      lastError = null

      const result = await new Promise<{ success: boolean; error: Error | null }>((resolve) => {
        streamChat(
          request,
          (token) => {
            content += token
            onToken?.(token)
          },
          () => resolve({ success: true, error: null }),
          (error) => {
            if (error.name === 'AbortError') {
              aborted = true
              resolve({ success: true, error: null })
            } else {
              resolve({ success: false, error })
            }
          },
          abortController!.signal,
        )
      })

      if (result.success) {
        streaming.value = false
        abortController = null
        return { success: true, content, error: null, isBalanceError: false, aborted }
      }

      if (abortController?.signal.aborted) {
        streaming.value = false
        abortController = null
        return { success: true, content, error: null, isBalanceError: false, aborted: true }
      }

      lastError = result.error
      if (attempt < maxRetries) {
        await new Promise((resolve) => {
          const delay = retryDelayMs * attempt
          const timer = setTimeout(resolve, delay)
          abortController?.signal.addEventListener(
            'abort',
            () => {
              clearTimeout(timer)
              resolve(undefined)
            },
            { once: true },
          )
        })
        if (abortController?.signal.aborted) {
          streaming.value = false
          abortController = null
          return { success: true, content, error: null, isBalanceError: false, aborted: true }
        }
        abortController = new AbortController()
      }
    }

    streaming.value = false
    abortController = null

    const isBalanceError = detectBalanceError(lastError)
    return { success: false, content, error: lastError, isBalanceError, aborted: false }
  }

  /** Abort the current stream. */
  function abort() {
    abortController?.abort()
    streaming.value = false
  }

  return { streaming, execute, abort }
}

/**
 * Detect if an error is related to insufficient balance/credits.
 */
function detectBalanceError(error: Error | null): boolean {
  if (!error) return false
  const msg = error.message.toLowerCase()
  return msg.includes('balance') || msg.includes('credit') || msg.includes('insufficient')
}
