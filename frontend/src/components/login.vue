<template>
  <el-card style="margin-top: 30vh">
    <template #header>
      <div class="card-header">
        <span>用户登录</span>
      </div>
    </template>
    <div>
      <el-input
          v-model="username"
          style="max-width: 600px"
          placeholder="请输入账号"
      >
        <template #prepend>账号</template>
      </el-input>
    </div>
    <div style="margin-top: 5%">
      <el-input
          v-model="password"
          style="max-width: 600px"
          placeholder="请输入密码"
      >
        <template #prepend>密码</template>
      </el-input>
    </div>
    <template #footer>
      <el-row justify="end">
        <el-button type="primary" @click="login">登录</el-button>
      </el-row>
    </template>
  </el-card>
</template>

<script lang="ts" setup>
import {ref} from 'vue'
import { post, get } from '../util/request.js'
import router from '../router'
import {ElMessage} from 'element-plus'

const username = ref('')
const password = ref('')

const login = async () => {
  const data = {
    username: username.value,
    password: password.value
  }
  try {
    const res = await post('user/login', data)
    if (res.data.status == true) {
      ElMessage.success(res.data.info)
      window.sessionStorage.setItem("token", res.data.token)
      await router.push("/statistics")
    } else {
      ElMessage.error(res.data.info)
    }
  } catch (error) {
    ElMessage.error('登录失败')
  }
}
</script>

<style scoped>

</style>
