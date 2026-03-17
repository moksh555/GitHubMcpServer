# GitHubMcpServer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastMCP](https://img.shields.io/badge/FastMCP-3.1.1%2B-green?logo=fastapi)
![GitHub API](https://img.shields.io/badge/GitHub-REST%20API-black?logo=github)
![License](https://img.shields.io/badge/License-MIT-yellow)
![MCP](https://img.shields.io/badge/Protocol-MCP-purple)

**A Custom GitHub MCP (Model Context Protocol) Server that exposes GitHub API operations as AI-ready tools for LLM agents and applications.**

[Overview](#-overview) • [Features](#-features) • [Installation](#-installation) • [Tools](#-available-mcp-tools) • [Configuration](#-configuration) • [Usage](#%EF%B8%8F-running-the-server)

</div>

---

## 📖 Overview

**GitHubMcpServer** is a lightweight, high-performance MCP server built with [FastMCP](https://github.com/jlowin/fastmcp) that bridges AI models and the GitHub REST API. It allows AI agents (such as Claude, GPT-4, etc.) to interact with GitHub repositories directly — fetching metadata, managing settings, tracking activity, listing and creating repositories — all through a standardized MCP interface over HTTP.

```
┌──────────────────────────┐        ┌───────────────────────────┐
│   AI Agent / LLM Client  │ ──────▶│   GitHubMcpServer         │
│  (Claude, GPT, etc.)     │◀────── │   FastMCP  •  Port 10000  │
└──────────────────────────┘        └──────────────┬────────────┘
                                                   │
                                       ┌───────────▼────────────┐
                                       │   GitHub REST API v3   │
                                       │   api.github.com       │
                                       └────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Get Repository Info** | Fetch detailed metadata for any repository |
| ✏️ **Update Repository Settings** | Modify name, description, visibility, merge strategies & more |
| 📊 **Track Repository Activity** | Query push history, branch changes, merges with filtering |
| 📂 **List All Repositories** | Paginate and sort all user repositories |
| 🆕 **Create Repositories** | Spin up new repos with custom configuration |
| ⚡ **Async & Non-blocking** | Built with `httpx` and `async/await` for high performance |
| 🌐 **CORS Enabled** | Ready for browser-based or cross-origin MCP clients |
| 🔒 **Secure Auth** | Token-based authentication via `.env` file |

---

## 📋 Prerequisites

- **Python 3.10+**
- A **GitHub Personal Access Token (PAT)** with required scopes
- [`uv`](https://github.com/astral-sh/uv) *(recommended)* or `pip`

### Required GitHub Token Scopes

| Scope | Purpose |
|-------|---------|
| `repo` | Full access to public & private repositories |
| `read:user` | Read authenticated user profile data |

> 💡 Generate your token at: **GitHub → Settings → Developer Settings → Personal Access Tokens**

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/moksh555/GitHUbMcpServer.git
cd GitHUbMcpServer
```

### 2. Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install "fastmcp>=3.1.1" httpx pydantic-settings
```

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
GITHUB_ACCESS_TOKEN=ghp_your_personal_access_token_here
OWNER_NAME=your_github_username
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_ACCESS_TOKEN` | ✅ | Your GitHub Personal Access Token |
| `OWNER_NAME` | ✅ | Your GitHub username (repository owner) |

> ⚠️ Never commit your `.env` file to version control. It is already listed in `.gitignore`.

---

## ▶️ Running the Server

```bash
uv run python gitHubMcpServer.py
```

The server starts on **`http://localhost:10000`** using HTTP transport with CORS support.

---

## 🛠️ Available MCP Tools

### `getUserRepo`
Retrieves detailed information for a specific GitHub repository.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repoName` | `string` | ✅ | The name of the repository |

**Returns:** ID, name, URL, privacy status, description, creation/update timestamps, primary language, open issues count.

---

### `updateRepo`
Updates settings for an existing repository. Only provide fields you want to change.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `repoName` | `string` | ✅ Current repository name |
| `name` | `string` | New repository name |
| `description` | `string` | New description |
| `homepage` | `string` | Homepage URL |
| `private` | `bool` | `true` for private, `false` for public |
| `visibility` | `string` | `public` or `private` |
| `has_issues` | `bool` | Enable/disable Issues tab |
| `has_projects` | `bool` | Enable/disable Projects tab |
| `has_wiki` | `bool` | Enable/disable Wiki tab |
| `default_branch` | `string` | Change default branch name |
| `allow_squash_merge` | `bool` | Allow squash merging |
| `archived` | `bool` | Archive the repository |

---

### `getRepoActivity`
Fetches a list of recent activities (pushes, merges, branch changes) for a repository.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `repoName` | `string` | ✅ Repository name |
| `direction` | `string` | `asc` or `desc` |
| `ref` | `string` | Git reference (e.g. `refs/heads/main`) |
| `actor` | `string` | Filter by username |
| `timePeriod` | `string` | `day`, `week`, or `month` |
| `activityType` | `string` | `push`, `force_push`, `branch_creation`, etc. |

**Returns:** Activity ID, user, type, branch, before/after SHA, timestamp.

---

### `geAllUserRepo`
Lists all repositories for the authenticated user with pagination and sorting.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `per_page` | `int` | Results per page (default: 30) |
| `page` | `int` | Page number for pagination |
| `sort` | `string` | Sort by: `created`, `updated`, `pushed`, `full_name` |

---

### `createRepository`
Creates a new GitHub repository under the authenticated user.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `name` | `string` | ✅ Repository name |
| `description` | `string` | Short description |
| `private` | `bool` | `true` for private (default: `false`) |
| `auto_init` | `bool` | Initialize with a README |

---

## 🔌 Connecting an AI Client

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "github": {
      "url": "http://localhost:10000/mcp",
      "transport": "http"
    }
  }
}
```

### Python MCP Client

```python
from mcp import ClientSession
from mcp.client.http import http_client

async with http_client("http://localhost:10000/mcp") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("getUserRepo", {"repoName": "my-repo"})
        print(result)
```

---

## 📁 Project Structure

```
GitHUbMcpServer/
├── gitHubMcpServer.py   # Main MCP server & all tool definitions
├── config.py            # Pydantic settings & .env loader
├── pyproject.toml       # Project metadata & dependencies
├── .python-version      # Python version pin
├── .gitignore           # Git ignore rules
├── uv.lock              # Locked dependency versions
└── README.md            # Project documentation
```

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 👤 Author

**moksh555** · [GitHub Profile](https://github.com/moksh555)

---

<div align="center">

Built with ❤️ using <a href="https://github.com/jlowin/fastmcp">FastMCP</a> & Python

⭐ Star this repo if you find it helpful!

</div>
