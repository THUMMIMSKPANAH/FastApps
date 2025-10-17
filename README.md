# FastApps Framework

<p align="center">
  <strong>A zero-boilerplate framework for building interactive ChatGPT widgets</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/v/fastapps.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/pyversions/fastapps.svg" alt="Python"></a>
  <a href="https://github.com/fastapps-framework/fastapps/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

📚 **Documentation**: [https://www.fastapps.org/](https://www.fastapps.org/)

👥 **Community**: [Join Our Discord](https://discord.gg/5cEy3Jqek3)

---

## Quick Start

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### 2. Install FastApps & Create Project

```bash
pip install fastapps
fastapps init my-app
```

This generates the complete project structure:

```
my-app/
├── server/
│   ├── __init__.py
│   ├── main.py              # Auto-discovery server
│   ├── tools/               # Widget backends
│   │   └── __init__.py
│   └── api/                 # (optional) Shared APIs
│       └── __init__.py
├── widgets/                 # Widget frontends (empty initially)
├── requirements.txt         # Python dependencies
├── package.json             # JavaScript dependencies
├── .gitignore
└── README.md
```

### 3. Install Dependencies

```bash
cd my-app
pip install -r requirements.txt
npm install
```

### 4. Create Your First Widget

```bash
fastapps create my-widget
```

This adds to your project:

```
my-app/
├── server/
│   └── tools/
│       └── my_widget_tool.py # ← Generated: Widget backend
└── widgets/
    └── my-widget/
        └── index.jsx         # ← Generated: Widget frontend
```

### 5. Edit Your Widget Code

**You only need to edit these 2 files:**

#### `server/tools/my_widget_tool.py` - Backend Logic

```python
from fastapps import BaseWidget, Field, ConfigDict
from pydantic import BaseModel
from typing import Dict, Any

class MyWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(default="World")

class MyWidgetTool(BaseWidget):
    identifier = "my-widget"
    title = "My Widget"
    input_schema = MyWidgetInput
    invoking = "Processing..."
    invoked = "Done!"
    
    widget_csp = {
        "connect_domains": [],      # APIs you'll call
        "resource_domains": []      # Images/fonts you'll use
    }
    
    async def execute(self, input_data: MyWidgetInput) -> Dict[str, Any]:
        # Your logic here
        return {
            "name": input_data.name,
            "message": f"Hello, {input_data.name}!"
        }
```

#### `widgets/my-widget/index.jsx` - Frontend UI

```jsx
import React from 'react';
import { useWidgetProps } from 'fastapps';

export default function MyWidget() {
  const props = useWidgetProps();
  
  return (
    <div style={{
      padding: '40px',
      textAlign: 'center',
      background: '#4A90E2',
      color: 'white',
      borderRadius: '12px'
    }}>
      <h1>{props.message}</h1>
      <p>Welcome, {props.name}!</p>
    </div>
  );
}
```

**That's it! These are the only files you need to write.**

### 6. Build Widgets

```bash
npm run build
```

### 7. Start Development Server with Public Access

**Option A: Using `fastapps dev` (Recommended)**

The easiest way to run and expose your server:

```bash
fastapps dev
```

On first run, you'll be prompted for your ngrok auth token:
- Get it free at: https://dashboard.ngrok.com/get-started/your-authtoken
- Token is saved and won't be asked again

You'll see:
```
🚀 FastApps Development Server
┌─────────┬─────────────────────────┐
│ Local   │ http://0.0.0.0:8001    │
│ Public  │ https://xyz.ngrok.io   │
└─────────┴─────────────────────────┘

📡 MCP Server Endpoint: https://xyz.ngrok.io
```

Use the public URL in ChatGPT Settings > Connectors.

**Option B: Manual Setup**

```bash
# Start server
python server/main.py

# In a separate terminal, create tunnel
ngrok http 8001
```

---

## What You Need to Know

### Widget Structure

Every widget has **exactly 2 files you write**:

1. **Python Tool** (`server/tools/*_tool.py`)
   - Define inputs with Pydantic
   - Write your logic in `execute()`
   - Return data as a dictionary

2. **React Component** (`widgets/*/index.jsx`)
   - Get data with `useWidgetProps()`
   - Render your UI
   - Use inline styles

**Everything else is automatic:**
- Widget discovery
- Registration
- Build process
- Server setup
- Mounting logic

### Input Schema

```python
from fastapps import Field, ConfigDict
from pydantic import BaseModel

class MyInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(default="", description="User's name")
    age: int = Field(default=0, ge=0, le=150)
    email: str = Field(default="", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

### CSP (Content Security Policy)

Allow external resources:

```python
widget_csp = {
    "connect_domains": ["https://api.example.com"],     # For API calls
    "resource_domains": ["https://cdn.example.com"]     # For images/fonts
}
```

### React Hooks

```jsx
import { useWidgetProps, useWidgetState, useOpenAiGlobal } from 'fastapps';

function MyWidget() {
  const props = useWidgetProps();              // Data from Python
  const [state, setState] = useWidgetState({}); // Persistent state
  const theme = useOpenAiGlobal('theme');      // ChatGPT theme
  
  return <div>{props.message}</div>;
}
```

---

## Documentation

- **[Quick Start Guide](./docs/QUICKSTART.md)** - Detailed setup instructions
- **[Tutorial](./docs/TUTORIAL.md)** - Step-by-step widget examples
- **[Python API](./docs/PYTHON_API.md)** - Programmatic dev server control
- **[API Reference](./docs/API.md)** - Complete API documentation
- **[Examples](./examples/)** - Real-world code examples

---

## CLI Commands

```bash
# Initialize new project
fastapps init my-app

# Create new widget (auto-generates both files)
fastapps create mywidget

# Start development server with ngrok tunnel
fastapps dev

# Start on custom port
fastapps dev --port 8080

# Reset ngrok auth token
fastapps reset-token

# View authentication guide
fastapps auth-info
```

**Tip**: If `fastapps` command is not found, use:
```bash
python -m fastapps.cli.main <command>
```

---

## Project Structure After `fastapps create`

When you run `python -m fastapps.cli.main create my-widget`, you get:

```
my-app/
├── server/
│   ├── __init__.py
│   ├── main.py                  # Already setup (no edits needed)
│   ├── tools/
│   │   ├── __init__.py
│   │   └── my_widget_tool.py    # ← Edit this: Your widget logic
│   └── api/                     # (optional: for shared APIs)
│
├── widgets/
│   └── my-widget/
│       └── index.jsx            # ← Edit this: Your UI
│
├── assets/                      # Auto-generated during build
│   ├── my-widget-HASH.html
│   └── my-widget-HASH.js
│
├── requirements.txt             # Python dependencies
├── package.json                 # JavaScript dependencies
└── build-all.mts                # Auto-copied from fastapps
```

**You only edit the 2 files marked with ←**

---

## Key Features

- **Zero Boilerplate** - Just write your widget code
- **Auto-Discovery** - Widgets automatically registered
- **Type-Safe** - Pydantic for Python, TypeScript for React
- **CLI Tools** - Scaffold widgets instantly
- **Python API** - Programmatic server control
- **ngrok Integration** - Public URLs with one command
- **React Hooks** - Modern React patterns via `fastapps`
- **MCP Protocol** - Native ChatGPT integration

---

## Python API

Start dev servers programmatically:

```python
from fastapps import start_dev_server

# Simple usage
start_dev_server()

# With configuration
start_dev_server(
    port=8080,
    auto_reload=True,
    ngrok_token="your_token"
)

# Get server info without starting
from fastapps import get_server_info
info = get_server_info(port=8001)
print(f"Public URL: {info.public_url}")
```

See [Python API Documentation](./docs/PYTHON_API.md) for more details.

---

## Examples

### Simple Widget

```python
# server/tools/hello_tool.py
class HelloTool(BaseWidget):
    identifier = "hello"
    title = "Hello"
    input_schema = HelloInput
    
    async def execute(self, input_data):
        return {"message": "Hello World!"}
```

```jsx
// widgets/hello/index.jsx
export default function Hello() {
  const props = useWidgetProps();
  return <h1>{props.message}</h1>;
}
```

### With API Call

```python
async def execute(self, input_data):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        data = response.json()
    return {"data": data}
```

### With State

```jsx
function Counter() {
  const [state, setState] = useWidgetState({ count: 0 });
  return (
    <button onClick={() => setState({ count: state.count + 1 })}>
      Count: {state.count}
    </button>
  );
}
```

---

## Troubleshooting

**Widget not loading?**
- Check `identifier` matches folder name
- Rebuild: `npm run build`
- Restart: `python server/main.py`

**Import errors?**
```bash
pip install --upgrade fastapps
npm install fastapps@latest
```

**Need help?** Check our [docs](./docs/) or [open an issue](https://github.com/fastapps-framework/fastapps/issues)

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

MIT © FastApps Team

## Links

- **PyPI**: https://pypi.org/project/fastapps/
- **ChatJS Hooks**: https://www.npmjs.com/package/fastapps
- **GitHub**: https://github.com/fastapps-framework/fastapps
- **MCP Spec**: https://modelcontextprotocol.io/
