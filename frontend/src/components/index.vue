<template>
  <div class="layout">
    <el-menu
        :default-active="activeIndex"
        class="el-menu-demo"
        mode="horizontal"
        :ellipsis="false"
        @select="handleSelect"
    >
      <el-menu-item index="1">数据总览</el-menu-item>
      <el-menu-item index="2">商品</el-menu-item>
      <el-menu-item index="3">订单</el-menu-item>
      <el-menu-item index="4">推广</el-menu-item>
      <el-menu-item index="5" style="margin-left: auto;" @click="logout">退出登录</el-menu-item>
    </el-menu>
    <div class="content">
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const activeIndex = ref('1')

// 根据当前路由激活对应菜单项
const routeToIndex: Record<string, string> = {
  '/statistics': '1',
  '/shops': '2',
  '/order': '3',
  '/promotion': '4'
}

// 监听路由变化，更新激活的菜单项
watch(() => route.path, (path) => {
  activeIndex.value = routeToIndex[path] || '1'
}, { immediate: true })

const handleSelect = (key: string, keyPath: string[]) => {
  const pathMap: Record<string, string> = {
    '1': '/statistics',
    '2': '/shops',
    '3': '/order',
    '4': '/promotion',
    '5': '/login'
  }

  if (key === '5') {
    // 退出登录
    logout()
  } else {
    router.push(pathMap[key])
  }
}

const logout = () => {
  window.sessionStorage.removeItem("token")
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-menu-demo {
  flex-shrink: 0;
}

.content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}
</style>
