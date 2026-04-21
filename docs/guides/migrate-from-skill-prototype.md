# Migrate From Skill Prototype

The current skill prototype lives at:

```text
~/.codex/skills/story-harness-writing
```

Migration goal:

1. keep the protocol
2. keep the command contract
3. move the core execution logic into this standalone repository
4. leave the skill as a thin adapter later

The first repository version intentionally keeps Python and stdlib-only behavior so the migration stays shallow and testable.
