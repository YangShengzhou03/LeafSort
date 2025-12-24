const normalizeSortBy = (sortBy) => {
  if (!sortBy) return null
  if (typeof sortBy === 'string') return sortBy
  if (typeof sortBy === 'object' && typeof sortBy.sortBy === 'string') return sortBy.sortBy
  return null
}

const tokenize = (text) => {
  if (!text) return []
  const raw = String(text)
  const chineseTokens = raw.match(/[\u4e00-\u9fa5]/g) || []
  const englishTokens = raw
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(token => token.length > 1)
  const specialTokens = raw.match(/\b\d+[xkp]?\b/g) || []
  return [...chineseTokens, ...englishTokens, ...specialTokens].filter(token => token && token.length > 0)
}

const getMaterialText = (material) => {
  const name = material?.name ? String(material.name) : ''
  const type = material?.type ? String(material.type) : ''
  const format = material?.format ? String(material.format) : ''
  const description = material?.description ? String(material.description) : ''
  const tags = Array.isArray(material?.tags) ? material.tags.join(' ') : ''
  return `${name} ${type} ${format} ${description} ${tags}`.toLowerCase()
}

export const filterMaterials = (materials, filters) => {
  const list = Array.isArray(materials) ? materials : []
  const f = filters && typeof filters === 'object' ? filters : null
  if (!f) return list

  const ids = Array.isArray(f.ids) ? new Set(f.ids) : null
  const type = typeof f.type === 'string' ? f.type : null
  const format = typeof f.format === 'string' ? f.format : null
  const tags = Array.isArray(f.tags) ? new Set(f.tags) : null
  const rating = typeof f.rating === 'number' ? f.rating : null
  const dateRange = f.dateRange && typeof f.dateRange === 'object' ? f.dateRange : null
  const size = f.size && typeof f.size === 'object' ? f.size : null
  const trashed = typeof f.trashed === 'boolean' ? f.trashed : null

  const startDate = dateRange?.start ? new Date(dateRange.start) : null
  const endDate = dateRange?.end ? new Date(dateRange.end) : null
  const minSize = typeof size?.min === 'number' ? size.min : null
  const maxSize = typeof size?.max === 'number' ? size.max : null

  return list.filter(material => {
    if (!material || typeof material !== 'object') return false

    if (ids && !ids.has(material.id)) return false
    if (type && material.type !== type) return false
    if (format && material.format !== format) return false

    if (tags && tags.size > 0) {
      const mtags = Array.isArray(material.tags) ? material.tags : []
      const ok = mtags.some(tag => tags.has(tag))
      if (!ok) return false
    }

    if (rating !== null) {
      const r = typeof material.rating === 'number' ? material.rating : 0
      if (r < rating) return false
    }

    if (startDate || endDate) {
      const d = material.date ? new Date(material.date) : null
      if (!d || isNaN(d.getTime())) return false
      if (startDate && d < startDate) return false
      if (endDate && d > endDate) return false
    }

    if (minSize !== null || maxSize !== null) {
      const s = typeof material.size === 'number' ? material.size : 0
      if (minSize !== null && s < minSize) return false
      if (maxSize !== null && s > maxSize) return false
    }

    if (trashed !== null) {
      const isTrashed = Boolean(material.isTrashed)
      if (isTrashed !== trashed) return false
    }

    return true
  })
}

export const sortMaterials = (materials, sortBy) => {
  const list = Array.isArray(materials) ? [...materials] : []
  const by = normalizeSortBy(sortBy)
  if (!by) return list

  list.sort((a, b) => {
    const aa = a || {}
    const bb = b || {}
    switch (by) {
    case 'name':
      return String(aa.name || '').localeCompare(String(bb.name || ''))
    case 'date':
      return new Date(bb.date || 0) - new Date(aa.date || 0)
    case 'modified':
      return new Date(bb.modified || 0) - new Date(aa.modified || 0)
    case 'size':
      return (Number(bb.size) || 0) - (Number(aa.size) || 0)
    case 'rating':
      return (Number(bb.rating) || 0) - (Number(aa.rating) || 0)
    default:
      return 0
    }
  })

  return list
}

export const searchMaterials = (materials, query) => {
  const list = Array.isArray(materials) ? materials : []
  const q = typeof query === 'string' ? query.trim() : ''
  if (!q) return list

  const terms = tokenize(q)
  if (terms.length === 0) return list

  const scored = []
  for (const material of list) {
    if (!material || typeof material !== 'object') continue
    const haystack = getMaterialText(material)
    let score = 0
    for (const term of terms) {
      if (!term) continue
      const t = String(term).toLowerCase()
      if (!t) continue

      if (String(material.name || '').toLowerCase().includes(t)) score += 4
      if (Array.isArray(material.tags) && material.tags.some(tag => String(tag).toLowerCase().includes(t))) score += 3
      if (String(material.format || '').toLowerCase() === t) score += 2
      if (String(material.type || '').toLowerCase() === t) score += 2
      if (String(material.description || '').toLowerCase().includes(t)) score += 1
      if (haystack.includes(t)) score += 1
    }
    if (score > 0) scored.push({ material, score })
  }

  scored.sort((a, b) => b.score - a.score)
  return scored.map(item => item.material)
}

export const applyMaterialQuery = (materials, query) => {
  const list = Array.isArray(materials) ? materials : []
  const q = query && typeof query === 'object' ? query : {}
  const filtered = filterMaterials(list, q.filter)
  const searched = searchMaterials(filtered, q.searchQuery)
  return sortMaterials(searched, q.sortBy)
}

export const groupDuplicates = (materials) => {
  const list = Array.isArray(materials) ? materials : []
  const groups = new Map()

  for (const material of list) {
    if (!material || typeof material !== 'object') continue
    if (material.isTrashed) continue
    const name = String(material.name || '').trim().toLowerCase()
    const size = Number(material.size) || 0
    if (!name || !size) continue
    const key = `${name}::${size}`
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(material)
  }

  return Array.from(groups.values()).filter(group => group.length > 1)
}

