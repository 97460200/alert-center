# Alert Center - 告警中台

[![CI](https://github.com/97460200/alert-center/actions/workflows/ci.yml/badge.svg)](https://github.com/97460200/alert-center/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4-green.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于微服务架构的综合告警管理平台，支持多数据源接入、智能告警处理、多渠道通知。

## 📋 目录

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [API 文档](#api-文档)
- [开发指南](#开发指南)

## ✨ 功能特性

### 告警接入
- **Prometheus Alertmanager** - 原生支持 Alertmanager Webhook
- **Zabbix** - 支持 Zabbix 告警推送
- **自定义告警** - REST API 接入业务系统告警
- **日志告警** - 支持日志分析系统告警接入

### 告警处理
- **去重 (Dedup)** - 基于指纹的告警去重
- **静默 (Silence)** - 维护窗口告警静默
- **抑制 (Suppress)** - 高优先级告警抑制低优先级
- **收敛 (Converge)** - 时间窗口内告警聚合
- **丰富 (Enrich)** - 告警信息补全

### 通知渠道
- **钉钉 (DingTalk)** - 机器人消息推送
- **企业微信 (WeChat)** - 企业微信机器人
- **飞书 (Feishu)** - 飞书机器人卡片消息
- **Webhook** - 通用 Webhook 回调
- **邮件 (Email)** - SMTP 邮件通知
- **短信 (SMS)** - 短信通知

### 管理功能
- 多租户隔离
- 告警生命周期管理
- 路由策略配置
- 告警统计分析

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        告警数据流                                │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │Prometheus│    │  Zabbix  │    │ 业务系统 │    │ 日志系统 │
  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
       │               │               │               │
       └───────────────┴───────────────┴───────────────┘
                               │
                        ┌──────▼──────┐
                        │   Gateway   │  网关服务 (FastAPI)
                        │   :8001     │
                        └──────┬──────┘
                               │ Kafka
                        ┌──────▼──────┐
                        │  Processor  │  处理服务
                        │   :8003     │  去重→静默→抑制→收敛→路由
                        └──────┬──────┘
                               │ Kafka
                        ┌──────▼──────┐
                        │  Notifier   │  通知服务
                        │   :8004     │  钉钉/微信/飞书/Webhook
                        └─────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │                      管理平面                                │
  └─────────────────────────────────────────────────────────────┘
  
  ┌──────────────┐         ┌──────────────┐
  │    Admin     │◄───────►│    MySQL     │
  │   :8002      │         │   告警数据    │
  └──────────────┘         └──────────────┘
         │
         ▼
  ┌──────────────┐
  │   Frontend   │  Vue3 + Element Plus
  │   :80        │
  └──────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- MySQL 8.0
- Redis 7
- Kafka 3.x

### 使用 Docker Compose 启动

```bash
# 克隆仓库
git clone https://github.com/97460200/alert-center.git
cd alert-center

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

服务启动后访问：
- 前端界面: http://localhost
- Admin API: http://localhost:8002
- Gateway API: http://localhost:8001

### 本地开发模式

```bash
# 1. 安装共享库
cd shared
pip install -e ".[dev]"

# 2. 安装各服务依赖
cd ../services/gateway && pip install -e ".[dev]"
cd ../services/processor && pip install -e ".[dev]"
cd ../services/notifier && pip install -e ".[dev]"
cd ../services/admin && pip install -e ".[dev]"

# 3. 启动基础设施
docker-compose up -d mysql redis kafka

# 4. 运行数据库迁移
cd ../../migrations
alembic upgrade head

# 5. 启动各服务
# 终端1: Gateway
cd services/gateway && uvicorn app.main:app --port 8001

# 终端2: Processor
cd services/processor && python -m app.main

# 终端3: Notifier
cd services/notifier && python -m app.main

# 终端4: Admin
cd services/admin && uvicorn app.main:app --port 8002

# 终端5: Frontend
cd frontend && npm install && npm run dev
```

## ⚙️ 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 数据库
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/alert_center

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# 钉钉机器人
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
DINGTALK_SECRET=SECxxx

# 企业微信机器人
WECHAT_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx

# 飞书机器人
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
FEISHU_SECRET=xxx
```

### 告警路由配置

通过 Admin API 配置路由策略：

```bash
# 创建路由策略
curl -X POST http://localhost:8002/api/v1/routes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "P0告警路由",
    "match_labels": {"severity": "P0"},
    "priority": 100,
    "channel_ids": ["dingtalk-ops", "sms-oncall"]
  }'
```

## 📦 部署指南

### 方式一：Docker Compose（快速体验）

```bash
git clone https://github.com/97460200/alert-center.git
cd alert-center
docker-compose up -d
```

访问地址：
- 前端界面: http://localhost
- Admin API: http://localhost:8002
- Gateway API: http://localhost:8001

### 方式二：Kubernetes + Helm（生产推荐）

#### 前置要求

- Kubernetes 集群 (1.24+)
- Helm 3.x
- kubectl 已配置

#### 快速部署

```bash
git clone https://github.com/97460200/alert-center.git
cd alert-center

# 运行部署脚本（自动安装 MySQL/Redis/Kafka + 应用服务）
chmod +x deploy-k8s.sh
./deploy-k8s.sh
```

#### 手动部署

```bash
# 1. 创建命名空间
kubectl create namespace alert-center

# 2. 添加 Helm 仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 3. 安装基础设施
helm install mysql bitnami/mysql -n alert-center \
  --set auth.rootPassword=alertcenter123 \
  --set auth.database=alert_center \
  --set auth.username=alert \
  --set auth.password=alert123 \
  --wait --timeout 300s

helm install redis bitnami/redis -n alert-center \
  --set auth.enabled=false \
  --wait --timeout 300s

helm install kafka bitnami/kafka -n alert-center \
  --set auth.clientProtocol=plaintext \
  --set persistence.enabled=true \
  --wait --timeout 300s

# 4. 安装 Alert Center 应用
helm install alert-center ./helm/alert-center \
  -n alert-center \
  -f ./helm/alert-center/values-prod.yaml \
  --wait --timeout 600s
```

#### 验证部署

```bash
# 查看 Pod 状态
kubectl get pods -n alert-center

# 查看服务
kubectl get svc -n alert-center

# 查看 Ingress
kubectl get ingress -n alert-center
```

#### 访问服务

```bash
# 端口转发（测试用）
kubectl port-forward svc/alert-center-gateway 8001:8001 -n alert-center
kubectl port-forward svc/alert-center-admin 8002:8002 -n alert-center
kubectl port-forward svc/alert-center-frontend 8080:80 -n alert-center
```

#### 生产环境配置

修改 `helm/alert-center/values-prod.yaml`：

```yaml
# 镜像仓库（已配置阿里云 ACR）
global:
  imageRegistry: "registry.cn-hangzhou.aliyuncs.com"

# Ingress 域名
frontend:
  ingress:
    enabled: true
    host: alert.your-domain.com
    tls: true
    annotations:
      kubernetes.io/ingress.class: nginx
      cert-manager.io/cluster-issuer: letsencrypt
```

更新配置：

```bash
helm upgrade alert-center ./helm/alert-center \
  -n alert-center \
  -f ./helm/alert-center/values-prod.yaml
```

#### 部署组件一览

| 组件 | 副本数 | 资源限制 | 自动扩缩容 |
|------|--------|----------|-----------|
| Gateway | 2 | 1CPU/1GB | - |
| Processor | 3 | 1CPU/1GB | ✅ 2~10 |
| Notifier | 2 | 0.5CPU/512MB | ✅ 2~10 |
| Admin | 2 | 0.5CPU/512MB | - |
| Frontend | 2 | 0.2CPU/256MB | - |
| MySQL | 1 | 10GB 存储 | - |
| Redis | 1 | 5GB 存储 | - |
| Kafka | 1 | 10GB 存储 | - |

## 📖 API 文档

### Gateway API (端口 8001)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/webhook/prometheus/{tenant_id}` | POST | Prometheus Alertmanager Webhook |
| `/api/v1/webhook/zabbix/{tenant_id}` | POST | Zabbix 告警接入 |
| `/api/v1/webhook/custom/{tenant_id}` | POST | 自定义告警接入 |
| `/api/v1/webhook/custom/{tenant_id}/batch` | POST | 批量告警接入 |
| `/api/v1/webhook/log/{tenant_id}` | POST | 日志告警接入 |

### Admin API (端口 8002)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/alerts` | GET | 告警列表 |
| `/api/v1/alerts/{id}` | GET | 告警详情 |
| `/api/v1/alerts/{id}/acknowledge` | POST | 确认告警 |
| `/api/v1/alerts/{id}/resolve` | POST | 解决告警 |
| `/api/v1/rules` | GET/POST | 告警规则管理 |
| `/api/v1/routes` | GET/POST | 路由策略管理 |
| `/api/v1/channels` | GET/POST | 通知渠道管理 |
| `/api/v1/silences` | GET/POST | 静默策略管理 |

### 示例：发送自定义告警

```bash
curl -X POST http://localhost:8001/api/v1/webhook/custom/tenant-001 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "数据库连接超时",
    "source": "custom",
    "severity": "P1",
    "labels": {
      "service": "order-api",
      "env": "production",
      "region": "cn-east-1"
    },
    "annotations": {
      "summary": "订单服务数据库连接超时",
      "description": "连接超时 30 秒，已重试 3 次"
    }
  }'
```

## 👨‍💻 开发指南

### 项目结构

```
alert-center/
├── shared/                 # 共享库
│   ├── shared/
│   │   ├── db/            # 数据库会话
│   │   ├── models/        # 数据模型
│   │   ├── kafka/         # Kafka 生产/消费
│   │   └── utils/         # 工具函数
│   └── tests/
├── services/
│   ├── gateway/           # 网关服务
│   ├── processor/         # 处理服务
│   ├── notifier/          # 通知服务
│   └── admin/             # 管理 API
├── frontend/              # Vue3 前端
├── migrations/            # 数据库迁移
├── helm/                  # Helm Chart
├── docker-compose.yml
└── .github/workflows/     # CI/CD
```

### 运行测试

```bash
# 运行所有测试
pytest shared/tests -v
pytest services/*/tests -v

# 运行单个测试
pytest services/gateway/tests/test_prometheus.py -v
```

### 添加新的通知渠道

1. 在 `services/notifier/app/channels/` 创建新文件
2. 继承 `BaseChannel` 类
3. 实现 `send()` 和 `test()` 方法
4. 在 `__init__.py` 中注册

```python
# services/notifier/app/channels/my_channel.py
from app.channels.base import BaseChannel

class MyChannel(BaseChannel):
    async def send(self, alert: dict) -> bool:
        # 实现发送逻辑
        pass
    
    async def test(self) -> bool:
        # 实现测试逻辑
        pass
```

## 📊 监控指标

服务暴露 Prometheus 指标：

- `alert_received_total` - 接收告警总数
- `alert_processed_total` - 处理告警总数
- `alert_notification_total` - 通知发送总数
- `alert_notification_errors` - 通知失败总数

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)
