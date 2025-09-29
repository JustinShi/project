# 📊 监控指南

本文档介绍如何监控 Python 多项目平台的运行状态和性能指标。

## 📋 监控概述

### 监控目标

- **可用性监控**: 确保服务正常运行
- **性能监控**: 监控系统性能指标
- **资源监控**: 监控 CPU、内存、磁盘、网络使用
- **业务监控**: 监控关键业务指标
- **安全监控**: 监控安全事件和异常

### 监控架构

```
[应用服务] → [指标收集] → [监控系统] → [告警通知]
     ↓              ↓           ↓           ↓
[日志输出] → [日志聚合] → [可视化] → [邮件/短信/钉钉]
```

## 🛠️ 监控工具

### 系统监控

- **Prometheus**: 指标收集和存储
- **Grafana**: 数据可视化和告警
- **Node Exporter**: 系统指标导出
- **cAdvisor**: 容器指标监控

### 应用监控

- **自定义指标**: 应用业务指标
- **健康检查**: 服务健康状态
- **性能分析**: 响应时间和吞吐量
- **错误追踪**: 异常和错误监控

### 日志监控

- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **Fluentd**: 日志收集和转发
- **Graylog**: 日志管理和分析

## 🚀 快速开始

### 安装监控工具

```bash
# 创建监控目录
mkdir -p monitoring
cd monitoring

# 下载 Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar -xzf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0

# 下载 Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar -xzf node_exporter-1.6.1.linux-amd64.tar.gz
```

### Docker Compose 部署

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

  # cAdvisor
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

## 🔧 配置监控

### Prometheus 配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  # 监控 Prometheus 自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # 监控 Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # 监控 cAdvisor
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # 监控应用服务
  - job_name: 'myplatform-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # 监控 Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  # 监控 MySQL
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql:3306']
```

### 告警规则配置

```yaml
# monitoring/alert_rules.yml
groups:
  - name: system_alerts
    rules:
      # CPU 使用率告警
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes"

      # 内存使用率告警
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 5 minutes"

      # 磁盘使用率告警
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage on {{ $labels.instance }}"
          description: "Disk usage is above 90% for more than 5 minutes"

  - name: application_alerts
    rules:
      # 应用响应时间告警
      - alert: HighResponseTime
        expr: http_request_duration_seconds > 2
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time on {{ $labels.instance }}"
          description: "Response time is above 2 seconds"

      # 错误率告警
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
          description: "Error rate is above 5% for more than 5 minutes"

  - name: service_alerts
    rules:
      # Redis 连接告警
      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down on {{ $labels.instance }}"
          description: "Redis service is not responding"

      # MySQL 连接告警
      - alert: MySQLDown
        expr: mysql_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MySQL is down on {{ $labels.instance }}"
          description: "MySQL service is not responding"
```

## 📊 应用指标收集

### 自定义指标

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client.exposition import start_http_server
import time

# 请求计数器
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 请求持续时间
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# 活跃连接数
ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

# 业务指标
USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total user registrations'
)

TRADE_VOLUME = Counter(
    'trade_volume_total',
    'Total trading volume',
    ['symbol', 'side']
)

# 性能指标
PROCESSING_TIME = Summary(
    'data_processing_seconds',
    'Time spent processing data'
)

# 启动指标服务器
def start_metrics_server(port=8000):
    """启动指标服务器"""
    start_http_server(port)
    print(f"Metrics server started on port {port}")

# 中间件装饰器
def track_metrics(func):
    """跟踪请求指标的装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            REQUEST_COUNT.labels(
                method='GET',
                endpoint=func.__name__,
                status=200
            ).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(
                method='GET',
                endpoint=func.__name__,
                status=500
            ).inc()
            raise e
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method='GET',
                endpoint=func.__name__
            ).observe(duration)
    
    return wrapper
```

### 健康检查端点

```python
# monitoring/health_check.py
from flask import Flask, jsonify
from common.storage.redis_client import RedisClient
from common.storage.db_client import DatabaseManager
import psutil
import time

app = Flask(__name__)

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        self.db_manager = DatabaseManager()
    
    def check_system_health(self):
        """检查系统健康状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
    
    def check_redis_health(self):
        """检查 Redis 健康状态"""
        try:
            # 简单的 ping 测试
            self.redis_client.ping()
            return {"status": "healthy", "service": "redis"}
        except Exception as e:
            return {"status": "unhealthy", "service": "redis", "error": str(e)}
    
    def check_database_health(self):
        """检查数据库健康状态"""
        try:
            self.db_manager.ping()
            return {"status": "healthy", "service": "database"}
        except Exception as e:
            return {"status": "unhealthy", "service": "database", "error": str(e)}
    
    def comprehensive_health_check(self):
        """综合健康检查"""
        system_health = self.check_system_health()
        redis_health = self.check_redis_health()
        db_health = self.check_database_health()
        
        overall_status = "healthy"
        if any(check["status"] == "unhealthy" for check in [system_health, redis_health, db_health]):
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "checks": {
                "system": system_health,
                "redis": redis_health,
                "database": db_health
            }
        }

health_checker = HealthChecker()

@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify(health_checker.comprehensive_health_check())

@app.route('/health/ready')
def ready():
    """就绪检查端点"""
    return jsonify({"status": "ready"})

@app.route('/health/live')
def live():
    """存活检查端点"""
    return jsonify({"status": "alive"})

@app.route('/metrics')
def metrics():
    """Prometheus 指标端点"""
    # 这里应该返回 Prometheus 格式的指标
    # 实际实现中应该使用 prometheus_client
    return "metrics endpoint"
```

## 📈 Grafana 仪表板

### 系统监控仪表板

```json
{
  "dashboard": {
    "title": "System Monitoring",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU %"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory %"
          }
        ]
      },
      {
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100",
            "legendFormat": "Disk %"
          }
        ]
      },
      {
        "title": "Network Traffic",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total[5m])",
            "legendFormat": "Receive"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total[5m])",
            "legendFormat": "Transmit"
          }
        ]
      }
    ]
  }
}
```

### 应用监控仪表板

```json
{
  "dashboard": {
    "title": "Application Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          },
          {
            "expr": "rate(http_requests_total{status=~\"4..\"}[5m])",
            "legendFormat": "4xx errors"
          }
        ]
      },
      {
        "title": "Active Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "http_active_connections",
            "legendFormat": "Active Connections"
          }
        ]
      }
    ]
  }
}
```

## 🔔 告警通知

### 告警管理器配置

```yaml
# monitoring/alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'

  - name: 'slack'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```

### 告警通知实现

```python
# monitoring/alert_notifier.py
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from common.logging.logger import get_logger

logger = get_logger(__name__)

class AlertNotifier:
    """告警通知器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logger
    
    def send_email_alert(self, alert):
        """发送邮件告警"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from']
            msg['To'] = self.config['email']['to']
            msg['Subject'] = f"Alert: {alert['summary']}"
            
            body = f"""
            Alert Details:
            - Summary: {alert['summary']}
            - Description: {alert['description']}
            - Severity: {alert['severity']}
            - Instance: {alert['instance']}
            - Time: {alert['timestamp']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent: {alert['summary']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, alert):
        """发送 Slack 告警"""
        try:
            webhook_url = self.config['slack']['webhook_url']
            
            message = {
                "text": f"🚨 *Alert: {alert['summary']}*",
                "attachments": [
                    {
                        "color": "danger" if alert['severity'] == 'critical' else "warning",
                        "fields": [
                            {
                                "title": "Description",
                                "value": alert['description'],
                                "short": False
                            },
                            {
                                "title": "Severity",
                                "value": alert['severity'],
                                "short": True
                            },
                            {
                                "title": "Instance",
                                "value": alert['instance'],
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            
            self.logger.info(f"Slack alert sent: {alert['summary']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    def send_dingtalk_alert(self, alert):
        """发送钉钉告警"""
        try:
            webhook_url = self.config['dingtalk']['webhook_url']
            
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"🚨 告警: {alert['summary']}",
                    "text": f"""
                    ### 🚨 系统告警
                    
                    **描述**: {alert['description']}
                    
                    **严重程度**: {alert['severity']}
                    
                    **实例**: {alert['instance']}
                    
                    **时间**: {alert['timestamp']}
                    """
                }
            }
            
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            
            self.logger.info(f"DingTalk alert sent: {alert['summary']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send DingTalk alert: {e}")
    
    def notify(self, alert):
        """发送告警通知"""
        # 根据配置发送不同类型的通知
        if self.config.get('email', {}).get('enabled', False):
            self.send_email_alert(alert)
        
        if self.config.get('slack', {}).get('enabled', False):
            self.send_slack_alert(alert)
        
        if self.config.get('dingtalk', {}).get('enabled', False):
            self.send_dingtalk_alert(alert)
```

## 📊 日志监控

### 日志收集配置

```yaml
# monitoring/fluentd.conf
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/fluentd/app.log.pos
  tag app.logs
  format json
  time_key timestamp
</source>

<filter app.logs>
  @type parser
  key_name message
  <parse>
    @type regexp
    expression /^(?<level>\w+)\s+(?<message>.*)$/
  </parse>
</filter>

<match app.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name app-logs
  type_name _doc
  logstash_format true
  logstash_prefix app-logs
  <buffer>
    @type file
    path /var/log/fluentd/buffer
    flush_interval 5s
    chunk_limit_size 2M
    queue_limit_length 8
  </buffer>
</match>
```

### 日志分析查询

```python
# monitoring/log_analyzer.py
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import json

class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, es_host='localhost', es_port=9200):
        self.es = Elasticsearch([{'host': es_host, 'port': es_port}])
    
    def get_error_logs(self, hours=24):
        """获取错误日志"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"level": "ERROR"}},
                        {"range": {
                            "@timestamp": {
                                "gte": f"now-{hours}h",
                                "lte": "now"
                            }
                        }}
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 100
        }
        
        response = self.es.search(index="app-logs", body=query)
        return response['hits']['hits']
    
    def get_error_summary(self, hours=24):
        """获取错误摘要"""
        query = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": f"now-{hours}h",
                        "lte": "now"
                    }
                }
            },
            "aggs": {
                "error_levels": {
                    "terms": {"field": "level.keyword"}
                },
                "error_timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "interval": "1h"
                    }
                }
            }
        }
        
        response = self.es.search(index="app-logs", body=query)
        return response['aggregations']
    
    def search_logs(self, query_text, hours=24):
        """搜索日志"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query_text}},
                        {"range": {
                            "@timestamp": {
                                "gte": f"now-{hours}h",
                                "lte": "now"
                            }
                        }}
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 100
        }
        
        response = self.es.search(index="app-logs", body=query)
        return response['hits']['hits']
```

## 🚨 故障排除

### 常见监控问题

#### 1. Prometheus 无法抓取指标

```bash
# 检查目标状态
curl http://localhost:9090/api/v1/targets

# 检查配置
curl http://localhost:9090/api/v1/status/config

# 查看日志
docker logs prometheus
```

#### 2. Grafana 无法连接数据源

```bash
# 检查 Prometheus 连接
curl http://prometheus:9090/api/v1/query?query=up

# 检查网络连接
docker exec grafana ping prometheus

# 查看 Grafana 日志
docker logs grafana
```

#### 3. 告警不触发

```bash
# 检查告警规则
curl http://localhost:9090/api/v1/rules

# 检查告警状态
curl http://localhost:9090/api/v1/alerts

# 检查告警管理器
curl http://localhost:9093/api/v1/alerts
```

### 性能优化

```python
# 指标收集优化
import time
from functools import wraps

def measure_time(func):
    """测量函数执行时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # 记录执行时间
        PROCESSING_TIME.observe(duration)
        
        return result
    return wrapper

# 使用示例
@measure_time
def process_data(data):
    """处理数据"""
    time.sleep(0.1)  # 模拟处理时间
    return data.upper()
```

## 📚 下一步

- 查看 [生产环境部署](production.md)
- 了解 [Docker 部署指南](docker.md)
- 阅读 [快速开始](../getting-started/quickstart.md)

## 🤝 获取帮助

如果遇到监控问题：

1. 检查服务状态
2. 查看错误日志
3. 验证配置文件
4. 联系技术支持
