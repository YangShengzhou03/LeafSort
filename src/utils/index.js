import { ElMessage } from 'element-plus'

export const notify = {
  success: (message, duration = 3000) => {
    ElMessage.success({ message, duration })
  },
  info: (message, duration = 3000) => {
    ElMessage.info({ message, duration })
  },
  warning: (message, duration = 3000) => {
    ElMessage.warning({ message, duration })
  },
  error: (message, duration = 3000) => {
    ElMessage.error({ message, duration })
  }
}

export const getTagType = (index) => {
  const types = ['primary', 'success', 'info', 'warning', 'danger']
  return types[index % types.length]
}

export default {
  notify,
  getTagType
}
