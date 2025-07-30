from setuptools import setup, find_packages

setup(
    name="agent-steam",
    version="0.1.2",
    description="A fast framework for building Docker-wrapped AI Agents",
    author="AgentSteam Team", 
    author_email="contact@agentsteam.dev",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "websockets>=12.0",
        "asyncio-mqtt>=0.16.0",
        "click>=8.0.0",
        "jinja2>=3.1.0",
        "rich>=13.0.0",
        "docker>=7.0.0",
        "anthropic>=0.52.0",
        "openai>=1.84.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agent-steam=agent_steam.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)