<template>
  <div>
    <h3>告警看板</h3>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>P0 致命</template>
          <div class="stat-value">0</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>P1 严重</template>
          <div class="stat-value">0</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>P2 警告</template>
          <div class="stat-value">0</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>今日总计</template>
          <div class="stat-value">0</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.stat-value {
  font-size: 32px;
  font-weight: bold;
  text-align: center;
  color: #409eff;
}
</style>
