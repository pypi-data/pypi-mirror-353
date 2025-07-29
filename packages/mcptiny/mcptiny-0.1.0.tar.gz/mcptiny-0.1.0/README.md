# MCPTiny

MCPTiny 是一个基于 Model Context Protocol (MCP) 的最小化服务示例，用于演示如何创建和使用 MCP 服务器。

## 安装要求

- Python 3.13 或更高版本
- FastMCP 库

## 安装方法

### 通过 pip 安装

```bash
pip install mcptiny
```

### 从源代码安装

```bash
git clone https://github.com/lvst-gh/mcptiny.git
cd mcptiny
pip install -e .
```

## 使用方法

### 在 Amazon Q 中配置

在 Amazon Q 配置文件中添加以下配置：

```json
{
  "mcp-servers": {
    "mcptiny": {
      "command": "uvx",
      "args": [
        "mcptiny@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

## 功能

- `list_files`: 获取指定路径下的文件列表

## 许可证

MIT
