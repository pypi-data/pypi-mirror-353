#!/usr/bin/env python3
"""
Setup script for TaskGuard - LLM Task Controller
Legacy setup.py for backward compatibility
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys

# Ensure Python 3.8+
if sys.version_info < (3, 8):
    sys.exit("TaskGuard requires Python 3.8 or higher")

# Read README for long description
here = Path(__file__).parent
readme_file = here / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "🧠 LLM Task Controller with Local AI Intelligence"


# Read version from package
def get_version():
    version_file = here / "src" / "taskguard" / "__init__.py"
    if version_file.exists():
        with open(version_file, "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split('"')[1]
    return "0.2.0"


# Core dependencies
install_requires = [
    "pyyaml>=6.0",
    "requests>=2.25.0",
    # Backward compatibility for older Python versions
    "pathlib2>=2.3.0;python_version<'3.4'",
    "typing-extensions>=4.0.0;python_version<'3.8'",
]

# Optional dependencies
extras_require = {
    # Development tools
    "dev": [
        "pytest>=7.0",
        "pytest-cov>=4.0",
        "black>=22.0",
        "isort>=5.0",
        "flake8>=5.0",
        "mypy>=1.0",
        "pre-commit>=2.0",
        "tox>=4.0",
    ],

    # LLM integrations
    "llm": [
        "ollama-python>=0.1.0",
        "openai>=1.0.0",
        "anthropic>=0.3.0",
    ],

    # Security tools
    "security": [
        "bandit>=1.7.0",
        "safety>=2.0.0",
        "semgrep>=1.0.0",
    ],

    # Documentation
    "docs": [
        "mkdocs>=1.4.0",
        "mkdocs-material>=8.0.0",
        "mkdocstrings[python]>=0.19.0",
    ],
}

# Add convenience 'all' extra
extras_require["all"] = [
    item for sublist in extras_require.values()
    for item in sublist
]

setup(
    # Basic metadata
    name="taskguard",
    version=get_version(),
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    maintainer="WRONAI Team",
    maintainer_email="team@wronai.com",

    # Package description
    description="🧠 LLM Task Controller - Intelligent project management with local AI",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # URLs
    url="https://github.com/wronai/taskguard",
    project_urls={
        "Homepage": "https://github.com/wronai/taskguard",
        "Documentation": "https://taskguard.readthedocs.io",
        "Repository": "https://github.com/wronai/taskguard.git",
        "Bug Reports": "https://github.com/wronai/taskguard/issues",
        "Feature Requests": "https://github.com/wronai/taskguard/discussions",
        "Changelog": "https://github.com/wronai/taskguard/blob/main/CHANGELOG.md",
    },

    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Include package data
    package_data={
        "taskguard": [
            "config/*.yaml",
            "templates/*.md",
            "scripts/*.sh",
        ],
    },
    include_package_data=True,

    # Python requirements
    python_requires=">=3.8",

    # Dependencies
    install_requires=install_requires,
    extras_require=extras_require,

    # Console scripts
    entry_points={
        "console_scripts": [
            "taskguard=taskguard.cli:main",
            "tg=taskguard.cli:main",
            "llmtask=taskguard.cli:main",
        ],
    },

    # PyPI classifiers
    classifiers=[
        # Development status
        "Development Status :: 4 - Beta",

        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",

        # Topic classification
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",

        # License
        "License :: OSI Approved :: Apache Software License",

        # Programming language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",

        # Operating system
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",

        # Environment
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",

        # Natural language
        "Natural Language :: English",

        # Framework
        "Framework :: AsyncIO",
    ],

    # Keywords for discovery
    keywords=[
        "llm", "task-management", "ai", "productivity", "development",
        "best-practices", "ollama", "local-ai", "focus", "automation",
        "code-quality", "safety", "monitoring", "intelligence", "control"
    ],

    # Platforms
    platforms=["any"],

    # License
    license="Apache-2.0",

    # Additional metadata
    zip_safe=False,

    # Test configuration
    test_suite="tests",
    tests_require=[
        "pytest>=7.0",
        "pytest-cov>=4.0",
    ],

    # Custom commands
    cmdclass={},

    # Distribution options
    options={
        "build_scripts": {
            "executable": "/usr/bin/env python3",
        },
        "egg_info": {
            "tag_build": "",
            "tag_date": False,
        },
    },
)

# Post-installation message
print("""
🧠 TaskGuard Installation Complete!

🚀 Quick Start:
   1. taskguard init                    # Initialize project
   2. taskguard setup ollama           # Setup local AI
   3. taskguard show-tasks             # View tasks
   4. taskguard start-task 1           # Start working

📚 Documentation: https://github.com/wronai/taskguard
🤖 Support: https://github.com/wronai/taskguard/issues

Happy intelligent development! 🎯
""")