<template>
  <div id="app">
    <img src="./assets/logo.png" width="200" height="200">
    <div style="margin-bottom: 20px">
      无水印视频下载
    </div>
    <router-view/>
    <div style="position:fixed; bottom: 5px; text-align: right">
      <el-link href="https://github.com/moyada/stealer/issues"
               type="primary" style="margin-left: 20px" target="_blank">
        问题反馈
      </el-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  white-space: normal;
  word-break: break-all;
}
</style>
