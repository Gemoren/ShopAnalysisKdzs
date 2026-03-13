<template>
  <router-view/>
</template>
<script setup>
import { watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const whitePath = ['/login', '/#/login']

// 路由守卫：检查 token
watch(route, (to) => {
  if (!to || !to.path) return

  const token = sessionStorage.getItem('token')

  // 如果不在白名单且没有 token，跳转到登录页
  if (!whitePath.includes(to.path) && !token) {
    router.push('/login')
  }
}, { immediate: true })

</script>
<style>
html, body, #app {
  height: 100%;
  overflow-x: hidden;
}
</style>
