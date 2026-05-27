import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderer = new marked.Renderer()

renderer.code = ({ text, lang }) => {
  const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
  const highlighted = hljs.highlight(text, { language }).value
  const langLabel = language !== 'plaintext' ? `<span class="code-lang">${language}</span>` : ''
  return `<div class="code-block">
    <div class="code-header">${langLabel}<button class="code-copy">Copy</button></div>
    <pre><code class="hljs language-${language}">${highlighted}</code></pre>
  </div>`
}

renderer.codespan = ({ text }) =>
  `<code class="inline-code">${text}</code>`

marked.use({ renderer })

export function useMarkdown() {
  function render(content: string): string {
    const raw = marked.parse(content) as string
    return DOMPurify.sanitize(raw, {
      ADD_TAGS: ['button'],
      ADD_ATTR: ['class'],
    })
  }

  return { render }
}
