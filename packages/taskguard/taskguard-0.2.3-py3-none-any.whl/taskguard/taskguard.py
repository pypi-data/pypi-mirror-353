#!/usr/bin/env python3
"""
🎯 LLM Task Controller - Focus & Best Practices Engine
Updated with new shell integration system
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Import shell integration
try:
    from .shell_integration import ShellIntegration
except ImportError:
    # Fallback for standalone execution
    from shell_integration import ShellIntegration


class LLMTaskController:
    def __init__(self):
        self.config = self.load_config()
        self.state = self.load_state()
        self.todo = self.load_todo()
        self.changelog = self.load_changelog()
        self.shell_integration = ShellIntegration(self.config)

    def load_config(self):
        """Load YAML configuration with best practices"""
        config_file = Path.cwd() / ".llmcontrol.yaml"

        default_config = {
            "focus": {
                "max_files_per_task": 3,
                "max_lines_per_file": 200,
                "require_todo_completion": True,
                "auto_changelog": True,
                "task_timeout_minutes": 30,
            },
            "best_practices": {
                "python": {
                    "enforce_docstrings": True,
                    "enforce_type_hints": True,
                    "max_function_length": 50,
                    "require_tests": True,
                    "naming_convention": "snake_case",
                    "imports_organization": True,
                },
                "javascript": {
                    "enforce_jsdoc": True,
                    "prefer_const": True,
                    "max_function_length": 30,
                    "require_error_handling": True,
                    "naming_convention": "camelCase",
                },
                "general": {
                    "single_responsibility": True,
                    "descriptive_names": True,
                    "no_hardcoded_values": True,
                    "consistent_formatting": True,
                    "meaningful_comments": True,
                },
            },
            "todo_management": {
                "categories": ["feature", "bugfix", "refactor", "test", "docs"],
                "priorities": ["high", "medium", "low"],
                "auto_create_subtasks": True,
                "require_estimation": True,
                "track_time": True,
            },
            "file_management": {
                "max_files_at_once": 5,
                "require_file_headers": True,
                "organize_by_feature": True,
                "prevent_large_files": True,
            },
            "quality_gates": {
                "syntax_check": True,
                "security_scan": True,
                "style_check": True,
                "test_coverage": 80,
                "complexity_limit": 10,
            },
            "responses": {
                "task_complete": "✅ Task completed: {task}",
                "focus_redirect": "🎯 Focus! Complete current task first: {current_task}",
                "best_practice_violation": "📋 Best practice reminder: {practice}",
                "quality_gate_failed": "🛑 Quality gate failed: {reason}",
                "changelog_updated": "📝 Changelog updated with: {changes}",
            },
        }

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    return self.merge_config(default_config, user_config or {})
            except Exception as e:
                print(f"⚠️ Config error: {e}, using defaults")

        # Create default config
        self.save_config(config_file, default_config)
        print(f"📋 Created default config: {config_file}")

        return default_config

    def save_config(self, file_path: Path, config: Dict):
        """Save config with comments"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                """# 🎯 LLM Task Controller Configuration
# Control LLM behavior, enforce best practices, maintain focus

"""
            )
            yaml.dump(config, f, default_flow_style=False, indent=2, allow_unicode=True)

    def merge_config(self, default: Dict, user: Dict) -> Dict:
        """Deep merge configurations"""
        for key, value in user.items():
            if (
                key in default
                and isinstance(default[key], dict)
                and isinstance(value, dict)
            ):
                default[key] = self.merge_config(default[key], value)
            else:
                default[key] = value
        return default

    def load_state(self) -> Dict:
        """Load current work state"""
        state_file = Path.cwd() / ".llmstate.json"
        default_state = {
            "current_task": None,
            "task_start_time": None,
            "files_modified_today": [],
            "focus_score": 100,
            "best_practice_violations": 0,
            "quality_gates_passed": 0,
            "session_start": time.time(),
            "productivity_metrics": {
                "tasks_completed": 0,
                "files_created": 0,
                "lines_written": 0,
                "time_focused": 0,
            },
        }

        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    return {**default_state, **json.load(f)}
            except:
                pass

        return default_state

    def save_state(self):
        """Save current state"""
        state_file = Path.cwd() / ".llmstate.json"
        with open(state_file, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def load_todo(self) -> List[Dict]:
        """Load TODO list"""
        todo_file = Path.cwd() / "TODO.yaml"

        if not todo_file.exists():
            default_todo = [
                {
                    "id": 1,
                    "title": "Setup project structure",
                    "category": "feature",
                    "priority": "high",
                    "status": "pending",
                    "estimated_hours": 2,
                    "description": "Create basic project structure with proper organization",
                    "subtasks": [
                        "Create main directories",
                        "Setup configuration files",
                        "Initialize version control",
                    ],
                },
                {
                    "id": 2,
                    "title": "Implement core functionality",
                    "category": "feature",
                    "priority": "high",
                    "status": "pending",
                    "estimated_hours": 4,
                    "description": "Implement the main features of the application",
                },
            ]

            with open(todo_file, "w") as f:
                f.write("# 🎯 Project TODO List\n# Managed by LLM Task Controller\n\n")
                yaml.dump(default_todo, f, default_flow_style=False, indent=2)

            print(f"📋 Created TODO list: {todo_file}")
            return default_todo

        try:
            with open(todo_file, "r") as f:
                content = f.read()
                # Remove comments for YAML parsing
                yaml_content = "\n".join(
                    line
                    for line in content.split("\n")
                    if not line.strip().startswith("#")
                )
                return yaml.safe_load(yaml_content) or []
        except Exception as e:
            print(f"⚠️ TODO parse error: {e}")
            return []

    def save_todo(self):
        """Save TODO list"""
        todo_file = Path.cwd() / "TODO.yaml"
        with open(todo_file, "w") as f:
            f.write("# 🎯 Project TODO List\n# Managed by LLM Task Controller\n\n")
            yaml.dump(self.todo, f, default_flow_style=False, indent=2)

    def load_changelog(self) -> List[Dict]:
        """Load changelog"""
        changelog_file = Path.cwd() / "CHANGELOG.md"

        if not changelog_file.exists():
            with open(changelog_file, "w") as f:
                f.write(
                    "# 📝 Changelog\n\nAll notable changes to this project will be documented here.\n\n"
                )
            return []

        # Parse existing changelog (simplified)
        try:
            with open(changelog_file, "r") as f:
                content = f.read()
            # Extract entries (basic parsing)
            return []  # Simplified for now
        except:
            return []

    def update_changelog(self, task: Dict, changes: List[str]):
        """Update changelog with completed task"""
        changelog_file = Path.cwd() / "CHANGELOG.md"

        date_str = datetime.now().strftime("%Y-%m-%d")

        # Read existing content
        if changelog_file.exists():
            with open(changelog_file, "r") as f:
                content = f.read()
        else:
            content = "# 📝 Changelog\n\nAll notable changes to this project will be documented here.\n\n"

        # Find or create today's section
        today_header = f"## [{date_str}]"

        if today_header not in content:
            # Add new date section after the main header
            lines = content.split("\n")
            insert_idx = 3  # After main header and description
            lines.insert(insert_idx, f"\n{today_header}\n")
            content = "\n".join(lines)

        # Add the completed task
        task_entry = f"- ✅ **{task['category'].title()}**: {task['title']}"
        if changes:
            task_entry += f"\n  - {chr(10).join(f'  - {change}' for change in changes)}"

        # Insert after today's header
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == today_header:
                lines.insert(i + 1, task_entry)
                break

        with open(changelog_file, "w") as f:
            f.write("\n".join(lines))

        print(
            self.config["responses"]["changelog_updated"].format(changes=task["title"])
        )

    def get_current_task(self) -> Optional[Dict]:
        """Get current active task"""
        if self.state["current_task"]:
            return next(
                (t for t in self.todo if t["id"] == self.state["current_task"]), None
            )

        # Auto-select next pending task
        pending = [t for t in self.todo if t["status"] == "pending"]
        if pending:
            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            pending.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
            return pending[0]

        return None

    def start_task(self, task_id: int):
        """Start working on a specific task"""
        task = next((t for t in self.todo if t["id"] == task_id), None)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False

        if task["status"] == "completed":
            print(f"✅ Task {task_id} already completed")
            return False

        self.state["current_task"] = task_id
        self.state["task_start_time"] = time.time()
        task["status"] = "in_progress"

        self.save_state()
        self.save_todo()

        print(f"🎯 Started task: {task['title']}")
        print(f"📋 Category: {task['category']} | Priority: {task['priority']}")

        if "subtasks" in task:
            print("📝 Subtasks:")
            for subtask in task["subtasks"]:
                print(f"   - {subtask}")

        return True

    def complete_task(self, changes: List[str] = None):
        """Mark current task as completed"""
        current_task = self.get_current_task()
        if not current_task:
            print("❌ No active task to complete")
            return False

        current_task["status"] = "completed"
        current_task["completed_at"] = datetime.now().isoformat()

        if self.state["task_start_time"]:
            duration = time.time() - self.state["task_start_time"]
            current_task["actual_hours"] = round(duration / 3600, 2)
            self.state["productivity_metrics"]["time_focused"] += duration

        # Update changelog
        if self.config["focus"]["auto_changelog"]:
            self.update_changelog(current_task, changes or [])

        # Update metrics
        self.state["productivity_metrics"]["tasks_completed"] += 1
        self.state["current_task"] = None
        self.state["task_start_time"] = None

        self.save_state()
        self.save_todo()

        print(
            self.config["responses"]["task_complete"].format(task=current_task["title"])
        )

        # Suggest next task
        next_task = self.get_current_task()
        if next_task:
            print(f"🎯 Next suggested task: {next_task['title']}")
            print(f"💡 Use: start_task {next_task['id']} to begin")
        else:
            print("🎉 All tasks completed! Add more tasks to continue.")

        return True

    def check_focus(self, command: List[str]) -> bool:
        """Check if command maintains focus on current task"""
        if not self.config["focus"]["require_todo_completion"]:
            return True

        current_task = self.get_current_task()
        if not current_task:
            print("📋 No active task. Use 'show_tasks' to see available tasks.")
            return False

        # Check if creating too many files
        if command[0] in ["touch", "echo"] or (
            command[0] == "python" and "create" in " ".join(command)
        ):
            files_today = len(self.state["files_modified_today"])
            if files_today >= self.config["focus"]["max_files_per_task"]:
                print(
                    self.config["responses"]["focus_redirect"].format(
                        current_task=current_task["title"]
                    )
                )
                print(
                    f"📊 Files modified today: {files_today}/{self.config['focus']['max_files_per_task']}"
                )
                return False

        # Check task timeout
        if self.state["task_start_time"]:
            duration = time.time() - self.state["task_start_time"]
            timeout = self.config["focus"]["task_timeout_minutes"] * 60
            if duration > timeout:
                print(
                    f"⏰ Task timeout ({self.config['focus']['task_timeout_minutes']}min)"
                )
                print("💡 Consider completing current task or extending timeout")
                return False

        return True

    def check_best_practices(self, file_path: str, content: str = None) -> List[str]:
        """Check file against best practices"""
        violations = []

        if not Path(file_path).exists() and not content:
            return violations

        file_ext = Path(file_path).suffix.lower()
        file_content = content or Path(file_path).read_text(errors="ignore")

        # Python best practices
        if file_ext == ".py":
            practices = self.config["best_practices"]["python"]

            if practices.get("enforce_docstrings"):
                if "def " in file_content and '"""' not in file_content:
                    violations.append("Missing docstrings in functions")

            if practices.get("enforce_type_hints"):
                functions = re.findall(r"def\s+\w+\([^)]*\):", file_content)
                if functions and "->" not in file_content:
                    violations.append("Missing type hints in functions")

            if practices.get("max_function_length"):
                functions = re.findall(
                    r"def\s+\w+.*?(?=\ndef|\nclass|\Z)", file_content, re.DOTALL
                )
                for func in functions:
                    lines = len(func.split("\n"))
                    if lines > practices["max_function_length"]:
                        violations.append(
                            f"Function too long: {lines} lines (max {practices['max_function_length']})"
                        )

        # JavaScript best practices
        elif file_ext in [".js", ".ts"]:
            practices = self.config["best_practices"]["javascript"]

            if practices.get("prefer_const"):
                if "let " in file_content and "const " not in file_content:
                    violations.append("Prefer const over let when possible")

            if practices.get("require_error_handling"):
                if "async" in file_content and "try" not in file_content:
                    violations.append("Missing error handling in async functions")

        # General best practices
        general = self.config["best_practices"]["general"]

        if general.get("no_hardcoded_values"):
            # Simple check for common hardcoded values
            if re.search(
                r'[\'"][A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}[\'"]',
                file_content,
            ):
                violations.append("Hardcoded email addresses found")
            if re.search(r'[\'"]https?://[^\'"]+[\'"]', file_content):
                violations.append("Hardcoded URLs found")

        if general.get("descriptive_names"):
            # Check for single letter variables (excluding common ones)
            vars_found = re.findall(r"\b[a-df-hj-z]\b", file_content)
            if len(vars_found) > 3:  # Allow some (i, j, k are common)
                violations.append("Use more descriptive variable names")

        return violations

    def safe_execute(self, command: List[str]) -> bool:
        """Execute command with focus and best practice checks"""

        # Check focus first
        if not self.check_focus(command):
            return False

        # Track file modifications
        if command[0] in ["python", "node", "touch"] and len(command) > 1:
            file_path = command[1]
            if file_path not in self.state["files_modified_today"]:
                self.state["files_modified_today"].append(file_path)

        # Execute command
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            # Post-execution checks for created/modified files
            if command[0] == "python" and len(command) > 1:
                file_path = command[1]
                if Path(file_path).exists():
                    violations = self.check_best_practices(file_path)
                    if violations:
                        print("\n📋 Best Practice Reminders:")
                        for violation in violations:
                            print(f"   - {violation}")
                        self.state["best_practice_violations"] += len(violations)
                    else:
                        self.state["quality_gates_passed"] += 1
                        print("✅ Code follows best practices!")

            self.save_state()
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            return False

    def setup_shell(self, force: bool = False):
        """Setup shell integration using new system"""
        print("🔧 Setting up shell integration...")

        success = self.shell_integration.setup_shell_integration(force=force)

        if success:
            print("\n🎯 Shell Integration Ready!")
            print("=" * 30)
            print("📋 Available commands:")
            print("  show_tasks              - List all tasks")
            print("  start_task <id>         - Start working on task")
            print("  complete_task           - Complete current task")
            print("  add_task '<title>'      - Add new task")
            print("  smart_analysis          - AI project analysis")
            print("  best_practices [file]   - Check code quality")
            print("  focus_status            - Show focus metrics")
            print("  productivity            - Show statistics")
            print("")
            print("🚀 Quick start:")
            print(f"  1. source {self.shell_integration.shell_file}")
            print("  2. show_tasks")
            print("  3. start_task 1")
            print("  4. Type 'tg_help' for all commands")

            # Offer to add to shell profile
            try:
                response = input(
                    "\n💡 Add to your shell profile for automatic loading? (y/N): "
                )
                if response.lower() in ["y", "yes"]:
                    # Detect shell
                    shell = os.environ.get("SHELL", "/bin/bash").split("/")[-1]
                    if shell in ["bash", "zsh"]:
                        self.shell_integration.add_to_profile(shell)
                    else:
                        print(f"⚠️ Unsupported shell: {shell}")
                        print("💡 Manually add this line to your shell profile:")
                        print(f"   source {self.shell_integration.shell_file}")
            except (KeyboardInterrupt, EOFError):
                pass

        return success

    def test_shell_integration(self):
        """Test shell integration"""
        return self.shell_integration.test_shell_integration()


# Legacy compatibility - keep existing interface
def main():
    """Main function for backward compatibility"""
    controller = LLMTaskController()

    if len(sys.argv) == 1:
        print("🎯 LLM Task Controller initialized!")
        print("💡 Use the new CLI: taskguard --help")
        print("🔧 Or setup shell integration: taskguard setup shell")
        return

    # Handle legacy commands
    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "setup_shell":
        controller.setup_shell(force="--force" in args)
    elif command == "test_shell":
        controller.test_shell_integration()
    else:
        print(f"⚠️ Legacy command: {command}")
        print("💡 Use the new CLI: taskguard --help")


if __name__ == "__main__":
    main()
