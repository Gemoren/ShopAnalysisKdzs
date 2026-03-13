<template>
  <div class="promotion-container">
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
          placeholder="搜索商品ID、名称、推广名称等"
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
    <el-table ref="tableRef" row-key="date" :data="tableData" v-loading="isProcessing" :style="{ height: '65vh' }">
      <el-table-column prop="date" label="日期" width="120"/>
      <el-table-column prop="product_id" label="商品id" width="120"/>
      <el-table-column prop="product_name" label="商品名称" width="150"/>
      <el-table-column prop="promotion_scene" label="推广场景" width="120"/>
      <el-table-column prop="promotion_name" label="推广名称" width="150"/>
      <el-table-column prop="bidding_method" label="出价方式" width="120"/>
      <el-table-column prop="total_cost" label="总花费(元)" width="120" sortable/>
      <el-table-column prop="transaction_cost" label="成交花费(元)" width="120" sortable/>
      <el-table-column prop="transaction_amount" label="交易额(元)" width="120" sortable/>
      <el-table-column prop="actual_roi" label="实际投产比" width="120" sortable/>
      <el-table-column prop="net_actual_roi" label="净实际投产比" width="120" sortable/>
      <el-table-column prop="net_transaction_amount" label="净交易额(元)" width="120" sortable/>
      <el-table-column prop="net_transaction_count" label="净成交笔数" width="100"/>
      <el-table-column prop="cost_per_net_transaction" label="每笔净成交花费(元)" width="140" sortable/>
      <el-table-column prop="net_transaction_ratio" label="净交易额占比" width="120" sortable/>
      <el-table-column prop="transaction_count" label="成交笔数" width="100"/>
      <el-table-column prop="cost_per_transaction" label="每笔成交花费(元)" width="140" sortable/>
      <el-table-column prop="amount_per_transaction" label="每笔成交金额(元)" width="140" sortable/>
      <el-table-column prop="direct_transaction_amount" label="直接交易额(元)" width="140" sortable/>
      <el-table-column prop="indirect_transaction_amount" label="间接交易额(元)" width="140" sortable/>
      <el-table-column prop="direct_transaction_count" label="直接成交笔数" width="120"/>
      <el-table-column prop="indirect_transaction_count" label="间接成交笔数" width="120"/>
      <el-table-column prop="direct_amount_per_transaction" label="每笔直接成交金额(元)" width="170" sortable/>
      <el-table-column prop="indirect_amount_per_transaction" label="每笔间接成交金额(元)" width="170" sortable/>
      <el-table-column prop="site_promotion_ratio" label="全站推广费比" width="120" sortable/>
      <el-table-column prop="exposure_count" label="曝光量" width="100"/>
      <el-table-column prop="click_count" label="点击量" width="100"/>
      <el-table-column prop="inquiry_cost" label="询单花费(元)" width="120" sortable/>
      <el-table-column prop="inquiry_count" label="询单量" width="100"/>
      <el-table-column prop="avg_inquiry_cost" label="平均询单成本(元)" width="140" sortable/>
      <el-table-column prop="favorite_cost" label="收藏花费(元)" width="120" sortable/>
      <el-table-column prop="favorite_count" label="收藏量" width="100"/>
      <el-table-column prop="avg_favorite_cost" label="平均收藏成本(元)" width="140" sortable/>
      <el-table-column prop="follow_cost" label="关注花费(元)" width="120" sortable/>
      <el-table-column prop="follow_count" label="关注量" width="100"/>
      <el-table-column prop="avg_follow_cost" label="平均关注成本(元)" width="140" sortable/>
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
    const res = await get('promotion/get_promotions', params)
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
    const res = await fileUpload('promotion/upload_file', formData)
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
.promotion-container {
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
