import time
from hello_agents.tools.builtin.protocol_tools import MCPTool

def main():
    print("🚀 初始化支持 SSE 的 MCPTool...")
    
    # 将配置字典传递给 server 参数，MCPClient 会自动识别为配置传输
    sse_config = {
        "transport": "sse",
        "url": "http://localhost:8000/sse"
    }
    
    arxiv_tool = MCPTool(
        name="arxiv_mcp",
        server=sse_config
    )
    
    print("\n🛠️ 可用工具列表 (从远端 Server 获取):")
    for t in getattr(arxiv_tool, "_available_tools", []):
         print(f"  - {t.get('name')}: {t.get('description', '')[:50]}...")

    print("\n🔍 给远端 Server 发送检索指令...")
    try:
        res = arxiv_tool.run({
            "action": "call_tool",
            "tool_name": "search_papers",
            "arguments": {
                "query": '"machine learning"',
                "max_results": 2
            }
        })
        print("\n✅ 返回结果成功:")
        print(res)
    except Exception as e:
        print(f"\n❌ 操作发生错误: {e}")

if __name__ == "__main__":
    main()

