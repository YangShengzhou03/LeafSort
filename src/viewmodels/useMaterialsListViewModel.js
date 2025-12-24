import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import libraryQueryStore from '../stores/libraryQueryStore'

const asArray = (value) => (Array.isArray(value) ? value : [])

export const useMaterialsListViewModel = (options = {}) => {
  const getMaterials = typeof options.getMaterials === 'function' ? options.getMaterials : () => []
  const subscribe = typeof options.subscribe === 'function' ? options.subscribe : null

  const baseMaterials = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const refresh = async () => {
    isLoading.value = true
    error.value = null
    try {
      const result = await Promise.resolve(getMaterials())
      baseMaterials.value = asArray(result)
    } catch (e) {
      error.value = e
      baseMaterials.value = []
    } finally {
      isLoading.value = false
    }
  }

  const materials = computed(() => libraryQueryStore.apply(baseMaterials.value, options.query || {}))

  let unsubscribe = null
  onMounted(() => {
    refresh()
    if (subscribe) {
      unsubscribe = subscribe(() => {
        refresh()
      })
    }
  })

  onBeforeUnmount(() => {
    if (unsubscribe) unsubscribe()
  })

  return {
    materials,
    baseMaterials,
    isLoading,
    error,
    refresh
  }
}

