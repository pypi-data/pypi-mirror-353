#!/usr/bin/env python3
"""
🎯 LLM Task Controller - Focus & Best Practices Engine
One file to control LLM behavior, enforce best practices, and maintain focus
"""

import os, sys, json, re, subprocess, time, yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class LLMTaskController:
    def __init__(self):
        self.config = self.load_config()
        self.state = self.load_state()
        self.todo = self.load_todo()
        self.changelog = self.load_changelog()
        self.setup_shell()

    def load_config(self):
        """Load YAML configuration with best practices"""
        config_file = Path.cwd() / ".llmcontrol.yaml"

        default_config = {
            'focus': {
                'max_files_per_task': 3,
                'max_lines_per_file': 200,
                'require_todo_completion': True,
                'auto_changelog': True,
                'task_timeout_minutes': 30
            },
            'best_practices': {
                'python': {
                    'enforce_docstrings': True,
                    'enforce_type_hints': True,
                    'max_function_length': 50,
                    'require_tests': True,
                    'naming_convention': 'snake_case',
                    'imports_organization': True
                },
                'javascript': {
                    'enforce_jsdoc': True,
                    'prefer_const': True,
                    'max_function_length': 30,
                    'require_error_handling': True,
                    'naming_convention': 'camelCase'
                },
                'general': {
                    'single_responsibility': True,
                    'descriptive_names': True,
                    'no_hardcoded_values': True,
                    'consistent_formatting': True,
                    'meaningful_comments': True
                }
            },
            'todo_management': {
                'categories': ['feature', 'bugfix', 'refactor', 'test', 'docs'],
                'priorities': ['high', 'medium', 'low'],
                'auto_create_subtasks': True,
                'require_estimation': True,
                'track_time': True
            },
            'file_management': {
                'max_files_at_once': 5,
                'require_file_headers': True,
                'organize_by_feature': True,
                'prevent_large_files': True
            },
            'quality_gates': {
                'syntax_check': True,
                'security_scan': True,
                'style_check': True,
                'test_coverage': 80,
                'complexity_limit': 10
            },
            'responses': {
                'task_complete': '✅ Task completed: {task}',
                'focus_redirect': '🎯 Focus! Complete current task first: {current_task}',
                'best_practice_violation': '📋 Best practice reminder: {practice}',
                'quality_gate_failed': '🛑 Quality gate failed: {reason}',
                'changelog_updated': '📝 Changelog updated with: {changes}'
            }
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
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
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("""# 🎯 LLM Task Controller Configuration
# Control LLM behavior, enforce best practices, maintain focus

""")
            yaml.dump(config, f, default_flow_style=False, indent=2, allow_unicode=True)

    def merge_config(self, default: Dict, user: Dict) -> Dict:
        """Deep merge configurations"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                default[key] = self.merge_config(default[key], value)
            else:
                default[key] = value
        return default

    def load_state(self) -> Dict:
        """Load current work state"""
        state_file = Path.cwd() / ".llmstate.json"
        default_state = {
            'current_task': None,
            'task_start_time': None,
            'files_modified_today': [],
            'focus_score': 100,
            'best_practice_violations': 0,
            'quality_gates_passed': 0,
            'session_start': time.time(),
            'productivity_metrics': {
                'tasks_completed': 0,
                'files_created': 0,
                'lines_written': 0,
                'time_focused': 0
            }
        }

        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return {**default_state, **json.load(f)}
            except:
                pass

        return default_state

    def save_state(self):
        """Save current state"""
        state_file = Path.cwd() / ".llmstate.json"
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def load_todo(self) -> List[Dict]:
        """Load TODO list"""
        todo_file = Path.cwd() / "TODO.yaml"

        if not todo_file.exists():
            default_todo = [
                {
                    'id': 1,
                    'title': 'Setup project structure',
                    'category': 'feature',
                    'priority': 'high',
                    'status': 'pending',
                    'estimated_hours': 2,
                    'description': 'Create basic project structure with proper organization',
                    'subtasks': [
                        'Create main directories',
                        'Setup configuration files',
                        'Initialize version control'
                    ]
                },
                {
                    'id': 2,
                    'title': 'Implement core functionality',
                    'category': 'feature',
                    'priority': 'high',
                    'status': 'pending',
                    'estimated_hours': 4,
                    'description': 'Implement the main features of the application'
                }
            ]

            with open(todo_file, 'w') as f:
                f.write("# 🎯 Project TODO List\n# Managed by LLM Task Controller\n\n")
                yaml.dump(default_todo, f, default_flow_style=False, indent=2)

            print(f"📋 Created TODO list: {todo_file}")
            return default_todo

        try:
            with open(todo_file, 'r') as f:
                content = f.read()
                # Remove comments for YAML parsing
                yaml_content = '\n'.join(line for line in content.split('\n')
                                         if not line.strip().startswith('#'))
                return yaml.safe_load(yaml_content) or []
        except Exception as e:
            print(f"⚠️ TODO parse error: {e}")
            return []

    def save_todo(self):
        """Save TODO list"""
        todo_file = Path.cwd() / "TODO.yaml"
        with open(todo_file, 'w') as f:
            f.write("# 🎯 Project TODO List\n# Managed by LLM Task Controller\n\n")
            yaml.dump(self.todo, f, default_flow_style=False, indent=2)

    def load_changelog(self) -> List[Dict]:
        """Load changelog"""
        changelog_file = Path.cwd() / "CHANGELOG.md"

        if not changelog_file.exists():
            with open(changelog_file, 'w') as f:
                f.write("# 📝 Changelog\n\nAll notable changes to this project will be documented here.\n\n")
            return []

        # Parse existing changelog (simplified)
        try:
            with open(changelog_file, 'r') as f:
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
            with open(changelog_file, 'r') as f:
                content = f.read()
        else:
            content = "# 📝 Changelog\n\nAll notable changes to this project will be documented here.\n\n"

        # Find or create today's section
        today_header = f"## [{date_str}]"

        if today_header not in content:
            # Add new date section after the main header
            lines = content.split('\n')
            insert_idx = 3  # After main header and description
            lines.insert(insert_idx, f"\n{today_header}\n")
            content = '\n'.join(lines)

        # Add the completed task
        task_entry = f"- ✅ **{task['category'].title()}**: {task['title']}"
        if changes:
            task_entry += f"\n  - {chr(10).join(f'  - {change}' for change in changes)}"

        # Insert after today's header
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == today_header:
                lines.insert(i + 1, task_entry)
                break

        with open(changelog_file, 'w') as f:
            f.write('\n'.join(lines))

        print(self.config['responses']['changelog_updated'].format(changes=task['title']))

    def get_current_task(self) -> Optional[Dict]:
        """Get current active task"""
        if self.state['current_task']:
            return next((t for t in self.todo if t['id'] == self.state['current_task']), None)

        # Auto-select next pending task
        pending = [t for t in self.todo if t['status'] == 'pending']
        if pending:
            # Sort by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            pending.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
            return pending[0]

        return None

    def start_task(self, task_id: int):
        """Start working on a specific task"""
        task = next((t for t in self.todo if t['id'] == task_id), None)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False

        if task['status'] == 'completed':
            print(f"✅ Task {task_id} already completed")
            return False

        self.state['current_task'] = task_id
        self.state['task_start_time'] = time.time()
        task['status'] = 'in_progress'

        self.save_state()
        self.save_todo()

        print(f"🎯 Started task: {task['title']}")
        print(f"📋 Category: {task['category']} | Priority: {task['priority']}")

        if 'subtasks' in task:
            print("📝 Subtasks:")
            for subtask in task['subtasks']:
                print(f"   - {subtask}")

        return True

    def complete_task(self, changes: List[str] = None):
        """Mark current task as completed"""
        current_task = self.get_current_task()
        if not current_task:
            print("❌ No active task to complete")
            return False

        current_task['status'] = 'completed'
        current_task['completed_at'] = datetime.now().isoformat()

        if self.state['task_start_time']:
            duration = time.time() - self.state['task_start_time']
            current_task['actual_hours'] = round(duration / 3600, 2)
            self.state['productivity_metrics']['time_focused'] += duration

        # Update changelog
        if self.config['focus']['auto_changelog']:
            self.update_changelog(current_task, changes or [])

        # Update metrics
        self.state['productivity_metrics']['tasks_completed'] += 1
        self.state['current_task'] = None
        self.state['task_start_time'] = None

        self.save_state()
        self.save_todo()

        print(self.config['responses']['task_complete'].format(task=current_task['title']))

        # Suggest next task
        next_task = self.get_current_task()
        if next_task:
            print(f"🎯 Next suggested task: {next_task['title']}")
            print("💡 Use: start_task {next_task['id']} to begin")
        else:
            print("🎉 All tasks completed! Add more tasks to continue.")

        return True

    def check_focus(self, command: List[str]) -> bool:
        """Check if command maintains focus on current task"""
        if not self.config['focus']['require_todo_completion']:
            return True

        current_task = self.get_current_task()
        if not current_task:
            print("📋 No active task. Use 'show_tasks' to see available tasks.")
            return False

        # Check if creating too many files
        if command[0] in ['touch', 'echo'] or (command[0] == 'python' and 'create' in ' '.join(command)):
            files_today = len(self.state['files_modified_today'])
            if files_today >= self.config['focus']['max_files_per_task']:
                print(self.config['responses']['focus_redirect'].format(
                    current_task=current_task['title']
                ))
                print(f"📊 Files modified today: {files_today}/{self.config['focus']['max_files_per_task']}")
                return False

        # Check task timeout
        if self.state['task_start_time']:
            duration = time.time() - self.state['task_start_time']
            timeout = self.config['focus']['task_timeout_minutes'] * 60
            if duration > timeout:
                print(f"⏰ Task timeout ({self.config['focus']['task_timeout_minutes']}min)")
                print("💡 Consider completing current task or extending timeout")
                return False

        return True

    def check_best_practices(self, file_path: str, content: str = None) -> List[str]:
        """Check file against best practices"""
        violations = []

        if not Path(file_path).exists() and not content:
            return violations

        file_ext = Path(file_path).suffix.lower()
        file_content = content or Path(file_path).read_text(errors='ignore')

        # Python best practices
        if file_ext == '.py':
            practices = self.config['best_practices']['python']

            if practices.get('enforce_docstrings'):
                if 'def ' in file_content and '"""' not in file_content:
                    violations.append("Missing docstrings in functions")

            if practices.get('enforce_type_hints'):
                functions = re.findall(r'def\s+\w+\([^)]*\):', file_content)
                if functions and '->' not in file_content:
                    violations.append("Missing type hints in functions")

            if practices.get('max_function_length'):
                functions = re.findall(r'def\s+\w+.*?(?=\ndef|\nclass|\Z)', file_content, re.DOTALL)
                for func in functions:
                    lines = len(func.split('\n'))
                    if lines > practices['max_function_length']:
                        violations.append(f"Function too long: {lines} lines (max {practices['max_function_length']})")

        # JavaScript best practices
        elif file_ext in ['.js', '.ts']:
            practices = self.config['best_practices']['javascript']

            if practices.get('prefer_const'):
                if 'let ' in file_content and 'const ' not in file_content:
                    violations.append("Prefer const over let when possible")

            if practices.get('require_error_handling'):
                if 'async' in file_content and 'try' not in file_content:
                    violations.append("Missing error handling in async functions")

        # General best practices
        general = self.config['best_practices']['general']

        if general.get('no_hardcoded_values'):
            # Simple check for common hardcoded values
            if re.search(r'[\'"][A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}[\'"]', file_content):
                violations.append("Hardcoded email addresses found")
            if re.search(r'[\'"]https?://[^\'"]+[\'"]', file_content):
                violations.append("Hardcoded URLs found")

        if general.get('descriptive_names'):
            # Check for single letter variables (excluding common ones)
            vars_found = re.findall(r'\b[a-df-hj-z]\b', file_content)
            if len(vars_found) > 3:  # Allow some (i, j, k are common)
                violations.append("Use more descriptive variable names")

        return violations

    def safe_execute(self, command: List[str]) -> bool:
        """Execute command with focus and best practice checks"""

        # Check focus first
        if not self.check_focus(command):
            return False

        # Track file modifications
        if command[0] in ['python', 'node', 'touch'] and len(command) > 1:
            file_path = command[1]
            if file_path not in self.state['files_modified_today']:
                self.state['files_modified_today'].append(file_path)

        # Execute command
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            # Post-execution checks for created/modified files
            if command[0] == 'python' and len(command) > 1:
                file_path = command[1]
                if Path(file_path).exists():
                    violations = self.check_best_practices(file_path)
                    if violations:
                        print("\n📋 Best Practice Reminders:")
                        for violation in violations:
                            print(f"   - {violation}")
                        self.state['best_practice_violations'] += len(violations)
                    else:
                        self.state['quality_gates_passed'] += 1
                        print("✅ Code follows best practices!")

            self.save_state()
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            return False

    def setup_shell(self):
        """Setup shell integration with task management"""
        shell_functions = f"""#!/bin/bash
# LLM Task Controller Shell Integration

# Override common commands
python() {{
    python3 {__file__} exec python "$@"
}}

node() {{
    python3 {__file__} exec node "$@"
}}

# Task management commands
show_tasks() {{
    python3 {__file__} show_tasks
}}

start_task() {{
    python3 {__file__} start_task "$1"
}}

complete_task() {{
    python3 {__file__} complete_task
}}

add_task() {{
    python3 {__file__} add_task "$@"
}}

focus_status() {{
    python3 {__file__} focus_status
}}

best_practices() {{
    python3 {__file__} best_practices "$1"
}}

productivity() {{
    python3 {__file__} productivity
}}
"""

        shell_file = Path.home() / ".llmtask_shell.sh"
        with open(shell_file, 'w') as f:
            f.write(shell_functions)
        shell_file.chmod(0o755)

        if len(sys.argv) == 1:
            print("🎯 LLM Task Controller initialized!")
            print(f"📋 Activate: source {shell_file}")
            print(f"⚙️ Configure: .llmcontrol.yaml")
            print(f"📝 Tasks: TODO.yaml")
            print(f"🚀 Start: show_tasks")


def main():
    controller = LLMTaskController()

    if len(sys.argv) == 1:
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "exec":
        controller.safe_execute(args)

    elif command == "show_tasks":
        print("📋 Current Tasks:")
        print("=" * 50)

        current = controller.get_current_task()
        if current:
            print(f"🎯 ACTIVE: #{current['id']} {current['title']}")
            if controller.state['task_start_time']:
                duration = time.time() - controller.state['task_start_time']
                print(f"   ⏱️ Working for: {int(duration // 60)}m {int(duration % 60)}s")
            print()

        for task in controller.todo:
            status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            icon = status_icon.get(task['status'], "❓")
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            p_icon = priority_icon.get(task.get('priority', 'low'), "⚪")

            print(f"{icon} #{task['id']} {p_icon} [{task['category']}] {task['title']}")
            if task.get('description'):
                print(f"    📝 {task['description']}")

        pending = [t for t in controller.todo if t['status'] == 'pending']
        if pending and not current:
            next_task = pending[0]
            print(f"\n💡 Suggested next: start_task {next_task['id']}")

    elif command == "start_task":
        if args:
            try:
                task_id = int(args[0])
                controller.start_task(task_id)
            except ValueError:
                print("❌ Invalid task ID")
        else:
            print("❌ Usage: start_task <task_id>")

    elif command == "complete_task":
        controller.complete_task()

    elif command == "add_task":
        if not args:
            print("❌ Usage: add_task <title> [category] [priority]")
            return

        title = args[0]
        category = args[1] if len(args) > 1 else 'feature'
        priority = args[2] if len(args) > 2 else 'medium'

        new_id = max((t['id'] for t in controller.todo), default=0) + 1
        new_task = {
            'id': new_id,
            'title': title,
            'category': category,
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        controller.todo.append(new_task)
        controller.save_todo()
        print(f"✅ Added task #{new_id}: {title}")

    elif command == "focus_status":
        current = controller.get_current_task()
        print("🎯 Focus Status:")
        print(f"Current Task: {current['title'] if current else 'None'}")
        print(f"Focus Score: {controller.state['focus_score']}/100")
        print(f"Files Modified Today: {len(controller.state['files_modified_today'])}")
        print(f"Best Practice Violations: {controller.state['best_practice_violations']}")

        if controller.state['task_start_time']:
            duration = time.time() - controller.state['task_start_time']
            timeout = controller.config['focus']['task_timeout_minutes'] * 60
            remaining = max(0, timeout - duration)
            print(f"Time Remaining: {int(remaining // 60)}m {int(remaining % 60)}s")

    elif command == "best_practices":
        if args:
            file_path = args[0]
            violations = controller.check_best_practices(file_path)
            if violations:
                print(f"📋 Best Practice Review for {file_path}:")
                for violation in violations:
                    print(f"   ❌ {violation}")
            else:
                print(f"✅ {file_path} follows all best practices!")
        else:
            print("📋 Available Best Practices:")
            for lang, practices in controller.config['best_practices'].items():
                print(f"\n{lang.title()}:")
                for practice, enabled in practices.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {practice}")

    elif command == "productivity":
        metrics = controller.state['productivity_metrics']
        session_time = time.time() - controller.state['session_start']

        print("📊 Productivity Metrics:")
        print(f"Tasks Completed: {metrics['tasks_completed']}")
        print(f"Files Created: {metrics['files_created']}")
        print(f"Lines Written: {metrics['lines_written']}")
        print(f"Time Focused: {int(metrics['time_focused'] // 3600)}h {int((metrics['time_focused'] % 3600) // 60)}m")
        print(f"Session Time: {int(session_time // 3600)}h {int((session_time % 3600) // 60)}m")

        if session_time > 0:
            efficiency = (metrics['time_focused'] / session_time) * 100
            print(f"Focus Efficiency: {efficiency:.1f}%")

    elif command == "config":
        config_file = Path.cwd() / ".llmcontrol.yaml"
        if args and args[0] == "edit":
            subprocess.run([os.environ.get("EDITOR", "nano"), str(config_file)])
        else:
            print(f"📝 Config file: {config_file}")
            print("\n🔧 Current Configuration:")
            print(yaml.dump(controller.config, default_flow_style=False, indent=2))


if __name__ == "__main__":
    main()