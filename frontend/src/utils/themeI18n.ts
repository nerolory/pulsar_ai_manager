/** Map theme id (kebab-case) to locale key segment (snake_case). */
export function themeLocaleKey(themeId: string): string {
  return themeId.replace(/-/g, '_')
}
