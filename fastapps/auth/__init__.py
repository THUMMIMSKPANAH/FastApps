"""
FastApps Authentication Module

Provides built-in JWT verification and re-exports FastMCP auth components.
"""

from .verifier import JWTVerifier

# Re-export FastMCP auth components for convenience
try:
    from mcp.server.auth.provider import TokenVerifier, AccessToken
except ImportError:
    # Graceful fallback if fastmcp version doesn't have auth
    TokenVerifier = None
    AccessToken = None

__all__ = [
    "JWTVerifier",
    "TokenVerifier",
    "AccessToken",
]

