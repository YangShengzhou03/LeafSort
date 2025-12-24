<template>
  <MaterialsGridPage
    title="AI咒语"
    subtitle="AI提示词相关的素材"
    empty-text="暂无AI咒语相关素材"
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
  name: 'AiPromptsView',
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
      getMaterials: () => materialManager.getByCategory('ai-prompts'),
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
