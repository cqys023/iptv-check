# 📺 IPTV Check - 智能源优选与自动维护系统

## 📖 项目简介

IPTV Check 是一个基于：

- 🐍 Python  
- ☁️ GitHub Actions  
- 🌐 Cloudflare Workers  

构建的 **自动 IPTV 源管理系统**。

---

## 🚀 核心能力

- 🔍 自动检测 IPTV 源  
- 🔄 自动切换失效 IP  
- 📡 自动生成 m3u 播放列表  
- ⚡ 智能避免误判（适配流媒体）  
- ☁️ 云端自动运行（无需服务器）  
- 🌐 支持在线访问（Worker 转发）  

---

## 🎯 在线使用

### 📡 M3U直链（自动更新）

👉 [点击访问](https://raw.githubusercontent.com/cqys023/iptv-check/main/output.m3u)

---

### 🌐 Worker 加速入口（推荐）

👉 [点击访问](https://gitiptv.feifanlib.shop)

👉 可用于播放器直接订阅

---

## 🧠 系统工作流程

```
IP池 (node_pool.js)
↓
检测 current_ip.txt
↓
是否可用？

✔ 可用 → 直接输出 m3u
❌ 失效 → 自动优选新IP
↓
更新 current_ip.txt
↓
生成 output.m3u
↓
GitHub 自动提交
```

---

## 📁 项目结构

```
iptv-check/
├── check_ip.py          # 核心脚本（智能检测）
├── node_pool.js         # IPTV IP池（候选源）
├── current_ip.txt       # 当前使用IP
├── output.m3u           # 输出播放列表
│
└── .github/workflows/
    └── run.yml          # 自动运行任务
```

---

## ⚙️ 自动运行

### 🕒 定时任务

每天自动执行检测与更新

### ▶️ 手动运行

```
GitHub → Actions → Run workflow
```

### 🔧 必须开启权限

```
Settings → Actions → General
✔ Read and write permissions
```

---

## 🧪 检测机制（核心亮点）

### ✔ M3U检测

判断：

- 是否包含 `#EXTM3U`  
- 是否包含 `#EXTINF`  

---

### ✔ 频道检测（优化版）

采用多策略：

- HEAD 请求检测  
- GET 流模式检测  
- 模拟浏览器访问（User-Agent）  

---

### ✔ 防误判机制（关键）

> IPTV 流 ≠ 普通网页  

因此：

- ❌ 不依赖完整下载  
- ✔ 支持流媒体检测  
- ✔ fallback：只要 M3U 存在即可使用  

---

## 🔄 自动切换逻辑

### 当前IP可用：

```
✔ 保持不变
✔ 更新 m3u
```

### 当前IP失效：

```
❌ 清空 current_ip.txt
🔄 从 IP池随机优选
✔ 写入新IP
✔ 生成新 m3u
```

---

## 📡 输出说明

### current_ip.txt

```
116.230.239.15:2222
```

### output.m3u

```
#EXTM3U
#EXTINF:-1,CCTV1
http://xxx
...
```

---

## 🌐 Cloudflare Worker（推荐）

```javascript
const TXT_URL = "https://raw.githubusercontent.com/cqys023/iptv-check/main/output.m3u";

export default {
  async fetch() {
    const res = await fetch(TXT_URL);
    return new Response(await res.text(), {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache"
      }
    });
  }
}
```

---

## 🚀 特性亮点

- 🧠 自动修复失效IP（自愈系统）  
- ⚡ 流媒体智能检测（防误判）  
- 🔄 自动优选IP  
- ☁️ 无服务器运行  
- 📦 轻量级（纯文本驱动）  

---

## 🔮 未来升级方向

- ⚡ 多线程并发检测（提速10倍）  
- 📊 IP测速评分系统  
- 🧹 自动清理失效IP池  
- 🌐 Web在线播放界面  
- 📱 手机电视页面  
- 🔗 多源融合系统  

---

## ⚠️ 免责声明

本项目仅用于学习与技术研究，请勿用于非法用途。  
IPTV 资源来源于网络，稳定性与合法性需自行判断。  

---

## ⭐ 支持项目

如果这个项目对你有帮助：

👉 点个 ⭐ Star 支持一下！

---

## 👨‍💻 作者

GitHub: https://github.com/cqys023
