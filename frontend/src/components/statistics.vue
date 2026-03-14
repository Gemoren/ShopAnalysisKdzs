<template>
  <div class="statistics-page">
    <div class="date-picker-container">
      <el-date-picker
        v-model="dateRange"
        type="monthrange"
        range-separator="至"
        start-placeholder="开始月份"
        end-placeholder="结束月份"
        format="YYYY-MM"
        value-format="YYYY-MM"
        @change="handleDateChange"
      />
      <el-button type="primary" @click="handleQuery" style="margin-left: 10px;">查询</el-button>
    </div>
    <el-row class="row-bg" justify="space-evenly">
      <el-col :span="12">
        <div class="statistics-container" style="width: 100%;">
          <h2>收入汇总</h2>
          <div ref="incomeChartRef" style="width: 100%; height: 40vh"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="statistics-container" style="width: 100%;">
          <h2>推广花费(拼多多)</h2>
          <div ref="promotionChartRef" style="width: 100%; height: 40vh;"></div>
        </div>
      </el-col>
    </el-row>
  </div>

</template>

<script setup>
import {ref, onMounted} from 'vue'
import * as echarts from 'echarts'
import {get} from '../util/request'

const incomeChartRef = ref(null)
const promotionChartRef = ref(null)
const dateRange = ref([])
let incomeChartInstance = null
let promotionChartInstance = null

// 计算最近六个月的日期范围
const setDefaultDateRange = () => {
  const now = new Date()
  const endYear = now.getFullYear()
  const endMonth = String(now.getMonth() + 1).padStart(2, '0')
  const endDate = `${endYear}-${endMonth}`

  // 计算六个月前的日期
  const startDate = new Date(now)
  startDate.setMonth(startDate.getMonth() - 5) // 减去5个月，加上当前月就是6个月
  const startYear = startDate.getFullYear()
  const startMonth = String(startDate.getMonth() + 1).padStart(2, '0')
  const startDateStr = `${startYear}-${startMonth}`

  dateRange.value = [startDateStr, endDate]
  console.log('默认日期范围:', dateRange.value)
}

onMounted(() => {
  // 设置默认日期范围为最近六个月
  setDefaultDateRange()

  // 初始化收入汇总图表
  if (incomeChartRef.value) {
    incomeChartInstance = echarts.init(incomeChartRef.value)
    fetchIncomeData(incomeChartInstance)
  }

  // 初始化推广花费图表
  if (promotionChartRef.value) {
    promotionChartInstance = echarts.init(promotionChartRef.value)
    fetchPromotionData(promotionChartInstance)
  }
})

// 处理日期变化
const handleDateChange = (value) => {
  console.log('日期范围变化:', value)
}

// 处理查询按钮点击
const handleQuery = () => {
  if (incomeChartInstance) {
    fetchIncomeData(incomeChartInstance)
  }
  if (promotionChartInstance) {
    fetchPromotionData(promotionChartInstance)
  }
}

// 获取收入汇总数据
const fetchIncomeData = async (chart) => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await get('order/get_orders_by_month', params)
    if (response.data.code === 200) {
      const dataList = response.data.data.list

      // 处理数据：按月份和店铺名称分组
      const monthMap = {}
      const storeSet = new Set()

      dataList.forEach(item => {
        const monthYear = new Date(item.month_year)
        const monthKey = `${monthYear.getFullYear()}-${String(monthYear.getMonth() + 1).padStart(2, '0')}`
        const storeName = item.store_name
        const totalReceived = item.total_received

        if (!monthMap[monthKey]) {
          monthMap[monthKey] = {}
        }
        monthMap[monthKey][storeName] = totalReceived
        storeSet.add(storeName)
      })

      // 获取所有年月并排序
      const months = Object.keys(monthMap).sort()
      const monthLabels = months

      // 获取所有店铺
      const stores = Array.from(storeSet)

      // 生成图表数据
      const series = stores.map(store => ({
        name: store,
        type: 'line',
        smooth: true,
        data: months.map(month => monthMap[month][store] || 0)
      }))

      const option = {
        // title: {
        //   text: '各店铺月度收入汇总（按年月）',
        //   left: 'center'
        // },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          type: 'scroll',
          data: stores,
          top: 10,
          itemWidth: 10,
          itemHeight: 10,
          textStyle: {
            fontSize: 12
          }
        },
        xAxis: {
          type: 'category',
          data: monthLabels,
          axisLabel: {
            interval: 0
          }
        },
        yAxis: {
          type: 'value',
          name: '实收金额（元）'
        },
        series: series,
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '80px',
          containLabel: true
        }
      }

      chart.setOption(option)

      // 响应式调整
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }
  } catch (error) {
    console.error('获取收入数据失败:', error)
  }
}

// 获取推广花费数据
const fetchPromotionData = async (chart) => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await get('promotion/get_promotions_by_month', params)
    if (response.data.code === 200) {
      const dataList = response.data.data.list

      // 处理数据：按月份和店铺名称分组
      const monthMap = {}
      const storeSet = new Set()

      dataList.forEach(item => {
        const monthYear = new Date(item.month_year)
        const monthKey = `${monthYear.getFullYear()}-${String(monthYear.getMonth() + 1).padStart(2, '0')}`
        const storeName = item.store_name || '未分类'
        const totalCost = item.total_cost_sum

        if (!monthMap[monthKey]) {
          monthMap[monthKey] = {}
        }
        monthMap[monthKey][storeName] = totalCost
        storeSet.add(storeName)
      })

      // 获取所有年月并排序
      const months = Object.keys(monthMap).sort()
      const monthLabels = months

      // 获取所有店铺
      const stores = Array.from(storeSet)

      // 生成图表数据
      const series = stores.map(store => ({
        name: store,
        type: 'line',
        smooth: true,
        data: months.map(month => monthMap[month][store] || 0)
      }))

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          type: 'scroll',
          data: stores,
          top: 10,
          itemWidth: 10,
          itemHeight: 10,
          textStyle: {
            fontSize: 12
          }
        },
        xAxis: {
          type: 'category',
          data: monthLabels,
          axisLabel: {
            interval: 0
          }
        },
        yAxis: {
          type: 'value',
          name: '总花费（元）'
        },
        series: series,
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '80px',
          containLabel: true
        }
      }

      chart.setOption(option)

      // 响应式调整
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }
  } catch (error) {
    console.error('获取推广花费数据失败:', error)
  }
}
</script>

<style scoped>
.statistics-page {
  padding: 20px;
}

.date-picker-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 4px;
}

.statistics-container {
  padding: 20px;
}

.statistics-container h2 {
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}
</style>