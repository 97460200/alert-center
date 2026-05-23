<template>
  <el-container style="height: 100vh">
    <el-aside width="200px">
      <el-menu :default-active="$route.path" router>
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>告警看板</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <span>告警列表</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <h2>Alert Center 告警中台</h2>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
</script>

<style scoped>
.el-header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e6e6e6;
}
.el-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}
</style>
