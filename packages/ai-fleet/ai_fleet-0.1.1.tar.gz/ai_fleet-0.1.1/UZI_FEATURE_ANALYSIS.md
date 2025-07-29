# UZI vs AI Fleet: Feature Analysis

## Superior Features in UZI

### 1. **Git Diff Statistics** ⭐⭐⭐
UZI displays real-time git diff stats (+additions/-deletions) directly in the ls output:
```
AGENT    MODEL    STATUS     DIFF        ADDR                PROMPT
agent-1  claude   ready      +42/-15     http://localhost:8080   Fix authentication bug
```

**Why it's better**: Provides immediate feedback on agent productivity without switching contexts.

**Implementation**:
- Temporarily stages all changes with `git add -A`
- Runs `git diff --cached --shortstat HEAD`
- Resets staging area
- Non-destructive way to see work progress

### 2. **Auto Mode (Hands-Free Operation)** ⭐⭐⭐
UZI has a sophisticated `uzi auto` command that monitors all agent sessions and automatically responds to prompts:
- Detects trust prompts ("Do you trust the files in this folder?")
- Detects continuation prompts ("Press Enter to continue")
- Automatically presses Enter when needed
- Uses content hashing to detect changes
- Runs continuously with graceful shutdown

**Why it's better**: Enables truly unattended operation of multiple agents, removing friction from the development workflow.

### 3. **Broadcast & Run Commands** ⭐⭐⭐
UZI can execute commands across all active agents:
- `uzi broadcast <message>`: Send a message to all agents
- `uzi run <command>`: Execute shell commands in all agent sessions
- Supports creating temporary windows for command execution

**Why it's better**: Powerful for coordinating multiple agents or gathering information from all sessions at once.

### 4. **Checkpoint/Rebase Workflow** ⭐⭐⭐
UZI's `checkpoint` command rebases agent changes back to your current branch:
```bash
uzi checkpoint <agent-name> "commit message"
```
- Commits changes in agent worktree
- Rebases agent branch onto current branch
- Effectively "merges" agent work into main workflow

**Why it's better**: Streamlined workflow for integrating agent work without manual git operations.

### 5. **Multi-Agent Spawning with Flexible Configuration** ⭐⭐
UZI can spawn multiple agents with different models in one command:
```bash
uzi prompt --agents=claude:2,gpt:3,random:1 "implement feature X"
```
- Spawn multiple instances of each model
- Support for "random" to get random agent names
- Configurable agent commands

**Why it's better**: Perfect for comparing different models or parallelizing work across multiple agents.

### 6. **Dev Server Integration with Port Management** ⭐⭐
UZI automatically spawns dev servers for each agent:
- Configurable dev command template (e.g., `npm run dev -- --port $PORT`)
- Automatic port allocation from configured range
- Each agent gets its own dev server instance
- Port tracking in state for web UI access

**Why it's better**: Each agent can have its own isolated development environment with live preview.

### 7. **Human-Friendly Agent Names** ⭐
UZI uses a curated list of ~100 human names for agents (john, emily, michael, etc.) instead of generic identifiers.

**Why it's better**: More memorable and easier to reference in conversation ("john is working on auth, emily on UI").

### 8. **Global State Management with Repo Filtering** ⭐
UZI uses a single global state file (`~/.local/share/uzi/state.json`) that tracks agents across ALL repositories, filtering by GitRepo field.

**Why it's better**:
- See all your agents across projects with `uzi ls -a`
- Better for developers working on multiple repos simultaneously
- Centralized agent management

### 9. **Model Tracking and Display** ⭐
UZI stores and displays which AI model each agent is using in the ls output.

**Why it's better**: Essential for comparing performance across different models or when using multiple AI providers.

### 10. **Prompt Storage and Display** ⭐
UZI shows the original prompt in the ls output, giving instant context about what each agent is working on.

**Why it's better**: No need to remember or check logs to know what task each agent is handling.

### 11. **UpdatedAt Tracking with Smart Sorting** ⭐
UZI tracks both CreatedAt and UpdatedAt timestamps, sorting agents by most recently active first.

**Why it's better**:
- See which agents are actively working vs stale
- Better workflow for resuming work
- Natural ordering for active development

## Features Better in AI Fleet

### 1. **Project-Isolated State**
AI Fleet's `.aifleet/state.json` keeps agent state with the project.

**Why it's better**:
- Better for teams (state travels with repo)
- Clear project boundaries
- No cross-project pollution

### 2. **Batch Operations**
AI Fleet has stronger batch management with dedicated batch IDs and operations.

### 3. **Process Statistics**
AI Fleet shows CPU and memory usage per agent using psutil.

### 4. **Python Ecosystem**
Easier to extend and integrate with Python-based AI tools.

### 5. **Update Command**
AI Fleet has a built-in update mechanism (`fleet update`).

## Key Architectural Differences

### Go vs Python
- **UZI (Go)**: Faster execution, single binary, better for system-level operations
- **AI Fleet (Python)**: Easier to extend, better library ecosystem, more accessible to contributors

### State Philosophy
- **UZI**: Global state with repo filtering - optimized for individual developers
- **AI Fleet**: Project-local state - optimized for team collaboration

### tmux Integration
- **UZI**: Direct subprocess calls - more control, better performance
- **AI Fleet**: libtmux library - more Pythonic, better abstraction

## Recommendations for AI Fleet

### Critical Features to Add (High Impact):
1. **Auto mode** - Hands-free operation is a game-changer
2. **Git diff stats** - Immediate productivity feedback
3. **Checkpoint/rebase workflow** - Streamline agent integration
4. **Broadcast/run commands** - Coordinate multiple agents

### High Priority Additions:
1. **Multi-agent spawning** - Launch multiple agents with different models
2. **Model tracking** - Essential for multi-model workflows
3. **Prompt display** - Critical context in list view
4. **UpdatedAt timestamps** - Better activity tracking
5. **Human-friendly names** - Better UX for referencing agents

### Medium Priority:
1. **Dev server integration** - Isolated development environments
2. **Global state option** - Add `--global` flag for cross-repo view
3. **Direct tmux commands** - For performance-critical operations

### Design Decisions to Consider:
1. **Hybrid state management**: Keep project-local by default but add global view option
2. **Plugin architecture**: Allow extending with custom commands like UZI's modularity
3. **Model detection**: Auto-detect from claude CLI or agent output
4. **Configurable columns**: Let users choose what to display in ls output