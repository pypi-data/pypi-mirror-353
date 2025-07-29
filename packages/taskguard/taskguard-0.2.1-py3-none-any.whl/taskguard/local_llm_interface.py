#!/usr/bin/env python3
"""
🧠 LLM Task Controller with Local LLM Intelligence
Smart parsing and analysis using local LLM (Ollama/LM Studio)
"""

import os, sys, json, subprocess, time, yaml, requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import re


class LocalLLMInterface:
    """Interface for local LLM services (Ollama, LM Studio, etc.)"""

    def __init__(self, config: Dict):
        self.config = config.get('local_llm', {})
        self.provider = self.config.get('provider', 'ollama')
        self.model = self.config.get('model', 'llama3.2:3b')
        self.base_url = self.config.get('base_url', 'http://localhost:11434')
        self.timeout = self.config.get('timeout', 30)

        # Test connection
        self.available = self.test_connection()

    def test_connection(self) -> bool:
        """Test if local LLM is available"""
        try:
            if self.provider == 'ollama':
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                return response.status_code == 200
            elif self.provider == 'lmstudio':
                response = requests.get(f"{self.base_url}/v1/models", timeout=5)
                return response.status_code == 200
            return False
        except:
            return False

    def query(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Query local LLM"""
        if not self.available:
            return None

        try:
            if self.provider == 'ollama':
                return self._query_ollama(prompt, system_prompt)
            elif self.provider == 'lmstudio':
                return self._query_lmstudio(prompt, system_prompt)
        except Exception as e:
            print(f"🤖 LLM query failed: {e}")
            return None

    def _query_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Query Ollama API"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent parsing
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            return response.json().get('response', '').strip()
        return ""

    def _query_lmstudio(self, prompt: str, system_prompt: str = "") -> str:
        """Query LM Studio API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        return ""


class IntelligentDocumentParser:
    """Parse various document formats using local LLM"""

    def __init__(self, llm: LocalLLMInterface):
        self.llm = llm
        self.fallback_parsers = {
            'todo': self._fallback_parse_todo,
            'changelog': self._fallback_parse_changelog
        }

    def parse_todo(self, file_path: Path) -> List[Dict]:
        """Parse TODO file in any format using LLM"""
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Try LLM parsing first
        if self.llm.available:
            parsed = self._llm_parse_todo(content)
            if parsed:
                return parsed

        # Fallback to regex parsing
        return self.fallback_parsers['todo'](content)

    def parse_changelog(self, file_path: Path) -> List[Dict]:
        """Parse changelog in any format using LLM"""
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Try LLM parsing first
        if self.llm.available:
            parsed = self._llm_parse_changelog(content)
            if parsed:
                return parsed

        # Fallback to regex parsing
        return self.fallback_parsers['changelog'](content)

    def _llm_parse_todo(self, content: str) -> Optional[List[Dict]]:
        """Use LLM to parse TODO content"""
        system_prompt = """You are a TODO list parser. Extract tasks from any format (markdown, plain text, YAML, etc.) and return valid JSON.

REQUIRED JSON FORMAT:
[
  {
    "id": 1,
    "title": "Task title",
    "status": "pending|in_progress|completed",
    "priority": "high|medium|low",
    "category": "feature|bugfix|refactor|test|docs",
    "description": "Task description",
    "subtasks": ["subtask1", "subtask2"],
    "estimated_hours": 2.5,
    "labels": ["label1", "label2"]
  }
]

Rules:
- Always return valid JSON array
- Extract ALL tasks found
- Infer missing fields logically
- Status from: ☐ pending, ⏳ in_progress, ✅ completed
- Priority from: 🔴 high, 🟡 medium, 🟢 low
- Be smart about parsing different formats"""

        prompt = f"""Parse this TODO content and extract all tasks:

{content}

Return only valid JSON array, no explanations."""

        result = self.llm.query(prompt, system_prompt)
        if result:
            try:
                # Clean up the response (remove markdown formatting if present)
                json_str = result.strip()
                if json_str.startswith('```'):
                    json_str = '\n'.join(json_str.split('\n')[1:-1])

                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError as e:
                print(f"🤖 LLM JSON parse error: {e}")

        return None

    def _llm_parse_changelog(self, content: str) -> Optional[List[Dict]]:
        """Use LLM to parse changelog content"""
        system_prompt = """You are a changelog parser. Extract entries from any format and return valid JSON.

REQUIRED JSON FORMAT:
[
  {
    "date": "2024-12-05",
    "version": "1.0.0",
    "entries": [
      {
        "type": "feature|bugfix|change|removal",
        "description": "What was changed",
        "details": ["detail1", "detail2"]
      }
    ]
  }
]

Rules:
- Always return valid JSON array
- Group by date/version
- Extract ALL changes
- Infer type from: ✅ feature, 🐛 bugfix, 🔄 change, ❌ removal
- Be smart about different changelog formats"""

        prompt = f"""Parse this changelog content:

{content}

Return only valid JSON array, no explanations."""

        result = self.llm.query(prompt, system_prompt)
        if result:
            try:
                json_str = result.strip()
                if json_str.startswith('```'):
                    json_str = '\n'.join(json_str.split('\n')[1:-1])

                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

        return None

    def _fallback_parse_todo(self, content: str) -> List[Dict]:
        """Fallback regex-based TODO parsing"""
        tasks = []
        task_id = 1

        lines = content.split('\n')
        current_task = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Look for task indicators
            if any(indicator in line for indicator in ['- [ ]', '- [x]', '☐', '✅', '⏳']):
                if current_task:
                    tasks.append(current_task)

                # Extract status
                status = 'pending'
                if '- [x]' in line or '✅' in line:
                    status = 'completed'
                elif '⏳' in line:
                    status = 'in_progress'

                # Extract priority
                priority = 'medium'
                if '🔴' in line or 'HIGH' in line.upper():
                    priority = 'high'
                elif '🟢' in line or 'LOW' in line.upper():
                    priority = 'low'

                # Extract title
                title = re.sub(r'[-\[\]x☐✅⏳🔴🟡🟢]', '', line).strip()
                title = re.sub(r'\s+', ' ', title)

                current_task = {
                    'id': task_id,
                    'title': title,
                    'status': status,
                    'priority': priority,
                    'category': 'feature',
                    'subtasks': []
                }
                task_id += 1

            elif current_task and line.startswith('  -'):
                # Subtask
                subtask = line[3:].strip()
                current_task['subtasks'].append(subtask)

        if current_task:
            tasks.append(current_task)

        return tasks

    def _fallback_parse_changelog(self, content: str) -> List[Dict]:
        """Fallback regex-based changelog parsing"""
        entries = []
        lines = content.split('\n')
        current_entry = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for date headers
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match and (line.startswith('#') or line.startswith('##')):
                if current_entry:
                    entries.append(current_entry)

                current_entry = {
                    'date': date_match.group(1),
                    'version': '',
                    'entries': []
                }

            elif current_entry and line.startswith('-'):
                # Change entry
                change_type = 'change'
                if '✅' in line or 'Added' in line:
                    change_type = 'feature'
                elif '🐛' in line or 'Fixed' in line:
                    change_type = 'bugfix'
                elif '❌' in line or 'Removed' in line:
                    change_type = 'removal'

                description = re.sub(r'[-✅🐛❌]', '', line).strip()

                current_entry['entries'].append({
                    'type': change_type,
                    'description': description,
                    'details': []
                })

        if current_entry:
            entries.append(current_entry)

        return entries


class IntelligentTaskController:
    """Enhanced task controller with LLM intelligence"""

    def __init__(self):
        self.config = self.load_config()
        self.llm = LocalLLMInterface(self.config)
        self.parser = IntelligentDocumentParser(self.llm)
        self.state = self.load_state()

        print(f"🤖 Local LLM: {'✅ Connected' if self.llm.available else '❌ Unavailable'}")
        if self.llm.available:
            print(f"📡 Using: {self.llm.provider} ({self.llm.model})")

    def load_config(self):
        """Load configuration with LLM settings"""
        config_file = Path.cwd() / ".llmcontrol.yaml"

        default_config = {
            'local_llm': {
                'provider': 'ollama',  # ollama, lmstudio, openai_compatible
                'model': 'llama3.2:3b',  # or 'microsoft/DialoGPT-medium', etc.
                'base_url': 'http://localhost:11434',
                'timeout': 30,
                'fallback_to_regex': True
            },
            'documents': {
                'todo_formats': ['markdown', 'yaml', 'plain_text', 'org_mode'],
                'changelog_formats': ['markdown', 'keep_a_changelog', 'conventional'],
                'auto_detect_format': True,
                'smart_parsing': True
            },
            'intelligence': {
                'analyze_task_context': True,
                'suggest_improvements': True,
                'detect_blockers': True,
                'estimate_completion': True,
                'auto_categorize': True
            },
            'focus': {
                'max_files_per_task': 3,
                'require_todo_completion': True,
                'auto_changelog': True,
                'smart_task_suggestions': True
            }
        }

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                    return self.merge_config(default_config, user_config or {})
            except:
                pass

        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)

        return default_config

    def merge_config(self, default: Dict, user: Dict) -> Dict:
        """Deep merge configurations"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                default[key] = self.merge_config(default[key], value)
            else:
                default[key] = value
        return default

    def load_state(self) -> Dict:
        """Load current state"""
        state_file = Path.cwd() / ".llmstate.json"
        default_state = {
            'current_task': None,
            'session_start': time.time(),
            'intelligence_insights': [],
            'auto_suggestions': []
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
        with open(Path.cwd() / ".llmstate.json", 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def get_smart_todo_analysis(self) -> Dict:
        """Get intelligent TODO analysis"""
        todo_files = self.find_todo_files()
        all_tasks = []

        for todo_file in todo_files:
            tasks = self.parser.parse_todo(todo_file)
            all_tasks.extend(tasks)

        analysis = {
            'total_tasks': len(all_tasks),
            'by_status': {},
            'by_priority': {},
            'by_category': {},
            'insights': []
        }

        # Basic analysis
        for task in all_tasks:
            status = task.get('status', 'unknown')
            priority = task.get('priority', 'unknown')
            category = task.get('category', 'unknown')

            analysis['by_status'][status] = analysis['by_status'].get(status, 0) + 1
            analysis['by_priority'][priority] = analysis['by_priority'].get(priority, 0) + 1
            analysis['by_category'][category] = analysis['by_category'].get(category, 0) + 1

        # LLM-powered insights
        if self.llm.available and all_tasks:
            insights = self.get_llm_project_insights(all_tasks)
            analysis['insights'] = insights

        return analysis

    def get_llm_project_insights(self, tasks: List[Dict]) -> List[str]:
        """Get AI insights about project state"""
        system_prompt = """You are a project management AI. Analyze tasks and provide actionable insights.

Focus on:
- Bottlenecks and blockers
- Task prioritization suggestions
- Workflow improvements
- Risk assessment
- Resource allocation

Provide 3-5 short, actionable insights."""

        tasks_summary = json.dumps(tasks, indent=2)
        prompt = f"""Analyze these project tasks and provide insights:

{tasks_summary}

Provide insights as a JSON array of strings:
["insight 1", "insight 2", "insight 3"]"""

        result = self.llm.query(prompt, system_prompt)
        if result:
            try:
                json_str = result.strip()
                if json_str.startswith('```'):
                    json_str = '\n'.join(json_str.split('\n')[1:-1])

                insights = json.loads(json_str)
                if isinstance(insights, list):
                    return insights[:5]  # Limit to 5 insights
            except:
                pass

        return []

    def find_todo_files(self) -> List[Path]:
        """Find all TODO-related files"""
        patterns = [
            'TODO.md', 'TODO.txt', 'TODO.yaml', 'TODO.yml',
            'todo.md', 'todo.txt', 'todo.yaml', 'todo.yml',
            'TASKS.md', 'tasks.md', 'backlog.md', 'BACKLOG.md'
        ]

        found_files = []
        for pattern in patterns:
            file_path = Path.cwd() / pattern
            if file_path.exists():
                found_files.append(file_path)

        return found_files

    def find_changelog_files(self) -> List[Path]:
        """Find all changelog files"""
        patterns = [
            'CHANGELOG.md', 'CHANGELOG.txt', 'changelog.md', 'changelog.txt',
            'CHANGES.md', 'changes.md', 'HISTORY.md', 'history.md'
        ]

        found_files = []
        for pattern in patterns:
            file_path = Path.cwd() / pattern
            if file_path.exists():
                found_files.append(file_path)

        return found_files

    def smart_task_suggestion(self) -> Optional[Dict]:
        """Get AI-powered task suggestion"""
        if not self.llm.available:
            return None

        # Analyze current project state
        todo_analysis = self.get_smart_todo_analysis()
        project_files = list(Path.cwd().rglob("*.py"))[:10]  # Sample of files

        context = {
            'todo_analysis': todo_analysis,
            'project_files': [str(f) for f in project_files],
            'current_time': datetime.now().isoformat()
        }

        system_prompt = """You are a smart project assistant. Based on the project state, suggest the most important next task.

Consider:
- High priority incomplete tasks
- Blocked dependencies
- Project health
- Best practices

Respond with JSON:
{
  "suggested_task_id": 1,
  "reasoning": "Why this task should be next",
  "estimated_time": "2 hours",
  "potential_blockers": ["blocker1", "blocker2"]
}"""

        prompt = f"""Analyze this project state and suggest the next task:

{json.dumps(context, indent=2)}

Return only JSON, no explanations."""

        result = self.llm.query(prompt, system_prompt)
        if result:
            try:
                json_str = result.strip()
                if json_str.startswith('```'):
                    json_str = '\n'.join(json_str.split('\n')[1:-1])

                suggestion = json.loads(json_str)
                return suggestion
            except:
                pass

        return None


def main():
    controller = IntelligentTaskController()

    if len(sys.argv) == 1:
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "smart_analysis":
        analysis = controller.get_smart_todo_analysis()

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

    elif command == "smart_suggest":
        suggestion = controller.smart_task_suggestion()
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

    elif command == "parse_todo":
        file_path = Path(args[0]) if args else Path("TODO.md")
        tasks = controller.parser.parse_todo(file_path)

        print(f"📋 Parsed TODO from {file_path}:")
        for task in tasks:
            status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            icon = status_icon.get(task['status'], "❓")
            print(f"{icon} #{task['id']} {task['title']}")

    elif command == "parse_changelog":
        file_path = Path(args[0]) if args else Path("CHANGELOG.md")
        entries = controller.parser.parse_changelog(file_path)

        print(f"📝 Parsed Changelog from {file_path}:")
        for entry in entries:
            print(f"📅 {entry['date']}")
            for change in entry['entries']:
                print(f"   - {change['type']}: {change['description']}")

    elif command == "test_llm":
        if controller.llm.available:
            print("🤖 Testing local LLM...")
            result = controller.llm.query("List 3 programming best practices",
                                          "You are a helpful coding assistant.")
            print(f"✅ Response: {result}")
        else:
            print("❌ Local LLM not available")

    elif command == "setup_ollama":
        print("🚀 Setting up Ollama for LLM Task Controller...")
        print("\n1. Install Ollama:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("\n2. Pull a lightweight model:")
        print("   ollama pull llama3.2:3b")
        print("\n3. Start Ollama service:")
        print("   ollama serve")
        print("\n4. Test integration:")
        print("   python3 llmtask.py test_llm")


if __name__ == "__main__":
    main()