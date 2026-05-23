<template>
  <div>
    <h3>告警列表</h3>
    <el-table :data="[]" style="width: 100%" empty-text="暂无告警数据">
      <el-table-column prop="fingerprint" label="指纹" width="120" />
      <el-table-column prop="severity" label="级别" width="80" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="source" label="来源" width="100" />
      <el-table-column prop="started_at" label="触发时间" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
</script>
