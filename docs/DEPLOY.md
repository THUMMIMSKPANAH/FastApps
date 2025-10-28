# FastApps Deployment Server API Specification

This document specifies the API that the FastApps deployment server must implement to support the `fastapps deploy` command.

## Overview

The deployment server provides OAuth 2.1 authentication with PKCE and accepts deployment artifacts for publishing FastApps projects.

**Base URL**: `https://deploy.fastapps.org` (configurable)

## Configuration

### Environment Variables

You can configure the deployment server URL using environment variables:

```bash
# Option 1: Set environment variable directly
export FASTAPPS_DEPLOY_URL=https://your-custom-server.com

# Option 2: Create .env file in your project root
echo "FASTAPPS_DEPLOY_URL=https://your-custom-server.com" > .env
```

**Priority Order:**
1. `--url` command-line flag (highest priority)
2. `FASTAPPS_DEPLOY_URL` environment variable
3. Saved URL in `~/.fastapps/config.json`
4. Default: `https://deploy.fastapps.org` (lowest priority)

**Example `.env` file:**
```bash
# Deployment Configuration
FASTAPPS_DEPLOY_URL=https://deploy.example.com
```

> **Note:** The `.env` file is automatically gitignored to prevent accidental exposure of sensitive configuration.

## Authentication

### OAuth 2.1 with PKCE

The server uses Clerk for OAuth authentication with PKCE (Proof Key for Code Exchange) flow.

#### 1. Authorization Endpoint

**Endpoint**: `GET /oauth/authorize`

**Description**: Redirects user to Clerk authentication page.

**Query Parameters**:
```
client_id=fastapps-cli
response_type=code
redirect_uri=http://localhost:8765/callback
code_challenge=<SHA256_HASH>
code_challenge_method=S256
scope=deploy
```

**Response**: HTTP 302 redirect to Clerk authorization page

**Success**: Redirects to `redirect_uri` with authorization code:
```
http://localhost:8765/callback?code=<AUTHORIZATION_CODE>
```

**Error**: Redirects to `redirect_uri` with error:
```
http://localhost:8765/callback?error=<ERROR_CODE>&error_description=<DESCRIPTION>
```

#### 2. Token Endpoint

**Endpoint**: `POST /oauth/token`

**Description**: Exchange authorization code for access token.

**Request Headers**:
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body** (form-encoded):
```
grant_type=authorization_code
client_id=fastapps-cli
code=<AUTHORIZATION_CODE>
redirect_uri=http://localhost:8765/callback
code_verifier=<PKCE_VERIFIER>
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "deploy"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "invalid_grant",
  "error_description": "Invalid authorization code"
}
```

## Deployment API

### Deploy Project

**Endpoint**: `POST /deploy`

**Description**: Upload and deploy a FastApps project artifact.

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: multipart/form-data
```

**Request Body** (multipart/form-data):
```
artifact: <deployment.tar.gz file>
```

**Artifact Format**: tar.gz archive containing:
- `.fastapps-manifest.json` - Deployment manifest (see Manifest Format below)
- `assets/` - Built widget HTML files
- `server/` - Python backend code
- `package.json` - Node.js dependencies
- `requirements.txt` - Python dependencies
- Optional: `README.md`, `.env.example`

**Success Response** (200 OK):
```json
{
  "success": true,
  "deployment_id": "dep_abc123xyz",
  "url": "https://myproject-abc123.fastapps.app",
  "message": "Deployment successful",
  "timestamp": "2025-10-28T10:30:00Z"
}
```

**Error Responses**:

**401 Unauthorized** - Invalid or expired token:
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired access token"
}
```

**400 Bad Request** - Invalid artifact:
```json
{
  "error": "invalid_artifact",
  "message": "Missing required file: server/main.py"
}
```

**413 Payload Too Large** - Artifact too large:
```json
{
  "error": "payload_too_large",
  "message": "Artifact must be less than 100MB",
  "max_size_mb": 100
}
```

**500 Internal Server Error** - Server error:
```json
{
  "error": "internal_error",
  "message": "Deployment failed due to server error"
}
```

## Manifest Format

The `.fastapps-manifest.json` file in the deployment artifact contains project metadata:

```json
{
  "fastapps_version": "1.1.1",
  "timestamp": "2025-10-28T10:30:00Z",
  "project_name": "my-fastapps-project",
  "widgets": ["weather", "calculator", "todo"],
  "dependencies": {
    "python": [
      "fastapps>=1.1.0",
      "httpx>=0.25.0"
    ],
    "node": {
      "react": "^18.3.1",
      "react-dom": "^18.3.1",
      "fastapps": "^1.0.0"
    }
  }
}
```

**Fields**:
- `fastapps_version`: Version of FastApps framework used
- `timestamp`: ISO 8601 timestamp of deployment creation
- `project_name`: Project identifier from package.json
- `widgets`: Array of widget identifiers found in assets/
- `dependencies.python`: Array of Python package specifications from requirements.txt
- `dependencies.node`: Object of Node.js package name to version from package.json

## Security Considerations

### PKCE Implementation

The client generates a cryptographically random `code_verifier` (64 URL-safe characters) and computes the `code_challenge` using SHA256:

```python
code_verifier = secrets.token_urlsafe(64)
code_challenge = hashlib.sha256(code_verifier.encode()).digest().hex()
```

The server must:
1. Store the `code_challenge` with the authorization code
2. Validate the `code_verifier` on token exchange by computing SHA256 and comparing with stored challenge
3. Reject token exchange if verification fails

### Token Validation

The server must validate:
- Bearer token is present in Authorization header
- Token is valid and not expired
- Token has the `deploy` scope
- Token is associated with a valid Clerk user

### Rate Limiting

Recommended rate limits:
- OAuth authorization: 10 requests per minute per IP
- Token exchange: 5 requests per minute per client_id
- Deployment: 10 deployments per hour per user

### Artifact Validation

The server must validate:
- Artifact is valid tar.gz format
- Artifact size is under limit (recommended: 100MB)
- Manifest file exists and is valid JSON
- Required files exist: `server/main.py`, `package.json`, `requirements.txt`
- No malicious file paths (e.g., `../../../etc/passwd`)

## Example Deployment Flow

```
1. User runs: fastapps deploy

2. CLI validates project structure

3. CLI builds widgets: npm run build

4. CLI checks for saved token in ~/.fastapps/config.json

5. If no token:
   a. CLI generates PKCE pair
   b. CLI starts local server on :8765
   c. CLI opens browser to /oauth/authorize
   d. User authorizes in browser
   e. Server redirects to localhost:8765/callback?code=...
   f. CLI exchanges code for token via /oauth/token
   g. CLI saves token to config.json

6. CLI packages artifacts into tar.gz

7. CLI uploads to POST /deploy with Bearer token

8. Server validates token, unpacks artifact, deploys project

9. Server responds with deployment URL

10. CLI displays success message with URL
```

## Implementation Notes for Server

### Clerk Configuration

The server should configure Clerk with:
- Client ID: `fastapps-cli`
- Redirect URI: `http://localhost:8765/callback`
- Grant types: `authorization_code`
- Token endpoint authentication: `none` (PKCE provides security)
- Scopes: `deploy`

### Deployment Process

The server should:
1. Validate and extract tar.gz artifact
2. Read and validate `.fastapps-manifest.json`
3. Provision deployment environment (container, VM, etc.)
4. Install Python dependencies from `requirements.txt`
5. Install Node.js dependencies from `package.json`
6. Copy server code and assets to deployment environment
7. Configure environment variables (if needed)
8. Start FastApps server via `uvicorn server.main:app`
9. Configure reverse proxy/load balancer
10. Generate unique deployment URL
11. Store deployment metadata
12. Return deployment URL to client

### Deployment URL Format

Recommended URL format:
```
https://{project_name}-{short_id}.fastapps.app
```

Example:
```
https://my-widgets-a1b2c3.fastapps.app
```

## Version History

- **v1.0** (2025-10-28): Initial API specification
