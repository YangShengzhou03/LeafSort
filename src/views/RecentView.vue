<template>
  <MaterialsGridPage
    title="最近添加"
    subtitle="最近添加的照片和视频"
    empty-text="暂无最近添加的照片和视频"
    empty-action-text="导入内容"
    :materials="vm.materials"
    :is-loading="vm.isLoading"
    :error="vm.error"
    @favorite="handleFavorite"
    @preview="handlePreview"
    @edit="handleEdit"
    @retry="vm.refresh"
    @empty-action="handleImportRedirect"
  />
</template>

<script>
import { ElMessage } from 'element-plus'
import MaterialsGridPage from '../components/MaterialsGridPage.vue'
import materialManager from '../utils/materialManager'
import { useMaterialsListViewModel } from '../viewmodels/useMaterialsListViewModel'

export default {
  name: 'RecentView',
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

    const handleImportRedirect = () => {
      window.dispatchEvent(new CustomEvent('toolbar-import'))
    }

    const vm = useMaterialsListViewModel({
      getMaterials: () => materialManager.getRecent(),
      subscribe: (cb) => materialManager.subscribe(cb)
    })

    return {
      vm,
      handleFavorite,
      handlePreview,
      handleEdit,
      handleImportRedirect
    }
  }
}
</script>

<style scoped>
</style>
