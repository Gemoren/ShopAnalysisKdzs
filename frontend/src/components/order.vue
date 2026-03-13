<template>
  <div class="order-container">
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
          placeholder="搜索订单编号、平台、店铺等"
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
    <el-table ref="tableRef" row-key="order_no" :data="tableData" v-loading="isProcessing" :style="{ height: '65vh' }">
      <el-table-column prop="order_no" label="订单编号" width="150"/>
      <el-table-column prop="platform" label="平台" width="100"/>
      <el-table-column prop="store_name" label="店铺名称" width="150"/>
      <el-table-column prop="order_time" label="下单时间" width="180"/>
      <el-table-column prop="order_status" label="订单状态" width="120"/>
      <el-table-column prop="courier_company" label="快递公司" width="120"/>
      <el-table-column prop="tracking_no" label="运单号" width="150"/>
      <el-table-column prop="product_total_price" label="商品总价" width="120" sortable/>
      <el-table-column prop="product_count" label="宝贝数量" width="100"/>
      <el-table-column prop="product_types" label="宝贝种类" width="100"/>
      <el-table-column prop="actual_payment" label="实付金额" width="120" sortable/>
      <el-table-column prop="actual_received" label="实收金额" width="120" sortable/>
      <el-table-column prop="store_discount" label="店铺优惠金额" width="120" sortable/>
      <el-table-column prop="platform_discount" label="平台优惠金额" width="120" sortable/>
      <el-table-column prop="system_no" label="系统单号" width="150"/>
      <el-table-column prop="platform_product_id" label="平台商品ID" width="150"/>
      <el-table-column prop="platform_sku_id" label="平台skuID" width="120"/>
      <el-table-column prop="spec_name" label="规格名称" width="150"/>
      <el-table-column prop="alias" label="别名" width="120"/>
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
    const res = await get('order/get_orders', params)
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
    const res = await fileUpload('order/upload_file', formData)
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
.order-container {
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
