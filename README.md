# Team Attention Plugins

Claude Code plugin marketplace for enhanced developer workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add team-attention/agents
```

## Available Plugins

### interactive-review

Interactive markdown review with web UI. Review plans and documents with checkbox approvals and inline comments.

```bash
/plugin install interactive-review@team-attention-plugins
```

**Features:**
- Visual review UI in browser
- Checkbox approvals for each section
- Inline comments
- Keyboard shortcuts (`Cmd+Enter` to submit)

**Usage:** Say "review this" or use `/review` after Claude generates a plan.

## Directory Structure

```
.claude-plugin/
└── marketplace.json         # Marketplace manifest

plugins/
└── interactive-review/      # Interactive review plugin
    ├── .claude-plugin/
    │   └── plugin.json      # Plugin manifest
    ├── skills/
    │   └── review/
    │       └── SKILL.md     # Review skill definition
    ├── mcp-server/
    │   ├── server.py        # MCP server
    │   ├── web_ui.py        # HTML generator
    │   └── requirements.txt # Python dependencies
    ├── .mcp.json            # MCP configuration
    └── README.md            # Plugin documentation
```

## Development

Test plugins locally:

```bash
claude --plugin-dir ./plugins/interactive-review
```

## Requirements

- Claude Code CLI
- Python 3.9+ (for interactive-review plugin)
- `mcp` package: `pip install mcp`
