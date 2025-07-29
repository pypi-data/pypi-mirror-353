# ai-xone-mcp-workflow

本模块是 AI Xone MCP 的工作流服务实现，基于 [fastmcp](https://pypi.org/project/fastmcp/) 框架，提供了调度大模型按指定工作流执行任务的能力。

## 主要功能

- 工作流的定义、执行、调度等

## 依赖

- Python >=3.10,<4.0
- fastmcp==2.3.5
- pyyaml==6.0.1

## 快速开始

1. 下载本模块
   ```bash
   git clone https://github.com/ai-xone/mcp
   ```

2. 安装依赖
   ```bash
   poetry install
   ```
3. 构建
   ```bash
    python -m build
   ```
4. 上传到pypi
   ```bash
   twine upload dist/*
   ```
5. 在 `mcp.json` 中添加以下配置

```json
{
  "mcpServers": {
    "ai-xone-mcp-workflow": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

## 参考

- [fastmcp 文档](https://pypi.org/project/fastmcp/)
- [awslabs/mcp 官方文档](https://github.com/awslabs/mcp/blob/main/src/amazon-kendra-index-mcp-server/README.md)

