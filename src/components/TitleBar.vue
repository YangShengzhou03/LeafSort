<template>
  <div class="title-bar">
    <div class="window-controls">
      <div class="control-btn minimize-btn" @click="handleMinimize"></div>
      <div class="control-btn maximize-btn" @click="handleMaximize"></div>
      <div class="control-btn close-btn" @click="handleClose"></div>
    </div>
  </div>
</template>

<script setup>
const handleClose = () => {
  window.electronAPI?.closeWindow()
}

const handleMinimize = () => {
  window.electronAPI?.minimizeWindow()
}

const handleMaximize = () => {
  window.electronAPI?.maximizeWindow()
}
</script>

<style scoped>
.title-bar {
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
  background: #ffffff;
  border-bottom: 1px solid #e5e6eb;
  user-select: none;
  -webkit-app-region: drag;
}

.window-controls {
  display: flex;
  -webkit-app-region: no-drag;
  gap: 8px;
}

.control-btn {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.minimize-btn {
  background: #ffbd2e;
}

.maximize-btn {
  background: #27c93f;
}

.close-btn {
  background: #ff5f57;
}

.control-btn:hover {
  opacity: 0.8;
}
</style>
