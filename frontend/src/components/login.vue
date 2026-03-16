<template>
  <el-card style="margin-top: 20vh; max-width: 500px; margin-left: auto; margin-right: auto;">
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
          type="password"
          show-password
      >
        <template #prepend>密码</template>
      </el-input>
    </div>
    <div style="margin-top: 5%">
      <el-row :gutter="10">
        <el-col :span="16">
          <el-input
              v-model="captcha"
              style="max-width: 100%"
              placeholder="请输入验证码"
          >
            <template #prepend>验证码</template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-image
            v-if="captchaImage"
            :src="captchaImage"
            style="width: 100%; height: 40px; cursor: pointer; border: 1px solid #dcdfe6; border-radius: 4px;"
            @click="fetchCaptcha"
            title="点击刷新验证码"
          />
        </el-col>
      </el-row>
    </div>
    <template #footer>
      <el-row justify="end">
        <el-button type="primary" @click="login" :loading="loading">登录</el-button>
      </el-row>
    </template>
  </el-card>
</template>

<script lang="ts" setup>
import {ref, onMounted} from 'vue'
import { post, get } from '../util/request.js'
import router from '../router'
import {ElMessage} from 'element-plus'

const username = ref('')
const password = ref('')
const captcha = ref('')
const captchaImage = ref('')
const captchaUuid = ref('')
const loading = ref(false)

// 获取验证码
const fetchCaptcha = async () => {
  try {
    const res = await get('user/captcha')
    if (res.data.code == 200) {
      captchaImage.value = res.data.base64str
      captchaUuid.value = res.data.uuid
    }
  } catch (error) {
    ElMessage.error('获取验证码失败')
  }
}

const login = async () => {
  if (!username.value || !password.value || !captcha.value) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loading.value = true
  const data = {
    username: username.value,
    password: password.value,
    captcha: captcha.value,
    uuid: captchaUuid.value
  }
  try {
    const res = await post('user/login', data)
    if (res.data.status == true) {
      ElMessage.success(res.data.info)
      window.sessionStorage.setItem("token", res.data.token)
      await router.push("/statistics")
    } else {
      ElMessage.error(res.data.info)
      // 登录失败时刷新验证码
      fetchCaptcha()
    }
  } catch (error) {
    ElMessage.error('登录失败')
    // 发生错误时刷新验证码
    fetchCaptcha()
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取验证码
onMounted(() => {
  fetchCaptcha()
})
</script>

<style scoped>

</style>
