
<template>
  <div>
    <div v-if="info == null">
      <img src="../assets/logo.png" height="400">
      <div style="margin-bottom: 20px">
        短视频去水印，支持抖音、快手、BiliBili
      </div>
    </div>
    <div v-if="info != null">
      <el-image style="height:400px;" :src=info.cover fit="contain"></el-image>
      <div style="margin-bottom: 20px">
        {{ info.desc }}
      </div>
    </div>
    <el-row display="margin-top: 10px">
      <el-input v-model="shareUrl" placeholder="请输入分享地址" style="display:inline-table; width: 30%;"></el-input>

      <el-popover
        placement="top-start"
        width="200"
        trigger="hover">
        <span style="color: #b0b0b0">获取下载链接</span>
        <el-button slot="reference" :loading="loading" @click="getInfo()" icon="el-icon-search" style="margin: 2px;">解析</el-button>
      </el-popover>

      <el-popover v-if="info == null" width="200">
        <el-button type="primary" slot="reference" disabled icon="el-icon-download" style="margin: 2px;">下载</el-button>
      </el-popover>

      <a v-if="info != null" class="download" href=''>
        <el-button type="primary" icon="el-icon-download" style="margin: 2px;">下载</el-button>
      </a>
    </el-row>
  </div>
</template>


<script>
  import constant from "./constant";

  export default {
    name: 'home',
    delimiters: ['[[', ']]'],
    data () {
      return {
        info: null,
        shareUrl: '',
        loading: false,
      }
  },
  mounted: function() {
  },
  methods: {
    getInfo() {
      let url = this.shareUrl.trim();
      if (url === '') {
        this.$message({
          message: '分享地址不能为空',
          type: 'warning'
        });
        return
      }
      this.loading = true;
      url = url.replaceAll('#', '')
      url = url.replaceAll('&', '')

      this.$axios.get(constant.host + 'video/info?url=' + url)
        .then((res) => {
          console.log('error', res)
          if (res.status === 200) {
            this.info = res.data
          } else {
            this.$message.error(res.data);
            this.info = null;
          }
        }).catch((err) => {
            this.$message.error(this.getErrData(err));
            this.info = null;
        }).finally(() => {
            this.loading = false;
            if (this.info != null) {
              let a = document.querySelector('.download')
              a.href = constant.host + 'video/download?token=' + this.info.token
              // a.down = this.info.filename;
            }
        });
    }
  }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
