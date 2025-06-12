# 🛠️ Tools API

一组常用字符串/时间处理工具的 API 服务，基于 Flask 构建，支持 Docker 多平台部署（`amd64` + `arm64`）。使用 Nginx 反向代理集成到 WordPress，提供可直接嵌入的 Web UI 界面。

---

## ✨ 功能列表

- `quote` / `unquote`: quote / unquot string
- `remove_extra_spaces`: renmove extra_spaces
- `remove_whitespace`: remove whitespaces
- `base64_encode` / `base64_decode`: Base64 encode/decode
- `url_encode` / `url_decode`: URL encode or decode
- `timestamp_to_mst`: Unix timetamp mills to MST timestamp
- `mst_to_timestamp`: MST timestamp to Unix timetamp mills

---

## 🔨 部署说明

### Docker 部署

1. 克隆仓库
```bash
git clone https://github.com/yourusername/tools-app.git
cd tools-app
```

2. 构建 Docker 镜像
```bash
docker build -t tools-api .
```

3. 运行容器
```bash
docker run -d -p 5000:5000 --name tools-api tools-api
```

### Nginx 配置

1. 创建 Nginx 配置文件
```bash
sudo nano /etc/nginx/sites-available/tools-api
```

2. 添加以下配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /tools {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 重写子路径
        rewrite ^/tools(/.*)?$ $1 break;
    }

    # 静态文件处理
    location /tools/static {
        proxy_pass http://localhost:5000/static;
    }
}
```

3. 启用站点配置
```bash
sudo ln -s /etc/nginx/sites-available/tools-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### WordPress 集成

1. 在 WordPress 仪表板中，创建新页面并设置其固定链接为 `/tools`。

2. 切换到文本编辑器模式，将以下代码添加到页面内容中：
```html
<div class="tools-container" style="width: 100%; height: 800px; overflow: hidden;">
    <iframe 
        src="/tools" 
        style="width: 100%; height: 100%; border: none; margin: 0; padding: 0; overflow: hidden;" 
        frameborder="0"
        allowtransparency="true"
    ></iframe>
</div>
<style>
    /* 移除 WordPress 主题可能添加的内边距 */
    .entry-content {
        padding: 0 !important;
        margin: 0 !important;
        max-width: none !important;
    }
    /* 确保工具占据完整宽度 */
    .tools-container {
        margin: -20px !important;  /* 抵消主题可能的边距 */
        width: calc(100% + 40px) !important;
    }
</style>
```

3. 发布页面后，工具将以全宽度显示在 `/tools` 页面上，并自动适应 WordPress 主题样式。

4. 如果页面显示 404 错误，请检查：
   - WordPress 固定链接设置是否正确
   - Nginx 配置文件中的 location 块是否正确
   - Nginx 重写规则是否正确应用
   - WordPress .htaccess 文件是否有冲突的重写规则

---

## 🚀 开发说明

### 本地开发

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行开发服务器
```bash
python app.py
```

访问 http://localhost:5000 即可使用工具。

### 多平台构建

支持 amd64 和 arm64 平台的 Docker 镜像构建：

```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t yourusername/tools-api:latest --push .
```

---
