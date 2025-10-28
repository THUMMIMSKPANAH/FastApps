from pathlib import Path
import sys
import importlib
import inspect

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import FastApps framework
from fastapps import WidgetBuilder, WidgetMCPServer, BaseWidget
import uvicorn

PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = Path(__file__).parent / "tools"

def auto_load_tools(build_results):
    """Automatically discover and load all widget tools."""
    tools = []
    for tool_file in TOOLS_DIR.glob("*_tool.py"):
        module_name = tool_file.stem
        try:
            module = importlib.import_module(f"server.tools.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseWidget) and obj is not BaseWidget:
                    tool_identifier = obj.identifier
                    if tool_identifier in build_results:
                        tool_instance = obj(build_results[tool_identifier])
                        tools.append(tool_instance)
                        print(f"[OK] Loaded tool: {name} (identifier: {tool_identifier})")
                    else:
                        print(f"[WARNING] Warning: No build result found for tool '{tool_identifier}'")
        except Exception as e:
            print(f"[ERROR] Error loading {tool_file.name}: {e}")
    return tools

# Build all widgets
builder = WidgetBuilder(PROJECT_ROOT)
build_results = builder.build_all()

# Auto-load and register tools
tools = auto_load_tools(build_results)

# Create MCP server
server = WidgetMCPServer(name="my-widgets", widgets=tools)

# Optional: Enable OAuth 2.1 authentication
# Uncomment and configure to protect your widgets with OAuth:
#
# server = WidgetMCPServer(
#     name="my-widgets",
#     widgets=tools,
#     auth_issuer_url="https://your-tenant.us.auth0.com",
#     auth_resource_server_url="https://yourdomain.com/mcp",
#     auth_required_scopes=["user"],
# )
#
# See docs: https://fastapps.dev/docs/auth

app = server.get_app()

if __name__ == "__main__":
    print(f"\n[START] Starting server with {len(tools)} tools")
    uvicorn.run(app, host="0.0.0.0", port=8001)
