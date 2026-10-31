/** Ignore shortcuts while editing or using browser commands. */
export function shortcutKey(event: KeyboardEvent): string | null {
  const target = event.target as HTMLElement | null
  if (event.repeat || event.isComposing || event.ctrlKey || event.metaKey || event.altKey || target?.isContentEditable || target?.closest?.('input, textarea, select, [contenteditable]:not([contenteditable="false"])')) return null
  const key = event.key.toLowerCase()
  return /^[1-7hk]$/.test(key) ? key : null
}
