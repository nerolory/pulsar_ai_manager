import { describe, it, expect } from 'vitest'
import { sanitizeForTTS } from '@/utils/ttsSanitize'

describe('sanitizeForTTS', () => {
  it('keeps plain text, numbers and allowed punctuation', () => {
    expect(sanitizeForTTS('Привет, мир! Число 42 + 1 - 2.')).toBe(
      'Привет, мир! Число 42 + 1 - 2.',
    )
  })

  it('removes emojis and control characters', () => {
    expect(sanitizeForTTS('Hello 👋\u0007world')).toBe('Hello world')
  })

  it('strips markdown and code fences', () => {
    expect(sanitizeForTTS('Title\n```js\nconst x = 1\n```\nDone `code`')).toBe(
      'Title Done',
    )
  })

  it('strips markdown links but keeps link text', () => {
    expect(sanitizeForTTS('See [docs](https://example.com) here')).toBe(
      'See docs here',
    )
  })

  it('removes markdown heading markers and special symbols', () => {
    expect(sanitizeForTTS('# Header *bold* _italic_ | pipe')).toBe(
      'Header bold italic pipe',
    )
  })

  it('returns empty string when nothing readable remains', () => {
    expect(sanitizeForTTS('👋🎉')).toBe('')
    expect(sanitizeForTTS('```\n```')).toBe('')
  })
})
