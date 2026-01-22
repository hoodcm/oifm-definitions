# CLAUDE.md

Claude Code instructions for this repository.

## 1. Project Overview

**Purpose**: Python library for Open Imaging Finding Models (OIFM) with AI-assisted authoring.

**Primary Workflow**: Stage OIFM codes from radiology observation lists.

- Observation lists live in `findingmodels/lists/` (e.g., Hood curated CXR findings)
- Python tools expand observations into OIFM definitions
- Definitions stored in `findingmodels/defs/` as `.fm.json` files

**Core Stack**: uv, Taskfile, Pydantic v2, OpenAI/Anthropic AI tooling, DuckDB search.

**Layout**:

- `src/findingmodel/` - Python library (models, tools, config, CLI)
- `findingmodels/` - OIFM definitions, schemas, observation lists
- `test/` - pytest unit tests
- `evals/` - AI quality evaluation suites
- `docs/context/` - Project context files (conventions, architecture notes)

## 2. Coding Standards

- **Formatting**: Ruff (120 char lines, preview mode). Run `task check` before committing.
- **Typing**: Annotate everything, prefer `Annotated`/`Field` for constraints.
- **Naming**: snake_case functions/vars, PascalCase classes, UPPER_SNAKE constants.
- **OIFM IDs**: Pattern `OIFM_{SOURCE}_{6_DIGITS}` (e.g., `OIFM_MSFT_123456`).
- **YAGNI**: Implement only what is required now.

## 3. Development Commands

```bash
task test          # unit tests (fast, no API)
task test-full     # integration tests (includes API calls)
task evals         # run all AI evaluation suites
task check         # format + lint + mypy
task build         # package build
```

## 4. Testing Structure

1. **Unit Tests** (`test/test_*.py`) - Verify logic with mocked dependencies
2. **Integration Tests** (`@pytest.mark.callout`) - Verify wiring with real APIs
3. **Evals** (`evals/*.py`) - Assess AI agent quality (0.0-1.0 scores)

## 5. Security

- Keep API keys in `.env`; never commit them.
- Required: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (or both)
- Optional: `TAVILY_API_KEY` for enhanced search

## 6. Workflow Notes

- Prefer programmatic solutions before invoking LLMs.
- See `docs/context/` for detailed architecture and conventions.

### CHANGELOG Updates (Required)

**After every major action**, update `CHANGELOG.md`:

- Add entries under `## [Unreleased]` section
- Use format: `- **Feature/Change Name** (YYYY-MM-DD): Description`
- Categories: Added, Changed, Deprecated, Removed, Fixed
- Include date with each significant entry
- Keep entries concise but descriptive

## 7. Related Documentation

For finding model content work (adding/editing `.fm.json` definitions, validation), see [findingmodels/CLAUDE.md](findingmodels/CLAUDE.md).

---

**IMPORTANT**: Do NOT commit without checking in first, especially with a proposed commit message.
