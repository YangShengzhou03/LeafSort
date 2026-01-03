const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  productionSourceMap: false,
  
  devServer: {
    port: 8080,
    hot: true,
    open: false,
    client: {
      overlay: {
        warnings: false,
        errors: true
      }
    }
  },
  
  configureWebpack: {
    externals: {
      electron: 'require("electron")'
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        cacheGroups: {
          vendors: {
            test: /[\\/]node_modules[\\/]/,
            priority: -10,
            reuseExistingChunk: true
          },
          elementPlus: {
            test: /[\\/]node_modules[\\/]element-plus[\\/]/,
            name: 'element-plus',
            priority: 20
          },
          vue: {
            test: /[\\/]node_modules[\\/](vue|@vue|pinia|vue-router)[\\/]/,
            name: 'vue-vendor',
            priority: 15
          }
        }
      }
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },
  
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].title = 'LeafSort Pro - 智能相册管理系统'
      return args
    })

    if (process.env.NODE_ENV === 'production') {
      config.optimization.minimizer('terser').tap(args => {
        args[0].terserOptions.compress.drop_console = true
        args[0].terserOptions.compress.drop_debugger = true
        return args
      })
    }
  },
  
  css: {
    extract: process.env.NODE_ENV === 'production',
    sourceMap: false
  }
})
