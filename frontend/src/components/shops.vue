<template>
  <div class="shops-container">
    <el-row class="row-bg" justify="space-between" style="margin-bottom: 1vh">
      <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          :on-exceed="handleExceed"
          :disabled="isProcessing"
      >
        <el-button type="primary" :disabled="isProcessing">上传文件更新</el-button>
      </el-upload>
      <el-input
          v-model="keyword"
          placeholder="搜索规格ID、名称、档口等"
          style="max-width: 20vw;height: 4vh"
          :disabled="isProcessing"
          clearable
          @clear="loadTableData"
          @keyup.enter="filterData"
      >
        <template #append>
          <el-icon @click="filterData" style="cursor: pointer">
            <Search/>
          </el-icon>
        </template>
      </el-input>
    </el-row>
    <el-table ref="tableRef" row-key="spec_id" :data="tableData" v-loading="isProcessing" :style="{ height: '65vh' }">
      <el-table-column prop="picture_url" label="图片URL">
        <template #default="scope">
          <el-image
              v-if="scope.row.picture_url"
              :src="scope.row.picture_url"
              style="width: 50px; height: 50px;"
              fit="cover"
              :preview-src-list="[]"
          />
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="spec_id" label="规格ID" width="130"/>
      <el-table-column prop="spec_alias" label="规格别名" width="150"/>
      <el-table-column prop="spec_name" label="规格名称" width="150"/>
      <el-table-column prop="spec_code" label="规格编码" width="150"/>
      <el-table-column prop="cost_price" label="成本价" width="100" sortable/>
      <el-table-column prop="market" label="市场" width="120"/>
      <el-table-column prop="shop" label="档口" width="120"/>
      <el-table-column prop="supplier" label="供应商" width="120"/>
      <el-table-column prop="platform" label="平台" width="100"/>
      <el-table-column prop="store" label="店铺" width="120"/>
      <el-table-column prop="product_id" label="商品ID" width="120"/>
      <el-table-column prop="product_name" label="商品" width="200"/>
      <el-table-column prop="merchant_code" label="商家编码" width="150"/>
      <el-table-column prop="abbreviation" label="简称" width="120"/>
    </el-table>

    <!-- 分页组件 -->
    <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTableData"
        @current-change="loadTableData"
        style="margin-top: 20px; justify-content: flex-end; position: sticky; bottom: 0; background: #fff; padding: 10px; z-index: 10; box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);"
    />

    <!-- 处理进度遮罩层 -->
    <div v-if="isProcessing" class="progress-overlay">
      <div class="progress-content">
        <el-progress
            type="circle"
            :percentage="progressPercentage"
            :width="120"
            :stroke-width="8"
        />
        <div class="progress-text">
          <p>{{ progressText }}</p>
          <p class="progress-detail">{{ progressDetail }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fileUpload, get } from '../util/request'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const tableRef = ref()
const tableData = ref([])
const uploadRef = ref()
const selectedFile = ref(null)
const isProcessing = ref(false)
const currentTaskId = ref(null)
const progressInfo = ref({
  status: '',
  totalRows: 0,
  processedRows: 0,
  errorMessage: ''
})

// 分页参数
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})

// 搜索关键词
const keyword = ref('')

// 页面加载完成时请求loadTableData()
onMounted(async () => {
  await loadTableData()
})

// 计算进度百分比
const progressPercentage = computed(() => {
  if (progressInfo.value.totalRows === 0) return 0
  return Math.round((progressInfo.value.processedRows / progressInfo.value.totalRows) * 100)
})

// 进度文本
const progressText = computed(() => {
  const statusMap = {
    'pending': '等待处理',
    'processing': '正在处理',
    'completed': '处理完成',
    'failed': '处理失败'
  }
  return statusMap[progressInfo.value.status] || '处理中'
})

// 进度详情
const progressDetail = computed(() => {
  if (progressInfo.value.status === 'completed') {
    return `共处理 ${progressInfo.value.processedRows} 条数据`
  } else if (progressInfo.value.status === 'failed') {
    return `错误: ${progressInfo.value.errorMessage || '未知错误'}`
  } else if (progressInfo.value.totalRows > 0) {
    return `${progressInfo.value.processedRows} / ${progressInfo.value.totalRows}`
  } else {
    return '正在准备...'
  }
})

// 轮询任务状态
const pollTaskStatus = async () => {
  try {
    const res = await get(`user/task_status?task_id=${currentTaskId.value}`)
    console.log('任务状态响应:', res)
    if (res.data.code === 200) {
      progressInfo.value = {
        status: res.data.data.status,
        totalRows: res.data.data.total_rows,
        processedRows: res.data.data.processed_rows,
        errorMessage: res.data.data.error_message
      }

      // 根据状态决定是否继续轮询
      if (res.data.data.status === 'completed') {
        ElMessage.success('文件处理完成')
        isProcessing.value = false
        // 刷新表格数据
        await loadTableData()
      } else if (res.data.data.status === 'failed') {
        ElMessage.error('文件处理失败')
        isProcessing.value = false
      } else {
        // 继续轮询，每秒查询一次
        setTimeout(pollTaskStatus, 1000)
      }
    } else {
      ElMessage.error('查询任务状态失败')
      isProcessing.value = false
    }
  } catch (error) {
    console.error('查询任务状态失败:', error)
    ElMessage.error('查询任务状态失败')
    isProcessing.value = false
  }
}

// 搜索数据
const filterData = async () => {
  pagination.value.page = 1
  await loadTableData()
}

// 加载表格数据
const loadTableData = async () => {
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      keyword: keyword.value
    }
    const res = await get('shops/get_shops', params)
    console.log('表格数据响应:', res)
    if (res.data.code === 200) {
      tableData.value = res.data.data.list
      pagination.value.total = res.data.data.total
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 文件选择后自动上传
const handleFileChange = async (file) => {
  selectedFile.value = file.raw
  await uploadFile()
}

// 手动上传文件
const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await fileUpload('shops/upload_file', formData)
    console.log('上传响应:', res)
    if (res.data.code === 200) {
      ElMessage.success('文件上传成功，正在后台处理')
      currentTaskId.value = res.data.task_id
      isProcessing.value = true
      progressInfo.value = {
        status: 'pending',
        totalRows: 0,
        processedRows: 0,
        errorMessage: ''
      }
      // 开始轮询任务状态
      pollTaskStatus()
    }
    // 上传成功后清空文件选择
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
    selectedFile.value = null
  } catch (error) {
    ElMessage.error('上传失败')
    console.error(error)
  }
}

const handleExceed = (files) => {
  ElMessage.warning('最多只能上传1个文件')
}
</script>


<style scoped>
.shops-container {
  padding: 20px;
  position: relative;
}

.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.progress-content {
  background: white;
  padding: 40px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 200px;
}

.progress-text {
  text-align: center;
}

.progress-text p {
  margin: 5px 0;
  font-size: 16px;
  color: #333;
}

.progress-detail {
  font-size: 14px;
  color: #666;
}
</style>


