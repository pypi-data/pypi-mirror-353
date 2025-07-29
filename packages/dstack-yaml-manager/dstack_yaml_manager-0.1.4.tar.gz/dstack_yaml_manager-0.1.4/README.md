# dstack Management Tool

A powerful Terminal User Interface (TUI) for managing dstack YAML configurations with virtual file storage, note-taking, and intelligent state restoration.

## Features

🌳 **Virtual File Tree** - Organize dstack YAML files by type (Task, Service, Fleet, Server) and custom groups  
📝 **Note Taking** - Add markdown notes to any file with auto-save functionality  
💾 **SQLite Storage** - All files and metadata stored in a local database  
🔄 **State Restoration** - Automatically restore your session when switching between directories  
⚡ **Fast Navigation** - Keyboard shortcuts for all operations  
📋 **Smart Clipboard** - Copy file paths and dstack commands with Ctrl+A  
🎯 **File Management** - Add, delete, and organize files with confirmation dialogs  

## Installation

Install via pip:

```bash
pip install dstack-yaml-manager
```

Or install from source:

```bash
git clone <repository-url>
cd dstack-mgmt-tool
pip install -e .
```

## Configuration

On first run, the tool automatically creates a configuration file at `~/.dstack-mgmt/config.yml`:

```yaml
database:
  path: ~/.dstack-mgmt/dstack_manager.db
  auto_backup: true
  backup_count: 5
ui:
  auto_save_notes: true
  auto_save_delay: 1.0
  restore_state: true
paths:
  default_workspace: ~/
  scan_hidden_dirs: false
```

## Usage

### Basic Usage

```bash
# Launch in current directory
dstack-yaml-manager

# Launch in specific directory
dstack-yaml-manager ~/my-dstack-project

# Show configuration
dstack-yaml-manager --config

# Reset configuration to defaults
dstack-yaml-manager --reset-config
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+X` | Smart quit (saves state and exits) |
| `Ctrl+N` | Add new file to database |
| `Ctrl+G` | Create new custom group |
| `Ctrl+R` | Refresh file tree |
| `Ctrl+A` | Navigate to file (copy paths/commands) |
| `Ctrl+S` | Save current note |
| `Ctrl+U` | Rename selected file or group |
| `Delete` / `Ctrl+D` | Delete selected file/group |
| `Escape` | Exit note editing mode |
| `Tab` | Auto-complete file paths |
| `↑↓←→` | Navigate tree and scroll preview |

### File Organization

Files are automatically grouped by type:
- **Task** - `*.task.dstack.yml`
- **Service** - `*.service.dstack.yml` 
- **Fleet** - `*.fleet.dstack.yml`
- **Server** - `*.server.dstack.yml`
- **Unknown** - Other `.dstack.yml` files

You can also create custom groups and assign files to them.

### Note Taking

Click on the **Note** tab to add markdown notes to any selected file. Notes are:
- Auto-saved as you type (1-second delay)
- Manually saved with `Ctrl+S`
- Stored in the SQLite database
- Persistent across sessions

### State Restoration

The tool automatically saves and restores your session state including:
- Selected file and active tab
- Expanded tree nodes
- Last working directory

## Database Location

By default, the database is stored at `~/.dstack-mgmt/dstack_manager.db`. You can change this in the configuration file.

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black dstack_mgmt/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Requirements

- Python 3.8+
- textual >= 0.38.0
- rich >= 13.0.0
- PyYAML >= 6.0