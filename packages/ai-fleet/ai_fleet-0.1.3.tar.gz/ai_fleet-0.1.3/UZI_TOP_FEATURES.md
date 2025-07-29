# Top UZI Features AI Fleet Should Implement

## 1. Auto Mode - The Game Changer 🚀
```bash
fleet auto  # Monitors all agents and auto-responds to prompts
```
- **Impact**: Removes biggest friction point - manually pressing Enter
- **Use Case**: Running overnight batches, unattended workflows
- **Implementation**: Monitor pane content, detect prompts, send Enter key

## 2. Git Diff Stats in List View 📊
```
BRANCH      BATCH    AGENT   STATUS    DIFF        CPU%   MEM    UPTIME
feature-x   abc123   claude  running   +142/-23    12.3   245    15m
```
- **Impact**: Instant productivity feedback without context switching
- **Use Case**: Quickly see which agents are making progress
- **Implementation**: Non-destructive git add/diff/reset per worktree

## 3. Checkpoint Command 🔀
```bash
fleet checkpoint feature-x "Implemented user authentication"
```
- **Impact**: Streamlines integration of agent work
- **Use Case**: Pull agent changes into main branch with one command
- **Implementation**: Commit in worktree, then rebase onto current branch

## 4. Broadcast/Run Commands 📢
```bash
fleet broadcast "Please focus on test coverage"
fleet run "git status"  # Runs in all agent sessions
```
- **Impact**: Coordinate multiple agents efficiently
- **Use Case**: Redirect agents, gather status, run diagnostics
- **Implementation**: Send keys to all active tmux sessions

## 5. Multi-Model Agent Spawning 🤖
```bash
fleet fanout --models claude:2,gpt4:1 "Implement search feature"
```
- **Impact**: Compare model performance, leverage different strengths
- **Use Case**: A/B testing approaches, model-specific tasks
- **Implementation**: Extend fanout to support model specification

## Quick Wins (Easy to Implement)

### Prompt Display in List
Show what each agent is working on directly in the list view.

### Human-Friendly Names
Replace `claude-1`, `claude-2` with `emily`, `john`, etc.

### UpdatedAt Timestamps
Track and sort by last activity, not just creation time.

### Model Tracking
Store and display which AI model each agent uses.

## Priority Matrix

```
High Impact + Easy: Git diff stats, Prompt display, UpdatedAt
High Impact + Medium: Auto mode, Checkpoint command
High Impact + Hard: Multi-model spawning
Medium Impact + Easy: Human names, Model tracking
Medium Impact + Medium: Broadcast/Run commands
```

## Next Steps
1. Start with git diff stats (high value, straightforward)
2. Add auto mode (biggest UX improvement)
3. Implement checkpoint workflow (developer efficiency)
4. Extend with broadcast/run for fleet management