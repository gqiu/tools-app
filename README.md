# 🛠️ Tools API

一组常用字符串/时间处理工具的 API 服务，基于 Flask 构建，支持 Docker 多平台部署（`amd64` + `arm64`）。使用 Nginx 反向代理集成到 WordPress，提供可直接嵌入的 Web UI 界面。

---

## ✨ 功能列表

- `quote string` : quote string, should excape original `"` and `\`.
- `unquote string`: unquot string, should unescape orignal `"` and `\`.
- `remove_extra_spaces`: renmove extra_spaces
- `remove_whitespace`: remove whitespaces
- `base64_encode`: Base64 encode a string
- `base64_decode`: Base64 decode a
- `url_encode`: URL encode
- `url_decode`: URL decode
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

    location /tools/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

1. 在 WordPress 页面编辑器中，添加"自定义 HTML"区块。

2. 将以下代码粘贴到区块中：
```html
<iframe src="/tools/" 
        width="100%" 
        height="800px" 
        frameborder="0" 
        style="border: none; width: 100%; height: 800px;">
</iframe>
```

3. 发布页面后，工具将作为内嵌页面显示在您的 WordPress 网站中。

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
