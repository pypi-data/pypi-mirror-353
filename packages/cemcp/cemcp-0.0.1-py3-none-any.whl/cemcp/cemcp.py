from fastmcp import FastMCP

mcp = FastMCP("cemcp")

@mcp.tool
def greet(name: str) -> str:
    """
    返回小明是谁
    """
    return f"Hello, {name}!"

def main():
    mcp.run()

if __name__ == "__main__":
    main()