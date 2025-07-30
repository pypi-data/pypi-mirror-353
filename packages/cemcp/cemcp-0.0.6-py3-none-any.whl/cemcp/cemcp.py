# from fastmcp import FastMCP
#
# mcp = FastMCP("cemcp")
#
# @mcp.tool
# def greet1(name: str) -> str:
#     """
#     返回小明是谁
#     """
#     return f"Hello, {name}!"
#
# def mcp_run():
#     mcp.run()
#
# if __name__ == "__main__":
#     mcp_run()

# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
def mcp_run():
    mcp.run(transport='stdio')

if __name__ == '__main__':
   mcp_run()