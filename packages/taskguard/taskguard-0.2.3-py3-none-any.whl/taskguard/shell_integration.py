#!/usr/bin/env python3
"""
🔧 Shell Integration for TaskGuard
Generates shell functions that wrap common commands for LLM control
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


class ShellIntegration:
    """Manages shell integration for TaskGuard."""

    def __init__(self, config: Dict):
        self.config = config
        self.shell_file = Path.home() / ".llmtask_shell.sh"
        self.taskguard_cmd = self._get_taskguard_command()

    def _get_taskguard_command(self) -> str:
        """Determine the correct taskguard command to use."""
        # Try to find taskguard in PATH
        import shutil

        # Check for different possible commands
        for cmd in ["taskguard", "tg", "llmtask"]:
            if shutil.which(cmd):
                return cmd

        # Fallback to python module execution
        return f"python -m taskguard.cli"

    def generate_shell_functions(self) -> str:
        """Generate shell functions for command wrapping."""

        shell_content = f"""#!/bin/bash
# 🧠 TaskGuard Shell Integration
# Auto-generated shell functions for LLM control
# Source this file: source ~/.llmtask_shell.sh

# ========================================
# CORE COMMAND WRAPPERS
# ========================================

# Python execution with safety checks
python() {{
    {self.taskguard_cmd} exec python "$@"
}}

python3() {{
    {self.taskguard_cmd} exec python3 "$@"
}}

# Node.js execution with safety checks
node() {{
    {self.taskguard_cmd} exec node "$@"
}}

# NPM with automatic backups
npm() {{
    {self.taskguard_cmd} exec npm "$@"
}}

# Git with safety checks
git() {{
    {self.taskguard_cmd} exec git "$@"
}}

# ========================================
# TASK MANAGEMENT COMMANDS
# ========================================

# Show current tasks
show_tasks() {{
    {self.taskguard_cmd} show-tasks
}}

# Alternative aliases
tasks() {{
    {self.taskguard_cmd} show-tasks
}}

list_tasks() {{
    {self.taskguard_cmd} show-tasks
}}

# Start working on a task
start_task() {{
    if [ -z "$1" ]; then
        echo "❌ Usage: start_task <task_id>"
        echo "💡 Run 'show_tasks' to see available tasks"
        return 1
    fi
    {self.taskguard_cmd} start-task "$1"
}}

# Complete current task
complete_task() {{
    {self.taskguard_cmd} complete-task "$@"
}}

# Alternative aliases
done_task() {{
    {self.taskguard_cmd} complete-task "$@"
}}

finish_task() {{
    {self.taskguard_cmd} complete-task "$@"
}}

# Add new task
add_task() {{
    if [ -z "$1" ]; then
        echo "❌ Usage: add_task '<title>' [category] [priority]"
        echo "📝 Example: add_task 'Fix login bug' bugfix high"
        return 1
    fi
    {self.taskguard_cmd} add-task "$@"
}}

# ========================================
# INTELLIGENCE COMMANDS
# ========================================

# AI-powered project analysis
smart_analysis() {{
    {self.taskguard_cmd} smart-analysis
}}

# AI task suggestions
smart_suggest() {{
    {self.taskguard_cmd} smart-suggest
}}

# Aliases for intelligence
analyze() {{
    {self.taskguard_cmd} smart-analysis
}}

insights() {{
    {self.taskguard_cmd} smart-analysis
}}

suggest() {{
    {self.taskguard_cmd} smart-suggest
}}

# ========================================
# FOCUS AND PRODUCTIVITY
# ========================================

# Show focus status
focus_status() {{
    {self.taskguard_cmd} focus-status
}}

# Show productivity metrics
productivity() {{
    {self.taskguard_cmd} productivity
}}

# Alternative aliases
focus() {{
    {self.taskguard_cmd} focus-status
}}

metrics() {{
    {self.taskguard_cmd} productivity
}}

stats() {{
    {self.taskguard_cmd} productivity
}}

# ========================================
# BEST PRACTICES AND QUALITY
# ========================================

# Check best practices
best_practices() {{
    {self.taskguard_cmd} best-practices "$@"
}}

# Aliases
check_code() {{
    {self.taskguard_cmd} best-practices "$@"
}}

lint() {{
    {self.taskguard_cmd} best-practices "$@"
}}

review() {{
    {self.taskguard_cmd} best-practices "$@"
}}

# ========================================
# SYSTEM COMMANDS
# ========================================

# Show system status
tg_status() {{
    {self.taskguard_cmd} status
}}

# Run health check
tg_health() {{
    {self.taskguard_cmd} health "$@"
}}

# Show configuration
tg_config() {{
    {self.taskguard_cmd} config "$@"
}}

# Create backup
tg_backup() {{
    {self.taskguard_cmd} backup "$@"
}}

# Rollback changes
tg_rollback() {{
    {self.taskguard_cmd} rollback "$@"
}}

# ========================================
# SAFE ALTERNATIVES
# ========================================

# Safe file deletion with backup
safe_rm() {{
    echo "🛡️ Using safe deletion (with backup)..."
    {self.taskguard_cmd} backup --name "before_rm_$(date +%s)"
    command rm "$@"
}}

# Safe git operations
safe_git() {{
    echo "🛡️ Using safe git (with backup)..."
    {self.taskguard_cmd} backup --name "before_git_$(date +%s)"
    command git "$@"
}}

# Force Python execution (bypass safety)
force_python() {{
    echo "⚠️ BYPASSING SAFETY CHECKS"
    command python "$@"
}}

# Force any command (emergency use)
force_exec() {{
    echo "🚨 EMERGENCY BYPASS - USE WITH CAUTION"
    command "$@"
}}

# ========================================
# HELP AND INFORMATION
# ========================================

# Show help
tg_help() {{
    echo "🧠 TaskGuard Shell Integration Help"
    echo "=================================="
    echo ""
    echo "📋 Task Management:"
    echo "  show_tasks              - List all tasks"
    echo "  start_task <id>         - Start working on task"
    echo "  complete_task           - Complete current task"
    echo "  add_task '<title>'      - Add new task"
    echo ""
    echo "🧠 AI Intelligence:"
    echo "  smart_analysis          - AI project analysis"
    echo "  smart_suggest           - AI task recommendations"
    echo "  best_practices [file]   - Check code quality"
    echo ""
    echo "🎯 Productivity:"
    echo "  focus_status            - Show focus metrics"
    echo "  productivity            - Show statistics"
    echo ""
    echo "🛡️ Safety:"
    echo "  tg_status               - System status"
    echo "  tg_health               - Health check"
    echo "  tg_backup               - Create backup"
    echo "  safe_rm <files>         - Safe deletion"
    echo ""
    echo "💡 Examples:"
    echo "  show_tasks"
    echo "  start_task 1"
    echo "  add_task 'Fix authentication' bugfix high"
    echo "  smart_analysis"
    echo "  best_practices auth.py"
    echo ""
    echo "🔧 For full CLI: {self.taskguard_cmd} --help"
}}

# Aliases for help
llm_help() {{
    tg_help
}}

taskguard_help() {{
    tg_help
}}

# ========================================
# ENHANCED LLM INTEGRATION
# ========================================

# Quick project overview (perfect for LLM)
overview() {{
    echo "🧠 Project Overview"
    echo "=================="
    {self.taskguard_cmd} status
    echo ""
    {self.taskguard_cmd} show-tasks
    echo ""
    echo "💡 Use 'tg_help' for available commands"
}}

# Quick check (for LLM to verify system state)
check() {{
    {self.taskguard_cmd} status >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ System OK"
        return 0
    else
        echo "❌ System issues detected"
        echo "💡 Run 'tg_health' for details"
        return 1
    fi
}}

# Initialize new project (for LLM)
init_project() {{
    echo "🚀 Initializing TaskGuard project..."
    {self.taskguard_cmd} init "$@"
    echo "✅ Project initialized!"
    echo "📋 Current tasks:"
    {self.taskguard_cmd} show-tasks
}}

# ========================================
# COMPLETION AND SETUP
# ========================================

# Auto-completion for bash
if [ -n "${{BASH_VERSION}}" ]; then
    # Task ID completion for start_task
    _start_task_completion() {{
        local cur="${{COMP_WORDS[COMP_CWORD]}}"
        local task_ids=$({self.taskguard_cmd} show-tasks 2>/dev/null | grep -o '#[0-9]\\+' | sed 's/#//' | tr '\\n' ' ')
        COMPREPLY=($(compgen -W "$task_ids" -- "$cur"))
    }}
    complete -F _start_task_completion start_task

    # File completion for best_practices
    complete -f best_practices check_code lint review
fi

# ========================================
# INITIALIZATION MESSAGE
# ========================================

echo "🧠 TaskGuard Shell Integration Loaded!"
echo "💡 Type 'tg_help' for available commands"
echo "🎯 Type 'overview' for project status"

# Check if TaskGuard is properly installed
if ! command -v {self.taskguard_cmd.split()[0]} &> /dev/null; then
    echo "⚠️  Warning: TaskGuard command not found in PATH"
    echo "💡 Make sure TaskGuard is properly installed"
fi

# Check if we're in a TaskGuard project
if [ ! -f ".llmcontrol.yaml" ]; then
    echo "📋 No TaskGuard project detected"
    echo "💡 Run 'init_project' to initialize"
fi
"""
        return shell_content

    def setup_shell_integration(self, force: bool = False) -> bool:
        """Setup shell integration by creating the shell file."""
        if self.shell_file.exists() and not force:
            print(f"🔧 Shell integration already exists: {self.shell_file}")
            print("💡 Use --force to regenerate")
            return True

        try:
            # Generate shell functions
            shell_content = self.generate_shell_functions()

            # Write to file
            with open(self.shell_file, "w") as f:
                f.write(shell_content)

            # Make executable
            self.shell_file.chmod(0o755)

            print(f"✅ Shell integration created: {self.shell_file}")
            print(f"🚀 Activate with: source {self.shell_file}")
            print("💡 Add to your ~/.bashrc or ~/.zshrc for automatic loading")

            return True

        except Exception as e:
            print(f"❌ Failed to setup shell integration: {e}")
            return False

    def add_to_profile(self, shell: str = "bash") -> bool:
        """Add shell integration to shell profile."""
        if shell == "bash":
            profile_file = Path.home() / ".bashrc"
        elif shell == "zsh":
            profile_file = Path.home() / ".zshrc"
        else:
            print(f"❌ Unsupported shell: {shell}")
            return False

        source_line = f"source {self.shell_file}"

        # Check if already added
        if profile_file.exists():
            with open(profile_file, "r") as f:
                if source_line in f.read():
                    print(f"✅ Already added to {profile_file}")
                    return True

        # Add to profile
        try:
            with open(profile_file, "a") as f:
                f.write(f"\n# TaskGuard Shell Integration\n")
                f.write(f"{source_line}\n")

            print(f"✅ Added to {profile_file}")
            print(f"🔄 Restart shell or run: source {profile_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to add to {profile_file}: {e}")
            return False

    def remove_shell_integration(self) -> bool:
        """Remove shell integration."""
        try:
            if self.shell_file.exists():
                self.shell_file.unlink()
                print(f"✅ Removed shell integration: {self.shell_file}")
            else:
                print("ℹ️ Shell integration file not found")

            # TODO: Remove from shell profiles
            print(
                "💡 You may want to remove the source line from ~/.bashrc or ~/.zshrc"
            )

            return True

        except Exception as e:
            print(f"❌ Failed to remove shell integration: {e}")
            return False

    def test_shell_integration(self) -> bool:
        """Test if shell integration is working."""
        if not self.shell_file.exists():
            print("❌ Shell integration file not found")
            return False

        # Test if TaskGuard command is available
        import shutil

        if not shutil.which(self.taskguard_cmd.split()[0]):
            print(f"❌ TaskGuard command not found: {self.taskguard_cmd}")
            return False

        print("✅ Shell integration looks good!")
        print(f"📁 File: {self.shell_file}")
        print(f"🔧 Command: {self.taskguard_cmd}")
        print("💡 Source the file to activate: source ~/.llmtask_shell.sh")

        return True


def main():
    """Standalone shell integration setup."""
    import argparse

    parser = argparse.ArgumentParser(description="TaskGuard Shell Integration")
    parser.add_argument("--setup", action="store_true", help="Setup shell integration")
    parser.add_argument("--force", action="store_true", help="Force regenerate")
    parser.add_argument(
        "--add-to-profile", choices=["bash", "zsh"], help="Add to shell profile"
    )
    parser.add_argument(
        "--remove", action="store_true", help="Remove shell integration"
    )
    parser.add_argument("--test", action="store_true", help="Test shell integration")

    args = parser.parse_args()

    # Default empty config
    config = {}
    shell_integration = ShellIntegration(config)

    if args.setup or (not any([args.remove, args.test, args.add_to_profile])):
        shell_integration.setup_shell_integration(force=args.force)

    if args.add_to_profile:
        shell_integration.add_to_profile(args.add_to_profile)

    if args.remove:
        shell_integration.remove_shell_integration()

    if args.test:
        shell_integration.test_shell_integration()


if __name__ == "__main__":
    main()
