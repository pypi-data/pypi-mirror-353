#!/usr/bin/env python3
"""
Main manager module for dstack Management Tool
"""

import os
import sys
import yaml
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from .config import ConfigManager
except ImportError:
    # Fallback for standalone usage
    ConfigManager = None


def get_log_file_path(filename: str) -> str:
    """Get path for log file in ~/.dstack-mgmt/ directory"""
    log_dir = Path.home() / ".dstack-mgmt"
    log_dir.mkdir(exist_ok=True)
    return str(log_dir / filename)

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    DirectoryTree, Header, Footer, Static, Button, Input, 
    TextArea, Tree, Label, TabbedContent, TabPane, ListView, ListItem, Select
)
from textual.binding import Binding
from textual.screen import ModalScreen, Screen
from textual.reactive import reactive
from textual.message import Message
from rich.syntax import Syntax
from rich.text import Text
from rich.console import Console
from rich.panel import Panel


class DStackConfigType(Enum):
    TASK = "task"
    SERVICE = "service"
    FLEET = "fleet"
    SERVER = "server"
    UNKNOWN = "unknown"


class DatabaseManager:
    """SQLite database manager for YAML file metadata"""
    
    def __init__(self, db_path: Path = None, config_manager=None):
        if db_path:
            self.db_path = db_path
        elif config_manager:
            self.db_path = config_manager.get_database_path()
        else:
            self.db_path = Path.home() / ".dstack-mgmt" / "dstack_manager.db"
            # Ensure the directory exists
            self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create yaml_files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS yaml_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                config_type TEXT NOT NULL,
                content TEXT NOT NULL,
                parsed_yaml TEXT,
                is_valid BOOLEAN NOT NULL DEFAULT 1,
                validation_errors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                file_hash TEXT
            )
        """)
        
        # Create tags table for categorization
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file_tags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES yaml_files (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        """)
        
        # Create templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                config_type TEXT NOT NULL,
                content TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create notes table for file-specific markdown notes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                note_content TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create type_group_names table for custom type group names
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS type_group_names (
                config_type TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create application settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create project settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                root_path TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file history table for version tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                content TEXT NOT NULL,
                change_type TEXT NOT NULL,
                change_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES yaml_files (id) ON DELETE CASCADE
            )
        """)
        
        # Create custom groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#1e90ff',
                icon TEXT DEFAULT '📁',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file_custom_groups junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_custom_groups (
                file_id INTEGER,
                group_id INTEGER,
                PRIMARY KEY (file_id, group_id),
                FOREIGN KEY (file_id) REFERENCES yaml_files (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES custom_groups (id) ON DELETE CASCADE
            )
        """)
        
        # Create file settings table for per-file project and environment settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                project_name TEXT,
                conda_env TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create dstack status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dstack_status (
                name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_file(self, yaml_file: 'YAMLFile') -> int:
        """Add a YAML file to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate file hash and size
        file_hash = self._calculate_hash(yaml_file.content)
        file_size = len(yaml_file.content.encode())
        
        cursor.execute("""
            INSERT OR REPLACE INTO yaml_files 
            (name, path, config_type, content, parsed_yaml, is_valid, validation_errors, 
             updated_at, file_size, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            yaml_file.name,
            str(yaml_file.path),
            yaml_file.config_type.value,
            yaml_file.content,
            str(yaml_file.parsed_yaml) if yaml_file.parsed_yaml else None,
            yaml_file.is_valid,
            str(yaml_file.validation_errors) if yaml_file.validation_errors else None,
            datetime.now().isoformat(),
            file_size,
            file_hash
        ))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    def get_all_files(self) -> List[Dict]:
        """Get all YAML files from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, path, config_type, content, parsed_yaml, 
                   is_valid, validation_errors, created_at, updated_at, 
                   file_size, file_hash
            FROM yaml_files 
            ORDER BY updated_at DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        files = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def get_file_by_path(self, path: str) -> Optional[Dict]:
        """Get a specific file by path"""
        import datetime
        
        debug_log = get_log_file_path("delete_debug.log")
        
        def log_debug(message):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.datetime.now()}: {message}\n")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        log_debug(f"🔍 LOOKUP: Looking up file by path: '{path}'")
        
        # First, let's see what paths are in the database
        cursor.execute("SELECT id, name, path FROM yaml_files")
        all_files = cursor.fetchall()
        log_debug(f"🔍 DATABASE: All files in database ({len(all_files)} total):")
        for file_record in all_files:
            log_debug(f"  ID: {file_record[0]}, Name: {file_record[1]}, Path: '{file_record[2]}'")
        
        cursor.execute("""
            SELECT id, name, path, config_type, content, parsed_yaml, 
                   is_valid, validation_errors, created_at, updated_at, 
                   file_size, file_hash
            FROM yaml_files 
            WHERE path = ?
        """, (str(path),))
        
        row = cursor.fetchone()
        if row:
            log_debug(f"✅ FOUND: File with ID: {row[0]} and path: '{row[2]}'")
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
        else:
            log_debug(f"❌ NOT_FOUND: No file found with path: '{path}'")
            result = None
        
        conn.close()
        return result
    
    def update_file(self, path: str, content: str, parsed_yaml: Any = None, 
                   is_valid: bool = True, validation_errors: List[str] = None):
        """Update file content and metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        file_hash = self._calculate_hash(content)
        file_size = len(content.encode())
        
        cursor.execute("""
            UPDATE yaml_files 
            SET content = ?, parsed_yaml = ?, is_valid = ?, validation_errors = ?,
                updated_at = ?, file_size = ?, file_hash = ?
            WHERE path = ?
        """, (
            content,
            str(parsed_yaml) if parsed_yaml else None,
            is_valid,
            str(validation_errors) if validation_errors else None,
            datetime.now().isoformat(),
            file_size,
            file_hash,
            str(path)
        ))
        
        conn.commit()
        conn.close()
    
    def delete_file(self, path: str):
        """Delete a file from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM yaml_files WHERE path = ?", (str(path),))
        
        conn.commit()
        conn.close()
    
    def get_files_by_type(self, config_type: str) -> List[Dict]:
        """Get files filtered by configuration type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, path, config_type, content, parsed_yaml, 
                   is_valid, validation_errors, created_at, updated_at, 
                   file_size, file_hash
            FROM yaml_files 
            WHERE config_type = ?
            ORDER BY updated_at DESC
        """, (config_type,))
        
        columns = [description[0] for description in cursor.description]
        files = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate hash for content change detection"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_template(self, name: str, config_type: str, content: str, description: str = ""):
        """Add a template to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO templates (name, config_type, content, description)
            VALUES (?, ?, ?, ?)
        """, (name, config_type, content, description))
        
        conn.commit()
        conn.close()
    
    def get_templates(self) -> List[Dict]:
        """Get all templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, config_type, content, description, created_at
            FROM templates 
            WHERE is_active = 1
            ORDER BY config_type, name
        """)
        
        columns = [description[0] for description in cursor.description]
        templates = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return templates
    
    def get_file_note(self, file_path: str) -> str:
        """Get note content for a file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT note_content FROM file_notes WHERE file_path = ?", (str(file_path),))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else ""
    
    def save_file_note(self, file_path: str, note_content: str):
        """Save note content for a file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO file_notes (file_path, note_content, updated_at)
            VALUES (?, ?, ?)
        """, (str(file_path), note_content, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get application setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set application setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def add_file_history(self, file_id: int, content: str, change_type: str, description: str = ""):
        """Add file history entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO file_history (file_id, content, change_type, change_description)
            VALUES (?, ?, ?, ?)
        """, (file_id, content, change_type, description))
        
        conn.commit()
        conn.close()
    
    def get_file_history(self, file_id: int) -> List[Dict]:
        """Get file history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, change_type, change_description, created_at
            FROM file_history 
            WHERE file_id = ?
            ORDER BY created_at DESC
        """, (file_id,))
        
        columns = [description[0] for description in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return history
    
    def export_file_to_filesystem(self, file_id: int, output_dir: Path = None) -> Path:
        """Export a file from database to filesystem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, content FROM yaml_files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"File with id {file_id} not found")
        
        name, content = row
        output_dir = output_dir or Path.cwd()
        file_path = output_dir / name
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        conn.close()
        return file_path
    
    def export_all_files_to_filesystem(self, output_dir: Path = None) -> List[Path]:
        """Export all files from database to filesystem"""
        files = self.get_all_files()
        output_dir = output_dir or Path.cwd()
        exported_paths = []
        
        for file_data in files:
            file_path = output_dir / file_data['name']
            with open(file_path, 'w') as f:
                f.write(file_data['content'])
            exported_paths.append(file_path)
        
        return exported_paths
    
    def add_custom_group(self, name: str, description: str = "", color: str = "#1e90ff", icon: str = "📁") -> int:
        """Add a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO custom_groups (name, description, color, icon)
            VALUES (?, ?, ?, ?)
        """, (name, description, color, icon))
        
        group_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return group_id
    
    def get_custom_groups(self) -> List[Dict]:
        """Get all custom groups"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, color, icon, created_at
            FROM custom_groups 
            WHERE is_active = 1
            ORDER BY name
        """)
        
        columns = [description[0] for description in cursor.description]
        groups = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return groups
    
    def ensure_default_group(self) -> int:
        """Ensure Default custom group exists and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if Default group already exists
        cursor.execute("SELECT id FROM custom_groups WHERE name = 'Default'")
        result = cursor.fetchone()
        
        if result:
            group_id = result[0]
        else:
            # Create Default group
            cursor.execute("""
                INSERT INTO custom_groups (name, icon)
                VALUES (?, ?)
            """, ("Default", "📁"))
            group_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return group_id
    
    def delete_custom_group(self, group_id: int):
        """Delete a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE custom_groups SET is_active = 0 WHERE id = ?", (group_id,))
        
        conn.commit()
        conn.close()
    
    def assign_file_to_custom_group(self, file_id: int, group_id: int):
        """Assign a file to a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO file_custom_groups (file_id, group_id)
            VALUES (?, ?)
        """, (file_id, group_id))
        
        conn.commit()
        conn.close()
    
    def get_files_in_custom_group(self, group_id: int) -> List[Dict]:
        """Get files in a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT yf.id, yf.name, yf.path, yf.config_type, yf.content, yf.parsed_yaml, 
                   yf.is_valid, yf.validation_errors, yf.created_at, yf.updated_at, 
                   yf.file_size, yf.file_hash
            FROM yaml_files yf
            JOIN file_custom_groups fcg ON yf.id = fcg.file_id
            WHERE fcg.group_id = ?
            ORDER BY yf.updated_at DESC
        """, (group_id,))
        
        columns = [description[0] for description in cursor.description]
        files = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def clear_all_data(self) -> bool:
        """Clear all data from the database - files, groups, templates, history, everything"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear all tables in the correct order (respecting foreign keys)
            cursor.execute("DELETE FROM file_custom_groups")
            cursor.execute("DELETE FROM file_history") 
            cursor.execute("DELETE FROM file_notes")
            cursor.execute("DELETE FROM custom_groups")
            cursor.execute("DELETE FROM templates")
            cursor.execute("DELETE FROM yaml_files")
            cursor.execute("DELETE FROM app_settings")
            cursor.execute("DELETE FROM type_group_names")
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
        finally:
            conn.close()
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a file from database (removes from all groups and history)"""
        import datetime
        
        debug_log = get_log_file_path("delete_debug.log")
        
        def log_debug(message):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.datetime.now()}: {message}\n")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            log_debug(f"🔍 DELETE: Attempting to delete file with ID: {file_id}")
            
            # Check if file exists first
            cursor.execute("SELECT id, name FROM yaml_files WHERE id = ?", (file_id,))
            file_exists = cursor.fetchone()
            if not file_exists:
                log_debug(f"❌ DELETE: File with ID {file_id} not found")
                return False
            
            log_debug(f"🔍 DELETE: Found file: {file_exists[1]} (ID: {file_exists[0]})")
            
            # Delete from related tables first (foreign key constraints)
            cursor.execute("DELETE FROM file_custom_groups WHERE file_id = ?", (file_id,))
            deleted_groups = cursor.rowcount
            log_debug(f"🔍 DELETE: Deleted {deleted_groups} custom group assignments")
            
            cursor.execute("DELETE FROM file_history WHERE file_id = ?", (file_id,))
            deleted_history = cursor.rowcount
            log_debug(f"🔍 DELETE: Deleted {deleted_history} history entries")
            
            # Get the file path first to delete notes (file_notes uses file_path, not file_id)
            cursor.execute("SELECT path FROM yaml_files WHERE id = ?", (file_id,))
            file_path_result = cursor.fetchone()
            if file_path_result:
                file_path = file_path_result[0]
                cursor.execute("DELETE FROM file_notes WHERE file_path = ?", (file_path,))
                deleted_notes = cursor.rowcount
                log_debug(f"🔍 DELETE: Deleted {deleted_notes} note entries for path: {file_path}")
            else:
                log_debug(f"🔍 DELETE: No file path found for ID {file_id}, skipping notes deletion")
            
            # Finally delete the file itself
            cursor.execute("DELETE FROM yaml_files WHERE id = ?", (file_id,))
            deleted_files = cursor.rowcount
            log_debug(f"🔍 DELETE: Deleted {deleted_files} file record")
            
            if deleted_files == 0:
                log_debug(f"❌ DELETE: No file was deleted for ID {file_id}")
                return False
            
            conn.commit()
            log_debug(f"✅ DELETE: Successfully deleted file ID {file_id}")
            return True
        except Exception as e:
            log_debug(f"❌ DELETE_ERROR: {str(e)}")
            return False
        finally:
            conn.close()
    
    def delete_custom_group(self, group_id: int) -> bool:
        """Delete a custom group and all files in it"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all files in this group
            cursor.execute("SELECT file_id FROM file_custom_groups WHERE group_id = ?", (group_id,))
            file_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete all files in the group
            for file_id in file_ids:
                cursor.execute("DELETE FROM file_custom_groups WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM file_history WHERE file_id = ?", (file_id,))
                
                # Get the file path to delete notes (file_notes uses file_path, not file_id)
                cursor.execute("SELECT path FROM yaml_files WHERE id = ?", (file_id,))
                file_path_result = cursor.fetchone()
                if file_path_result:
                    file_path = file_path_result[0]
                    cursor.execute("DELETE FROM file_notes WHERE file_path = ?", (file_path,))
                
                cursor.execute("DELETE FROM yaml_files WHERE id = ?", (file_id,))
            
            # Delete the group itself
            cursor.execute("DELETE FROM custom_groups WHERE id = ?", (group_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting custom group: {e}")
            return False
        finally:
            conn.close()
    
    def rename_file(self, old_name: str, new_name: str) -> bool:
        """Rename a file in the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Update the file record
            cursor.execute("""
                UPDATE yaml_files 
                SET name = ?, updated_at = ?
                WHERE name = ?
            """, (new_name, datetime.now().isoformat(), old_name))
            
            if cursor.rowcount == 0:
                return False
            
            # Update any notes that reference this file
            cursor.execute("""
                UPDATE file_notes 
                SET file_path = REPLACE(file_path, ?, ?)
                WHERE file_path LIKE ?
            """, (old_name, new_name, f'%{old_name}'))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error renaming file: {e}")
            return False
        finally:
            conn.close()
    
    def rename_custom_group(self, old_name: str, new_name: str) -> bool:
        """Rename a custom group in the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Update the group name
            cursor.execute("""
                UPDATE custom_groups 
                SET name = ?
                WHERE name = ?
            """, (new_name, old_name))
            
            if cursor.rowcount == 0:
                return False
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error renaming custom group: {e}")
            return False
        finally:
            conn.close()
    
    def get_type_group_name(self, config_type: str) -> str:
        """Get custom display name for a type group, or return default"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT display_name FROM type_group_names WHERE config_type = ?", (config_type,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row[0]
        else:
            # Return default name
            return config_type.title()
    
    def set_type_group_name(self, config_type: str, display_name: str) -> bool:
        """Set custom display name for a type group"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO type_group_names (config_type, display_name, updated_at)
                VALUES (?, ?, ?)
            """, (config_type, display_name, datetime.now().isoformat()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting type group name: {e}")
            return False
        finally:
            conn.close()
    
    def get_dstack_projects(self) -> List[Dict[str, Any]]:
        """Get projects from dstack global config"""
        try:
            config_path = Path.home() / ".dstack" / "config.yml"
            if not config_path.exists():
                return []
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            projects = config.get('projects', [])
            repos = config.get('repos', [])
            
            # Combine projects with repo information
            result = []
            for project in projects:
                project_info = {
                    'name': project.get('name', 'Unknown'),
                    'url': project.get('url', ''),
                    'is_default': project.get('default', False),
                    'repos': []
                }
                
                # Find associated repos (though dstack config doesn't directly link them)
                project_info['repos'] = repos
                result.append(project_info)
            
            # If no projects found, create a default entry
            if not result and repos:
                result.append({
                    'name': 'Default Project',
                    'url': '',
                    'is_default': True,
                    'repos': repos
                })
                
            return result
            
        except Exception as e:
            print(f"Error reading dstack config: {e}")
            return []
    
    def get_conda_environments(self) -> List[Dict[str, str]]:
        """Get conda environments from ~/.conda/environments.txt"""
        try:
            conda_envs_path = Path.home() / ".conda" / "environments.txt"
            if not conda_envs_path.exists():
                return []
            
            environments = []
            with open(conda_envs_path, 'r') as f:
                for line in f:
                    env_path = line.strip()
                    if env_path and Path(env_path).exists():
                        # Extract environment name from path
                        env_name = Path(env_path).name
                        if env_name == "miniconda3":  # base environment
                            env_name = "base"
                        
                        environments.append({
                            'name': env_name,
                            'path': env_path,
                            'display_name': f"conda: {env_name}"
                        })
            
            return environments
            
        except Exception as e:
            print(f"Error reading conda environments: {e}")
            return []
    
    def save_file_settings(self, file_path: str, project_name: str = None, conda_env: str = None):
        """Save project and environment settings for a specific file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO file_settings (file_path, project_name, conda_env, updated_at)
                VALUES (?, ?, ?, ?)
            """, (file_path, project_name, conda_env, datetime.now().isoformat()))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving file settings: {e}")
        finally:
            conn.close()
    
    def get_file_settings(self, file_path: str) -> dict:
        """Get project and environment settings for a specific file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT project_name, conda_env FROM file_settings
                WHERE file_path = ?
            """, (file_path,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'project_name': result[0],
                    'conda_env': result[1]
                }
            else:
                return {'project_name': None, 'conda_env': None}
                
        except Exception as e:
            print(f"Error getting file settings: {e}")
            return {'project_name': None, 'conda_env': None}
        finally:
            conn.close()
    
    def save_dstack_status(self, status_dict: dict):
        """Save dstack status to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing status
            cursor.execute("DELETE FROM dstack_status")
            
            # Insert new status entries
            for name, status in status_dict.items():
                cursor.execute("""
                    INSERT INTO dstack_status (name, status, last_updated) 
                    VALUES (?, ?, ?)
                """, (name, status, datetime.now().isoformat()))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving dstack status: {e}")
        finally:
            conn.close()
    
    def load_dstack_status(self) -> dict:
        """Load dstack status from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name, status FROM dstack_status")
            rows = cursor.fetchall()
            
            status_dict = {}
            for name, status in rows:
                status_dict[name] = status
            
            return status_dict
        except Exception as e:
            print(f"Error loading dstack status: {e}")
            return {}
        finally:
            conn.close()
    
    def clear_dstack_status(self):
        """Clear all dstack status from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM dstack_status")
            conn.commit()
        except Exception as e:
            print(f"Error clearing dstack status: {e}")
        finally:
            conn.close()


@dataclass
class YAMLFile:
    path: Path
    name: str
    config_type: DStackConfigType
    content: str
    parsed_yaml: Optional[Dict[str, Any]] = None
    is_valid: bool = True
    validation_errors: List[str] = None


class YAMLManager:
    def __init__(self, root_path: Path = None, config_manager=None):
        self.root_path = root_path or Path.cwd()
        self.yaml_files: List[YAMLFile] = []
        self.config_manager = config_manager
        self.db = DatabaseManager(config_manager=config_manager)
        self.scan_files()
    
    def scan_files(self):
        """Load all files from database (SQLite is now primary storage)"""
        print("📊 SCANNING FILES FROM DATABASE")
        self.yaml_files.clear()
        
        # First, cleanup non-existent files from database
        self._cleanup_missing_files()
        
        # Load all files from database
        db_files = self.db.get_all_files()
        print(f"   Found {len(db_files)} files in database")
        
        for i, db_file in enumerate(db_files):
            print(f"   Loading file {i+1}: {db_file.get('name', 'UNNAMED')}")
            yaml_file = self._create_yaml_file_from_db(db_file)
            if yaml_file:
                self.yaml_files.append(yaml_file)
                print(f"     ✅ Loaded: {yaml_file.name}")
            else:
                print(f"     ❌ Failed to create YAMLFile from db_file")
        
        print(f"   Total loaded yaml_files: {len(self.yaml_files)}")
    
    def _cleanup_missing_files(self):
        """Remove database entries for files that no longer exist on disk"""
        print("🧹 CLEANING UP MISSING FILES")
        db_files = self.db.get_all_files()
        removed_count = 0
        
        for db_file in db_files:
            file_path = Path(db_file['path'])
            if not file_path.exists():
                print(f"   🗑️  Removing missing file: {db_file['name']} ({file_path})")
                self.db.delete_file(str(file_path))
                removed_count += 1
        
        if removed_count > 0:
            print(f"   Cleaned up {removed_count} missing files from database")
        else:
            print("   No missing files found")
    
    def create_new_file(self, path: str, content: str, config_type: DStackConfigType) -> Optional[YAMLFile]:
        """Create a new YAML file in database (primary storage)"""
        try:
            # Parse YAML content
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            # Use the full path as entered by the user
            file_path = Path(path)
            
            yaml_file = YAMLFile(
                path=file_path,
                name=file_path.name,  # Extract filename from the full path
                config_type=config_type,
                content=content,
                parsed_yaml=parsed_yaml,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
            
            # Add to database
            file_id = self.db.add_file(yaml_file)
            
            # Add to current list
            self.yaml_files.append(yaml_file)
            
            # Add creation history
            self.db.add_file_history(file_id, content, "created", "File created")
            
            return yaml_file
            
        except Exception as e:
            return None
    
    def update_file_content(self, yaml_file: YAMLFile, new_content: str) -> bool:
        """Update file content in database"""
        try:
            # Parse new content
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(new_content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            # Update database
            self.db.update_file(
                str(yaml_file.path),
                new_content,
                parsed_yaml,
                is_valid,
                validation_errors
            )
            
            # Update object
            yaml_file.content = new_content
            yaml_file.parsed_yaml = parsed_yaml
            yaml_file.is_valid = is_valid
            yaml_file.validation_errors = validation_errors
            
            # Add to history
            file_data = self.db.get_file_by_path(str(yaml_file.path))
            if file_data:
                self.db.add_file_history(file_data['id'], new_content, "updated", "Content updated")
            
            return True
            
        except Exception as e:
            return False
    
    def delete_file(self, yaml_file: YAMLFile) -> bool:
        """Delete file from database"""
        try:
            self.db.delete_file(str(yaml_file.path))
            if yaml_file in self.yaml_files:
                self.yaml_files.remove(yaml_file)
            return True
        except:
            return False
    
    def _is_dstack_yaml(self, path: Path) -> bool:
        """Check if file is a dstack YAML configuration"""
        name = path.name.lower()
        return (
            name.endswith('.dstack.yml') or
            name.endswith('.dstack.yaml') or
            name in ['config.yml', 'config.yaml'] and 'dstack' in str(path.parent) or
            self._contains_dstack_config(path)
        )
    
    def _contains_dstack_config(self, path: Path) -> bool:
        """Check if YAML contains dstack configuration"""
        try:
            with open(path, 'r') as f:
                content = f.read()
                if 'type:' in content and any(t in content for t in ['task', 'service', 'fleet']):
                    return True
        except:
            pass
        return False
    
    def _create_yaml_file(self, path: Path) -> Optional[YAMLFile]:
        """Create YAMLFile object from path"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            # Parse YAML
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            # Determine config type
            config_type = self._determine_config_type(path, parsed_yaml)
            
            return YAMLFile(
                path=path,
                name=path.name,
                config_type=config_type,
                content=content,
                parsed_yaml=parsed_yaml,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
        except Exception as e:
            return None
    
    def _create_yaml_file_from_db(self, db_file: Dict) -> Optional[YAMLFile]:
        """Create YAMLFile object from database record"""
        try:
            config_type = DStackConfigType(db_file['config_type'])
            parsed_yaml = None
            validation_errors = None
            
            if db_file['parsed_yaml']:
                try:
                    parsed_yaml = eval(db_file['parsed_yaml'])
                except:
                    pass
            
            if db_file['validation_errors']:
                try:
                    validation_errors = eval(db_file['validation_errors'])
                except:
                    validation_errors = [db_file['validation_errors']]
            
            return YAMLFile(
                path=Path(db_file['path']),
                name=db_file['name'],
                config_type=config_type,
                content=db_file['content'],
                parsed_yaml=parsed_yaml,
                is_valid=bool(db_file['is_valid']),
                validation_errors=validation_errors
            )
        except Exception as e:
            return None
    
    def _determine_config_type(self, path: Path, parsed_yaml: Optional[Dict]) -> DStackConfigType:
        """Determine the type of dstack configuration"""
        if parsed_yaml and isinstance(parsed_yaml, dict):
            yaml_type = parsed_yaml.get('type', '').lower()
            if yaml_type in ['task', 'service', 'fleet']:
                return DStackConfigType(yaml_type)
        
        # Fallback to filename patterns
        name = path.name.lower()
        if 'service' in name:
            return DStackConfigType.SERVICE
        elif 'fleet' in name:
            return DStackConfigType.FLEET
        elif 'config' in name:
            return DStackConfigType.SERVER
        else:
            return DStackConfigType.TASK
    
    def get_files_by_type(self, config_type: DStackConfigType) -> List[YAMLFile]:
        """Get files filtered by configuration type"""
        return [f for f in self.yaml_files if f.config_type == config_type]
    
    def get_files_by_directory(self) -> Dict[str, List[YAMLFile]]:
        """Group files by directory"""
        groups = {}
        for yaml_file in self.yaml_files:
            dir_name = str(yaml_file.path.parent.relative_to(self.root_path))
            if dir_name not in groups:
                groups[dir_name] = []
            groups[dir_name].append(yaml_file)
        return groups


class FileTreeWidget(Tree):
    def __init__(self, yaml_manager: YAMLManager, main_app=None, **kwargs):
        super().__init__("dstack YAML Files", **kwargs)
        self.yaml_manager = yaml_manager
        self.main_app = main_app
        self.current_file = reactive(None)
        self.build_tree()
    
    def build_tree(self):
        """Build the file tree with grouping"""
        print("🌳 BUILDING TREE")
        self.clear()
        
        # Add dstack global config as first node
        print("   Adding global config node...")
        global_config_node = self.root.add("🌐 dstack Global Config")
        global_config_file = self._load_global_config()
        global_config_node.data = global_config_file
        print(f"   Global config: {global_config_file.name}")
        
        # Get all files that are in custom groups so we can exclude them from default type groups
        files_in_custom_groups = set()
        custom_groups = self.yaml_manager.db.get_custom_groups()
        for group in custom_groups:
            files_in_group = self.yaml_manager.db.get_files_in_custom_group(group['id'])
            for file_data in files_in_group:
                files_in_custom_groups.add(file_data['path'])
        
        # Group by type (excluding files that are in custom groups)
        print("   Adding type groups...")
        type_nodes = {}
        for config_type in DStackConfigType:
            files = self.yaml_manager.get_files_by_type(config_type)
            # Filter out files that are in custom groups
            files_not_in_custom_groups = [f for f in files if str(f.path) not in files_in_custom_groups]
            print(f"   {config_type.value}: {len(files_not_in_custom_groups)} files (total: {len(files)}, in custom: {len(files) - len(files_not_in_custom_groups)})")
            if files_not_in_custom_groups:
                custom_name = self.yaml_manager.db.get_type_group_name(config_type.value)
                type_node = self.root.add(f"📁 {custom_name} ({len(files_not_in_custom_groups)})")
                type_nodes[config_type] = type_node
                # Store config_type in node data for renaming
                type_node.data = {'type': 'type_group', 'config_type': config_type.value}
                
                for yaml_file in files_not_in_custom_groups:
                    print(f"     Adding file: {yaml_file.name}")
                    circle = self._get_status_circle(yaml_file) if self.main_app else '[dim]●[/dim]'
                    file_node = type_node.add(f"{yaml_file.name} {circle}")
                    file_node.data = yaml_file
        
        # Add custom groups
        custom_groups = self.yaml_manager.db.get_custom_groups()
        
        # Find the Default group among custom groups, or create a virtual one
        default_group = None
        other_custom_groups = []
        
        for group in custom_groups or []:
            if group['name'] == 'Default':
                default_group = group
            else:
                other_custom_groups.append(group)
        
        # Add default "Default" group (always visible, shows files from Default custom group)
        print("   Adding Default group...")
        if default_group:
            files_in_default = self.yaml_manager.db.get_files_in_custom_group(default_group['id'])
            group_files = [self.yaml_manager._create_yaml_file_from_db(f) for f in files_in_default if f]
            group_files = [f for f in group_files if f]  # Filter out None
            count = len(group_files)
            
            default_group_node = self.root.add(f"📁 Default ({count})")
            default_group_node.data = {'type': 'custom_group', 'group_data': default_group}
            
            for yaml_file in group_files:
                circle = self._get_status_circle(yaml_file) if self.main_app else '[dim]●[/dim]'
                file_node = default_group_node.add(f"{yaml_file.name} {circle}")
                file_node.data = yaml_file
        else:
            # No Default group exists yet, show empty
            default_group_node = self.root.add("📁 Default (0)")
            default_group_node.data = {'type': 'default_group', 'name': 'Default'}
        # Add other custom groups (excluding Default which we handled above)
        if other_custom_groups:
            for group in other_custom_groups:
                files_in_group = self.yaml_manager.db.get_files_in_custom_group(group['id'])
                group_files = [self.yaml_manager._create_yaml_file_from_db(f) for f in files_in_group if f]
                group_files = [f for f in group_files if f]  # Filter out None
                
                group_node = self.root.add(f"{group['icon']} {group['name']} ({len(group_files)})")
                group_node.data = {'type': 'custom_group', 'group_data': group}
                
                for yaml_file in group_files:
                    circle = self._get_status_circle(yaml_file) if self.main_app else '[dim]●[/dim]'
                    file_node = group_node.add(f"{yaml_file.name} {circle}")
                    file_node.data = yaml_file
        
        # Expand all nodes
        for node in self.root.children:
            if hasattr(node, 'allow_expand') and not node.allow_expand:
                continue
            node.expand()
    
    def _get_status_circle(self, yaml_file) -> str:
        """Get colored circle based on dstack status"""
        if not self.main_app or not hasattr(self.main_app, 'dstack_status'):
            return '[dim]●[/dim]'  # Default gray circle
        
        # Show blinking circle if status check is in progress AND this is the selected file
        if (hasattr(self.main_app, 'dstack_checking') and self.main_app.dstack_checking and 
            self.current_file and self.current_file == yaml_file):
            return '[blink yellow]●[/blink yellow]'  # Blinking yellow circle while checking
        
        # Extract the name from the YAML file for status matching
        # First try to get name from YAML content
        file_name = None
        if yaml_file.parsed_yaml and isinstance(yaml_file.parsed_yaml, dict):
            file_name = yaml_file.parsed_yaml.get('name')
        
        # If no name in YAML, use filename without extension
        if not file_name:
            file_name = yaml_file.name.replace('.dstack.yml', '').replace('.yml', '').replace('.yaml', '')
        
        # Check status
        status = self.main_app.dstack_status.get(file_name, 'unknown')
        
        
        if status == 'running':
            return '[green]●[/green]'  # Green circle for running
        elif status == 'terminated':
            return '[red]●[/red]'  # Red circle for terminated
        elif status == 'failed':
            return '[red]●[/red]'  # Red circle for failed
        elif status == 'unknown':
            return '[dim]●[/dim]'  # Gray circle for unknown
        else:
            return '[yellow]●[/yellow]'  # Yellow circle for other statuses
    
    def _load_global_config(self) -> YAMLFile:
        """Load dstack global config from ~/.dstack/config.yml"""
        try:
            global_config_path = Path.home() / ".dstack" / "config.yml"
            
            if global_config_path.exists():
                with open(global_config_path, 'r') as f:
                    content = f.read()
            else:
                # Create default content if file doesn't exist
                content = """# dstack global configuration
# See: https://dstack.ai/docs/reference/server/config.yml

projects: []

backends: []
"""
            
            # Parse YAML
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            return YAMLFile(
                path=global_config_path,
                name="config.yml",
                config_type=DStackConfigType.SERVER,
                content=content,
                parsed_yaml=parsed_yaml,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            # Return error placeholder if we can't load
            return YAMLFile(
                path=Path.home() / ".dstack" / "config.yml",
                name="config.yml",
                config_type=DStackConfigType.SERVER,
                content=f"# Error loading global config: {str(e)}",
                parsed_yaml=None,
                is_valid=False,
                validation_errors=[str(e)]
            )
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle file selection"""
        if hasattr(event.node, 'data') and event.node.data:
            # Only handle actual YAML files (not groups or other nodes)
            if hasattr(event.node.data, 'name') and hasattr(event.node.data, 'path'):
                self.current_file = event.node.data
                self.post_message(FileSelected(event.node.data))
                # Also notify for debugging
                self.main_app.notify(f"Tree: {event.node.data.name}", timeout=2)


class FileSelected(Message):
    def __init__(self, yaml_file: YAMLFile):
        super().__init__()
        self.yaml_file = yaml_file


class ProjectChanged(Message):
    def __init__(self, project_name: str, project_path: Path):
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path


class CondaEnvChanged(Message):
    def __init__(self, env_name: str, env_path: str):
        super().__init__()
        self.env_name = env_name
        self.env_path = env_path


class YAMLPreviewWidget(Container):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
        self.yaml_manager = yaml_manager
    
    def compose(self) -> ComposeResult:
        # Get projects from dstack config
        projects = self.yaml_manager.db.get_dstack_projects()
        project_options = []
        default_project = None
        
        if projects:
            for project in projects:
                label = f"🚀 {project['name']}"
                if project['is_default']:
                    label += " (default)"
                    default_project = project['name']
                project_options.append((label, project['name']))
        
        # Get conda environments
        conda_envs = self.yaml_manager.db.get_conda_environments()
        conda_options = []
        default_conda = None
        
        if conda_envs:
            for env in conda_envs:
                conda_options.append((env['display_name'], env['name']))
                if env['name'] == 'base':  # Default to base environment
                    default_conda = env['name']
            
            # If no base environment, use the first one
            if not default_conda and conda_options:
                default_conda = conda_options[0][1]
        
        # Dropdown container with both project and conda dropdowns side by side
        
        dropdown_widgets = [
            Container(
                Static("Project:", id="project-label"),
                Select(project_options, value=default_project, id="project-select"),
                id="project-selector",
                classes="dropdown-item"
            )
        ]
        
        # Add conda dropdown if environments are available
        if conda_options:
            dropdown_widgets.append(
                Container(
                    Static("Environment:", id="conda-label"),
                    Select(conda_options, value=default_conda, id="conda-select"),
                    id="conda-selector",
                    classes="dropdown-item"
                )
            )
        
        yield Container(
            *dropdown_widgets,
            id="dropdowns-container",
            classes="dropdowns-horizontal"
        )
        
        # Tabbed content below the dropdowns
        with TabbedContent(initial="preview"):
            with TabPane("Preview", id="preview"):
                with ScrollableContainer(id="preview-container"):
                    yield Static("Select a YAML file to preview", id="preview-content")
            with TabPane("Edit", id="edit"):
                with Container(id="edit-container"):
                    yield TextArea("Select a YAML file to edit", language="yaml", show_line_numbers=True, id="edit-content")
            with TabPane("Note", id="note"):
                with Container(id="note-container"):
                    yield TextArea("Select a YAML file to add notes", id="note-content")
            with TabPane("Metadata", id="metadata"):
                with ScrollableContainer(id="metadata-container"):
                    yield Static("Select a YAML file to view metadata", id="metadata-content")
            with TabPane("Chat", id="chat"):
                with Container(id="chat-container"):
                    with ScrollableContainer(id="chat-messages"):
                        yield Static("Welcome! This is a service chatbot interface.\nAsk me anything about your service!", id="chat-welcome")
                    with Container(id="chat-input-container"):
                        yield Input(placeholder="Type your message here...", id="chat-input")
                        yield Button("Send", variant="primary", id="chat-send")
    
    def update_preview(self, yaml_file: YAMLFile):
        """Update all tabs with selected YAML file"""
        self.current_file = yaml_file
        self._update_preview_tab(yaml_file)
        self._update_edit_tab(yaml_file)
        self._update_note_tab(yaml_file)
        self._update_metadata_tab(yaml_file)
        self._update_chat_tab_visibility(yaml_file)
        self._update_dropdowns_for_file(yaml_file)
    
    def _update_preview_tab(self, yaml_file: YAMLFile):
        """Update the preview tab with syntax highlighted content"""
        try:
            syntax = Syntax(
                yaml_file.content,
                "yaml",
                theme="monokai",
                line_numbers=True,
                word_wrap=False
            )
            
            content_widget = self.query_one("#preview-content", Static)
            content_widget.update(Panel(syntax, title=yaml_file.name))
            
        except Exception as e:
            content_widget = self.query_one("#preview-content", Static)
            content_widget.update(f"Error displaying file: {str(e)}")
    
    def _update_edit_tab(self, yaml_file: YAMLFile):
        """Update the edit tab with editable YAML content"""
        try:
            edit_widget = self.query_one("#edit-content", TextArea)
            edit_widget.text = yaml_file.content
            
            # Store current file path for saving in the main app
            self.app.current_edit_file_path = yaml_file.path
            
        except Exception as e:
            edit_widget = self.query_one("#edit-content", TextArea)
            edit_widget.text = f"Error loading file for editing: {str(e)}"
    
    def _update_note_tab(self, yaml_file: YAMLFile):
        """Update the note tab with markdown content for the selected file"""
        try:
            # Get note for this file from database (editable)
            note_content = self._get_file_note(yaml_file.path)
            note_widget = self.query_one("#note-content", TextArea)
            if note_content:
                # Load note content into editable text area
                note_widget.text = note_content
            else:
                note_widget.text = "# Notes for this file\n\nAdd your notes here..."
            
            # Store current file path for saving in the main app
            self.app.current_note_file_path = yaml_file.path
        except Exception as e:
            note_widget = self.query_one("#note-content", TextArea)
            note_widget.text = f"Error loading note: {str(e)}"
    
    def _get_file_note(self, file_path: Path) -> str:
        """Get note content for a file from database"""
        # Access database through the app's yaml_manager
        if hasattr(self.app, 'yaml_manager'):
            return self.app.yaml_manager.db.get_file_note(str(file_path))
        return ""
    
    def _update_metadata_tab(self, yaml_file: YAMLFile):
        """Update the metadata tab with file information"""
        try:
            metadata_lines = []
            
            # Basic file information
            metadata_lines.append("📄 **File Information**")
            metadata_lines.append(f"Name: {yaml_file.name}")
            metadata_lines.append(f"Path: {yaml_file.path}")
            metadata_lines.append(f"Type: {yaml_file.config_type.value}")
            
            # Check if it's a global config by examining the path
            is_global = "/.dstack/" in str(yaml_file.path) and yaml_file.name == "config.yml"
            metadata_lines.append(f"Global Config: {'Yes' if is_global else 'No'}")
            metadata_lines.append("")
            
            # File size and content info
            content_size = len(yaml_file.content.encode('utf-8'))
            line_count = yaml_file.content.count('\n') + 1
            metadata_lines.append("📊 **Content Statistics**")
            metadata_lines.append(f"File Size: {content_size:,} bytes")
            metadata_lines.append(f"Lines: {line_count:,}")
            metadata_lines.append(f"Characters: {len(yaml_file.content):,}")
            metadata_lines.append("")
            
            # Validation status
            metadata_lines.append("✅ **Validation Status**")
            metadata_lines.append(f"Valid YAML: {'Yes' if yaml_file.is_valid else 'No'}")
            if yaml_file.validation_errors and len(yaml_file.validation_errors) > 0:
                metadata_lines.append("Errors:")
                for error in yaml_file.validation_errors:
                    metadata_lines.append(f"  • {error}")
            else:
                metadata_lines.append("No validation errors")
            metadata_lines.append("")
            
            # Database information
            if hasattr(self.app, 'yaml_manager'):
                db_info = self.app.yaml_manager.db.get_file_by_path(str(yaml_file.path))
                if db_info:
                    metadata_lines.append("💾 **Database Information**")
                    metadata_lines.append(f"Created: {db_info.get('created_at', 'Unknown')}")
                    metadata_lines.append(f"Modified: {db_info.get('updated_at', 'Unknown')}")
                    metadata_lines.append(f"History Entries: {db_info.get('history_count', 0)}")
                    metadata_lines.append("")
            
            # YAML structure info
            if yaml_file.parsed_yaml:
                metadata_lines.append("🏗️ **YAML Structure**")
                try:
                    import yaml
                    if isinstance(yaml_file.parsed_yaml, dict):
                        key_count = len(yaml_file.parsed_yaml.keys())
                        metadata_lines.append(f"Top-level keys: {key_count}")
                        metadata_lines.append("Keys:")
                        for key in sorted(yaml_file.parsed_yaml.keys()):
                            value = yaml_file.parsed_yaml[key]
                            value_type = type(value).__name__
                            metadata_lines.append(f"  • {key}: {value_type}")
                    elif isinstance(yaml_file.parsed_yaml, list):
                        metadata_lines.append(f"Array with {len(yaml_file.parsed_yaml)} items")
                    else:
                        metadata_lines.append(f"Single value: {type(yaml_file.parsed_yaml).__name__}")
                except Exception as e:
                    metadata_lines.append(f"Error analyzing structure: {e}")
                metadata_lines.append("")
            
            # Join all metadata into a single string
            metadata_content = "\n".join(metadata_lines)
            
            metadata_widget = self.query_one("#metadata-content", Static)
            metadata_widget.update(metadata_content)
            
        except Exception as e:
            metadata_widget = self.query_one("#metadata-content", Static)
            metadata_widget.update(f"Error loading metadata: {str(e)}")
    
    def _update_chat_tab_visibility(self, yaml_file: YAMLFile):
        """Show/hide chat tab based on file type and initialize chat if needed"""
        try:
            # Check if this is a service type YAML
            is_service = yaml_file.config_type == DStackConfigType.SERVICE
            
            # Get the tabbed content
            tabbed_content = self.query_one("TabbedContent")
            
            if is_service:
                # Show chat tab and initialize it
                tabbed_content.show_tab("chat")
                self._initialize_chat_for_service(yaml_file)
            else:
                # Hide chat tab
                tabbed_content.hide_tab("chat")
                    
        except Exception as e:
            # Silently handle errors in chat tab visibility
            pass
    
    def _initialize_chat_for_service(self, yaml_file: YAMLFile):
        """Initialize chat interface with service-specific context"""
        try:
            # Initialize chat messages with service context
            self._add_initial_chat_messages(yaml_file)
            
        except Exception as e:
            # Handle initialization errors gracefully
            pass
    
    def _add_initial_chat_messages(self, yaml_file: YAMLFile):
        """Add initial chat messages based on service configuration"""
        try:
            chat_messages = self.query_one("#chat-messages", ScrollableContainer)
            
            # Clear existing messages
            chat_messages.remove_children()
            
            # Add welcome message
            service_name = "your service"
            if yaml_file.parsed_yaml and isinstance(yaml_file.parsed_yaml, dict):
                service_name = yaml_file.parsed_yaml.get('name', 'your service')
            
            welcome_msg = f"""🤖 **Service Assistant**: Hello! I'm here to help you with {service_name}.

**I can help you with:**

- Service configuration and setup
- Port and endpoint management  
- Environment variables and secrets
- Deployment troubleshooting
- Performance optimization
- Scaling and resource management

**Try asking me:**

- "How do I configure environment variables?"
- "What ports does this service use?"
- "How can I scale this service?"
- "What's the health check endpoint?"

Type your question below! 👇"""
            
            from textual.widgets import Markdown
            chat_messages.mount(Markdown(welcome_msg, classes="chat-bot chat-message"))
            
        except Exception as e:
            # Fallback to simple message
            try:
                chat_messages = self.query_one("#chat-messages", ScrollableContainer)
                chat_messages.remove_children()
                from textual.widgets import Markdown
                chat_messages.mount(Markdown("🤖 Service chat ready! Ask me anything about your service.", classes="chat-bot chat-message"))
            except:
                pass
    
    def _update_dropdowns_for_file(self, yaml_file: YAMLFile):
        """Update dropdown selections based on file-specific settings"""
        try:
            # Get saved settings for this file
            file_settings = self.yaml_manager.db.get_file_settings(str(yaml_file.path))
            
            # Update project dropdown if we have a saved project
            if file_settings.get('project_name'):
                try:
                    project_select = self.query_one("#project-select", Select)
                    # Check if the saved project exists in current options
                    for option_label, option_value in project_select._options:
                        if option_value == file_settings['project_name']:
                            project_select.value = file_settings['project_name']
                            break
                except Exception as e:
                    print(f"Error updating project dropdown: {e}")
            
            # Update conda dropdown if we have a saved environment
            if file_settings.get('conda_env'):
                try:
                    conda_select = self.query_one("#conda-select", Select)
                    # Check if the saved conda env exists in current options
                    for option_label, option_value in conda_select._options:
                        if option_value == file_settings['conda_env']:
                            conda_select.value = file_settings['conda_env']
                            break
                except Exception as e:
                    print(f"Error updating conda dropdown: {e}")
                    
        except Exception as e:
            print(f"Error updating dropdowns for file: {e}")
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle project and conda environment selection changes"""
        if event.control.id == "project-select":
            selected_project = event.value
            
            # Save project setting for current file
            if self.current_file:
                self.yaml_manager.db.save_file_settings(
                    str(self.current_file.path), 
                    project_name=selected_project
                )
            
            # Find the selected project and get its repo path
            projects = self.yaml_manager.db.get_dstack_projects()
            selected_project_info = None
            for project in projects:
                if project['name'] == selected_project:
                    selected_project_info = project
                    break
            
            if selected_project_info and selected_project_info['repos']:
                # Use the first repo path as the working directory
                repo_path = Path(selected_project_info['repos'][0]['path'])
                if repo_path.exists():
                    self.app.post_message(ProjectChanged(selected_project, repo_path))
                else:
                    # Show error if repo path doesn't exist
                    self.app.notify(f"Repository path not found: {repo_path}", severity="error")
        
        elif event.control.id == "conda-select":
            selected_env = event.value
            
            # Save conda environment setting for current file
            if self.current_file:
                self.yaml_manager.db.save_file_settings(
                    str(self.current_file.path), 
                    conda_env=selected_env
                )
            
            # Find the selected conda environment
            conda_envs = self.yaml_manager.db.get_conda_environments()
            selected_env_info = None
            for env in conda_envs:
                if env['name'] == selected_env:
                    selected_env_info = env
                    break
            
            if selected_env_info:
                self.app.post_message(CondaEnvChanged(selected_env, selected_env_info['path']))
            else:
                self.app.notify(f"Conda environment not found: {selected_env}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle chat button presses"""
        if event.button.id == "chat-send":
            self._handle_chat_send()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle chat input submission (Enter key)"""
        if event.input.id == "chat-input":
            self._handle_chat_send()
    
    def _handle_chat_send(self):
        """Process chat message and generate response"""
        try:
            chat_input = self.query_one("#chat-input", Input)
            user_message = chat_input.value.strip()
            
            if not user_message:
                return
            
            # Clear input
            chat_input.value = ""
            
            # Add user message to chat
            self._add_chat_message(user_message, is_user=True)
            
            # Generate bot response
            bot_response = self._generate_bot_response(user_message)
            self._add_chat_message(bot_response, is_user=False)
            
        except Exception as e:
            # Handle chat errors gracefully
            self._add_chat_message("Sorry, I encountered an error. Please try again.", is_user=False)
    
    def _add_chat_message(self, message: str, is_user: bool = False):
        """Add a message to the chat interface"""
        try:
            chat_messages = self.query_one("#chat-messages", ScrollableContainer)
            
            # Create message styling
            if is_user:
                prefix = "👤 **You**: "
                classes = "chat-user chat-message"
            else:
                prefix = "🤖 **Assistant**: "
                classes = "chat-bot chat-message"
            
            # Create markdown message
            from textual.widgets import Markdown
            message_content = f"{prefix}{message}"
            chat_messages.mount(Markdown(message_content, classes=classes))
            
            # Scroll to bottom
            chat_messages.scroll_end()
            
        except Exception as e:
            # Fallback for message display errors
            pass
    
    def _generate_bot_response(self, user_message: str) -> str:
        """Generate a dummy bot response based on user message"""
        message_lower = user_message.lower()
        
        # Service configuration responses
        if any(word in message_lower for word in ['port', 'endpoint', 'url']):
            return """For service ports and endpoints:

**Port Configuration:**
```yaml
ports:
  - "8080:8080"  # host:container port mapping
```

**Health Check Endpoint:**
```yaml
http_healthcheck: "/health"
```

**Service URL:**
Your service will be available at `https://<gateway-domain>/<service-name>`"""

        elif any(word in message_lower for word in ['env', 'environment', 'variable']):
            return """Environment variables can be configured in several ways:

**Method 1: Direct in YAML**
```yaml
env:
  - DATABASE_URL=postgresql://user:pass@db:5432/mydb
  - API_KEY=your-secret-key
```

**Method 2: From file**
```yaml
env:
  - .env
```

**Method 3: Secret variables**
```yaml
env:
  - DATABASE_URL=${{ secrets.DATABASE_URL }}
```"""

        elif any(word in message_lower for word in ['scale', 'scaling', 'replicas']):
            return """Service scaling options:

**Horizontal Scaling:**
```yaml
replicas: 3  # Run 3 instances
```

**Resource Limits:**
```yaml
resources:
  cpu: 2
  memory: 4GB
  gpu: 1  # Optional GPU
```

**Auto-scaling** (if supported):
```yaml
replicas:
  min: 1
  max: 10
```"""

        elif any(word in message_lower for word in ['health', 'check', 'monitoring']):
            return """Health check configuration:

**HTTP Health Check:**
```yaml
http_healthcheck: "/health"
```

**Custom Health Command:**
```yaml
healthcheck:
  - curl
  - -f
  - http://localhost:8080/health
```

**Health Check Settings:**
```yaml
healthcheck_timeout: 30s
healthcheck_interval: 60s
```"""

        elif any(word in message_lower for word in ['deploy', 'deployment', 'run']):
            return """To deploy your service:

**1. Run the service:**
```bash
dstack run . -f your-service.yml
```

**2. Check status:**
```bash
dstack ps
```

**3. View logs:**
```bash
dstack logs <run-name>
```

**4. Stop service:**
```bash
dstack stop <run-name>
```"""

        elif any(word in message_lower for word in ['help', 'what', 'how']):
            return """I can help you with:

🔧 **Configuration**: Ports, environment variables, resources
📊 **Scaling**: Replicas, auto-scaling, resource limits  
🏥 **Health Checks**: HTTP endpoints, custom commands
🚀 **Deployment**: Running, monitoring, troubleshooting
🔒 **Security**: Secrets, authentication, networking

Try asking specific questions like:

- "How do I set environment variables?"
- "What ports should I configure?"
- "How do I scale my service?"
- "How do I add health checks?"
"""

        else:
            return f"""I understand you're asking about: "{user_message}"

For service-related questions, I can help with:

- **Configuration** (ports, env vars, resources)
- **Deployment** (running, monitoring, logs)
- **Scaling** (replicas, auto-scaling) 
- **Health Checks** (endpoints, monitoring)
- **Troubleshooting** (common issues, debugging)

Could you be more specific about what you'd like to know?"""



class YAMLPropertiesWidget(ScrollableContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        yield Static("Select a YAML file to view properties", id="properties-content", markup=True)
    
    def update_properties(self, yaml_file: YAMLFile):
        """Update properties panel with file details"""
        self.current_file = yaml_file
        
        # Build properties with rich text instead of markup to avoid parsing issues
        from rich.text import Text
        
        text = Text()
        text.append("File: ", style="bold")
        text.append(f"{yaml_file.name}\n")
        text.append("Type: ", style="bold")
        text.append(f"{yaml_file.config_type.value}\n")
        text.append("Path: ", style="bold")
        text.append(f"{yaml_file.path}\n")
        
        if yaml_file.parsed_yaml:
            # Extract key properties from parsed YAML
            if isinstance(yaml_file.parsed_yaml, dict):
                for key in ['type', 'name', 'python', 'image', 'port', 'resources']:
                    if key in yaml_file.parsed_yaml:
                        value = yaml_file.parsed_yaml[key]
                        text.append(f"{key.title()}: ", style="bold")
                        text.append(f"{value}\n")
        
        if not yaml_file.is_valid and yaml_file.validation_errors:
            text.append("Errors:\n", style="bold red")
            for error in yaml_file.validation_errors:
                text.append("  • ", style="red")
                # Truncate very long error messages
                error_text = str(error)[:200] + "..." if len(str(error)) > 200 else str(error)
                text.append(f"{error_text}\n")
        
        properties_widget = self.query_one("#properties-content", Static)
        properties_widget.update(text)


class AddFileModal(ModalScreen):
    """Modal screen for adding YAML files"""
    
    CSS = """
    AddFileModal {
        align: center middle;
        background: $surface-darken-2 80%;
    }
    
    #add-file-dialog {
        width: 80;
        height: auto;
        border: thick $primary 80%;
        background: $surface;
        layout: vertical;
        padding: 1;
    }
    
    #group-select {
        margin: 1 0;
    }
    
    #template-select {
        margin: 1 0;
    }
    
    #completion-dropdown {
        height: 6;
        margin: 1 0;
        display: none;
    }
    
    #button-container {
        layout: horizontal;
        height: 3;
        width: 100%;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
        width: 12;
    }
    
    #filepath-input {
        margin: 1 0;
    }
    
    #completion-hint {
        height: 2;
        margin: 1 0;
        color: $text-muted;
    }
    
    #completion-dropdown {
        height: 8;
        margin: 1 0;
        border: solid $accent;
        display: none;
    }
    
    #completion-dropdown.visible {
        display: block;
    }
    
    #template-select {
        margin: 1 0;
    }
    
    #template-label {
        margin: 1 0;
    }
    
    #button-row {
        layout: horizontal;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "handle_enter", "Add File"),
        Binding("tab", "show_completions", "Complete"),
        Binding("up", "completion_up", "Up", show=False),
        Binding("down", "completion_down", "Down", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.template_visible = False
        self.dropdown_visible = False
        self.current_completions = []
        self.completion_index = 0
    
    def compose(self) -> ComposeResult:
        with Container(id="add-file-dialog"):
            yield Static("📁 Add YAML File", id="add-file-title")
            yield Static("Enter file path:", id="filepath-label")
            yield Input(placeholder="Enter path to .dstack.yml file", id="filepath-input")
            yield Tree("Completions", id="completion-dropdown")
            yield Static("Select Group:", id="group-label")
            group_options = self._get_group_options()
            yield Select(group_options, id="group-select")
            yield Static("Select Template:", id="template-label")
            yield Select([
                ("Task", "task"),
                ("IDE", "ide"), 
                ("Service", "service"),
                ("Fleet", "fleet")
            ], id="template-select")
            with Container(id="button-container"):
                yield Button("Add File", variant="primary", id="add-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    def _check_file_exists_and_update_ui(self, filepath: str):
        """Check if file exists and show/hide template dropdown accordingly"""
        debug_log = get_log_file_path("modal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        try:
            log_debug(f"=== _check_file_exists_and_update_ui called with filepath: '{filepath}' ===")
            file_path = Path(filepath)
            log_debug(f"Created Path object: {file_path}")
            log_debug(f"File exists check: {file_path.exists()}")
            
            template_select = self.query_one("#template-select", Select)
            template_label = self.query_one("#template-label", Static)
            title = self.query_one("#add-file-title", Static)
            log_debug(f"Found template widgets - select: {template_select}, label: {template_label}, title: {title}")
            
            if filepath and not file_path.exists():
                # File doesn't exist, show template selection
                log_debug("SHOWING TEMPLATE - File doesn't exist")
                template_select.visible = True
                template_label.visible = True
                title.update("📁 Create New YAML File")
                self.template_visible = True
                log_debug(f"Set template_select.visible = {template_select.visible}")
                log_debug(f"Set template_label.visible = {template_label.visible}")
                log_debug(f"Updated title to: Create New YAML File")
                log_debug(f"Set self.template_visible = {self.template_visible}")
                self.refresh()
                log_debug("Called self.refresh()")
            else:
                # File exists, hide template selection
                log_debug("HIDING TEMPLATE - File exists or path empty")
                template_select.visible = False
                template_label.visible = False
                title.update("📁 Add Existing YAML File")
                self.template_visible = False
                log_debug(f"Set template_select.visible = {template_select.visible}")
                log_debug(f"Set template_label.visible = {template_label.visible}")
                log_debug(f"Updated title to: Add Existing YAML File")
                log_debug(f"Set self.template_visible = {self.template_visible}")
                self.refresh()
                log_debug("Called self.refresh()")
        except Exception as e:
            log_debug(f"ERROR in _check_file_exists_and_update_ui: {e}")
            import traceback
            log_debug(f"Traceback: {traceback.format_exc()}")
    
    def _get_group_options(self):
        """Get list of available groups for the dropdown"""
        group_options = []
        
        if hasattr(self.app, 'yaml_manager'):
            # Add custom groups
            custom_groups = self.app.yaml_manager.db.get_custom_groups()
            for group in custom_groups or []:
                icon = group.get('icon', '📁')
                group_options.append((f"{icon} {group['name']}", f"custom:{group['id']}"))
            
            # Always add Default group
            group_options.append(("📁 Default", "default:0"))
        
        return group_options if group_options else [("📁 Default", "default:0")]
    
    def on_mount(self) -> None:
        """Setup the modal when it opens"""
        debug_log = get_log_file_path("modal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug("=== on_mount called for AddFileModal ===")
        
        try:
            # Initially hide template elements
            template_select = self.query_one("#template-select", Select)
            template_label = self.query_one("#template-label", Static)
            log_debug(f"Found template widgets on mount - select: {template_select}, label: {template_label}")
            
            template_select.visible = False
            template_label.visible = False
            self.template_visible = False
            log_debug(f"Set template widgets to hidden: select.visible={template_select.visible}, label.visible={template_label.visible}")
            log_debug(f"Set self.template_visible = {self.template_visible}")
            
            # Set default selections
            group_select = self.query_one("#group-select", Select)
            log_debug(f"Group select options: {[str(opt) for opt in group_select.options]}")
            
            if group_select.options:
                group_select.value = group_select.options[0].value
                log_debug(f"Set default group selection: {group_select.value}")
            
            log_debug(f"Template select options: {[str(opt) for opt in template_select.options]}")
            if template_select.options:
                template_select.value = template_select.options[0].value
                log_debug(f"Set default template selection: {template_select.value}")
            
            # Focus filepath input
            filepath_input = self.query_one("#filepath-input", Input)
            filepath_input.focus()
            log_debug("Focused filepath input")
            
        except Exception as e:
            log_debug(f"ERROR in on_mount: {e}")
            import traceback
            log_debug(f"Traceback: {traceback.format_exc()}")
    
    def _load_template(self, template_type: str) -> str:
        """Load template content from external template file"""
        try:
            template_path = Path(__file__).parent / "templates" / f"{template_type}.yml"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    return f.read()
            else:
                # Fallback basic template
                return f"""type: {template_type}
name: my-{template_type}

# Add your configuration here
"""
        except Exception as e:
            return f"""type: {template_type}
name: my-{template_type}

# Error loading template: {e}
"""
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to check file existence"""
        debug_log = get_log_file_path("modal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug(f"=== on_input_changed called - input.id: {event.input.id}, value: '{event.value}' ===")
        
        if event.input.id == "filepath-input":
            log_debug("Calling _check_file_exists_and_update_ui")
            self._check_file_exists_and_update_ui(event.value)
        else:
            log_debug("Input ID does not match filepath-input")
    
    def _load_template(self, template_type: str) -> str:
        """Load template content from external template file"""
        try:
            template_path = Path(__file__).parent / "templates" / f"{template_type}.yml"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    return f.read()
            else:
                # Fallback basic template
                return f"""type: {template_type}
name: my-{template_type}

# Add your configuration here
"""
        except Exception as e:
            return f"""type: {template_type}
name: my-{template_type}

# Error loading template: {e}
"""
    
    def _get_config_type_from_template(self, template_type: str) -> DStackConfigType:
        """Map template type to DStackConfigType"""
        template_mapping = {
            "task": DStackConfigType.TASK,
            "ide": DStackConfigType.TASK,  # IDE is treated as task type
            "service": DStackConfigType.SERVICE,
            "fleet": DStackConfigType.FLEET
        }
        return template_mapping.get(template_type, DStackConfigType.TASK)
    
    
    def action_show_completions(self) -> None:
        """Show completion dropdown when Tab is pressed, or auto-complete if only one option"""
        filepath_input = self.query_one("#filepath-input", Input)
        current_path = filepath_input.value
        
        if not current_path:
            current_path = str(Path.cwd()) + "/"
            filepath_input.value = current_path
            filepath_input.cursor_position = len(current_path)
        
        completions = self.get_completions(current_path)
        if completions:
            if len(completions) == 1:
                # Auto-complete when there's only one option
                completion = completions[0]
                filepath_input.value = completion['path']
                filepath_input.cursor_position = len(completion['path'])
                self.hide_completion_dropdown()
            else:
                # Show dropdown when there are multiple options
                self.show_completion_dropdown(completions)
        else:
            self.hide_completion_dropdown()
    
    def action_completion_up(self) -> None:
        """Move up in completion dropdown"""
        if self.dropdown_visible and self.current_completions:
            self.completion_index = (self.completion_index - 1) % len(self.current_completions)
            self.update_completion_selection()
    
    def action_completion_down(self) -> None:
        """Move down in completion dropdown"""
        if self.dropdown_visible and self.current_completions:
            self.completion_index = (self.completion_index + 1) % len(self.current_completions)
            self.update_completion_selection()
    
    def get_completions(self, current_path: str) -> list:
        """Get list of possible completions for current path"""
        completions = []
        try:
            input_path = Path(current_path)
            
            # Expand home directory shortcut
            if current_path.startswith("~"):
                current_path = str(Path(current_path).expanduser())
                input_path = Path(current_path)
            
            if current_path.endswith('/') or input_path.is_dir():
                # Show directory contents
                search_dir = input_path if input_path.is_dir() else input_path.parent
                try:
                    for item in search_dir.iterdir():
                        if item.is_dir():
                            completions.append({
                                'path': str(item) + "/",
                                'display': f"📂 {item.name}/",
                                'type': 'directory'
                            })
                        elif item.name.endswith(('.yml', '.yaml')):
                            icon = "📄" if 'dstack' in item.name else "📋"
                            completions.append({
                                'path': str(item),
                                'display': f"{icon} {item.name}",
                                'type': 'yaml'
                            })
                except PermissionError:
                    pass
            else:
                # Show matching files in parent directory
                parent_dir = input_path.parent
                filename_start = input_path.name
                try:
                    for item in parent_dir.iterdir():
                        if item.name.startswith(filename_start):
                            if item.is_dir():
                                completions.append({
                                    'path': str(item) + "/",
                                    'display': f"📂 {item.name}/",
                                    'type': 'directory'
                                })
                            elif item.name.endswith(('.yml', '.yaml')):
                                icon = "📄" if 'dstack' in item.name else "📋"
                                completions.append({
                                    'path': str(item),
                                    'display': f"{icon} {item.name}",
                                    'type': 'yaml'
                                })
                except (FileNotFoundError, PermissionError):
                    pass
            
            # Sort: directories first, then YAML files, then others
            completions.sort(key=lambda x: (x['type'] != 'directory', x['type'] != 'yaml', x['display'].lower()))
            
        except Exception:
            pass
        
        return completions
    
    def show_completion_dropdown(self, completions: list):
        """Show the completion dropdown with options"""
        self.current_completions = completions
        self.completion_index = 0
        self.dropdown_visible = True
        
        dropdown = self.query_one("#completion-dropdown", Tree)
        dropdown.clear()
        
        for i, completion in enumerate(completions):
            node = dropdown.root.add(completion['display'])
            node.data = completion['path']
        
        dropdown.root.expand()
        dropdown.display = True
        
        # Select first item
        if completions:
            self.update_completion_selection()
    
    def hide_completion_dropdown(self):
        """Hide the completion dropdown"""
        self.dropdown_visible = False
        dropdown = self.query_one("#completion-dropdown", Tree)
        dropdown.display = False
        dropdown.clear()
    
    def update_completion_selection(self):
        """Update the selected item in dropdown"""
        dropdown = self.query_one("#completion-dropdown", Tree)
        if self.current_completions and 0 <= self.completion_index < len(self.current_completions):
            # Rebuild dropdown with selected item highlighted
            dropdown.clear()
            
            for i, completion in enumerate(self.current_completions):
                if i == self.completion_index:
                    # Highlight selected item
                    display_text = f"→ {completion['display']}"
                else:
                    display_text = f"  {completion['display']}"
                
                node = dropdown.root.add(display_text)
                node.data = completion['path']
            
            dropdown.root.expand()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle completion selection from dropdown"""
        # Check if this is from the completion dropdown
        if hasattr(event.node, 'data') and event.node.data:
            # Get the tree that triggered this event
            tree = event.control
            if tree.id == "completion-dropdown":
                # Find which completion was selected and update completion_index
                for i, completion in enumerate(self.current_completions):
                    if completion['path'] == event.node.data:
                        self.completion_index = i
                        break
                
                filepath_input = self.query_one("#filepath-input", Input)
                filepath_input.value = event.node.data
                filepath_input.cursor_position = len(event.node.data)
                self.hide_completion_dropdown()
                filepath_input.focus()
        
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to check file existence and show template dropdown"""
        if event.input.id == "filepath-input":
            # Hide completion dropdown when user types
            if self.dropdown_visible:
                self.hide_completion_dropdown()
            # Check if file exists and update template visibility
            self._check_file_exists_and_update_ui(event.value)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key pressed in input field"""
        if event.input.id == "filepath-input":
            if self.dropdown_visible and self.current_completions:
                # Enter selects current completion
                if 0 <= self.completion_index < len(self.current_completions):
                    completion = self.current_completions[self.completion_index]
                    event.input.value = completion['path']
                    event.input.cursor_position = len(completion['path'])
                    self.hide_completion_dropdown()
                    return
            
            # Regular add file functionality if no dropdown
            self.add_file()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        debug_log = get_log_file_path("modal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug(f"=== on_button_pressed called - button.id: {event.button.id} ===")
        
        if event.button.id == "add-btn":
            log_debug("Add button clicked, calling add_file()")
            self.add_file()
        elif event.button.id == "cancel-btn":
            log_debug("Cancel button clicked, popping screen")
            self.app.pop_screen()
    
    def action_cancel(self) -> None:
        """Cancel and return to main screen"""
        self.app.pop_screen()
    
    def on_click(self, event) -> None:
        """Handle clicking outside the modal to close it"""
        # Check if the click was outside the add-file-container
        try:
            container = self.query_one("#add-file-container")
            if not container.region.contains(event.screen_x, event.screen_y):
                self.action_cancel()
        except:
            # If there's any error, don't close the modal
            pass
    
    def action_handle_enter(self) -> None:
        """Handle Enter key - either select completion or add file"""
        if self.dropdown_visible and self.current_completions:
            # Enter selects current completion
            if 0 <= self.completion_index < len(self.current_completions):
                completion = self.current_completions[self.completion_index]
                filepath_input = self.query_one("#filepath-input", Input)
                filepath_input.value = completion['path']
                filepath_input.cursor_position = len(completion['path'])
                self.hide_completion_dropdown()
                # Focus the input field after selection
                filepath_input.focus()
                return
        
        # Regular add file functionality
        self.add_file()
    
    def add_file(self) -> None:
        """Add existing YAML file to selected group"""
        debug_log = get_log_file_path("modal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug("=== add_file method called ===")
        
        group_select = self.query_one("#group-select", Select)
        filepath_input = self.query_one("#filepath-input", Input)
        log_debug(f"Got widgets - group_select: {group_select}, filepath_input: {filepath_input}")
        
        # Get selected group
        selected_group_value = group_select.value
        log_debug(f"Selected group value: {selected_group_value}")
        
        if not selected_group_value or selected_group_value == group_select.BLANK:
            log_debug("No group selected, showing warning")
            self.notify("Please select a group", severity="warning", markup=False)
            return
        
        # Parse the group value (format: "type:task", "custom:123", "default:0")
        try:
            group_type, group_id = selected_group_value.split(":", 1)
            log_debug(f"Parsed group - type: {group_type}, id: {group_id}")
        except AttributeError:
            log_debug("Failed to parse group value")
            self.notify("Please select a group", severity="warning", markup=False)
            return
        
        filepath = filepath_input.value.strip()
        log_debug(f"Filepath from input: '{filepath}'")
        
        if not filepath:
            log_debug("Empty filepath, showing warning")
            self.notify("Please enter a file path", severity="warning", markup=False)
            return
        
        file_path = Path(filepath)
        log_debug(f"Created Path object: {file_path}")
        log_debug(f"File exists: {file_path.exists()}")
        
        # Check if file exists - if not, try to create from template
        if not file_path.exists():
            log_debug(f"File doesn't exist. Template visible flag: {self.template_visible}")
            
            # Check template widgets visibility
            try:
                template_select = self.query_one("#template-select", Select)
                template_label = self.query_one("#template-label", Static)
                log_debug(f"Template widgets - select.visible: {template_select.visible}, label.visible: {template_label.visible}")
                log_debug(f"Template select value: {template_select.value}")
            except Exception as e:
                log_debug(f"Error getting template widgets: {e}")
            
            if self.template_visible:
                log_debug("Template is visible, creating from template")
                # File doesn't exist but we can create it from template
                template_select = self.query_one("#template-select", Select)
                selected_template = template_select.value
                log_debug(f"Selected template: {selected_template}")
                
                if not selected_template or selected_template == template_select.BLANK:
                    log_debug("No template selected, showing warning")
                    self.notify("Please select a template for the new file", severity="warning", markup=False)
                    return
                
                # Load template content
                log_debug(f"Loading template content for: {selected_template}")
                template_content = self._load_template(selected_template)
                log_debug(f"Template content loaded (length: {len(template_content)})")
                
                # Create the directory if it doesn't exist
                log_debug(f"Creating parent directory: {file_path.parent}")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create the file with template content
                try:
                    log_debug(f"Writing file to: {file_path}")
                    with open(file_path, 'w') as f:
                        f.write(template_content)
                    log_debug("File written successfully")
                    self.notify(f"Created new file: {file_path.name}", severity="information", markup=False)
                except Exception as e:
                    log_debug(f"Failed to write file: {e}")
                    self.notify(f"Failed to create file: {e}", severity="error", markup=False)
                    return
            else:
                log_debug("Template not visible, showing file does not exist error")
                self.notify("File does not exist", severity="error", markup=False)
                return
        
        # Check if it's a YAML file
        if not file_path.name.endswith(('.yml', '.yaml')):
            self.notify("File must be a .yml or .yaml file", severity="error", markup=False)
            return
        
        # Check if file already exists in database
        if hasattr(self.app, 'yaml_manager'):
            existing_file = self.app.yaml_manager.db.get_file_by_path(str(file_path))
            if existing_file:
                self.notify("File already added to database", severity="error", markup=False)
                return
        
        try:
            # Read and add file to database
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Determine config type - if file was created from template, use template type
            if self.template_visible:
                template_select = self.query_one("#template-select", Select)
                selected_template = template_select.value
                config_type = self._get_config_type_from_template(selected_template)
            else:
                # For existing files, default to TASK
                config_type = DStackConfigType.TASK
            
            # Determine group handling based on dropdown selection
            if group_type == 'default':
                # Default group
                group_name = "Default"
                
                # First, ensure we have a "Default" custom group in the database
                default_group_id = self.app.yaml_manager.db.ensure_default_group()
                
                if hasattr(self.app, 'yaml_manager'):
                    yaml_file = self.app.yaml_manager.create_new_file(str(file_path), content, config_type)
                    if not yaml_file:
                        raise Exception("Failed to add file to database")
                    
                    # Assign the file to the Default custom group
                    file_data = self.app.yaml_manager.db.get_file_by_path(str(file_path))
                    if file_data:
                        self.app.yaml_manager.db.assign_file_to_custom_group(
                            file_data['id'], 
                            default_group_id
                        )
                        
            elif group_type == 'custom':
                # Custom group
                custom_group_id = int(group_id)
                custom_groups = self.app.yaml_manager.db.get_custom_groups()
                group_name = "Custom Group"
                for group in custom_groups:
                    if group['id'] == custom_group_id:
                        group_name = group['name']
                        break
                
                if hasattr(self.app, 'yaml_manager'):
                    yaml_file = self.app.yaml_manager.create_new_file(str(file_path), content, config_type)
                    if not yaml_file:
                        raise Exception("Failed to add file to database")
                    
                    # Assign the file to the custom group
                    file_data = self.app.yaml_manager.db.get_file_by_path(str(file_path))
                    if file_data:
                        self.app.yaml_manager.db.assign_file_to_custom_group(
                            file_data['id'], 
                            custom_group_id
                        )
            
            self.notify(f"Added {file_path.name} to {group_name} group", 
                       severity="information", markup=False)
            self.app.pop_screen()
            
            # Refresh the main screen
            if hasattr(self.app, 'action_refresh'):
                self.app.action_refresh()
                
        except Exception as e:
            self.notify(f"Failed to add file: {str(e)}", severity="error", markup=False)



class NewGroupScreen(Screen):
    """Screen for creating new custom groups"""
    
    CSS = """
    NewGroupScreen {
        layout: vertical;
        align: center middle;
    }
    
    #new-group-container {
        width: 60;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    #group-name-input {
        margin: 1 0;
    }
    
    #group-description-input {
        margin: 1 0;
    }
    
    #icon-selector {
        height: 8;
        border: solid $accent;
        margin: 1 0;
    }
    
    #button-row {
        layout: horizontal;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "create_group", "Create Group"),
    ]
    
    def __init__(self):
        super().__init__()
        self.icons = ["📁", "🗂️", "📂", "🎯", "⭐", "🏷️", "🔖", "📝", "💼", "🎨"]
        self.selected_icon = "📁"
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Create New Group", id="title"),
            Static("Group Name:", id="name-label"),
            Input(placeholder="Enter group name", id="group-name-input"),
            Static("Description (optional):", id="description-label"),
            Input(placeholder="Enter description", id="group-description-input"),
            Static("Select Icon:", id="icon-label"),
            Tree("Icons", id="icon-selector"),
            Horizontal(
                Button("Create Group", variant="primary", id="create-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                id="button-row"
            ),
            id="new-group-container"
        )
    
    def on_mount(self) -> None:
        """Setup the icon selector and focus name input"""
        # Setup icon tree
        icon_tree = self.query_one("#icon-selector", Tree)
        for icon in self.icons:
            node = icon_tree.root.add(f"{icon}")
            node.data = icon
        icon_tree.root.expand()
        
        # Focus name input
        self.query_one("#group-name-input", Input).focus()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle icon selection"""
        if hasattr(event.node, 'data') and event.node.data:
            tree = event.control
            if tree.id == "icon-selector":
                self.selected_icon = event.node.data
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "create-btn":
            self.create_group()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
    
    def action_cancel(self) -> None:
        """Cancel and return to main screen"""
        self.app.pop_screen()
    
    def action_create_group(self) -> None:
        """Create group on Enter key"""
        self.create_group()
    
    def create_group(self) -> None:
        """Create the new custom group"""
        name_input = self.query_one("#group-name-input", Input)
        description_input = self.query_one("#group-description-input", Input)
        
        group_name = name_input.value.strip()
        group_description = description_input.value.strip()
        
        if not group_name:
            self.notify("Please enter a group name", severity="warning", markup=False)
            return
        
        try:
            if hasattr(self.app, 'yaml_manager'):
                group_id = self.app.yaml_manager.db.add_custom_group(
                    group_name, 
                    group_description, 
                    "#1e90ff",  # Default color
                    self.selected_icon
                )
                
                self.notify(f"Created group '{group_name}' successfully!", 
                           severity="information", markup=False)
                self.app.pop_screen()
                
                # Refresh the main screen
                if hasattr(self.app, 'action_refresh'):
                    self.app.action_refresh()
                    
        except Exception as e:
            error_msg = "Group name already exists" if "UNIQUE constraint failed" in str(e) else "Failed to create group"
            self.notify(error_msg, severity="error", markup=False)


class YAMLEditorScreen(Screen):
    """Full-screen YAML editor"""
    
    CSS = """
    YAMLEditorScreen {
        layout: vertical;
    }
    
    #editor-header {
        height: 3;
        background: $primary;
        color: $text;
        margin-bottom: 1;
    }
    
    #editor-textarea {
        height: 1fr;
        margin: 0 1;
        border: solid $primary;
    }
    
    #editor-footer {
        height: 3;
        background: $surface;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+s", "save_file", "Save"),
        Binding("escape", "save_and_exit", "Save & Exit"),
    ]
    
    def __init__(self, yaml_file: YAMLFile):
        super().__init__()
        self.yaml_file = yaml_file
        self.original_content = yaml_file.content
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Editing: {self.yaml_file.name} | Ctrl+S: Save | Esc: Save & Exit", 
                   id="editor-header"),
            TextArea(
                self.yaml_file.content,
                language="yaml",
                theme="monokai",
                id="editor-textarea"
            ),
            Static("", id="editor-footer"),
            id="editor-container"
        )
    
    def on_mount(self) -> None:
        """Focus the text area when screen opens"""
        text_area = self.query_one("#editor-textarea", TextArea)
        text_area.focus()
    
    def action_save_file(self) -> None:
        """Save the file"""
        text_area = self.query_one("#editor-textarea", TextArea)
        new_content = text_area.text
        
        try:
            # Validate YAML before saving
            yaml.safe_load(new_content)
            
            # Check if this is the global config file
            if str(self.yaml_file.path).endswith("/.dstack/config.yml"):
                # Save global config to filesystem
                self.yaml_file.path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.yaml_file.path, 'w') as f:
                    f.write(new_content)
                
                # Update the object
                self.yaml_file.content = new_content
                self.yaml_file.parsed_yaml = yaml.safe_load(new_content)
                self.yaml_file.is_valid = True
                self.yaml_file.validation_errors = []
                
                self.notify("Global config saved successfully!", severity="information", markup=False)
            else:
                # Update in database for regular files
                if hasattr(self.app, 'yaml_manager'):
                    success = self.app.yaml_manager.update_file_content(self.yaml_file, new_content)
                    if not success:
                        raise Exception("Failed to update file in database")
                
                self.notify("File saved successfully!", severity="information", markup=False)
            
        except yaml.YAMLError as e:
            # Simple error message without special characters
            self.notify("YAML syntax error - please check your formatting", severity="error", markup=False)
        except Exception as e:
            self.notify("Save error - could not write file", severity="error", markup=False)
    
    
    def action_save_and_exit(self) -> None:
        """Save file and return to main screen"""
        try:
            self.action_save_file()
        except:
            # If save fails, still exit but don't update the file object
            pass
        # Always exit regardless of save success/failure
        self.app.pop_screen()


class ConfirmDeleteScreen(Screen):
    """Confirmation modal for delete operations"""
    
    CSS = """
    ConfirmDeleteScreen {
        align: center middle;
        background: $surface-darken-2 80%;
    }
    
    #delete-dialog {
        width: 60;
        height: 15;
        border: thick $warning 80%;
        background: $surface;
        content-align: center middle;
        layout: vertical;
    }
    
    #delete-title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $warning;
    }
    
    #delete-message {
        width: 100%;
        height: 5;
        content-align: center middle;
        text-align: center;
    }
    
    #button-container {
        layout: horizontal;
        width: 100%;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
        width: 12;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm_delete", "Delete"),
        Binding("y", "confirm_delete", "Yes"),
        Binding("n", "cancel", "No"),
    ]
    
    def __init__(self, item_name: str, item_type: str, callback):
        super().__init__()
        self.item_name = item_name
        self.item_type = item_type
        self.callback = callback
    
    def compose(self) -> ComposeResult:
        with Container(id="delete-dialog"):
            yield Static("⚠️ Confirm Delete", id="delete-title")
            yield Static(f"Are you sure you want to delete the {self.item_type}:\n\n'{self.item_name}'?\n\nThis action cannot be undone.", id="delete-message")
            with Container(id="button-container"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Delete", variant="error", id="delete-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete-btn":
            self.action_confirm_delete()
        else:
            self.action_cancel()
    
    def action_confirm_delete(self) -> None:
        """Confirm the deletion"""
        self.app.pop_screen()
        if self.callback:
            self.callback()
    
    def action_cancel(self) -> None:
        """Cancel the deletion"""
        self.app.pop_screen()


class NavigateInfoScreen(Screen):
    """Modal to show directory navigation and command options"""
    
    CSS = """
    NavigateInfoScreen {
        align: center middle;
        background: $surface-darken-2 80%;
    }
    
    #navigate-dialog {
        width: 80;
        height: 15;
        border: thick $primary 80%;
        background: $surface;
        layout: vertical;
        padding: 1;
    }
    
    #navigate-title {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-style: bold;
        color: $primary;
    }
    
    #navigate-path {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-align: center;
        text-style: italic;
        color: $text;
        margin-bottom: 1;
    }
    
    #commands-list {
        height: 6;
        border: solid $accent;
        background: $surface-lighten-1;
    }
    
    #button-container {
        layout: horizontal;
        width: 100%;
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
        width: 12;
    }
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "copy_selected", "Copy Selected"),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
    ]
    
    def __init__(self, directory_path: str, filename: str):
        super().__init__()
        self.directory_path = directory_path
        self.filename = filename
        self.selected_index = 0
        self.commands = [
            {
                "label": "📋 Copy file path",
                "command": f'"{directory_path}/{filename}"'
            },
            {
                "label": "🚀 Copy file path and dstack apply",
                "command": f'cd "{directory_path}" && dstack apply -f {filename}'
            }
        ]
    
    def compose(self) -> ComposeResult:
        with Container(id="navigate-dialog"):
            yield Static("📁 File Actions", id="navigate-title")
            yield Static(f"{self.directory_path}/{self.filename}", id="navigate-path")
            yield ListView(
                *[ListItem(Label(cmd['label'])) for cmd in self.commands],
                id="commands-list"
            )
            with Container(id="button-container"):
                yield Button("Close (Esc)", variant="default", id="close-btn")
    
    def on_mount(self) -> None:
        """Set initial selection"""
        commands_list = self.query_one("#commands-list", ListView)
        commands_list.index = 0
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.action_close()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection - copy and close"""
        self.action_copy_selected()
    
    def action_cursor_up(self) -> None:
        """Move selection up"""
        commands_list = self.query_one("#commands-list", ListView)
        if commands_list.index > 0:
            commands_list.index -= 1
    
    def action_cursor_down(self) -> None:
        """Move selection down"""
        commands_list = self.query_one("#commands-list", ListView)
        if commands_list.index < len(self.commands) - 1:
            commands_list.index += 1
    
    def action_copy_selected(self) -> None:
        """Copy the selected command to clipboard and close modal"""
        try:
            commands_list = self.query_one("#commands-list", ListView)
            selected_command = self.commands[commands_list.index]
            
            import subprocess
            # Copy to clipboard on macOS
            subprocess.run(['pbcopy'], input=selected_command['command'].encode(), check=True)
            self.notify(f"📋 Copied: {selected_command['label']}", timeout=2)
            
            # Close modal after copying
            self.app.pop_screen()
        except Exception:
            self.notify("❌ Could not copy to clipboard", severity="error")
    
    def action_close(self) -> None:
        """Close the modal"""
        self.app.pop_screen()


class RenameScreen(ModalScreen):
    """Modal screen for renaming files and groups"""
    
    CSS = """
    RenameScreen {
        align: center middle;
        background: $surface-darken-2 80%;
    }
    
    #rename-dialog {
        width: 60;
        height: 12;
        border: thick $primary 80%;
        background: $surface;
        layout: vertical;
        padding: 1;
    }
    
    #rename-title {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-style: bold;
        color: $primary;
    }
    
    #current-name {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-style: italic;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #rename-input {
        width: 100%;
        height: 3;
        border: solid $accent;
        margin-bottom: 1;
    }
    
    #button-container {
        layout: horizontal;
        width: 100%;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
        width: 12;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm_rename", "Rename"),
    ]
    
    def __init__(self, item_type: str, current_name: str, item_data: Any):
        super().__init__()
        self.item_type = item_type  # "file" or "group"
        self.current_name = current_name
        self.item_data = item_data
        self.new_name = current_name
    
    def compose(self) -> ComposeResult:
        with Container(id="rename-dialog"):
            yield Static(f"🏷️ Rename {self.item_type.title()}", id="rename-title")
            yield Static(f"Current: {self.current_name}", id="current-name")
            yield Input(value=self.current_name, placeholder=f"Enter new {self.item_type} name", id="rename-input")
            with Container(id="button-container"):
                yield Button("Rename", variant="primary", id="rename-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    def on_mount(self) -> None:
        """Focus the input field and select all text"""
        def setup_input():
            input_widget = self.query_one("#rename-input", Input)
            input_widget.focus()
            # Select all text for easy replacement
            if input_widget.value:
                input_widget.cursor_position = len(input_widget.value)
                input_widget.selection_anchor = 0
        
        # Delay the setup slightly to ensure the widget is fully mounted
        self.call_later(setup_input)
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Update new name as user types"""
        if event.input.id == "rename-input":
            self.new_name = event.value.strip()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "rename-btn":
            self.action_confirm_rename()
        elif event.button.id == "cancel-btn":
            self.action_cancel()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field"""
        if event.input.id == "rename-input":
            self.action_confirm_rename()
    
    def action_confirm_rename(self) -> None:
        """Confirm the rename operation"""
        # Get the current value directly from the input field
        input_widget = self.query_one("#rename-input", Input)
        self.new_name = input_widget.value.strip()
        
        if not self.new_name:
            self.notify("❌ Name cannot be empty", severity="error")
            return
        
        if self.new_name == self.current_name:
            self.notify("ℹ️ Name unchanged", severity="info")
            self.dismiss({"action": "cancel"})
            return
        
        # Validate the name
        if self.item_type == "file":
            if not self.new_name.endswith('.yml'):
                self.new_name += '.yml'
            
            # Basic filename validation
            invalid_chars = '<>:"/\\|?*'
            if any(char in self.new_name for char in invalid_chars):
                self.notify("❌ Invalid filename characters", severity="error")
                return
        
        # Return the result to the calling screen
        result = {"action": "rename", "old_name": self.current_name, "new_name": self.new_name, "item_data": self.item_data}
        self.dismiss(result)
    
    def action_cancel(self) -> None:
        """Cancel the rename operation"""
        self.dismiss({"action": "cancel"})


class DStackYAMLManager(App):
    """dstack YAML Management TUI"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 1fr 2fr;
        grid-rows: auto 1fr auto;
        height: 100vh;
    }
    
    Header {
        column-span: 2;
        height: auto;
    }
    
    #file-tree {
        border: solid $primary;
        margin: 1;
        height: 1fr;
    }
    
    Tree > TreeNode {
        margin: 1 0;
        padding: 0 1;
    }
    
    #preview-pane {
        border: solid $primary;
        margin: 1;
        height: 1fr;
    }
    
    TabbedContent {
        height: 1fr;
    }
    
    TabPane {
        height: 1fr;
    }
    
    #preview-container, #edit-container, #note-container, #metadata-container, #chat-container {
        height: 1fr;
        width: 1fr;
    }
    
    #preview-content, #metadata-content {
        padding: 1;
        height: auto;
        width: 1fr;
    }
    
    #edit-content, #note-content {
        padding: 1;
        height: 1fr;
        width: 1fr;
        border: solid $accent;
        background: $surface-lighten-1;
    }
    
    #chat-container {
        layout: vertical;
        padding: 1;
    }
    
    
    #chat-messages {
        height: 1fr;
        border: solid $accent;
        background: $surface-lighten-1;
        margin-bottom: 1;
        padding: 1;
    }
    
    #chat-input-container {
        layout: horizontal;
        height: 3;
        align: center middle;
    }
    
    #chat-input {
        width: 1fr;
        margin-right: 1;
    }
    
    #chat-send {
        width: 10;
    }
    
    .chat-message {
        margin: 1 0;
        padding: 1;
    }
    
    .chat-user {
        background: $primary-lighten-2;
        text-align: right;
    }
    
    .chat-bot {
        background: $surface-lighten-2;
        text-align: left;
    }
    
    .dropdowns-horizontal {
        layout: horizontal;
        height: auto;
        margin: 0 1;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }
    
    .dropdown-item {
        layout: horizontal;
        height: auto;
        width: 1fr;
        margin-right: 1;
        padding: 0 1;
    }
    
    .dropdown-item:last-child {
        margin-right: 0;
    }
    
    #project-label, #conda-label {
        width: auto;
        margin-right: 1;
        content-align: center middle;
        min-width: 12;
    }
    
    #project-select, #conda-select {
        width: 1fr;
    }
    
    Footer {
        column-span: 2;
        height: auto;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+x", "smart_quit", "Quit"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+n", "add_file", "Add File"),
        Binding("ctrl+e", "edit_file", "Edit File"),
        Binding("ctrl+g", "new_group", "New Group"),
        Binding("ctrl+t", "check_dstack_status", "Check Status"),
        Binding("delete", "delete_selected", "Delete"),
        Binding("ctrl+d", "delete_selected", "Delete"),
        Binding("ctrl+a", "navigate_to_file", "Navigate to File"),
        Binding("ctrl+s", "save_note", "Save Content"),
        Binding("ctrl+u", "rename_selected", "Rename"),
    ]
    
    def __init__(self, root_path: str = None, config_manager=None, restore_state_file: str = None):
        super().__init__()
        self.config_manager = config_manager
        self.yaml_manager = YAMLManager(
            Path(root_path) if root_path else None,
            config_manager=config_manager
        )
        self._terminal_script_path = None
        self._restore_state_file = restore_state_file
        # Initialize conda environment tracking
        self.selected_conda_env = None
        self.selected_conda_path = None
        # Initialize dstack status tracking
        self.dstack_status = {}  # {filename: status}
        self.dstack_checking = False  # Track if status check is in progress
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header()
        yield FileTreeWidget(self.yaml_manager, main_app=self, id="file-tree")
        yield YAMLPreviewWidget(self.yaml_manager, id="preview-pane")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app starts"""
        print("🚀 APP MOUNTED")
        self.title = "dstack YAML Manager"
        self.sub_title = f"Managing YAML files in {self.yaml_manager.root_path} • Use ↑↓←→ keys or Page Up/Down to scroll preview"
        print(f"📁 Root path: {self.yaml_manager.root_path}")
        
        # Initialize note tracking
        self.current_note_file_path = None
        
        # Load saved dstack status from database
        self.dstack_status = self.yaml_manager.db.load_dstack_status()
        print(f"📊 Loaded {len(self.dstack_status)} dstack status entries from database")
        
        # Let's see if the tree is built properly
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            print(f"🌳 File tree found: {file_tree}")
            print(f"   Tree children count: {len(file_tree.root.children)}")
            
            # Force rebuild tree to see if it shows the logs
            print("🔄 Forcing tree rebuild...")
            file_tree.build_tree()
            print(f"   Tree children count after rebuild: {len(file_tree.root.children)}")
            
            # Show what's actually in the tree
            print("🔍 Tree contents:")
            for i, child in enumerate(file_tree.root.children):
                print(f"   Child {i}: {child.label if hasattr(child, 'label') else 'NO_LABEL'}")
                print(f"     Has data: {hasattr(child, 'data') and child.data is not None}")
                if hasattr(child, 'children'):
                    print(f"     Subchildren: {len(child.children)}")
                    for j, subchild in enumerate(child.children):
                        print(f"       Subchild {j}: {subchild.label if hasattr(subchild, 'label') else 'NO_LABEL'}")
                        print(f"         Has data: {hasattr(subchild, 'data') and subchild.data is not None}")
                        
        except Exception as e:
            print(f"❌ Could not find file tree: {e}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
        
        # Check for restore state file passed via CLI or auto-restore hint file
        if self._restore_state_file:
            print(f"🔄 CLI restore mode: {self._restore_state_file}")
            if os.path.exists(self._restore_state_file):
                print("✅ State file exists, restoring...")
                self.call_later(lambda: self.restore_app_state(self._restore_state_file))
            else:
                print("❌ CLI state file no longer exists")
        else:
            # Check for auto-restore hint file
            restore_hint_file = os.path.join(self.yaml_manager.root_path, ".dstack_restore_state")
            if os.path.exists(restore_hint_file):
                print("🔄 Found restore hint file, attempting auto-restore...")
                try:
                    with open(restore_hint_file, 'r') as f:
                        state_file_path = f.read().strip()
                    
                    print(f"📄 State file path: {state_file_path}")
                    
                    if os.path.exists(state_file_path):
                        print("✅ State file exists, restoring...")
                        # Schedule restoration after the UI is fully loaded
                        self.call_later(lambda: self.restore_app_state(state_file_path))
                        
                        # Clean up hint file
                        os.remove(restore_hint_file)
                        print("🗑️ Removed restore hint file")
                    else:
                        print("❌ State file no longer exists")
                        os.remove(restore_hint_file)
                        
                except Exception as e:
                    print(f"❌ Error during auto-restore: {e}")
                    # Clean up hint file on error
            else:
                # Check for hint files in project directories
                print("🔍 No hint file in current directory, checking project directories...")
                projects = self.yaml_manager.db.get_dstack_projects()
                for project in projects:
                    if project.get('repos'):
                        for repo in project['repos']:
                            repo_hint_file = os.path.join(repo['path'], ".dstack_restore_state")
                            if os.path.exists(repo_hint_file):
                                print(f"🔄 Found restore hint file in project repo: {repo_hint_file}")
                                try:
                                    with open(repo_hint_file, 'r') as f:
                                        state_file_path = f.read().strip()
                                    
                                    print(f"📄 State file path: {state_file_path}")
                                    
                                    if os.path.exists(state_file_path):
                                        print("✅ State file exists, restoring...")
                                        # Schedule restoration after the UI is fully loaded
                                        self.call_later(lambda: self.restore_app_state(state_file_path))
                                        
                                        # Clean up hint file
                                        os.remove(repo_hint_file)
                                        print("🗑️ Removed restore hint file")
                                        return  # Exit after finding the first valid hint file
                                    else:
                                        print("❌ State file no longer exists")
                                        os.remove(repo_hint_file)
                                        
                                except Exception as e:
                                    print(f"❌ Error during project auto-restore: {e}")
                                    try:
                                        os.remove(repo_hint_file)
                                    except:
                                        pass
                    try:
                        os.remove(restore_hint_file)
                    except:
                        pass
    
    def on_key(self, event) -> None:
        """Handle key events globally"""
        # Debug logging to file
        debug_log = get_log_file_path("terminal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug(f"KEY PRESSED: {event.key}")
        
        # Handle escape key in note editing mode
        if event.key == "escape":
            try:
                # Check if note TextArea currently has focus
                note_widget = self.query_one("#note-content", TextArea)
                if note_widget.has_focus:
                    # Remove focus from TextArea to exit editing mode
                    self.set_focus(None)
                    self.notify("📝 Exited note editing mode", timeout=1)
                    return
            except Exception:
                pass
        
        # Handle specific Ctrl+X for smart quit
        if event.key == "ctrl+x":
            log_debug("Ctrl+X detected in on_key, calling action_smart_quit")
            self.action_smart_quit()
            return
        
        # Handle specific Ctrl+N for add file
        if event.key == "ctrl+n":
            log_debug("Ctrl+N detected in on_key, calling action_add_file")
            self.action_add_file()
            return
        
        # Handle specific Ctrl+E for edit file
        if event.key == "ctrl+e":
            log_debug("Ctrl+E detected in on_key, calling action_edit_file")
            self.action_edit_file()
            return
        
        # Use notify instead of print for TUI apps  
        if "ctrl" in event.key.lower():
            self.notify(f"🔑 CTRL Key: {event.key}", timeout=2)
            log_debug(f"CTRL key detected: {event.key}")
        
    def on_text_area_changed(self, event) -> None:
        """Auto-save note content when TextArea changes"""
        try:
            # Only auto-save if it's the note content and we have a file selected
            if (hasattr(event.text_area, 'id') and 
                event.text_area.id == "note-content" and 
                self.current_note_file_path):
                
                # Debounce auto-save - only save after a brief delay
                self.set_timer(1.0, self._auto_save_note)
        except Exception:
            pass  # Silently handle any auto-save errors
    def _auto_save_note(self) -> None:
        """Internal method for auto-saving notes"""
        try:
            if self.current_note_file_path:
                note_widget = self.query_one("#note-content", TextArea)
                note_content = note_widget.text
                self.yaml_manager.db.save_file_note(str(self.current_note_file_path), note_content)
        except Exception:
            pass  # Silently handle auto-save errors
    
    def on_file_selected(self, event: FileSelected) -> None:
        """Handle file selection from tree"""
        # Use notifications in TUI apps instead of print
        self.notify(f"Selected: {event.yaml_file.name}", severity="information")
        
        # Make sure the tree widget stores the current file
        file_tree = self.query_one("#file-tree", FileTreeWidget)
        file_tree.current_file = event.yaml_file
        self.notify(f"Stored in tree: {event.yaml_file.name}", timeout=1)
        
        preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
        preview_widget.update_preview(event.yaml_file)
    
    def on_project_changed(self, event: ProjectChanged) -> None:
        """Handle project selection change"""
        try:
            # Change working directory to the selected project
            self.notify(f"Switching to project: {event.project_name}", severity="information")
            # Update the yaml_manager root path
            self.yaml_manager.root_path = event.project_path
            # Refresh file tree with new path
            self.action_refresh()
            # Update the title
            self.sub_title = f"Managing YAML files in {event.project_path} • Project: {event.project_name}"
        except Exception as e:
            self.notify(f"Error switching project: {e}", severity="error")
    
    def on_conda_env_changed(self, event: CondaEnvChanged) -> None:
        """Handle conda environment selection change"""
        try:
            self.notify(f"Selected conda environment: {event.env_name}", severity="information")
            # Store the selected conda environment for future use
            # This could be used for activating the environment when running dstack commands
            self.selected_conda_env = event.env_name
            self.selected_conda_path = event.env_path
            # Update the subtitle to show the selected environment
            current_subtitle = self.sub_title or "Managing YAML files"
            if "Environment:" in current_subtitle:
                # Replace existing environment info
                parts = current_subtitle.split(" • Environment:")
                current_subtitle = parts[0]
            self.sub_title = f"{current_subtitle} • Environment: {event.env_name}"
        except Exception as e:
            self.notify(f"Error selecting conda environment: {e}", severity="error")
    
    def action_refresh(self) -> None:
        """Refresh the file list"""
        self.yaml_manager.scan_files()
        file_tree = self.query_one("#file-tree", FileTreeWidget)
        file_tree.build_tree()
    
    
    def action_export_all(self) -> None:
        """Export all files to filesystem"""
        try:
            export_dir = Path.cwd() / "exported_dstack_configs"
            export_dir.mkdir(exist_ok=True)
            
            exported_paths = self.yaml_manager.db.export_all_files_to_filesystem(export_dir)
            
            self.notify(f"Exported {len(exported_paths)} files to {export_dir}", 
                       severity="information", markup=False)
        except Exception as e:
            self.notify("Export failed", severity="error", markup=False)
    
    def action_new_group(self) -> None:
        """Create a new group/category"""
        new_group_screen = NewGroupScreen()
        self.push_screen(new_group_screen)
    
    def action_add_file(self) -> None:
        """Add an existing file"""
        self.push_screen(AddFileModal())
    
    def action_edit_file(self) -> None:
        """Switch to edit tab for the currently selected YAML file"""
        try:
            # Get the current file from the file tree widget
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            current_file = file_tree.current_file
            
            if not current_file:
                self.notify("No file selected", severity="warning")
                return
            
            # Switch to the edit tab
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            tabbed_content = preview_widget.query_one("TabbedContent")
            tabbed_content.active = "edit"
            
            # Focus the edit text area
            edit_widget = preview_widget.query_one("#edit-content", TextArea)
            edit_widget.focus()
            
            self.notify("📝 Switched to edit mode", severity="info")
            
        except Exception as e:
            self.notify(f"Cannot switch to edit mode: {e}", severity="error")
    
    def action_check_dstack_status(self) -> None:
        """Check dstack status and update file indicators"""
        import subprocess
        import threading
        
        self.notify("🔍 Checking dstack status...", timeout=2)
        
        # Set checking flag and update tree to show blinking
        self.dstack_checking = True
        self._update_tree_with_status()
        
        # Run dstack ps in background
        def check_status():
            try:
                # Get current conda environment name from per-file settings or app state
                conda_env = self.selected_conda_env or "base"
                
                # Build command to properly activate conda and run dstack ps
                # Use bash -c with conda source for proper activation
                cmd = f'bash -c "source $(conda info --base)/etc/profile.d/conda.sh && conda activate {conda_env} && dstack ps"'
                
                # Run command
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Parse the output
                    self._parse_dstack_output(result.stdout)
                    # Save status to database
                    self.yaml_manager.db.save_dstack_status(self.dstack_status)
                    # Clear checking flag and update the tree view
                    self.dstack_checking = False
                    self.call_from_thread(self._update_tree_with_status)
                else:
                    # Clear checking flag and notify error
                    self.dstack_checking = False
                    self.call_from_thread(self._update_tree_with_status)
                    self.call_from_thread(lambda: self.notify(f"dstack command failed: {result.stderr}", severity="error"))
                    
            except subprocess.TimeoutExpired:
                # Clear checking flag and notify timeout
                self.dstack_checking = False
                self.call_from_thread(self._update_tree_with_status)
                self.call_from_thread(lambda: self.notify("dstack command timed out", severity="error"))
            except Exception as e:
                # Clear checking flag and notify error
                self.dstack_checking = False
                self.call_from_thread(self._update_tree_with_status)
                self.call_from_thread(lambda: self.notify(f"Error checking dstack status: {e}", severity="error"))
        
        # Run in background thread
        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()
    
    def _parse_dstack_output(self, output: str):
        """Parse dstack ps output and update status tracking"""
        # Clear previous status
        self.dstack_status.clear()
        
        lines = output.strip().split('\n')
        
        # Skip header lines and find data rows
        for line_num, line in enumerate(lines[1:], 1):  # Skip header
            if line.strip():
                # Split by whitespace and extract name and status
                parts = line.split()
                
                if len(parts) >= 9:  # Ensure we have enough columns
                    name = parts[0].strip()
                    status = parts[8].strip()  # STATUS column
                    
                    # Store status for this name
                    self.dstack_status[name] = status
    
    def _update_tree_with_status(self):
        """Update tree view with status indicators"""
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            file_tree.build_tree()  # Rebuild tree with new status
            self.notify(f"✅ Updated status for {len(self.dstack_status)} items", timeout=2)
        except Exception as e:
            self.notify(f"Error updating tree: {e}", severity="error")
    
    def action_clear_all_data(self) -> None:
        """Clear all data from the database"""
        try:
            self.notify("🗑️ Clearing all data...", timeout=2)
            
            # Clear database
            if self.yaml_manager.db.clear_all_data():
                # Clear in-memory data
                self.yaml_manager.yaml_files = []
                
                # Refresh the UI
                self.action_refresh()
                
                self.notify("✅ All data cleared successfully!", timeout=3)
            else:
                self.notify("❌ Failed to clear data", severity="error")
                
        except Exception as e:
            self.notify(f"❌ Error clearing data: {str(e)}", severity="error")
    
    def action_delete_selected(self) -> None:
        """Delete the currently selected item (file or group)"""
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            if not file_tree.cursor_node or not file_tree.cursor_node.data:
                self.notify("❌ No item selected", severity="warning")
                return
            
            selected_data = file_tree.cursor_node.data
            
            # Handle different types of selected items
            if hasattr(selected_data, 'name'):
                # This is a file
                item_name = selected_data.name
                item_type = "file"
                
                def delete_file_callback():
                    import datetime
                    
                    debug_log = get_log_file_path("delete_debug.log")
                    
                    def log_debug(message):
                        with open(debug_log, "a") as f:
                            f.write(f"{datetime.datetime.now()}: {message}\n")
                    
                    # Get file ID from database
                    file_path_str = str(selected_data.path)
                    log_debug(f"🎯 CALLBACK: Starting delete for file: {file_path_str}")
                    log_debug(f"🎯 CALLBACK: Selected data type: {type(selected_data)}")
                    log_debug(f"🎯 CALLBACK: Selected data attributes: {dir(selected_data)}")
                    
                    self.notify(f"🔍 Looking for file: {file_path_str}", timeout=2)
                    
                    file_data = self.yaml_manager.db.get_file_by_path(file_path_str)
                    if file_data:
                        log_debug(f"🎯 CALLBACK: Found file data: {file_data}")
                        self.notify(f"🔍 Found file ID: {file_data['id']}", timeout=2)
                        delete_result = self.yaml_manager.db.delete_file(file_data['id'])
                        log_debug(f"🎯 CALLBACK: Delete result: {delete_result}")
                        if delete_result:
                            self.notify(f"✅ Deleted file: {item_name}", timeout=3)
                            self.action_refresh()
                        else:
                            self.notify(f"❌ Failed to delete file: {item_name}", severity="error")
                    else:
                        log_debug(f"🎯 CALLBACK: File not found in database")
                        self.notify(f"❌ File not found in database: {file_path_str}", severity="error")
                
                # Show confirmation dialog
                confirm_screen = ConfirmDeleteScreen(item_name, item_type, delete_file_callback)
                self.push_screen(confirm_screen)
                
            elif isinstance(selected_data, dict) and selected_data.get('type') == 'custom_group':
                # This is a custom group
                group_data = selected_data['group_data']
                item_name = group_data['name']
                item_type = "group"
                
                def delete_group_callback():
                    if self.yaml_manager.db.delete_custom_group(group_data['id']):
                        self.notify(f"✅ Deleted group: {item_name}", timeout=3)
                        self.action_refresh()
                    else:
                        self.notify(f"❌ Failed to delete group: {item_name}", severity="error")
                
                # Show confirmation dialog
                confirm_screen = ConfirmDeleteScreen(item_name, item_type, delete_group_callback)
                self.push_screen(confirm_screen)
                
            else:
                self.notify("❌ Cannot delete this item type", severity="warning")
                
        except Exception as e:
            self.notify(f"❌ Error during delete: {str(e)}", severity="error")
    
    def action_navigate_to_file(self) -> None:
        """Navigate to selected file's directory and quit"""
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            if not file_tree.cursor_node or not file_tree.cursor_node.data:
                self.notify("❌ No file selected", severity="warning")
                return
            
            selected_data = file_tree.cursor_node.data
            
            # Only works for files, not groups
            if hasattr(selected_data, 'path'):
                file_path = Path(selected_data.path)
                target_directory = file_path.parent
                filename = file_path.name
                
                # Show modal with navigation and command options
                navigate_screen = NavigateInfoScreen(str(target_directory), filename)
                self.push_screen(navigate_screen)
            else:
                self.notify("❌ Please select a file (not a group)", severity="warning")
                
        except Exception as e:
            self.notify(f"❌ Error navigating to file: {str(e)}", severity="error")
    
    def action_save_note(self) -> None:
        """Save the current content (note or file edit) based on active tab"""
        try:
            # Check which tab is active
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            tabbed_content = preview_widget.query_one("TabbedContent")
            active_tab = tabbed_content.active
            
            if active_tab == "edit":
                # Save edited YAML file content
                self.action_save_edit()
            elif active_tab == "note":
                # Save note content
                if not self.current_note_file_path:
                    self.notify("❌ No file selected for note saving", severity="warning")
                    return
                
                # Get the note content from the TextArea
                note_widget = self.query_one("#note-content", TextArea)
                note_content = note_widget.text
                
                # Save to database
                self.yaml_manager.db.save_file_note(str(self.current_note_file_path), note_content)
                self.notify("💾 Note saved!", timeout=2)
            else:
                self.notify("💡 Switch to Edit or Note tab to save content", severity="info")
            
        except Exception as e:
            self.notify(f"❌ Error saving: {str(e)}", severity="error")
    
    def action_save_edit(self) -> None:
        """Save the edited YAML file content to disk"""
        try:
            if not hasattr(self, 'current_edit_file_path') or not self.current_edit_file_path:
                self.notify("❌ No file selected for editing", severity="warning")
                return
            
            # Get the edit content from the TextArea
            edit_widget = self.query_one("#edit-content", TextArea)
            edit_content = edit_widget.text
            
            # Validate YAML syntax before saving
            try:
                yaml.safe_load(edit_content)
            except yaml.YAMLError as e:
                self.notify(f"❌ Invalid YAML syntax: {str(e)}", severity="error")
                return
            
            # Create backup if file exists
            file_path = Path(self.current_edit_file_path)
            if file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                import shutil
                shutil.copy2(file_path, backup_path)
            
            # Save the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(edit_content)
            
            # Update the file in database and memory
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            if file_tree.current_file:
                self.yaml_manager.update_file_content(file_tree.current_file, edit_content)
                
                # Refresh the preview tab to show updated content
                preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
                preview_widget._update_preview_tab(file_tree.current_file)
            
            self.notify("💾 File saved successfully!", timeout=2)
            
        except Exception as e:
            self.notify(f"❌ Error saving file: {str(e)}", severity="error")
    
    def action_rename_selected(self) -> None:
        """Rename the selected file or group"""
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            if not file_tree.cursor_node or not file_tree.cursor_node.data:
                self.notify("❌ No item selected", severity="warning")
                return
            
            selected_data = file_tree.cursor_node.data
            selected_label = file_tree.cursor_node.label.plain if hasattr(file_tree.cursor_node.label, 'plain') else str(file_tree.cursor_node.label)
            
            
            # Determine if it's a file or group
            if hasattr(selected_data, 'path'):
                # It's a file
                item_type = "file"
                current_name = selected_data.name
                
                # Show rename modal
                def handle_rename_result(result):
                    if result and result.get("action") == "rename":
                        old_name = result["old_name"]
                        new_name = result["new_name"]
                        
                        # Update in database
                        if self.yaml_manager.db.rename_file(old_name, new_name):
                            # Update the data object
                            selected_data.name = new_name
                            # Refresh tree to show changes
                            self.action_refresh()
                            self.notify(f"✅ File renamed to '{new_name}'", timeout=2)
                        else:
                            self.notify("❌ Failed to rename file", severity="error")
                
                rename_screen = RenameScreen(item_type, current_name, selected_data)
                self.push_screen(rename_screen, handle_rename_result)
                
            elif isinstance(selected_data, dict) and selected_data.get('type') == 'custom_group':
                # It's a custom group
                item_type = "group"
                group_data = selected_data.get('group_data', {})
                current_name = group_data.get('name', 'Unknown')
                
                # Show rename modal
                def handle_group_rename_result(result):
                    if result and result.get("action") == "rename":
                        old_name = result["old_name"]
                        new_name = result["new_name"]
                        
                        # Update in database
                        if self.yaml_manager.db.rename_custom_group(old_name, new_name):
                            # Refresh tree to show changes
                            self.action_refresh()
                            self.notify(f"✅ Group renamed to '{new_name}'", timeout=2)
                        else:
                            self.notify("❌ Failed to rename group", severity="error")
                
                rename_screen = RenameScreen(item_type, current_name, selected_data)
                self.push_screen(rename_screen, handle_group_rename_result)
                
            elif isinstance(selected_data, dict) and selected_data.get('type') == 'default_group':
                # It's the Default group (virtual/special case)
                item_type = "group"
                current_name = selected_data.get('name', 'Default')
                
                # Show rename modal  
                def handle_default_group_rename_result(result):
                    if result and result.get("action") == "rename":
                        old_name = result["old_name"]
                        new_name = result["new_name"]
                        
                        # For default group, we need special handling
                        # First ensure it exists in database, then rename it
                        default_group_id = self.yaml_manager.db.ensure_default_group()
                        if self.yaml_manager.db.rename_custom_group(old_name, new_name):
                            # Refresh tree to show changes
                            self.action_refresh()
                            self.notify(f"✅ Group renamed to '{new_name}'", timeout=2)
                        else:
                            self.notify("❌ Failed to rename group", severity="error")
                
                rename_screen = RenameScreen(item_type, current_name, selected_data)
                self.push_screen(rename_screen, handle_default_group_rename_result)
                
            elif isinstance(selected_data, dict) and selected_data.get('type') == 'type_group':
                # It's a type group (Task, Service, Fleet, Server) - user-renameable groupings
                item_type = "group"
                config_type = selected_data.get('config_type')
                current_name = self.yaml_manager.db.get_type_group_name(config_type)
                
                # Show rename modal
                def handle_type_group_rename_result(result):
                    if result and result.get("action") == "rename":
                        old_name = result["old_name"]
                        new_name = result["new_name"]
                        
                        # Update type group name in database
                        if self.yaml_manager.db.set_type_group_name(config_type, new_name):
                            # Refresh tree to show changes
                            self.action_refresh()
                            self.notify(f"✅ Type group renamed to '{new_name}'", timeout=2)
                        else:
                            self.notify("❌ Failed to rename type group", severity="error")
                
                rename_screen = RenameScreen(item_type, current_name, selected_data)
                self.push_screen(rename_screen, handle_type_group_rename_result)
                
            else:
                # Debug: Show what type of data we have
                data_info = f"Type: {type(selected_data)}, Label: {selected_label}"
                if isinstance(selected_data, dict):
                    data_info += f", Dict keys: {list(selected_data.keys())}"
                self.notify(f"❌ Cannot rename this item: {data_info}", severity="warning")
                
        except Exception as e:
            self.notify(f"❌ Error during rename: {str(e)}", severity="error")
    
    def save_app_state(self) -> str:
        """Save current app state to a temporary file"""
        import json
        import tempfile
        
        # Use notification for TUI debugging
        self.notify("Saving state...", timeout=2)
        
        try:
            # Get currently selected file and its details
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            
            selected_file_data = None
            
            if file_tree.current_file:
                # Ensure we save the absolute path
                file_path = file_tree.current_file.path
                if not file_path.is_absolute():
                    file_path = self.yaml_manager.root_path / file_path
                
                selected_file_data = {
                    "path": str(file_path),
                    "name": file_tree.current_file.name,
                    "config_type": file_tree.current_file.config_type.value,
                    "is_global_config": str(file_path).endswith("/.dstack/config.yml")
                }
                self.notify(f"State: {file_tree.current_file.name} at {file_path}", timeout=3)
            else:
                self.notify("No file selected to save!", severity="warning", timeout=3)
            
            # Get active tab in preview pane
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            active_tab = "preview"  # Default
            try:
                tabbed_content = preview_widget.query_one("TabbedContent")
                if tabbed_content.active_tab:
                    active_tab = tabbed_content.active_tab.id
            except:
                pass
            
            # Get expanded tree nodes for restoration
            expanded_nodes = []
            try:
                def collect_expanded_nodes(node, path=""):
                    if hasattr(node, 'expanded') and node.expanded:
                        node_id = node.label.plain if hasattr(node, 'label') else str(node)
                        expanded_nodes.append(f"{path}/{node_id}" if path else node_id)
                        for child in node.children:
                            collect_expanded_nodes(child, f"{path}/{node_id}" if path else node_id)
                
                collect_expanded_nodes(file_tree.root)
            except:
                pass
            
            state = {
                "selected_file": selected_file_data,
                "active_tab": active_tab,
                "expanded_nodes": expanded_nodes,
                "root_path": str(self.yaml_manager.root_path),
                "timestamp": str(datetime.now())
            }
            
            print(f"   Final state to save: {state}")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(state, f, indent=2)
                temp_file = f.name
                
            print(f"   State saved to: {temp_file}")
            return temp_file
                
        except Exception as e:
            print(f"❌ Failed to save state: {e}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
            return None
    
    def action_smart_quit(self) -> None:
        """Smart quit: save state, change to relevant directory, and exit"""
        import subprocess
        import os
        import sys
        import tempfile
        
        # Comprehensive logging
        debug_log = get_log_file_path("terminal_debug.log")
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug("=== ACTION_SMART_QUIT CALLED ===")
        
        # Show notification first to confirm it's called
        self.notify("👋 Smart quit triggered!", severity="information", timeout=3)
        log_debug("Notifications sent")
        
        # Simple and elegant approach: save state, change directory, and exit
        try:
            log_debug("Starting simple directory change approach...")
            
            # Save current app state first
            log_debug("Starting state save...")
            self.notify("💾 Saving app state...", timeout=2)
            state_file = self.save_app_state()
            log_debug(f"State saved to: {state_file}")
            
            # Determine target directory based on selected file
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            target_dir = self.yaml_manager.root_path  # Default to project root
            
            if file_tree.current_file:
                # Special handling for global dstack config
                if (str(file_tree.current_file.path).endswith("/.dstack/config.yml") or 
                    (file_tree.current_file.name == "config.yml" and "/.dstack/" in str(file_tree.current_file.path))):
                    target_dir = str(Path.home() / ".dstack")
                    log_debug(f"Selected global config, changing to: {target_dir}")
                    self.notify(f"📁 Changing to global config directory", timeout=2)
                else:
                    # For virtual database files, use project root but show selected file info
                    log_debug(f"Selected virtual file: {file_tree.current_file.name}, staying in project root")
                    self.notify(f"📁 Changing to project directory", timeout=2)
            else:
                log_debug("No file selected, using project root")
                self.notify(f"📁 Changing to project directory", timeout=2)
            
            log_debug(f"Target directory: {target_dir}")
            
            # Create a restoration hint file for next startup
            restore_hint_file = os.path.join(self.yaml_manager.root_path, ".dstack_restore_state")
            try:
                with open(restore_hint_file, 'w') as f:
                    f.write(state_file)
                log_debug(f"Created restore hint file: {restore_hint_file}")
            except Exception as e:
                log_debug(f"Failed to create restore hint: {e}")
            
            # Change to target directory
            try:
                os.chdir(target_dir)
                log_debug(f"Changed directory to: {target_dir}")
                self.notify(f"🎯 Directory changed to: {target_dir}", timeout=3)
            except Exception as e:
                log_debug(f"Failed to change directory: {e}")
                self.notify(f"❌ Failed to change directory: {e}", severity="error")
            
            # Show final message and exit  
            self.notify("✅ State saved! Restart the app to restore your session.", timeout=4)
            log_debug("App smart quit complete")
            
            # Exit the app cleanly
            self.exit()
            
        except Exception as e:
            # Log the error and show notification
            log_debug(f"EXCEPTION in action_open_terminal: {e}")
            import traceback
            log_debug(f"Exception traceback: {traceback.format_exc()}")
            self.notify(f"Terminal error: {str(e)}", severity="error", markup=False)
    
    def restore_app_state(self, state_file_path: str):
        """Restore app state from saved file"""
        import json
        import os
        
        # Log to a separate file that won't be captured by TUI
        def log_restore(msg):
            with open(get_log_file_path("restore.log"), "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        log_restore(f"🚀 restore_app_state called with: {state_file_path}")
        
        try:
            log_restore(f"📁 Checking if state file exists: {state_file_path}")
            if not os.path.exists(state_file_path):
                log_restore("❌ No state file found - starting fresh")
                return
            
            log_restore("📖 Reading state file...")
            with open(state_file_path, 'r') as f:
                state = json.load(f)
            
            log_restore(f"✅ Loaded state: {state}")
            log_restore(f"🔄 Restoring app state from {state.get('timestamp', 'unknown time')}")
            
            # Refresh the file tree first to ensure all files are loaded
            log_restore("🔄 Refreshing file tree...")
            self.action_refresh()
            
            # Restore selected file after tree expansion completes
            # Note: Project and conda environment will be restored automatically when file is selected
            # via the _update_dropdowns_for_file method
            if state.get("selected_file"):
                log_restore(f"⏰ Scheduling file selection in 0.2s for: {state['selected_file']}")
                self.set_timer(0.2, lambda: self._debug_and_restore_file_selection(state["selected_file"]))
            else:
                log_restore("⚠️ No selected_file in state")
            
            # Restore active tab after file selection
            if state.get("active_tab"):
                log_restore(f"⏰ Scheduling tab restoration in 0.4s for: {state['active_tab']}")
                self.set_timer(0.4, lambda: self._restore_active_tab(state["active_tab"]))
            else:
                log_restore("⚠️ No active_tab in state")
            
            # Clean up state file
            try:
                log_restore(f"🗑️ Cleaning up state file: {state_file_path}")
                os.unlink(state_file_path)
                log_restore("✅ State file cleaned up")
            except Exception as cleanup_error:
                log_restore(f"⚠️ Failed to cleanup state file: {cleanup_error}")
            
        except Exception as e:
            log_restore(f"❌ Failed to restore state: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")
            # If restore fails, just continue normally
            pass
    
    def _debug_and_restore_file_selection(self, file_data: dict):
        """Debug version that shows tree structure and attempts restoration"""
        def log_restore(msg):
            with open(get_log_file_path("restore.log"), "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            target_path = file_data.get("path")
            target_name = file_data.get("name")
            
            log_restore(f"🔍 DEBUG: Tree has {len(file_tree.root.children)} top-level nodes")
            log_restore(f"🎯 Looking for file: {target_name} at {target_path}")
            
            # First, let's see what's in the tree
            def debug_tree_structure(node, depth=0):
                indent = "  " * depth
                log_restore(f"{indent}📋 Node: {node.label if hasattr(node, 'label') else 'NO_LABEL'}")
                if hasattr(node, 'data') and node.data:
                    if hasattr(node.data, 'path'):
                        log_restore(f"{indent}   Path: {node.data.path}")
                    if hasattr(node.data, 'name'):
                        log_restore(f"{indent}   Name: {node.data.name}")
                log_restore(f"{indent}   Children: {len(node.children)}")
                
                if depth < 2:  # Limit depth to avoid too much logging
                    for child in node.children:
                        debug_tree_structure(child, depth + 1)
            
            log_restore("🌳 Tree structure:")
            debug_tree_structure(file_tree.root)
            
            # Now try to find and select the file
            log_restore("🔍 Starting file selection process...")
            self._restore_file_selection(file_data)
            
        except Exception as e:
            log_restore(f"❌ Debug error: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")
    
    def _restore_file_selection(self, file_data: dict):
        """Helper to restore file selection using detailed file data"""
        def log_restore(msg):
            with open(get_log_file_path("restore.log"), "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            target_path = file_data.get("path")
            target_name = file_data.get("name")
            
            log_restore(f"🎯 Looking for file: {target_name} at {target_path}")
            
            # Find the file in the tree and expand path to it
            def find_and_expand_to_file(node, path_to_node=[], depth=0):
                indent = "  " * depth
                current_path = path_to_node + [node]
                
                if hasattr(node, 'data') and node.data:
                    # Check for path match (handle both absolute and relative paths)
                    if hasattr(node.data, 'path'):
                        node_path = str(node.data.path)
                        # Try exact match first
                        if node_path == target_path:
                            log_restore(f"{indent}✅ Found exact path match: {node_path}")
                            return self._select_found_file(node, current_path, target_path, log_restore)
                        # Try matching by filename (since tree has relative paths, target has absolute)
                        elif target_path.endswith(node_path) or node_path == target_name:
                            log_restore(f"{indent}✅ Found filename match: {node_path} for target {target_path}")
                            return self._select_found_file(node, current_path, node_path, log_restore)
                        
                        # Also check by name as fallback
                        if hasattr(node.data, 'name'):
                            node_name = str(node.data.name)
                            if node_name == target_name:
                                log_restore(f"{indent}✅ Found target by name: {node_name}")
                                return self._select_found_file(node, current_path, node_name, log_restore)
                
                # First expand this node if it's a group/folder
                if hasattr(node, 'expand') and hasattr(node, 'children') and len(node.children) > 0:
                    node.expand()
                
                # Recursively search children
                for child in node.children:
                    if find_and_expand_to_file(child, current_path, depth + 1):
                        return True
                return False
            
            if find_and_expand_to_file(file_tree.root):
                log_restore(f"✅ Successfully restored and expanded to: {target_name}")
            else:
                log_restore(f"❌ Could not find file: {target_name}")
                # As fallback, expand all nodes to make sure file is visible
                log_restore("🔄 Expanding all nodes as fallback...")
                self._expand_all_tree_nodes(file_tree.root)
                
        except Exception as e:
            log_restore(f"❌ Error restoring file selection: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")

    def _select_found_file(self, node, current_path, node_path, log_restore):
        """Helper to select a found file node"""
        # Expand all nodes in the path to this file
        for path_node in current_path[:-1]:  # Don't expand the file itself
            if hasattr(path_node, 'expand'):
                path_node.expand()
                log_restore(f"📂 Expanded: {path_node.label}")
        
        # Wait a moment for expansion to complete, then select
        def delayed_selection():
            log_restore(f"🎯 Selecting file after expansion: {node_path}")
            
            try:
                file_tree = self.query_one("#file-tree", FileTreeWidget)
                
                # Method 1: Update internal file tracking
                file_tree.current_file = node.data
                log_restore(f"✅ Set current_file to: {node.data.name}")
                
                # Method 2: Try to set tree cursor (for visual highlighting)
                try:
                    # Use the proper Textual Tree API to select the node
                    if hasattr(file_tree, 'select_node'):
                        file_tree.select_node(node)
                        log_restore(f"✅ Selected node using select_node")
                    elif hasattr(node, 'action_select'):
                        node.action_select()
                        log_restore(f"✅ Selected node using action_select")
                    
                    # Try to scroll to the node and make it visible
                    if hasattr(file_tree, 'scroll_to_node'):
                        file_tree.scroll_to_node(node)
                        log_restore(f"✅ Scrolled to node")
                    
                    # Refresh the tree widget to update visual state
                    file_tree.refresh()
                    log_restore(f"✅ Refreshed tree widget")
                    
                except Exception as e:
                    log_restore(f"⚠️ Tree cursor/scroll failed: {e}")
                
                # Method 3: Post the FileSelected message
                file_tree.post_message(FileSelected(node.data))
                log_restore(f"✅ Posted FileSelected message")
                
                # Method 4: Direct preview update as backup
                try:
                    preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
                    preview_widget.update_preview(node.data)
                    log_restore(f"✅ Updated preview for: {node.data.name}")
                except Exception as e:
                    log_restore(f"⚠️ Preview update failed: {e}")
                
                # Method 5: Focus the tree widget
                try:
                    file_tree.focus()
                    log_restore(f"✅ Focused tree widget")
                except Exception as e:
                    log_restore(f"⚠️ Tree focus failed: {e}")
                    
            except Exception as e:
                log_restore(f"❌ Delayed selection failed: {e}")
        
        # Schedule selection after expansion delay
        self.set_timer(0.2, delayed_selection)
        return True
    
    def _expand_all_tree_nodes(self, node):
        """Helper to expand all tree nodes"""
        try:
            if hasattr(node, 'expand'):
                node.expand()
            for child in node.children:
                self._expand_all_tree_nodes(child)
        except:
            pass
    
    def _restore_project_selection(self, project_name: str):
        """Helper to restore project selection"""
        def log_restore(msg):
            with open(get_log_file_path("restore.log"), "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        try:
            log_restore(f"🔄 Restoring project selection: {project_name}")
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            log_restore(f"Found preview widget: {preview_widget}")
            
            project_select = preview_widget.query_one("#project-select", Select)
            log_restore(f"Found project select: {project_select}")
            log_restore(f"Project select options: {list(project_select._options)}")
            
            # Check if the project exists in the dropdown options
            for option_label, option_value in project_select._options:
                if option_value == project_name:
                    project_select.value = project_name
                    log_restore(f"✅ Successfully restored project: {project_name}")
                    return
            
            log_restore(f"⚠️ Project not found in options: {project_name}")
        except Exception as e:
            log_restore(f"❌ Error restoring project: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")
    
    def _restore_conda_selection(self, conda_env: str):
        """Helper to restore conda environment selection"""
        def log_restore(msg):
            with open(get_log_file_path("restore.log"), "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        try:
            log_restore(f"🔄 Restoring conda env selection: {conda_env}")
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            log_restore(f"Found preview widget: {preview_widget}")
            
            conda_select = preview_widget.query_one("#conda-select", Select)
            log_restore(f"Found conda select: {conda_select}")
            log_restore(f"Conda select options: {list(conda_select._options)}")
            
            # Check if the conda environment exists in the dropdown options
            for option_label, option_value in conda_select._options:
                if option_value == conda_env:
                    conda_select.value = conda_env
                    log_restore(f"✅ Successfully restored conda env: {conda_env}")
                    return
            
            log_restore(f"⚠️ Conda env not found in options: {conda_env}")
        except Exception as e:
            log_restore(f"❌ Error restoring conda env: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")
    
    def _restore_active_tab(self, tab_id: str):
        """Helper to restore active tab"""
        try:
            print(f"🔄 Restoring active tab: {tab_id}")
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            tabbed_content = preview_widget.query_one("TabbedContent")
            tabbed_content.active = tab_id
            print(f"✅ Successfully restored tab: {tab_id}")
        except Exception as e:
            print(f"❌ Error restoring tab: {e}")
            pass
    


# This module is now imported as part of the dstack-mgmt package
# The main entry point is in cli.py