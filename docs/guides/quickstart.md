# Quickstart

## 1. Install

```powershell
uv sync
```

## 2. Initialize a project

```powershell
uv run story-harness init --root .\demo --title "Fog Harbor" --genre "Mystery"
```

## 3. Replace the first chapter with tagged prose

Prefer `@{实体}` in Chinese prose:

```markdown
# 第一章

@{林舟}拖着受伤的手臂走进仓库，掌心还在流血。
```

## 4. Run the chapter loop

```powershell
uv run story-harness chapter analyze --root .\demo --chapter-id chapter-001
uv run story-harness chapter suggest --root .\demo --chapter-id chapter-001
uv run story-harness review apply --root .\demo --chapter-id chapter-001 --all-pending --decision accepted
uv run story-harness projection apply --root .\demo --chapter-id chapter-001
uv run story-harness context refresh --root .\demo --chapter-id chapter-001
```

## 5. Inspect machine-facing state

- `demo/reviews/change-requests.yaml`
- `demo/projections/projection.yaml`
- `demo/projections/context-lens.yaml`
