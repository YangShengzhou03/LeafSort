<template>
  <MaterialsGridPage
    :title="sceneTitle"
    :subtitle="sceneSubtitle"
    :empty-text="sceneEmptyText"
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
import { useRoute } from 'vue-router'

export default {
  name: 'SceneMaterialsView',
  components: {
    MaterialsGridPage
  },
  setup() {
    const route = useRoute()
    
    // 场景配置映射
    const sceneConfig = {
      'landscape': {
        title: '风景照片',
        subtitle: '自然风景相关的照片和视频',
        emptyText: '没有找到风景相关的照片和视频',
        sceneTag: '风景'
      },
      'people': {
        title: '人物照片',
        subtitle: '人物相关的照片和视频',
        emptyText: '没有找到人物相关的照片和视频',
        sceneTag: '人物'
      },
      'animals': {
        title: '动物照片',
        subtitle: '动物相关的照片和视频',
        emptyText: '没有找到动物相关的照片和视频',
        sceneTag: '动物'
      },
      'food': {
        title: '美食照片',
        subtitle: '美食相关的照片和视频',
        emptyText: '没有找到美食相关的照片和视频',
        sceneTag: '食物'
      },
      'travel': {
        title: '旅行照片',
        subtitle: '旅行相关的照片和视频',
        emptyText: '没有找到旅行相关的照片和视频',
        sceneTag: '旅行'
      }
    }
    
    // 从路由中获取场景类型
    const getSceneType = () => {
      const path = route.path
      const sceneMatch = path.match(/^\/scene-(\w+)$/)
      return sceneMatch ? sceneMatch[1] : 'landscape'
    }
    
    const getSceneConfig = () => {
      const sceneType = getSceneType()
      return sceneConfig[sceneType] || sceneConfig['landscape']
    }
    
    const sceneConfigRef = getSceneConfig()
    
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
      getMaterials: () => {
        const config = getSceneConfig()
        return materialManager.getMaterialsByScene(config.sceneTag)
      },
      subscribe: (cb) => materialManager.subscribe(cb)
    })

    return {
      vm,
      sceneTitle: sceneConfigRef.title,
      sceneSubtitle: sceneConfigRef.subtitle,
      sceneEmptyText: sceneConfigRef.emptyText,
      handleFavorite,
      handlePreview,
      handleEdit
    }
  }
}
</script>

<style scoped>
</style>