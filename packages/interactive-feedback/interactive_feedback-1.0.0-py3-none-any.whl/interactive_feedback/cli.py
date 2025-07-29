# interactive_feedback/cli.py
import argparse
from .server import start_mcp_service  # 导入服务启动函数

def main():
    parser = argparse.ArgumentParser(description="MCP Feedback Service CLI.")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to the MCP service configuration file (currently not used by server).",
        required=False
    )
    # Add other arguments as needed, e.g., port, host for overrides

    args = parser.parse_args()

    print("MCP Feedback Service CLI starting...")
    if args.config:
        print(f"Configuration file specified: {args.config}")
        # 在 server.py 的 start_mcp_service 中，您可以添加逻辑来加载和使用这个配置文件
        # 例如: load_and_apply_config(args.config)
    else:
        print("No configuration file specified. Using default server settings.")

    # 启动 MCP 服务
    start_mcp_service()

    # 注意: start_mcp_service() 中的 mcp.run() 是一个阻塞调用，
    # 所以下面的 print 语句通常不会执行，除非服务正常停止。
    print("MCP Feedback Service CLI finished.")

if __name__ == "__main__":
    main()
