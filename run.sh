#!/bin/bash
# BioMedAgent 启动脚本
# 用法: ./run.sh <task_type>
# task_type 可选: machine_learning | statistics_t_test | statistics_qq_plot | visualization_survival_plot | visualization_violin_plot | omics

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TASK=${1:-machine_learning}
REDIS_BIN="/tmp/redis-stable/src/redis-server"
VENV_PYTHON="./venv/bin/python"

# 检查 API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ 请先设置 OPENAI_API_KEY: export OPENAI_API_KEY='your-key'"
    exit 1
fi

# 启动 Redis (如果未运行)
if ! /tmp/redis-stable/src/redis-cli ping > /dev/null 2>&1; then
    echo "▶ 启动 Redis..."
    $REDIS_BIN --daemonize yes --logfile /tmp/redis.log --port 6379
    sleep 1
fi
echo "✓ Redis 运行中"

# 创建必要目录
mkdir -p BioLog log task

echo "▶ 运行任务: $TASK"
$VENV_PYTHON demo.py --task "$TASK"
