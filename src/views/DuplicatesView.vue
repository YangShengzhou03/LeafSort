<template>
  <MaterialsGridPage
    title="相似照片"
    subtitle="系统检测到的相似照片"
    empty-text="没有检测到相似照片"
    :materials="vm.materials"
    :is-loading="vm.isLoading"
    :error="vm.error"
    @favorite="handleFavorite"
    @preview="handlePreview"
    @edit="handleEdit"
    @retry="vm.refresh"
  />
</template>

<script>
import { ElMessage } from 'element-plus'
import MaterialsGridPage from '../components/MaterialsGridPage.vue'
import materialManager from '../utils/materialManager'
import { useMaterialsListViewModel } from '../viewmodels/useMaterialsListViewModel'

export default {
  name: 'DuplicatesView',
  components: {
    MaterialsGridPage
  },
  setup() {
    const handleFavorite = (material) => {
      materialManager.toggleFavorite(material.id)
    }

    const handlePreview = (material) => {
      window.dispatchEvent(new CustomEvent('preview-material', { detail: material }))
    }

    const handleEdit = (material) => {
      ElMessage.info(`编辑: ${material.name}`)
    }

    const vm = useMaterialsListViewModel({
      getMaterials: () => materialManager.getDuplicates(),
      subscribe: (cb) => materialManager.subscribe(cb)
    })

    return {
      vm,
      handleFavorite,
      handlePreview,
      handleEdit
    }
  }
}
</script>

<style scoped></style>