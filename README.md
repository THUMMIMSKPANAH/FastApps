# FastApps
<img width="1024" height="390" alt="image 39" src="https://github.com/user-attachments/assets/9404c861-8bfd-4f24-ba5c-543fe27f3d3e" />

<p align="center">
  <strong>The python framework for ChatGPT apps</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/v/fastapps.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/pyversions/fastapps.svg" alt="Python"></a>
  <a href="https://pepy.tech/projects/fastapps"><img src="https://static.pepy.tech/personalized-badge/fastapps?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=downloads" alt="PyPI Downloads"></a>
  <a href="https://github.com/DooiLabs/FastApps/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <br>
  <a href="https://github.com/DooiLabs/FastApps/actions"><img src="https://github.com/DooiLabs/FastApps/workflows/CI/badge.svg" alt="CI Status"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/DooiLabs/FastApps"><img src="https://img.shields.io/github/stars/DooiLabs/FastApps?style=social" alt="GitHub Stars"></a>
</p>

---

📚 **Documentation**: [https://www.fastapps.org/](https://www.fastapps.org/)

👥 **Community**: [Join Our Discord](https://discord.gg/5cEy3Jqek3)

---

## Quick Start

```bash
# 0. Set virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate # Mac/Linux
.venv\Scripts\Activate.ps1 # Windows PowerShell

# 1. Install
pip install fastapps

# 2. Create project (includes example widget + auto npm install)
fastapps init my-app

# 3. Run
cd my-app
fastapps dev
```
That's it! Your example widget is now running at a public URL.
On first run, you'll need an [ngrok auth token](https://dashboard.ngrok.com/get-started/your-authtoken) (free).


## Test App

**Option A: Test on MCPJam Inspector**

Add your public URL + /mcp to ChatGPT:
Example: https://xyz.ngrok-free.app/mcp
```bash
npx @mcpjam/inspector@latest
```

**Option B: Test on ChatGPT**

Add your public URL + /mcp to ChatGPT's "Settings > Connectors":
Example: https://xyz.ngrok-free.app/mcp



## Creating More Widgets

```bash
fastapps create another-widget
```


### Editing Your Widget

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

---

## Contributing

We welcome contributions! Please see our contributing guidelines:

- **[Contributing Guide](https://github.com/DooiLabs/FastApps/blob/main/CONTRIBUTING.md)** - How to contribute to FastApps
- **[Code Style Guide](https://github.com/DooiLabs/FastApps/blob/main/CODE_STYLE.md)** - Code formatting and style standards
- **[GitHub Workflows](https://github.com/DooiLabs/FastApps/blob/main/.github/WORKFLOWS.md)** - CI/CD documentation

### Quick Start for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/FastApps.git
cd FastApps

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Make changes and ensure they pass checks
black .
ruff check --fix .
pytest

# Submit a pull request
```

## License

MIT © Dooi Labs

## Links

- **PyPI**: https://pypi.org/project/fastapps/
- **React Hooks**: https://www.npmjs.com/package/fastapps
- **GitHub**: https://github.com/DooiLabs/FastApps
- **MCP Spec**: https://modelcontextprotocol.io/
