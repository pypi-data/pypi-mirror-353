#!/usr/bin/env python3
"""
🎯 TaskGuard CLI - Command Line Interface

Main entry point for TaskGuard LLM Task Controller.
Provides comprehensive command-line interface for task management,
best practices enforcement, and LLM intelligence.
"""

import sys
import argparse
import os
from pathlib import Path
from typing import List, Optional
import json

# Import core TaskGuard components
try:
    from .taskguard import LLMTaskController
    from .local_llm_interface import IntelligentTaskController
    from . import __version__, __description__
except ImportError:
    # Fallback for development/standalone execution
    sys.path.insert(0, str(Path(__file__).parent))
    from taskguard import LLMTaskController
    from local_llm_interface import IntelligentTaskController

    __version__ = "0.2.0-dev"
    __description__ = "LLM Task Controller"


class TaskGuardCLI:
    """Main CLI interface for TaskGuard."""

    def __init__(self):
        self.controller = None
        self.intelligent_controller = None
        self.setup_controllers()

    def setup_controllers(self):
        """Initialize controllers with error handling."""
        try:
            self.controller = LLMTaskController()
        except Exception as e:
            print(f"⚠️ Warning: Basic controller failed to initialize: {e}")

        try:
            self.intelligent_controller = IntelligentTaskController()
        except Exception as e:
            print(f"⚠️ Warning: Intelligent controller failed to initialize: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            prog="taskguard",
            description=__description__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  taskguard init                    # Initialize new project
  taskguard show-tasks             # Show current tasks
  taskguard start-task 1           # Start working on task 1
  taskguard complete-task          # Complete current task
  taskguard smart-analysis         # AI-powered project analysis
  taskguard best-practices file.py # Check best practices
  taskguard status                 # Show system status

For more information, visit: https://github.com/wronai/taskguard
            """
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"TaskGuard {__version__}"
        )

        parser.add_argument(
            "--config",
            type=str,
            help="Path to configuration file (default: .llmcontrol.yaml)"
        )

        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )

        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode"
        )

        # Create subparsers for different commands
        subparsers = parser.add_subparsers(
            dest="command",
            help="Available commands",
            metavar="COMMAND"
        )

        # Core task management commands
        self._add_task_commands(subparsers)

        # Intelligence and analysis commands
        self._add_intelligence_commands(subparsers)

        # Configuration and setup commands
        self._add_config_commands(subparsers)

        # Development and utility commands
        self._add_utility_commands(subparsers)

        return parser

    def _add_task_commands(self, subparsers):
        """Add task management commands."""

        # Initialize project
        init_parser = subparsers.add_parser(
            "init",
            help="Initialize TaskGuard in current directory"
        )
        init_parser.add_argument(
            "--template",
            choices=["basic", "python", "javascript", "enterprise"],
            default="basic",
            help="Project template to use"
        )

        # Show tasks
        subparsers.add_parser(
            "show-tasks",
            aliases=["tasks", "list"],
            help="Show current tasks"
        )

        # Start task
        start_parser = subparsers.add_parser(
            "start-task",
            aliases=["start"],
            help="Start working on a specific task"
        )
        start_parser.add_argument(
            "task_id",
            type=int,
            help="ID of task to start"
        )

        # Complete task
        complete_parser = subparsers.add_parser(
            "complete-task",
            aliases=["complete", "done"],
            help="Mark current task as completed"
        )
        complete_parser.add_argument(
            "--changes",
            nargs="*",
            help="List of changes made"
        )

        # Add task
        add_parser = subparsers.add_parser(
            "add-task",
            aliases=["add"],
            help="Add a new task"
        )
        add_parser.add_argument("title", help="Task title")
        add_parser.add_argument(
            "--category",
            choices=["feature", "bugfix", "refactor", "test", "docs"],
            default="feature",
            help="Task category"
        )
        add_parser.add_argument(
            "--priority",
            choices=["high", "medium", "low"],
            default="medium",
            help="Task priority"
        )
        add_parser.add_argument(
            "--estimate",
            type=float,
            help="Estimated hours"
        )

        # Focus status
        subparsers.add_parser(
            "focus-status",
            aliases=["focus"],
            help="Show current focus metrics"
        )

        # Productivity metrics
        subparsers.add_parser(
            "productivity",
            aliases=["metrics"],
            help="Show productivity analytics"
        )

    def _add_intelligence_commands(self, subparsers):
        """Add AI intelligence commands."""

        # Smart analysis
        subparsers.add_parser(
            "smart-analysis",
            aliases=["analyze", "insights"],
            help="AI-powered project analysis"
        )

        # Smart suggestions
        subparsers.add_parser(
            "smart-suggest",
            aliases=["suggest"],
            help="Get AI task recommendations"
        )

        # Parse documents
        parse_parser = subparsers.add_parser(
            "parse",
            help="Parse TODO or changelog files"
        )
        parse_parser.add_argument(
            "file_type",
            choices=["todo", "changelog"],
            help="Type of file to parse"
        )
        parse_parser.add_argument(
            "file_path",
            nargs="?",
            help="Path to file (default: auto-detect)"
        )

        # Best practices check
        bp_parser = subparsers.add_parser(
            "best-practices",
            aliases=["bp", "check"],
            help="Check best practices compliance"
        )
        bp_parser.add_argument(
            "file_path",
            nargs="?",
            help="File to check (default: show available practices)"
        )

        # Test LLM connection
        subparsers.add_parser(
            "test-llm",
            help="Test local LLM connection"
        )

    def _add_config_commands(self, subparsers):
        """Add configuration commands."""

        # Show configuration
        config_parser = subparsers.add_parser(
            "config",
            help="Show or edit configuration"
        )
        config_parser.add_argument(
            "--edit",
            action="store_true",
            help="Edit configuration file"
        )
        config_parser.add_argument(
            "--template",
            choices=["startup", "enterprise", "learning"],
            help="Apply configuration template"
        )

        # Setup commands
        setup_parser = subparsers.add_parser(
            "setup",
            help="Setup TaskGuard components"
        )
        setup_parser.add_argument(
            "component",
            choices=["ollama", "shell", "monitoring", "team"],
            help="Component to setup"
        )

        # Status
        subparsers.add_parser(
            "status",
            help="Show system status"
        )

        # Health check
        health_parser = subparsers.add_parser(
            "health",
            help="Run project health check"
        )
        health_parser.add_argument(
            "--full",
            action="store_true",
            help="Run comprehensive health check"
        )

    def _add_utility_commands(self, subparsers):
        """Add utility commands."""

        # Execute command safely
        exec_parser = subparsers.add_parser(
            "exec",
            help="Execute command with safety checks"
        )
        exec_parser.add_argument(
            "command",
            nargs="+",
            help="Command to execute"
        )

        # Backup
        backup_parser = subparsers.add_parser(
            "backup",
            help="Create project backup"
        )
        backup_parser.add_argument(
            "--name",
            help="Backup name (default: auto-generated)"
        )

        # Rollback
        rollback_parser = subparsers.add_parser(
            "rollback",
            help="Rollback to previous state"
        )
        rollback_parser.add_argument(
            "--backup",
            help="Specific backup to restore (default: latest)"
        )

        # System info
        subparsers.add_parser(
            "info",
            aliases=["version"],
            help="Show system information"
        )

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        # Set debug/verbose mode
        if parsed_args.debug:
            os.environ["TASKGUARD_DEBUG"] = "1"
        if parsed_args.verbose:
            os.environ["TASKGUARD_VERBOSE"] = "1"

        # Handle no command case
        if not parsed_args.command:
            parser.print_help()
            return 0

        # Route to appropriate handler
        try:
            return self._handle_command(parsed_args)
        except KeyboardInterrupt:
            print("\n⚠️ Operation cancelled by user")
            return 1
        except Exception as e:
            if parsed_args.debug:
                raise
            print(f"❌ Error: {e}")
            return 1

    def _handle_command(self, args) -> int:
        """Handle specific command execution."""
        command = args.command

        # Task management commands
        if command == "init":
            return self._cmd_init(args)
        elif command in ["show-tasks", "tasks", "list"]:
            return self._cmd_show_tasks(args)
        elif command in ["start-task", "start"]:
            return self._cmd_start_task(args)
        elif command in ["complete-task", "complete", "done"]:
            return self._cmd_complete_task(args)
        elif command in ["add-task", "add"]:
            return self._cmd_add_task(args)
        elif command in ["focus-status", "focus"]:
            return self._cmd_focus_status(args)
        elif command in ["productivity", "metrics"]:
            return self._cmd_productivity(args)

        # Intelligence commands
        elif command in ["smart-analysis", "analyze", "insights"]:
            return self._cmd_smart_analysis(args)
        elif command in ["smart-suggest", "suggest"]:
            return self._cmd_smart_suggest(args)
        elif command == "parse":
            return self._cmd_parse(args)
        elif command in ["best-practices", "bp", "check"]:
            return self._cmd_best_practices(args)
        elif command == "test-llm":
            return self._cmd_test_llm(args)

        # Configuration commands
        elif command == "config":
            return self._cmd_config(args)
        elif command == "setup":
            return self._cmd_setup(args)
        elif command == "status":
            return self._cmd_status(args)
        elif command == "health":
            return self._cmd_health(args)

        # Utility commands
        elif command == "exec":
            return self._cmd_exec(args)
        elif command == "backup":
            return self._cmd_backup(args)
        elif command == "rollback":
            return self._cmd_rollback(args)
        elif command in ["info", "version"]:
            return self._cmd_info(args)

        else:
            print(f"❌ Unknown command: {command}")
            return 1

    # Command implementations
    def _cmd_init(self, args) -> int:
        """Initialize TaskGuard in current directory."""
        print("🚀 Initializing TaskGuard...")

        if self.controller:
            # Create default configuration based on template
            template_configs = {
                "basic": {"focus": {"max_files_per_task": 3}},
                "python": {
                    "focus": {"max_files_per_task": 2},
                    "best_practices": {
                        "python": {
                            "enforce_docstrings": True,
                            "enforce_type_hints": True,
                            "require_tests": True
                        }
                    }
                },
                "javascript": {
                    "focus": {"max_files_per_task": 3},
                    "best_practices": {
                        "javascript": {
                            "enforce_jsdoc": True,
                            "prefer_const": True,
                            "require_error_handling": True
                        }
                    }
                },
                "enterprise": {
                    "focus": {"max_files_per_task": 1, "task_timeout_minutes": 45},
                    "quality_gates": {"test_coverage": 90, "security_scan": True}
                }
            }

            config = template_configs.get(args.template, template_configs["basic"])

            # Save configuration
            config_file = Path.cwd() / ".llmcontrol.yaml"
            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            print(f"✅ Created configuration: {config_file}")
            print(f"📋 Using template: {args.template}")

            # Setup shell integration
            self.controller.setup_shell()
            print("✅ Shell integration ready")

            print("\n🎯 Next steps:")
            print("1. source ~/.llmtask_shell.sh")
            print("2. show_tasks")
            print("3. start_task 1")

            return 0
        else:
            print("❌ Controller initialization failed")
            return 1

    def _cmd_show_tasks(self, args) -> int:
        """Show current tasks."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        print("📋 Current Tasks:")
        print("=" * 50)

        current = self.controller.get_current_task()
        if current:
            print(f"🎯 ACTIVE: #{current['id']} {current['title']}")
            if self.controller.state.get('task_start_time'):
                import time
                duration = time.time() - self.controller.state['task_start_time']
                print(f"   ⏱️ Working for: {int(duration // 60)}m {int(duration % 60)}s")
            print()

        for task in self.controller.todo:
            status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            icon = status_icon.get(task['status'], "❓")
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            p_icon = priority_icon.get(task.get('priority', 'low'), "⚪")

            print(f"{icon} #{task['id']} {p_icon} [{task['category']}] {task['title']}")
            if task.get('description'):
                print(f"    📝 {task['description']}")

        pending = [t for t in self.controller.todo if t['status'] == 'pending']
        if pending and not current:
            next_task = pending[0]
            print(f"\n💡 Suggested next: taskguard start-task {next_task['id']}")

        return 0

    def _cmd_start_task(self, args) -> int:
        """Start working on a specific task."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        success = self.controller.start_task(args.task_id)
        return 0 if success else 1

    def _cmd_complete_task(self, args) -> int:
        """Complete current task."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        changes = args.changes if hasattr(args, 'changes') else None
        success = self.controller.complete_task(changes)
        return 0 if success else 1

    def _cmd_add_task(self, args) -> int:
        """Add a new task."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        new_id = max((t['id'] for t in self.controller.todo), default=0) + 1
        new_task = {
            'id': new_id,
            'title': args.title,
            'category': args.category,
            'priority': args.priority,
            'status': 'pending',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if hasattr(args, 'estimate') and args.estimate:
            new_task['estimated_hours'] = args.estimate

        self.controller.todo.append(new_task)
        self.controller.save_todo()

        print(f"✅ Added task #{new_id}: {args.title}")
        return 0

    def _cmd_focus_status(self, args) -> int:
        """Show focus status."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        current = self.controller.get_current_task()
        print("🎯 Focus Status:")
        print(f"Current Task: {current['title'] if current else 'None'}")
        print(f"Focus Score: {self.controller.state.get('focus_score', 100)}/100")
        print(f"Files Modified Today: {len(self.controller.state.get('files_modified_today', []))}")
        print(f"Best Practice Violations: {self.controller.state.get('best_practice_violations', 0)}")

        if self.controller.state.get('task_start_time'):
            import time
            duration = time.time() - self.controller.state['task_start_time']
            timeout = self.controller.config['focus']['task_timeout_minutes'] * 60
            remaining = max(0, timeout - duration)
            print(f"Time Remaining: {int(remaining // 60)}m {int(remaining % 60)}s")

        return 0

    def _cmd_productivity(self, args) -> int:
        """Show productivity metrics."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        metrics = self.controller.state.get('productivity_metrics', {})
        import time
        session_time = time.time() - self.controller.state.get('session_start', time.time())

        print("📊 Productivity Metrics:")
        print(f"Tasks Completed: {metrics.get('tasks_completed', 0)}")
        print(f"Files Created: {metrics.get('files_created', 0)}")
        print(f"Lines Written: {metrics.get('lines_written', 0)}")

        time_focused = metrics.get('time_focused', 0)
        print(f"Time Focused: {int(time_focused // 3600)}h {int((time_focused % 3600) // 60)}m")
        print(f"Session Time: {int(session_time // 3600)}h {int((session_time % 3600) // 60)}m")

        if session_time > 0:
            efficiency = (time_focused / session_time) * 100
            print(f"Focus Efficiency: {efficiency:.1f}%")

        return 0

    def _cmd_smart_analysis(self, args) -> int:
        """Run AI-powered project analysis."""
        if not self.intelligent_controller:
            print("❌ Intelligent controller not available")
            print("💡 Make sure local LLM is running (ollama serve)")
            return 1

        analysis = self.intelligent_controller.get_smart_todo_analysis()

        print("🧠 Smart TODO Analysis:")
        print("=" * 40)
        print(f"📊 Total Tasks: {analysis['total_tasks']}")

        if analysis['by_status']:
            print("\n📈 By Status:")
            for status, count in analysis['by_status'].items():
                print(f"   {status}: {count}")

        if analysis['by_priority']:
            print("\n🎯 By Priority:")
            for priority, count in analysis['by_priority'].items():
                print(f"   {priority}: {count}")

        if analysis['insights']:
            print("\n💡 AI Insights:")
            for i, insight in enumerate(analysis['insights'], 1):
                print(f"   {i}. {insight}")

        return 0

    def _cmd_smart_suggest(self, args) -> int:
        """Get AI task suggestions."""
        if not self.intelligent_controller:
            print("❌ Intelligent controller not available")
            return 1

        suggestion = self.intelligent_controller.smart_task_suggestion()
        if suggestion:
            print("🤖 AI Task Suggestion:")
            print(f"🎯 Task ID: {suggestion.get('suggested_task_id', 'N/A')}")
            print(f"💭 Reasoning: {suggestion.get('reasoning', 'N/A')}")
            print(f"⏱️ Estimated Time: {suggestion.get('estimated_time', 'N/A')}")

            blockers = suggestion.get('potential_blockers', [])
            if blockers:
                print("⚠️ Potential Blockers:")
                for blocker in blockers:
                    print(f"   - {blocker}")
        else:
            print("🤖 AI suggestion not available")

        return 0

    def _cmd_parse(self, args) -> int:
        """Parse documents."""
        if not self.intelligent_controller:
            print("❌ Intelligent controller not available")
            return 1

        if args.file_type == "todo":
            file_path = Path(args.file_path) if args.file_path else Path("TODO.md")
            tasks = self.intelligent_controller.parser.parse_todo(file_path)

            print(f"📋 Parsed TODO from {file_path}:")
            for task in tasks:
                status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
                icon = status_icon.get(task['status'], "❓")
                print(f"{icon} #{task['id']} {task['title']}")

        elif args.file_type == "changelog":
            file_path = Path(args.file_path) if args.file_path else Path("CHANGELOG.md")
            entries = self.intelligent_controller.parser.parse_changelog(file_path)

            print(f"📝 Parsed Changelog from {file_path}:")
            for entry in entries:
                print(f"📅 {entry['date']}")
                for change in entry['entries']:
                    print(f"   - {change['type']}: {change['description']}")

        return 0

    def _cmd_best_practices(self, args) -> int:
        """Check best practices."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        if hasattr(args, 'file_path') and args.file_path:
            violations = self.controller.check_best_practices(args.file_path)
            if violations:
                print(f"📋 Best Practice Review for {args.file_path}:")
                for violation in violations:
                    print(f"   ❌ {violation}")
            else:
                print(f"✅ {args.file_path} follows all best practices!")
        else:
            print("📋 Available Best Practices:")
            for lang, practices in self.controller.config['best_practices'].items():
                print(f"\n{lang.title()}:")
                for practice, enabled in practices.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {practice}")

        return 0

    def _cmd_test_llm(self, args) -> int:
        """Test LLM connection."""
        if not self.intelligent_controller:
            print("❌ Intelligent controller not available")
            return 1

        if self.intelligent_controller.llm.available:
            print("🤖 Testing local LLM...")
            result = self.intelligent_controller.llm.query(
                "List 3 programming best practices",
                "You are a helpful coding assistant."
            )
            print(f"✅ Response: {result}")
            return 0
        else:
            print("❌ Local LLM not available")
            print("💡 Setup instructions:")
            print("   1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   2. Start service: ollama serve")
            print("   3. Pull model: ollama pull llama3.2:3b")
            return 1

    def _cmd_config(self, args) -> int:
        """Show or edit configuration."""
        config_file = Path.cwd() / ".llmcontrol.yaml"

        if hasattr(args, 'edit') and args.edit:
            import subprocess
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(config_file)])
            return 0

        if hasattr(args, 'template') and args.template:
            # Apply template configuration
            templates = {
                "startup": {
                    "focus": {"max_files_per_task": 5, "task_timeout_minutes": 60},
                    "best_practices": {"python": {"enforce_docstrings": False}}
                },
                "enterprise": {
                    "focus": {"max_files_per_task": 2, "require_code_review": True},
                    "quality_gates": {"security_scan": True, "test_coverage": 90}
                },
                "learning": {
                    "focus": {"max_files_per_task": 1, "educational_hints": True},
                    "best_practices": {"explain_violations": True}
                }
            }

            if args.template in templates:
                import yaml
                with open(config_file, 'w') as f:
                    yaml.dump(templates[args.template], f, default_flow_style=False, indent=2)
                print(f"✅ Applied {args.template} template to {config_file}")
                return 0

        # Show current configuration
        if config_file.exists():
            print(f"📝 Configuration file: {config_file}")
            with open(config_file, 'r') as f:
                print(f.read())
        else:
            print("❌ No configuration file found")
            print("💡 Run 'taskguard init' to create one")

        return 0

    def _cmd_setup(self, args) -> int:
        """Setup TaskGuard components."""
        component = args.component

        if component == "ollama":
            print("🚀 Setting up Ollama for TaskGuard...")
            print("\n1. Install Ollama:")
            print("   curl -fsSL https://ollama.ai/install.sh | sh")
            print("\n2. Start Ollama service:")
            print("   ollama serve")
            print("\n3. Pull recommended model:")
            print("   ollama pull llama3.2:3b")
            print("\n4. Test integration:")
            print("   taskguard test-llm")

        elif component == "shell":
            print("🔧 Setting up shell integration...")
            if self.controller:
                success = self.controller.setup_shell(force=True)
                if success:
                    print("\n✅ Shell integration setup complete!")
                    print("🎯 Next steps:")
                    print("   1. source ~/.llmtask_shell.sh")
                    print("   2. show_tasks")
                    print("   3. start_task 1")
                    print("   4. Type 'tg_help' for all available commands")
                    return 0
                else:
                    print("❌ Shell integration setup failed")
                    return 1
            else:
                print("❌ Controller not available")
                return 1

        elif component == "monitoring":
            print("📊 Setting up monitoring...")
            monitoring_config = {
                "alerts": {"focus_drop": True, "quality_issues": True},
                "metrics": {"track_productivity": True, "track_violations": True},
                "thresholds": {
                    "focus_score_min": 70,
                    "health_score_min": 80,
                    "max_violations_per_session": 5
                }
            }

            with open(".llmmonitoring.yaml", 'w') as f:
                import yaml
                yaml.dump(monitoring_config, f, default_flow_style=False, indent=2)

            print("✅ Monitoring configuration created: .llmmonitoring.yaml")
            print("📊 Monitoring features:")
            print("   - Focus score tracking")
            print("   - Quality violation alerts")
            print("   - Productivity metrics")

        elif component == "team":
            print("👥 Setting up team configuration...")
            team_config = {
                "team_settings": {
                    "shared_practices": True,
                    "team_dashboard": True,
                    "code_review_required": True,
                    "shared_todo": False
                },
                "collaboration": {
                    "task_assignment": True,
                    "progress_sharing": True,
                    "best_practice_sync": True
                },
                "notifications": {
                    "task_completion": True,
                    "quality_issues": True,
                    "team_insights": True
                }
            }

            with open(".llmteam.yaml", 'w') as f:
                import yaml
                yaml.dump(team_config, f, default_flow_style=False, indent=2)

            print("✅ Team configuration created: .llmteam.yaml")
            print("👥 Team features:")
            print("   - Shared best practices")
            print("   - Code review requirements")
            print("   - Team dashboard")
            print("   - Progress sharing")

        return 0

    def _cmd_status(self, args) -> int:
        """Show system status."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        print("🛡️ TaskGuard Status")
        print("=" * 30)

        # Basic status
        health_score = self.controller.state.get('health_score', 100)
        commands_blocked = self.controller.state.get('commands_blocked', 0)

        if health_score >= 80:
            print(f"Health Score: {health_score}/100 ✅")
        elif health_score >= 60:
            print(f"Health Score: {health_score}/100 ⚠️")
        else:
            print(f"Health Score: {health_score}/100 🚨")

        print(f"Commands Blocked: {commands_blocked}")

        # LLM status
        if self.intelligent_controller and self.intelligent_controller.llm.available:
            print(f"🤖 Local LLM: ✅ Connected ({self.intelligent_controller.llm.model})")
        else:
            print("🤖 Local LLM: ❌ Unavailable")

        # Current task
        current = self.controller.get_current_task()
        if current:
            print(f"🎯 Current Task: #{current['id']} {current['title']}")
        else:
            print("🎯 Current Task: None")

        return 0

    def _cmd_health(self, args) -> int:
        """Run health check."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        print("🔍 Running health check...")

        issues = 0

        # Check Python files
        py_files = list(Path.cwd().glob("*.py"))[:5]
        if py_files:
            print("🐍 Checking Python files...")
            for py_file in py_files:
                try:
                    import subprocess
                    subprocess.run(["python", "-m", "py_compile", str(py_file)],
                                   check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print(f"❌ Syntax error: {py_file}")
                    issues += 1

        # Check package.json if exists
        if Path("package.json").exists():
            print("📦 Checking Node.js project...")
            try:
                with open("package.json", 'r') as f:
                    json.load(f)
                print("✅ Valid package.json")
            except json.JSONDecodeError:
                print("❌ Invalid package.json")
                issues += 1

        # Check git status
        if Path(".git").exists():
            try:
                import subprocess
                result = subprocess.run(["git", "status", "--porcelain"],
                                        capture_output=True, text=True, check=True)
                changed_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                if changed_files > 10:
                    print(f"⚠️ Many files changed: {changed_files}")
                else:
                    print(f"✅ Git status clean ({changed_files} changed)")
            except:
                print("⚠️ Could not check git status")

        if issues == 0:
            print("🎉 Health check passed!")
            return 0
        else:
            print(f"🚨 Health check found {issues} issues")
            return 1

    def _cmd_exec(self, args) -> int:
        """Execute command safely."""
        if not self.controller:
            print("❌ Controller not available")
            return 1

        success = self.controller.safe_execute(args.command)
        return 0 if success else 1

    def _cmd_backup(self, args) -> int:
        """Create backup."""
        print("📦 Creating backup...")

        try:
            import time
            backup_name = args.name if hasattr(args, 'name') and args.name else f"backup_{int(time.time())}"

            # Simple backup using git or file copy
            if Path(".git").exists():
                import subprocess
                subprocess.run(["git", "add", "."], check=False)
                result = subprocess.run(
                    ["git", "commit", "-m", f"TaskGuard backup: {backup_name}"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ Git backup created: {backup_name}")
                    return 0

            # Fallback: create backup directory
            backup_dir = Path.home() / ".taskguard_backups" / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)

            import shutil
            for item in Path.cwd().iterdir():
                if item.name not in ['.git', '__pycache__', 'node_modules']:
                    if item.is_file():
                        shutil.copy2(item, backup_dir)
                    elif item.is_dir():
                        shutil.copytree(item, backup_dir / item.name,
                                        ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))

            print(f"✅ File backup created: {backup_dir}")
            return 0

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return 1

    def _cmd_rollback(self, args) -> int:
        """Rollback to previous state."""
        print("🔄 Rolling back...")

        try:
            if Path(".git").exists():
                import subprocess
                result = subprocess.run(["git", "log", "--oneline", "-5"],
                                        capture_output=True, text=True)
                commits = result.stdout.strip().split('\n')

                backup_commits = [c for c in commits if "TaskGuard backup" in c]
                if backup_commits:
                    commit_hash = backup_commits[0].split()[0]
                    subprocess.run(["git", "reset", "--hard", commit_hash], check=True)
                    print(f"✅ Rolled back to: {backup_commits[0]}")
                    return 0
                else:
                    print("❌ No backup commits found")
                    return 1
            else:
                print("❌ No git repository found")
                return 1

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return 1

    def _cmd_info(self, args) -> int:
        """Show system information."""
        import sys
        import platform

        print("🧠 TaskGuard System Information")
        print("=" * 35)
        print(f"TaskGuard Version: {__version__}")
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Architecture: {platform.machine()}")

        # Check features
        features = {}
        try:
            import yaml
            features["YAML Support"] = "✅"
        except ImportError:
            features["YAML Support"] = "❌"

        try:
            import requests
            features["HTTP Requests"] = "✅"
        except ImportError:
            features["HTTP Requests"] = "❌"

        print("\n🔧 Available Features:")
        for feature, status in features.items():
            print(f"   {status} {feature}")

        # LLM status
        if self.intelligent_controller:
            llm_status = "✅ Connected" if self.intelligent_controller.llm.available else "❌ Unavailable"
            print(f"\n🤖 Local LLM: {llm_status}")
            if self.intelligent_controller.llm.available:
                print(f"   Provider: {self.intelligent_controller.llm.provider}")
                print(f"   Model: {self.intelligent_controller.llm.model}")

        return 0


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for TaskGuard CLI."""
    cli = TaskGuardCLI()
    return cli.run(args)


if __name__ == "__main__":
    import time

    sys.exit(main())