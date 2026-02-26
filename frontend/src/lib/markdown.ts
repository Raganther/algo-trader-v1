import fs from 'fs'
import path from 'path'

export function readStrategyMarkdown(filename: string): string {
  const filepath = path.join(process.cwd(), '../.claude/memory/strategies/', filename)
  try {
    return fs.readFileSync(filepath, 'utf-8')
  } catch {
    return `*Research notes not found for ${filename}.*`
  }
}
