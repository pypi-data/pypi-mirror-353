import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()  # 初始化 MCP 服务实例

@mcp.tool()
def get_desktop_files(path: str = "/Users/zwguo/Documents/VSCodeFolder/ec2-price/mcp-awspricing"):
    """获取指定路径下的文件列表，默认为原有路径。若无权限或路径不存在，返回错误信息。"""
    try:
        return os.listdir(os.path.expanduser(path))
    except PermissionError:
        return f"Permission denied: {path}"
    except FileNotFoundError:
        return f"Path not found: {path}"
    except Exception as e:
        return f"Error accessing {path}: {e}"

def main():
    mcp.run(transport='stdio')  # 启动服务，使用标准输入输出通信

if __name__ == "__main__":
    main()
