/**
 * Prepare LLM text for browser TTS (Speech Synthesis API).
 * Keeps letters, digits, spaces, common punctuation, and + / - only.
 */

const CONTROL_CHARS = /[\u0000-\u001F\u007F-\u009F\u200B-\u200F\u2028-\u202F\uFEFF]/g
const EMOJI = /\p{Extended_Pictographic}/gu
const ALLOWED_CHARS = /[^\p{L}\p{M}\p{N}\s.,!?;:«»"'…+\-]/gu

export function sanitizeForTTS(text: string): string {
  if (!text) return ''

  let result = text
    .replace(CONTROL_CHARS, '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)]\([^)]*\)/g, '$1')
    .replace(/https?:\/\/\S+/gi, ' ')
    .replace(EMOJI, ' ')
    .replace(ALLOWED_CHARS, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  return result
}
