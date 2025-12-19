# Claude Agents Crew
Crew of claude agents for project automation and task orchestration.
Focussed on software engineering tasks.

### Quick start

```bash
chmod +x sync-subagents.sh
./sync-subagents.sh
```

### Examples

* Sync to chosen target (interactive):

```bash
./sync-subagents.sh
```

* Dry run:

```bash
./sync-subagents.sh --dry-run
```

* Mirror exactly (delete removed agents from target):

```bash
./sync-subagents.sh --delete
```

* Non-interactive:

```bash
./sync-subagents.sh --yes
```
