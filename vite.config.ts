import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { fileURLToPath } from 'url'

// 获取当前目录的绝对路径
const __dirname = fileURLToPath(new URL('.', import.meta.url))

export default defineConfig({
  plugins: [
    vue(),
  ],
  base: './',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@router': resolve(__dirname, 'src/router'),
      '@types': resolve(__dirname, 'src/types'),
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
  },
  server: {
    port: 5173,
    host: true, // 允许从外部访问
    open: false, // 不自动打开浏览器
    proxy: {
      // 这里可以添加代理配置，用于开发环境API调用
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    assetsDir: 'assets',
    cssCodeSplit: true,
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    chunkSizeWarningLimit: 1000, // 调整块大小警告限制
    rollupOptions: {
      output: {
        manualChunks: {
          // 将大型依赖包拆分为单独的块
          vue: ['vue', 'vue-router', 'pinia'],
          element: ['element-plus', '@element-plus/icons-vue'],
          utils: ['axios', 'chokidar', 'crypto-js', 'fs-extra'],
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use '@/styles/variables.scss' as vars;`,
      },
    },
    devSourcemap: false,
  },
  // 优化依赖
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'element-plus',
      '@element-plus/icons-vue',
      'axios',
    ],
  },
  // 环境变量配置
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
    '__VUE_PROD_DEVTOOLS__': false,
    '__VUE_OPTIONS_API__': false,
  },
})