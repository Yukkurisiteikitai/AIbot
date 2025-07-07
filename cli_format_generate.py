#!/usr/bin/env python3
"""
PersonaAnalyzer CLI File Structure Generator
指定されたディレクトリ構造とファイルを自動生成するスクリプト
"""

import os
from pathlib import Path
from typing import Dict, List, Union

# ファイル構造定義
FILE_STRUCTURE = {
    "CLI": {
        "main.py": "# PersonaAnalyzer CLI entry point\n",
        "cli": {
            "__init__.py": "",
            "commands": {
                "__init__.py": "",
                "core.py": "# Core interaction commands (Talk, Check, END, SET, Mad)\n",
                "data.py": "# Data management commands\n",
                "analysis.py": "# Analysis commands (analyze, simulate, compare)\n",
                "config.py": "# Configuration commands\n",
                "auth.py": "# Authentication commands (login, register, init)\n",
                "dev.py": "# Development commands (db, ai, log, test)\n"
            },
            "parsers": {
                "__init__.py": "",
                "base.py": "# Base parser functionality\n",
                "command_parsers.py": "# Command line argument parsers\n"
            },
            "utils": {
                "__init__.py": "",
                "output.py": "# Output formatting utilities\n",
                "session.py": "# Session management\n",
                "validation.py": "# Input validation\n"
            }
        },
        "core": {
            "__init__.py": "",
            "database": {
                "__init__.py": "",
                "models.py": "# Database models\n",
                "operations.py": "# CRUD operations\n",
                "migrations.py": "# Database schema management\n"
            },
            "ai": {
                "__init__.py": "",
                "inference.py": "# AI inference engine\n",
                "analysis.py": "# Analysis logic\n",
                "simulation.py": "# Simulation logic\n",
                "classification.py": "# Text classification\n"
            },
            "persona": {
                "__init__.py": "",
                "manager.py": "# Persona management\n",
                "profile.py": "# Profile processing\n",
                "feedback.py": "# Feedback processing\n"
            },
            "security": {
                "__init__.py": "",
                "auth.py": "# Authentication logic\n",
                "encryption.py": "# Encryption utilities\n"
            }
        },
        "config": {
            "__init__.py": "",
            "settings.py": "# Default settings\n",
            "schema.py": "# Configuration schema\n",
            "loader.py": "# Configuration loader\n"
        },
        "utils": {
            "__init__.py": "",
            "logging.py": "# Logging configuration\n",
            "exceptions.py": "# Custom exceptions\n",
            "helpers.py": "# Common helper functions\n"
        },
        "tests": {
            "__init__.py": "",
            "test_commands": {
                "__init__.py": "",
                "test_core.py": "# Tests for core commands\n",
                "test_data.py": "# Tests for data commands\n",
                "test_analysis.py": "# Tests for analysis commands\n"
            },
            "test_core": {
                "__init__.py": "",
                "test_database.py": "# Database tests\n",
                "test_ai.py": "# AI module tests\n",
                "test_persona.py": "# Persona tests\n"
            },
            "fixtures": {
                "__init__.py": "",
                "sample_data.json": "{}",
                "test_config.yaml": "# Test configuration\n"
            }
        },
        "requirements.txt": "# Python dependencies\n",
        "setup.py": "# Package setup script\n",
        "README.md": "# PersonaAnalyzer CLI\n",
        ".gitignore": "# Git ignore file\n",
        "Dockerfile": "# Docker configuration\n",
        "docker-compose.yml": "# Docker Compose configuration\n"
    }
}

class FileStructureGenerator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
    
    def create_structure(self, structure: Dict, current_path: Path = None):
        """
        再帰的にファイル構造を作成
        
        Args:
            structure: ファイル構造の辞書
            current_path: 現在のパス
        """
        if current_path is None:
            current_path = self.base_path
        
        for name, content in structure.items():
            item_path = current_path / name
            
            if isinstance(content, dict):
                # ディレクトリの場合
                print(f"📁 Creating directory: {item_path}")
                item_path.mkdir(parents=True, exist_ok=True)
                
                # 再帰的にサブディレクトリを作成
                self.create_structure(content, item_path)
            
            elif isinstance(content, str):
                # ファイルの場合
                print(f"📄 Creating file: {item_path}")
                
                # 親ディレクトリが存在しない場合は作成
                item_path.parent.mkdir(parents=True, exist_ok=True)
                
                # ファイルを作成（既存ファイルは上書きしない）
                if not item_path.exists():
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    print(f"  ⚠️  File already exists, skipping: {item_path}")
    
    def generate_tree_view(self, structure: Dict, prefix: str = "", is_last: bool = True) -> str:
        """
        ツリー表示用の文字列を生成
        
        Args:
            structure: ファイル構造の辞書
            prefix: プレフィックス文字列
            is_last: 最後の要素かどうか
        
        Returns:
            ツリー表示の文字列
        """
        result = []
        items = list(structure.items())
        
        for i, (name, content) in enumerate(items):
            is_last_item = i == len(items) - 1
            current_prefix = "└── " if is_last_item else "├── "
            
            if isinstance(content, dict):
                # ディレクトリの場合
                result.append(f"{prefix}{current_prefix}{name}/")
                
                # 次のレベルのプレフィックスを設定
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                result.append(self.generate_tree_view(content, next_prefix, is_last_item))
            else:
                # ファイルの場合
                result.append(f"{prefix}{current_prefix}{name}")
        
        return "\n".join(result)
    
    def print_structure(self, structure: Dict = None):
        """ファイル構造をツリー表示で出力"""
        if structure is None:
            structure = FILE_STRUCTURE
        
        print("📁 PersonaAnalyzer CLI File Structure:")
        print("=" * 50)
        print(self.generate_tree_view(structure))
        print("=" * 50)
    
    def create_additional_files(self):
        """追加的なファイルを作成"""
        additional_files = {
            "CLI/.env.example": "# Environment variables example\nBACKEND_URL=https://your-backend-url.com\nAPI_KEY=your-api-key\n",
            "CLI/.github/workflows/ci.yml": "# GitHub Actions CI configuration\n",
            "CLI/docs/API.md": "# API Documentation\n",
            "CLI/docs/USAGE.md": "# Usage Guide\n",
            "CLI/scripts/install.sh": "#!/bin/bash\n# Installation script\n",
            "CLI/scripts/run_tests.sh": "#!/bin/bash\n# Test runner script\n"
        }
        
        for file_path, content in additional_files.items():
            full_path = self.base_path / file_path
            print(f"📄 Creating additional file: {full_path}")
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not full_path.exists():
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(f"  ⚠️  File already exists, skipping: {full_path}")

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PersonaAnalyzer CLI File Structure Generator")
    parser.add_argument("--path", "-p", default=".", help="Base path for file generation (default: current directory)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Show structure without creating files")
    parser.add_argument("--additional", "-a", action="store_true", help="Create additional files (docs, scripts, etc.)")
    
    args = parser.parse_args()
    
    generator = FileStructureGenerator(args.path)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be created")
        generator.print_structure()
    else:
        print("🚀 Starting file structure generation...")
        generator.print_structure()
        print("\n📁 Creating files and directories...")
        
        try:
            generator.create_structure(FILE_STRUCTURE)
            
            if args.additional:
                print("\n📄 Creating additional files...")
                generator.create_additional_files()
            
            print("\n✅ File structure generation completed!")
            print(f"📂 Files created in: {Path(args.path).resolve()}")
            
        except Exception as e:
            print(f"❌ Error during generation: {str(e)}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())