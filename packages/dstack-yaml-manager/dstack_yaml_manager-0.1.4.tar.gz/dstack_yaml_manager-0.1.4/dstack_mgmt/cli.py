#!/usr/bin/env python3
"""
Command Line Interface for dstack Management Tool
"""

import sys
import argparse
from pathlib import Path
from .config import ConfigManager
from .manager import DStackYAMLManager

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="dstack Management Tool - A TUI for managing dstack YAML configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dstack-mgmt                          # Launch in current directory
  dstack-mgmt ~/projects               # Launch in specific directory
  dstack-mgmt --config                 # Show configuration info
  dstack-mgmt --reset-config           # Reset configuration to defaults
        """
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to scan for dstack YAML files (default: current directory)"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show configuration information and exit"
    )
    
    parser.add_argument(
        "--reset-config", 
        action="store_true",
        help="Reset configuration to defaults"
    )
    
    parser.add_argument(
        "--restore-state",
        help="Restore from a saved state file (internal use)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.4"
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    if args.config:
        print("📋 dstack Management Tool Configuration:")
        print("=" * 50)
        config_info = config_manager.get_config_info()
        for key, value in config_info.items():
            print(f"{key:20}: {value}")
        return
    
    if args.reset_config:
        print("🔄 Resetting configuration to defaults...")
        config_manager.config_file.unlink(missing_ok=True)
        config_manager._ensure_config_exists()
        print("✅ Configuration reset successfully!")
        return
    
    # Resolve the target path
    target_path = Path(args.path).resolve()
    
    if not target_path.exists():
        print(f"❌ Error: Path '{target_path}' does not exist")
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"❌ Error: Path '{target_path}' is not a directory")
        sys.exit(1)
    
    # Check if dstack is configured
    dstack_config_path = Path.home() / ".dstack" / "config.yml"
    if not dstack_config_path.exists():
        print("❌ dstack is not configured!")
        print("")
        print("Please run the following command first to set up dstack:")
        print("  dstack server")
        print("")
        print("For more information, visit: https://www.dstack.ai")
        print("")
        print("After setting up dstack, you can launch this tool again.")
        sys.exit(1)
    
    # Launch the TUI application
    try:
        app = DStackYAMLManager(
            root_path=str(target_path),
            config_manager=config_manager,
            restore_state_file=args.restore_state
        )
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()