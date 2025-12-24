import { reactive } from 'vue'
import { applyMaterialQuery } from '../utils/materialQuery'

const state = reactive({
  searchQuery: '',
  filter: null,
  sortBy: 'date',
  searchResults: null // 新增：存储搜索结果
})

const setSearchQuery = (searchQuery) => {
  state.searchQuery = typeof searchQuery === 'string' ? searchQuery : ''
}

const setFilter = (filter) => {
  state.filter = filter && typeof filter === 'object' ? filter : null
}

const setSortBy = (sortBy) => {
  if (typeof sortBy === 'string' && sortBy.trim()) {
    state.sortBy = sortBy
    return
  }
  if (sortBy && typeof sortBy === 'object' && typeof sortBy.sortBy === 'string') {
    state.sortBy = sortBy.sortBy
  }
}

// 新增：设置搜索结果
const setSearchResults = (results) => {
  state.searchResults = Array.isArray(results) ? results : null
}

// 新增：清除搜索结果
const clearSearchResults = () => {
  state.searchResults = null
}

const apply = (materials, extra = {}) => {
  // 如果有搜索结果，使用搜索结果，否则使用原始材料
  const sourceMaterials = state.searchResults || materials
  
  const mergedFilter = extra.filter
    ? { ...(state.filter || {}), ...(extra.filter || {}) }
    : state.filter

  return applyMaterialQuery(sourceMaterials, {
    searchQuery: state.searchQuery,
    filter: mergedFilter,
    sortBy: extra.sortBy || state.sortBy
  })
}

export default {
  state,
  setSearchQuery,
  setFilter,
  setSortBy,
  setSearchResults,
  clearSearchResults,
  apply
}

