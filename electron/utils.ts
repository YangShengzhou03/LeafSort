import { join } from 'path'

export const isDev = process.env.NODE_ENV === 'development'

export function getAssetPath(...paths: string[]): string {
  const RESOURCES_PATH = isDev
    ? join(process.cwd(), 'assets')
    : join(process.resourcesPath, 'assets')

  return join(RESOURCES_PATH, ...paths)
}

export function getPreloadPath(): string {
  return isDev
    ? join(process.cwd(), 'electron', 'preload.js')
    : join(__dirname, 'preload.js')
}