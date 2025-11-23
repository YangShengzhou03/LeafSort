<template>
  <div class="waveform-container" ref="waveformRef">
    <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight"></canvas>
    <div class="waveform-overlay" v-if="isPlaying">
      <div class="play-indicator" :style="{ left: `${progress * 100}%` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, PropType } from 'vue'

interface WaveformProps {
  audioId: string
  isPlaying?: boolean
  progress?: number
  color?: string
  showProgress?: boolean
}

const props = withDefaults(defineProps<WaveformProps>(), {
  isPlaying: false,
  progress: 0,
  color: '#409eff',
  showProgress: true
})

const canvasRef = ref<HTMLCanvasElement | null>(null)
const waveformRef = ref<HTMLDivElement | null>(null)
const canvasWidth = ref(0)
const canvasHeight = ref(0)

// 生成模拟波形数据
const generateWaveformData = (length: number, intensity: number = 0.5): number[] => {
  const data: number[] = []
  
  // 创建有规律的波形模式
  for (let i = 0; i < length; i++) {
    // 使用正弦函数和随机值创建更真实的波形
    const baseHeight = Math.sin(i * 0.05) * 0.5 + 0.5
    const randomVariation = Math.random() * 0.4 + 0.3
    const segmentFactor = getSegmentFactor(i, length)
    
    data.push(baseHeight * randomVariation * intensity * segmentFactor)
  }
  
  return data
}

// 获取不同段落的波形因子，使波形看起来更自然
const getSegmentFactor = (index: number, length: number): number => {
  const position = index / length
  
  // 两端的波形较低，中间部分较高
  if (position < 0.1 || position > 0.9) {
    return 0.3 + Math.random() * 0.2
  } else if (position < 0.2 || position > 0.8) {
    return 0.5 + Math.random() * 0.3
  } else if (position < 0.3 || position > 0.7) {
    return 0.7 + Math.random() * 0.2
  } else {
    return 0.6 + Math.random() * 0.4
  }
}

// 绘制波形
const drawWaveform = () => {
  if (!canvasRef.value) return
  
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 设置线条颜色
  ctx.strokeStyle = props.color
  ctx.lineWidth = 1
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  
  // 生成波形数据
  const waveformData = generateWaveformData(Math.floor(canvasWidth.value / 2))
  
  // 绘制波形
  const centerY = canvasHeight.value / 2
  const barWidth = 2
  
  waveformData.forEach((amplitude, index) => {
    const x = index * barWidth
    const barHeight = amplitude * (canvasHeight.value - 20)
    
    // 绘制对称的波形
    ctx.beginPath()
    ctx.moveTo(x, centerY - barHeight / 2)
    ctx.lineTo(x, centerY + barHeight / 2)
    ctx.stroke()
    
    // 添加渐变效果
    const gradient = ctx.createLinearGradient(x, 0, x, canvasHeight.value)
    gradient.addColorStop(0, props.color)
    gradient.addColorStop(0.5, props.color)
    gradient.addColorStop(1, props.color)
    ctx.strokeStyle = gradient
    ctx.stroke()
  })
  
  // 如果需要显示进度
  if (props.showProgress) {
    drawProgressBar()
  }
}

// 绘制进度条
const drawProgressBar = () => {
  if (!canvasRef.value) return
  
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const progressX = (props.progress || 0) * canvasWidth.value
  
  // 绘制进度遮罩
  ctx.save()
  ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
  ctx.fillRect(progressX, 0, canvasWidth.value - progressX, canvasHeight.value)
  ctx.restore()
  
  // 绘制进度线
  ctx.beginPath()
  ctx.strokeStyle = props.color
  ctx.lineWidth = 2
  ctx.moveTo(progressX, 0)
  ctx.lineTo(progressX, canvasHeight.value)
  ctx.stroke()
}

// 调整画布大小
const resizeCanvas = () => {
  if (!waveformRef.value || !canvasRef.value) return
  
  const containerWidth = waveformRef.value.clientWidth
  const containerHeight = waveformRef.value.clientHeight
  
  canvasWidth.value = containerWidth
  canvasHeight.value = containerHeight
  
  nextTick(() => {
    drawWaveform()
  })
}

// 监听属性变化
watch(() => props.isPlaying, () => {
  drawWaveform()
})

watch(() => props.progress, () => {
  if (props.showProgress) {
    drawWaveform()
  }
})

watch(() => props.color, () => {
  drawWaveform()
})

onMounted(() => {
  resizeCanvas()
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeCanvas)
  
  // 组件卸载时清理
  const cleanup = () => {
    window.removeEventListener('resize', resizeCanvas)
  }
  
  // 返回清理函数
  return cleanup
})
</script>

<style scoped>
.waveform-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: rgba(0, 0, 0, 0.05);
}

.waveform-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.play-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #409eff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.8);
}
</style>