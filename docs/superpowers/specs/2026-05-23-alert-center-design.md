# 告警中台设计规格说明

> 日期：2026-05-23
> 状态：待审查

## 1. 概述

### 1.1 目标

构建一个综合告警中台，统一管理基础设施/应用监控告警和业务规则告警，提供告警全生命周期管理、多渠道通知分发、多租户路由、告警收敛/抑制和统计分析能力，同时作为告警能力平台供其他系统集成。

### 1.2 核心约束

- 技术栈：Python FastAPI
- 数据库：MySQL 8.0（纯 MySQL，通过分表策略处理时序数据）
- 消息队列：Kafka
- 缓存：Redis
- 部署：Kubernetes + Helm
- 前端：Vue 3 + Vite + Element Plus

### 1.3 成功标准

- 支持日均百万级告警处理
- 告警通知延迟 < 5 秒（P99）
- 支持多租户隔离
- 提供 REST API + 管理后台 + CLI 三种接入方式

## 2. 架构设计

### 2.1 架构风格

事件驱动微服务架构。各服务通过 Kafka 事件总线解耦，独立部署和扩展。

### 2.2 整体架构图

```
                          ┌──────────────────┐
                          │   Nginx Ingress   │
                          └────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
     ┌────────▼────────┐ ┌───────▼────────┐ ┌─────────▼───────┐
     │   接入服务        │ │   管理服务       │ │   前端服务       │
     │  (Gateway)       │ │  (Admin API)   │ │  (Dashboard)   │
     │                  │ │                │ │                │
     │ • Webhook 接收    │ │ • 告警规则 CRUD │ │ • 告警看板      │
     │ • Prometheus     │ │ • 路由策略配置   │ │ • 统计图表      │
     │   Alertmanager   │ │ • 通知渠道管理   │ │ • 规则配置      │
     │ • Zabbix 集成    │ │ • 用户/租户管理  │ │ • 告警认领/处理  │
     │ • 业务 SDK 接入  │ │ • 统计分析 API  │ │                │
     └────────┬────────┘ └───────┬────────┘ └────────────────┘
              │                  │
              │         ┌───────▼────────┐
              │         │   规则引擎服务   │
              │         │  (Rule Engine)  │
              │         │                │
              │         │ • 阈值规则匹配   │
              │         │ • 组合条件判断   │
              │         │ • 日志关键字匹配 │
              │         └───────┬────────┘
              │                 │
     ┌────────▼─────────────────▼────────┐
     │          Kafka (Event Bus)         │
     │                                    │
     │  Topics:                           │
     │  • alert.raw        (原始告警)      │
     │  • alert.enriched   (富化后告警)    │
     │  • alert.deduped    (去重后告警)    │
     │  • alert.notify     (待通知告警)    │
     │  • alert.lifecycle  (生命周期事件)   │
     └────────────────┬──────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
  ┌──────▼──────┐ ┌──▼───────┐ ┌─▼──────────┐
  │  处理引擎    │ │ 通知服务  │ │ 统计服务    │
  │ (Processor) │ │(Notifier)│ │ (Analytics) │
  │             │ │          │ │             │
  │ • 告警去重   │ │ • IM推送  │ │ • 实时统计  │
  │ • 告警收敛   │ │ • 短信    │ │ • MTTA/MTTR│
  │ • 告警抑制   │ │ • 邮件    │ │ • 趋势分析  │
  │ • 告警富化   │ │ • Webhook│ │ • 报表生成  │
  │ • 路由分发   │ │ • 电话    │ │             │
  │ • 优先级计算 │ │          │ │             │
  └──────┬──────┘ └────┬─────┘ └─────┬──────┘
         │              │             │
         └──────────────┼─────────────┘
                        │
              ┌─────────▼─────────┐
              │   MySQL + Redis    │
              └───────────────────┘
```

### 2.3 服务职责

| 服务 | 职责 | 独立扩展场景 |
|------|------|-------------|
| 接入服务 (Gateway) | 接收所有外部告警，标准化后写入 Kafka | 告警量暴增时 |
| 管理服务 (Admin) | CRUD、配置管理、用户/租户管理 | 管理操作频繁时 |
| 规则引擎 (Rule Engine) | 规则匹配、条件判断、日志分析 | 规则数量多/复杂时 |
| 处理引擎 (Processor) | 去重、收敛、抑制、富化、路由 | 告警处理瓶颈时 |
| 通知服务 (Notifier) | 多渠道通知分发 | 通知量大时 |
| 统计服务 (Analytics) | 聚合统计、报表、趋势分析 | 查询量大时 |
| 前端服务 (Dashboard) | 管理后台 Web UI | 用户量大时 |

## 3. 核心数据模型

### 3.1 Tenant（租户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 租户 ID |
| name | VARCHAR(100) | 租户名称 |
| status | ENUM(active/disabled) | 状态 |
| config | JSON | 租户级配置（默认通知渠道、标签等） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3.2 User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 用户 ID |
| username | VARCHAR(100) | 用户名 |
| tenant_id | BIGINT, FK | 所属租户 |
| role | ENUM(admin/operator/viewer) | 角色 |
| oncall | BOOLEAN | 是否值班 |
| phone | VARCHAR(20) | 手机号 |
| email | VARCHAR(200) | 邮箱 |
| created_at | DATETIME | 创建时间 |

### 3.3 AlertRule（告警规则）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 规则 ID |
| tenant_id | BIGINT, FK | 所属租户 |
| name | VARCHAR(200) | 规则名称 |
| source | ENUM(prometheus/zabbix/business/log/rule) | 来源类型 |
| condition | JSON | 触发条件（阈值、组合条件等） |
| severity | ENUM(P0/P1/P2/P3/P4) | 默认严重等级 |
| labels | JSON | 标签匹配规则 |
| annotations | JSON | 告警描述模板 |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3.4 Alert（告警记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID, PK | 告警 ID |
| tenant_id | BIGINT, FK | 所属租户 |
| fingerprint | VARCHAR(64) | 告警指纹（source + labels 哈希） |
| status | ENUM(pending/firing/resolved/silenced/acknowledged) | 状态 |
| source | VARCHAR(50) | 来源 |
| severity | ENUM(P0/P1/P2/P3/P4) | 严重等级 |
| labels | JSON | 业务标签 |
| annotations | JSON | 描述信息 |
| rule_id | BIGINT, FK, NULL | 关联规则 |
| assignee | BIGINT, FK, NULL | 认领人 |
| dedup_count | INT, DEFAULT 0 | 去重计数 |
| notification_count | INT, DEFAULT 0 | 通知次数 |
| started_at | DATETIME | 触发时间 |
| resolved_at | DATETIME, NULL | 解决时间 |
| last_notified_at | DATETIME, NULL | 最后通知时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

索引：tenant_id, fingerprint, status, severity, started_at

### 3.5 AlertEvent（告警事件日志）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 事件 ID |
| alert_id | UUID, FK | 关联告警 |
| action | VARCHAR(50) | 操作类型 |
| operator | VARCHAR(100), NULL | 操作人 |
| detail | JSON | 操作详情 |
| created_at | DATETIME | 创建时间 |

action 枚举值：created, deduped, converged, suppressed, silenced, notified, acknowledged, escalated, resolved

### 3.6 RoutePolicy（路由策略）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 路由 ID |
| tenant_id | BIGINT, FK | 所属租户 |
| name | VARCHAR(200) | 路由名称 |
| match_labels | JSON | 标签匹配规则 |
| priority | INT | 优先级（数字越大优先级越高） |
| targets | JSON | 通知目标（用户列表、用户组等） |
| channel_ids | JSON | 通知渠道 ID 列表 |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |

### 3.7 NotifyChannel（通知渠道）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 渠道 ID |
| tenant_id | BIGINT, FK | 所属租户 |
| name | VARCHAR(200) | 渠道名称 |
| type | ENUM(dingtalk/wechat/feishu/sms/phone/email/webhook) | 渠道类型 |
| config | JSON | 渠道配置（加密存储） |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |

### 3.8 SilencePolicy（静默策略）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 静默 ID |
| tenant_id | BIGINT, FK | 所属租户 |
| match_labels | JSON | 标签匹配规则 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| reason | VARCHAR(500) | 静默原因 |
| creator | VARCHAR(100) | 创建人 |
| created_at | DATETIME | 创建时间 |

### 3.9 AlertStats（告警统计，按月分表）

表名格式：`alert_stats_YYYYMM`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT, PK | 统计 ID |
| stat_date | DATE | 统计日期 |
| tenant_id | BIGINT, FK | 所属租户 |
| source | VARCHAR(50) | 来源 |
| severity | ENUM(P0/P1/P2/P3/P4) | 严重等级 |
| total_count | INT | 总告警数 |
| resolved_count | INT | 已解决数 |
| avg_resolve_seconds | INT | 平均解决耗时（秒） |
| notify_count | INT | 通知次数 |
| dedup_count | INT | 去重次数 |
| created_at | DATETIME | 创建时间 |

索引：stat_date, tenant_id, source, severity

## 4. 告警处理流程

### 4.1 处理流水线

```
外部告警 → 接入服务 → Kafka[alert.raw]
                              │
                              ▼
                    1. 标准化 & 校验（统一为内部格式）
                              │
                              ▼
                    2. 告警去重（fingerprint 匹配，窗口期内合并计数）
                              │
                              ▼
                    3. 静默检查（匹配 SilencePolicy → 丢弃，记录事件）
                              │
                              ▼
                    4. 告警抑制（存在同组高优先级告警 → 标记 suppressed）
                              │
                              ▼
                    5. 告警收敛（时间窗口内同标签组告警聚合为摘要）
                              │
                              ▼
                    6. 告警富化（补充业务信息、计算优先级）
                              │
                              ▼
                    7. 路由匹配（匹配 RoutePolicy，确定通知目标）
                              │
                              ▼
                    Kafka[alert.notify]
                              │
                              ▼
                    8. 通知分发（按渠道发送，记录结果）
```

### 4.2 策略说明

| 策略 | 规则 | 目的 |
|------|------|------|
| 去重 | 相同 fingerprint 的告警在窗口期内合并，计数 +1，更新 last_notified_at | 避免重复通知 |
| 静默 | 匹配 SilencePolicy 的告警直接丢弃，记录事件 | 计划内维护窗口 |
| 抑制 | 如果存在同组的更高 severity 告警，低级别告警标记为 suppressed | 减少噪音 |
| 收敛 | 时间窗口内（默认 5 分钟）同标签组的告警聚合为一条摘要通知 | 防止告警风暴 |
| 富化 | 根据规则配置补充 CMDB 信息、负责人、关联告警等 | 提供上下文 |
| 路由 | 按 labels 匹配 RoutePolicy，确定通知渠道和目标人 | 精准触达 |

### 4.3 严重等级定义

| 等级 | 名称 | 说明 | 默认通知策略 |
|------|------|------|-------------|
| P0 | 致命 | 核心服务完全不可用 | 立即通知所有值班人 + 电话 |
| P1 | 严重 | 核心功能受损 | 立即通知值班人 + IM |
| P2 | 警告 | 非核心功能异常 | 5 分钟内通知值班人 |
| P3 | 通知 | 需要关注但不紧急 | 汇总通知 |
| P4 | 信息 | 仅供记录 | 仅记录，不主动通知 |

## 5. API 设计

### 5.1 告警管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/alerts | 告警列表（分页、筛选） |
| GET | /api/v1/alerts/{id} | 告警详情 |
| POST | /api/v1/alerts/{id}/acknowledge | 认领告警 |
| POST | /api/v1/alerts/{id}/resolve | 解决告警 |
| POST | /api/v1/alerts/{id}/escalate | 升级告警 |
| GET | /api/v1/alerts/{id}/events | 告警事件日志 |

### 5.2 告警规则

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/rules | 规则列表 |
| POST | /api/v1/rules | 创建规则 |
| PUT | /api/v1/rules/{id} | 更新规则 |
| DELETE | /api/v1/rules/{id} | 删除规则 |
| POST | /api/v1/rules/{id}/enable | 启用规则 |
| POST | /api/v1/rules/{id}/disable | 禁用规则 |

### 5.3 路由策略

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/routes | 路由列表 |
| POST | /api/v1/routes | 创建路由 |
| PUT | /api/v1/routes/{id} | 更新路由 |
| DELETE | /api/v1/routes/{id} | 删除路由 |

### 5.4 通知渠道

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/channels | 渠道列表 |
| POST | /api/v1/channels | 创建渠道 |
| PUT | /api/v1/channels/{id} | 更新渠道 |
| DELETE | /api/v1/channels/{id} | 删除渠道 |
| POST | /api/v1/channels/{id}/test | 测试渠道 |

### 5.5 静默策略

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/silences | 静默列表 |
| POST | /api/v1/silences | 创建静默 |
| DELETE | /api/v1/silences/{id} | 删除静默 |

### 5.6 统计分析

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/stats/overview | 概览统计 |
| GET | /api/v1/stats/trend | 趋势数据 |
| GET | /api/v1/stats/top-sources | 告警来源排行 |
| GET | /api/v1/stats/mtta-mttr | 响应/恢复时效 |

### 5.7 租户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/tenants | 租户列表 |
| POST | /api/v1/tenants | 创建租户 |
| PUT | /api/v1/tenants/{id} | 更新租户 |

### 5.8 Webhook 接入

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/webhook/prometheus | Prometheus Alertmanager 接入 |
| POST | /api/v1/webhook/zabbix | Zabbix 接入 |
| POST | /api/v1/webhook/custom | 自定义业务告警接入 |
| POST | /api/v1/webhook/log | 日志告警接入 |

## 6. 通知渠道

| 渠道 | 实现方式 | 配置项 |
|------|---------|--------|
| 钉钉机器人 | Webhook + 签名 | webhook_url, secret, @user |
| 企业微信机器人 | Webhook | webhook_url, mentioned_list |
| 飞书机器人 | Webhook + 签名 | webhook_url, secret |
| 短信 | 阿里云 SMS SDK | access_key, sign_name, template_code |
| 电话 | 阿里云语音 SDK | access_key, called_number, tts_code |
| 邮件 | SMTP | host, port, username, password, tls |
| Webhook | HTTP POST | url, headers, body_template |

每个渠道实现为独立的 ChannelHandler 类，通过工厂模式按类型实例化，方便扩展新渠道。

## 7. 项目结构

```
alert-center/
├── helm/
│   └── alert-center/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-prod.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── gateway-deployment.yaml
│           ├── gateway-service.yaml
│           ├── admin-deployment.yaml
│           ├── admin-service.yaml
│           ├── rule-engine-deployment.yaml
│           ├── rule-engine-service.yaml
│           ├── processor-deployment.yaml
│           ├── notifier-deployment.yaml
│           ├── analytics-deployment.yaml
│           ├── celery-deployment.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-ingress.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           ├── kafka-statefulset.yaml
│           ├── mysql-statefulset.yaml
│           └── redis-statefulset.yaml
│
├── services/
│   ├── gateway/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── prometheus.py
│   │   │   ├── zabbix.py
│   │   │   ├── custom.py
│   │   │   └── log.py
│   │   ├── schemas/
│   │   └── normalizers/
│   │
│   ├── admin/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── alerts.py
│   │   │   ├── rules.py
│   │   │   ├── routes.py
│   │   │   ├── channels.py
│   │   │   ├── silences.py
│   │   │   ├── stats.py
│   │   │   └── tenants.py
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── rule-engine/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── engine/
│   │   │   ├── evaluator.py
│   │   │   ├── threshold.py
│   │   │   ├── composite.py
│   │   │   └── log_matcher.py
│   │   └── schemas/
│   │
│   ├── processor/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── workers/
│   │   │   ├── dedup.py
│   │   │   ├── silence.py
│   │   │   ├── suppress.py
│   │   │   ├── converge.py
│   │   │   ├── enrich.py
│   │   │   └── router.py
│   │   └── strategies/
│   │
│   ├── notifier/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── channels/
│   │   │   ├── base.py
│   │   │   ├── dingtalk.py
│   │   │   ├── wechat.py
│   │   │   ├── feishu.py
│   │   │   ├── sms.py
│   │   │   ├── phone.py
│   │   │   ├── email.py
│   │   │   └── webhook.py
│   │   └── dispatcher.py
│   │
│   └── analytics/
│       ├── Dockerfile
│       ├── main.py
│       ├── aggregators/
│       └── routers/
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── AlertList.vue
│   │   │   ├── AlertDetail.vue
│   │   │   ├── RuleConfig.vue
│   │   │   ├── RouteConfig.vue
│   │   │   ├── ChannelConfig.vue
│   │   │   ├── SilenceConfig.vue
│   │   │   ├── Stats.vue
│   │   │   └── TenantMgmt.vue
│   │   ├── components/
│   │   ├── api/
│   │   └── stores/
│   └── vite.config.ts
│
├── cli/
│   ├── setup.py
│   └── alertctl/
│       ├── __init__.py
│       └── commands/
│
├── shared/
│   ├── models/
│   ├── schemas/
│   ├── kafka/
│   ├── auth/
│   └── utils/
│
├── migrations/
├── configs/
│   ├── gateway.yaml
│   ├── admin.yaml
│   ├── rule-engine.yaml
│   ├── processor.yaml
│   ├── notifier.yaml
│   └── analytics.yaml
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── Makefile
└── README.md
```

## 8. 技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | 异步高性能，自动 OpenAPI 文档 |
| ORM | SQLAlchemy 2.0 + Alembic | 异步支持，数据库迁移 |
| 数据库 | MySQL 8.0 | 主数据存储 |
| 缓存 | Redis | 去重窗口、会话、缓存 |
| 消息队列 | Kafka | 事件总线，服务间解耦 |
| 异步任务 | Celery + Redis | 通知发送、统计聚合等异步任务 |
| 认证 | JWT + RBAC | 多租户权限隔离 |
| 前端 | Vue 3 + Vite + Element Plus | 管理后台 |
| CLI | Click | 命令行工具 |
| 容器化 | Docker + Kubernetes | 容器编排 |
| 包管理 | Helm | K8s 应用部署 |
| API 文档 | Swagger UI (FastAPI 自带) | 自动生成 |
| 日志 | structlog | 结构化日志 |

## 9. 部署方案

### 9.1 Helm Chart 结构

```yaml
# values.yaml 核心配置
global:
  imageRegistry: ""
  imagePullSecrets: []
  namespace: alert-center

mysql:
  enabled: true

redis:
  enabled: true

kafka:
  enabled: true

gateway:
  replicaCount: 2
  image:
    repository: alert-center/gateway
    tag: "latest"
  resources:
    limits: { cpu: 500m, memory: 512Mi }

admin:
  replicaCount: 2

processor:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilization: 70

notifier:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilization: 70

frontend:
  replicaCount: 2
  ingress:
    enabled: true
    host: alert.example.com
    tls: true
    certManager: true
```

### 9.2 K8s 特性

- HPA：processor、notifier、celery-worker 支持 CPU/自定义指标自动扩缩
- PDB：PodDisruptionBudget 保证滚动更新时服务可用
- ConfigMap + Secrets：配置与密文分离
- Ingress + cert-manager：自动 HTTPS 证书
- StatefulSet：MySQL、Redis、Kafka 有状态服务
- 健康检查：livenessProbe + readinessProbe 每个服务都配置

## 10. 告警来源接入

### 10.1 Prometheus Alertmanager

通过 Webhook 接收 Alertmanager 的告警通知，解析标准格式后写入 Kafka。

### 10.2 Zabbix

通过 Zabbix Webhook 媒体类型或 API 轮询方式接入。

### 10.3 业务系统推送

提供标准化 REST API 和 Python SDK，业务系统按规范推送告警。

### 10.4 日志告警

支持日志关键字匹配规则，对接 ELK/EFK 等日志系统。

### 10.5 自定义规则引擎

支持用户配置阈值规则、组合条件规则，由规则引擎服务定期评估。

## 11. 错误处理

- 接入服务：对格式错误的告警返回 400，记录日志但不阻塞
- 处理引擎：单个告警处理失败不影响其他告警，记录到死信队列
- 通知服务：通知失败重试 3 次（指数退避），最终失败记录到告警详情
- 所有服务：结构化日志 + 异常追踪，支持日志采集到 ELK
