<template>
  <MaterialsGridPage
    title="全部照片和视频"
    subtitle="所有导入的照片和视频"
    empty-text="暂无照片或视频，点击下方按钮导入内容"
    empty-action-text="导入内容"
    :materials="vm.materials"
    :is-loading="vm.isLoading"
    :error="vm.error"
    @empty-action="handleEmptyAction"
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
  name: 'AllMaterialsView',
  components: {
    MaterialsGridPage
  },
  setup() {
    const handleEmptyAction = () => {
      // 触发导入功能
      window.dispatchEvent(new CustomEvent('toolbar-import'))
    }

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
      getMaterials: () => materialManager.getAllMaterials(),
      subscribe: (cb) => materialManager.subscribe(cb)
    })

    return {
      vm,
      handleEmptyAction,
      handleFavorite,
      handlePreview,
      handleEdit
    }
  }
}
</script>

<style scoped></style>