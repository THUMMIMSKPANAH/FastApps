# fastapps-demo

ChatGPT widgets built with [FastApps](https://pypi.org/project/fastapps/).

## Quick Start

Your project includes an example widget (`my_widget`) to get you started!

```bash
fastapps dev
```

This will build your widgets and start the development server.

## Creating More Widgets

```bash
fastapps create another_widget
fastapps dev
```

## Project Structure

```
fastapps-demo/
├── server/
│   ├── main.py              # Server (auto-discovery)
│   └── tools/               # Widget backends
│       └── my_widget_tool.py   # Example widget
│
├── widgets/                 # Widget frontends
│   └── my_widget/
│       └── index.jsx        # Example React component
│
├── assets/                  # Built widgets (auto-generated)
└── package.json
```

## Learn More

- **FastApps Framework**: https://pypi.org/project/fastapps/
- **FastApps (React)**: https://www.npmjs.com/package/fastapps
- **Documentation**: https://github.com/fastapps-framework/fastapps

## License

MIT
