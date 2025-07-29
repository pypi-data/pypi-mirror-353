# Complete Guide: Building a JupyterLab Extension from Scratch

## Overview
This document covers the complete process of building a modern JupyterLab extension with session tracking, popup UI, and proper distribution packaging. The example project creates a session tracer that displays current JupyterLab session information in a beautiful popup with clipboard functionality.

## 🏗️ Project Structure

```
jupyter-session-tracer/
├── src/                           # TypeScript source files
│   ├── index.ts                   # Main plugin entry point
│   ├── sessionTracer.ts          # Session tracking logic
│   └── sessionPopup.ts           # Popup widget UI
├── style/                         # CSS styles
│   └── index.css                 # Extension styles
├── jupyter_session_tracer/        # Python package
│   ├── __init__.py               # Package initialization
│   ├── _version.py               # Version management
│   └── labextension/             # Built extension files
├── scripts/                       # Build scripts
│   ├── build.sh                  # Development build
│   ├── develop.sh                # Development setup
│   ├── build-wheel.sh            # Production wheel build
│   └── install-local.sh          # Local installation
├── package.json                   # Node.js dependencies
├── pyproject.toml                 # Python project config
├── setup.py                       # Python package setup
├── tsconfig.json                  # TypeScript config
├── Makefile                       # Convenient build commands
└── README.md                      # Documentation
```

## 🚀 Key Features Implemented

### 1. Session Tracking
- **Real-time monitoring**: Tracks notebook open/close/activation events
- **Kernel information**: Captures kernel ID, name, and connection status
- **Path tracking**: Full server URL + notebook path
- **Timestamp logging**: ISO format timestamps for all events

### 2. Beautiful UI Components
- **Top-level menu**: "📊 Session Info" menu next to Help
- **Toolbar button**: Clickable 📊 icon in top menu bar
- **Popup widget**: Modern, responsive design with dark mode support
- **Syntax highlighting**: JSON display with color-coded syntax
- **Auto-copy**: Automatically copies data to clipboard when opened

### 3. Modern Build System
- **hatchling**: Modern Python packaging with build hooks
- **hatch-jupyter-builder**: Automatic NPM/webpack integration
- **TypeScript compilation**: Full type safety and modern JS features
- **Webpack optimization**: Code splitting, minification, source maps
- **Watch mode**: Live development with automatic rebuilds

## 🛠️ Technical Implementation

### Core Plugin Structure (`src/index.ts`)

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-session-tracer:plugin',
  description: 'Session information display extension',
  autoStart: true,
  requires: [IDocumentManager, INotebookTracker],
  optional: [IMainMenu, ICommandPalette],
  activate: (app, docManager, notebookTracker, mainMenu, palette) => {
    // Initialize session tracer
    const sessionTracer = new SessionTracer(app, docManager, notebookTracker);
    
    // Register commands
    app.commands.addCommand('session-tracer:show-info', {
      label: '📊 Show Session Info',
      execute: () => {
        const data = sessionTracer.getCurrentSessionInfo();
        const popup = new SessionPopup(data);
        const widget = new MainAreaWidget({ content: popup });
        app.shell.add(widget, 'main');
      }
    });
    
    // Add to menu bar
    if (mainMenu) {
      const menu = new Menu({ commands: app.commands });
      menu.title.label = '📊 Session Info';
      menu.addItem({ command: 'session-tracer:show-info' });
      mainMenu.addMenu(menu);
    }
  }
};
```

### Session Data Interface

```typescript
export interface SessionData {
  timestamp: string;              // ISO timestamp
  notebookPath?: string;         // Full server URL + path
  kernelId?: string;             // Kernel identifier
  kernelName?: string;           // e.g., "python3"
  kernelState?: string;          // Connection status
  sessionName?: string;          // Session name
  jupyterlabVersion?: string;    // JupyterLab version
  currentWidget?: string;        // Active widget name
}
```

### Modern Python Packaging (`pyproject.toml`)

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"

[project]
name = "jupyter_session_tracer"
dynamic = ["version", "description", "authors", "urls", "keywords"]
dependencies = ["jupyter_server>=2.0.1,<3"]

[tool.hatch.version]
source = "nodejs"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyter_session_tracer/labextension/static/style.js",
    "jupyter_session_tracer/labextension/package.json",
]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]
```

## 🎨 UI Design Patterns

### Responsive Popup Layout
```css
.jp-SessionPopup-container {
  max-width: 800px;
  margin: 20px auto;
  background: var(--jp-layout-color1);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.jp-SessionPopup-summaryGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}
```

### Syntax Highlighting
```typescript
private applySyntaxHighlighting(element: HTMLElement): void {
  const highlighted = jsonText
    .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
    .replace(/:\s*"([^"]*)"/g, ': <span class="json-string">"$1"</span>')
    .replace(/:\s*(\d+)/g, ': <span class="json-number">$1</span>');
  element.innerHTML = highlighted;
}
```

## 🔧 Build System Integration

### Development Workflow
```bash
# Setup development environment
make develop          # Install deps + enable extension
jlpm watch           # Live development with hot reload

# Build for production
make build-wheel     # Creates optimized wheel + source dist
```

### Build Scripts Architecture
- **build.sh**: Development builds with source maps
- **build-wheel.sh**: Production builds with optimization
- **develop.sh**: Development environment setup
- **Makefile**: Convenient command interface

### Package.json Scripts
```json
{
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension:dev",
    "build:prod": "jlpm clean && jlpm build:lib:prod && jlpm build:labextension",
    "build:lib": "tsc --sourceMap",
    "build:lib:prod": "tsc",
    "build:labextension": "jupyter labextension build .",
    "watch": "run-p watch:src watch:labextension",
    "clean": "jlpm clean:lib && jlpm clean:labextension"
  }
}
```

## 🐛 Common Issues & Solutions

### 1. TypeScript Import Errors
**Problem**: Cannot find module './sessionTracer'
**Solution**: Ensure TypeScript compilation succeeds before webpack build

### 2. Menu API Usage
**Problem**: Incorrect menu.addMenu() parameters
**Solution**: Use `new Menu({ commands })` then `mainMenu.addMenu(menu)`

### 3. Resource Exhaustion During Build
**Problem**: "No file descriptors available" during yarn/jlpm install
**Solution**: Clean node_modules, use `jlpm install` consistently

### 4. Wheel vs Source Distribution
**Problem**: Building tar.gz instead of wheel
**Solution**: Use modern build system with `python -m build`

### 5. Extension Loading Issues
**Problem**: Extension not appearing in JupyterLab
**Solution**: Verify package.json metadata and labextension build

## 📦 Distribution Strategy

### Wheel Building Process
1. **Clean environment**: Remove old builds and caches
2. **Install dependencies**: Use jlpm for consistency
3. **TypeScript compilation**: Build lib/ directory
4. **Webpack bundling**: Create optimized labextension
5. **Python packaging**: Use hatchling with build hooks
6. **Validation**: Test installation and functionality

### Installation Methods
```bash
# From wheel (recommended)
pip install dist/jupyter_session_tracer-*.whl

# From source
pip install .

# Development installation
pip install -e .
jupyter labextension develop . --overwrite
```

## 🧪 Testing & Validation

### Development Testing
```bash
# Build and test
jlpm run build
jupyter labextension list  # Verify installation
jupyter lab                # Manual testing

# Production testing
make build-wheel
pip install dist/*.whl --force-reinstall
jupyter lab
```

### Extension Validation Checklist
- [ ] Extension appears in JupyterLab
- [ ] Menu item works correctly
- [ ] Popup displays proper data
- [ ] Clipboard functionality works
- [ ] No console errors
- [ ] Responsive design works
- [ ] Dark mode compatibility

## 🚀 Advanced Features

### Event Tracking System
```typescript
private setupNotebookTracking(): void {
  this.notebookTracker.widgetAdded.connect((sender, notebook) => {
    console.log('Notebook opened:', notebook.context.path);
    
    notebook.context.sessionContext.kernelChanged.connect((context, args) => {
      console.log('Kernel changed:', {
        oldKernelId: args.oldValue?.id,
        newKernelId: args.newValue?.id
      });
    });
  });
}
```

### Clipboard Integration
```typescript
private async copyToClipboard(): Promise<void> {
  try {
    const jsonString = JSON.stringify(this.sessionData, null, 2);
    await navigator.clipboard.writeText(jsonString);
    this.showCopyFeedback();
  } catch (error) {
    this.selectAllText(); // Fallback
  }
}
```

### Server URL Integration
```typescript
getCurrentSessionInfo(): SessionData {
  const serverUrl = this.app.serviceManager.serverSettings.baseUrl;
  const notebookPath = currentNotebook.context.path;
  sessionData.notebookPath = `${serverUrl}${notebookPath}`;
}
```

## 📝 Best Practices Learned

### 1. **Always Use jlpm Consistently**
- Don't mix yarn/npm with jlpm
- Clean lockfiles when switching tools
- Use jlpm for all package operations

### 2. **Modern Build System Architecture**
- Use hatchling + hatch-jupyter-builder
- Implement proper build hooks
- Separate development and production builds

### 3. **TypeScript Best Practices**
- Define clear interfaces for data structures
- Use proper type annotations
- Maintain consistent import patterns

### 4. **UI/UX Considerations**
- Implement auto-copy for user convenience
- Provide visual feedback for actions
- Support both light and dark themes
- Use responsive grid layouts

### 5. **Extension Distribution**
- Always build wheels for distribution
- Include proper metadata in package.json
- Test installation from wheel files
- Document installation procedures

## 🎯 Future Enhancement Ideas

### Additional Features to Consider
- **Export formats**: CSV, XML, YAML output options
- **Historical tracking**: Session history with timestamps
- **Performance metrics**: Kernel execution times, memory usage
- **Collaborative features**: Multi-user session tracking
- **Integration hooks**: REST API endpoints for external tools
- **Customizable display**: User-configurable field selection
- **Notification system**: Alerts for kernel state changes
- **Data persistence**: Save session logs to files

### Technical Improvements
- **Unit testing**: Jest/pytest test suites
- **E2E testing**: Playwright integration tests
- **CI/CD pipeline**: GitHub Actions for automated builds
- **Documentation**: Sphinx-based API documentation
- **Internationalization**: Multi-language support
- **Plugin architecture**: Extensible session data providers

## 📚 References & Resources

### Essential Documentation
- [JupyterLab Extension Developer Guide](https://jupyterlab.readthedocs.io/en/latest/extension/extension_dev.html)
- [Lumino Widget Documentation](https://lumino.readthedocs.io/)
- [Hatchling Build System](https://hatch.pypa.io/latest/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Example Extensions
- [JupyterLab Git Extension](https://github.com/jupyterlab/jupyterlab-git)
- [JupyterLab LSP](https://github.com/jupyter-lsp/jupyterlab-lsp)
- [JupyterLab Extension Examples](https://github.com/jupyterlab/extension-examples)

This comprehensive guide provides a complete blueprint for creating modern JupyterLab extensions with professional-grade build systems, UI components, and distribution strategies. 