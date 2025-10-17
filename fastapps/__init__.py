"""
FastApps - ChatGPT Widget Framework

A zero-boilerplate framework for building interactive ChatGPT widgets.

Example:
    from fastapps import BaseWidget, Field
    from typing import Dict, Any
    
    class MyWidget(BaseWidget):
        identifier = "my_widget"
        title = "My Widget"
        
        async def execute(self, input_data) -> Dict[str, Any]:
            return {"message": "Hello from FastApps!"}
"""

__version__ = "1.0.7"
__author__ = "FastApps Team"

from .core.widget import BaseWidget, ClientContext
from .core.server import WidgetMCPServer
from .builder.compiler import WidgetBuilder, WidgetBuildResult
from .types.schema import Field, ConfigDict

# Auth exports (optional, graceful if not available)
try:
    from .auth.verifier import JWTVerifier
    from .auth import TokenVerifier, AccessToken
    _auth_exports = ["JWTVerifier", "TokenVerifier", "AccessToken"]
except ImportError:
    _auth_exports = []

__all__ = [
    "BaseWidget",
    "ClientContext",
    "WidgetMCPServer",
    "WidgetBuilder",
    "WidgetBuildResult",
    "Field",
    "ConfigDict",
] + _auth_exports

