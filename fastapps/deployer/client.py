"""HTTP client for FastApps deployment API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    success: bool
    deployment_url: Optional[str] = None
    deployment_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class DeployClient:
    """Client for interacting with FastApps deployment server."""

    def __init__(self, base_url: str, access_token: str):
        """
        Initialize deployment client.

        Args:
            base_url: Base URL of deployment server
            access_token: OAuth access token
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialized HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
        return self._client

    async def deploy(self, tarball_path: Path) -> DeploymentResult:
        """
        Deploy artifact to server.

        Args:
            tarball_path: Path to deployment tarball

        Returns:
            DeploymentResult with deployment information

        Raises:
            RuntimeError: If deployment fails
        """
        try:
            # Read tarball content to avoid file handle issues
            with open(tarball_path, "rb") as f:
                file_content = f.read()

            files = {"artifact": ("deployment.tar.gz", file_content, "application/gzip")}

            # Send deployment request
            response = await self.client.post(
                f"{self.base_url}/deploy",
                files=files,
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            # Handle response
            if response.status_code == 200:
                data = response.json()
                return DeploymentResult(
                    success=True,
                    deployment_url=data.get("url"),
                    deployment_id=data.get("deployment_id"),
                    message=data.get("message", "Deployment successful"),
                )
            elif response.status_code == 401:
                return DeploymentResult(
                    success=False,
                    error="Authentication failed. Please run 'fastapps deploy' again to re-authenticate.",
                )
            elif response.status_code == 400:
                # Fix: Check if content-type contains json (handles charset)
                content_type = response.headers.get("content-type", "")
                data = response.json() if "application/json" in content_type else {}
                error_msg = data.get("error", response.text)
                return DeploymentResult(
                    success=False,
                    error=f"Invalid deployment package: {error_msg}",
                )
            else:
                return DeploymentResult(
                    success=False,
                    error=f"Deployment failed: {response.status_code} - {response.text}",
                )

        except httpx.ConnectError as e:
            return DeploymentResult(
                success=False,
                error=f"Connection error: Cannot reach deployment server",
            )
        except httpx.TimeoutException as e:
            return DeploymentResult(
                success=False,
                error=f"Network timeout: Request took too long",
            )
        except httpx.RequestError as e:
            return DeploymentResult(
                success=False,
                error=f"Network error during deployment: {e}",
            )
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=f"Unexpected error: {e}",
            )

    async def close(self):
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
