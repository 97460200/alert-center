#!/bin/bash
# Alert Center Kubernetes 部署脚本

set -e

NAMESPACE="alert-center"
HELM_CHART="./helm/alert-center"
VALUES_FILE="./helm/alert-center/values-prod.yaml"

echo "=========================================="
echo "  Alert Center Kubernetes 部署脚本"
echo "=========================================="
echo ""

# 检查 kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl 未安装"
    exit 1
fi

# 检查 helm
if ! command -v helm &> /dev/null; then
    echo "❌ Helm 未安装"
    exit 1
fi

echo "✅ kubectl 和 helm 已安装"
echo ""

# 创建命名空间
echo "📦 创建命名空间: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# 添加依赖仓库
echo "📦 添加 Helm 依赖仓库"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 安装依赖 (MySQL, Redis, Kafka)
echo "📦 安装基础设施 (MySQL, Redis, Kafka)"

# 安装 MySQL
helm upgrade --install mysql bitnami/mysql \
  --namespace $NAMESPACE \
  --set auth.rootPassword=alertcenter123 \
  --set auth.database=alert_center \
  --set auth.username=alert \
  --set auth.password=alert123 \
  --set primary.persistence.enabled=true \
  --set primary.persistence.size=10Gi \
  --wait --timeout 300s

# 安装 Redis
helm upgrade --install redis bitnami/redis \
  --namespace $NAMESPACE \
  --set auth.enabled=false \
  --set master.persistence.enabled=true \
  --set master.persistence.size=5Gi \
  --wait --timeout 300s

# 安装 Kafka
helm upgrade --install kafka bitnami/kafka \
  --namespace $NAMESPACE \
  --set auth.clientProtocol=plaintext \
  --set auth.interBrokerProtocol=plaintext \
  --set persistence.enabled=true \
  --set persistence.size=10Gi \
  --wait --timeout 300s

echo ""
echo "✅ 基础设施安装完成"
echo ""

# 等待基础设施就绪
echo "⏳ 等待基础设施就绪..."
sleep 10

# 安装 Alert Center
echo "📦 安装 Alert Center 服务"
helm upgrade --install alert-center $HELM_CHART \
  --namespace $NAMESPACE \
  --values $VALUES_FILE \
  --wait --timeout 600s

echo ""
echo "=========================================="
echo "  ✅ 部署完成!"
echo "=========================================="
echo ""
echo "查看服务状态:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "查看服务:"
echo "  kubectl get svc -n $NAMESPACE"
echo ""
echo "前端访问地址:"
echo "  kubectl get ingress -n $NAMESPACE"
echo ""
echo "Gateway API 端口转发:"
echo "  kubectl port-forward svc/gateway 8001:8001 -n $NAMESPACE"
echo ""
echo "Admin API 端口转发:"
echo "  kubectl port-forward svc/admin 8002:8002 -n $NAMESPACE"
echo ""
