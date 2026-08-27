# AETHER Contributor & Collaboration Guide

Welcome to the **AETHER** research engineering codebase. This guide establishes the collaboration protocols for our three-person research and engineering team (Project Lead + 2 Research Engineers).

---

## 1. Core Principles & Scientific Integrity

1. **`main` Branch Protection:** The `main` branch represents verified, reproducible research code. Direct pushes to `main` are prohibited for standard development.
2. **Pull Request (PR) Standard:** All code, tests, and configuration changes must enter `main` via reviewed Pull Requests.
3. **CI Gate Mandatory:** All CI automated checks (Ruff linting/formatting, Pytest unit and leakage suites) must pass with 100% green status before any merge.
4. **Peer Review:** Every PR requires approval from at least one other team member.
5. **Zero Silent Scientific Drift:** Any modification to frozen scientific assumptions (split dates, failure labels, benchmark basin lists, normalization definitions) requires explicit documentation in PR descriptions and an updated Architectural Decision Record (ADR).

---

## 2. Branch Naming Conventions

Branches must be created from `main` using the following standardized prefixes:

| Branch Pattern | Purpose | Example |
|:---|:---|:---|
| `feature/<description>` | New algorithmic component or feature extractor | `feature/cqr-engine` |
| `fix/<description>` | Bug fixes or alignment corrections | `fix/lookback-buffer-index` |
| `test/<description>` | Expanding unit, integration, or leakage test suites | `test/causal-leakage-suite` |
| `experiment/<description>` | New experiment runners and benchmark scripts | `experiment/exp001-failure-benchmark` |
| `docs/<description>` | Documentation, ADRs, or reproducibility notes | `docs/adr-001-lightgbm` |

---

## 3. Commit Message Conventions (Conventional Commits)

Commit messages must follow the structured format: `<type>(<scope>): <short description>`

### Allowed Types:
* `feat`: A new feature, pipeline step, or model component
* `fix`: A bug fix or data alignment patch
* `test`: Adding or correcting tests (leakage, unit, integration)
* `refactor`: Code refactoring without changing functional/scientific behavior
* `docs`: Documentation updates, README changes, or ADRs
* `exp`: Experiment configurations and benchmark execution scripts
* `chore`: Dependency updates, tooling, and build configuration

### Examples:
```bash
feat(data): implement CAMELS-US benchmark basin registry loader
test(leakage): add test for lookback window boundary isolation
fix(configs): fix Pydantic Path serialization for YAML export
docs(adr): add ADR-001 documenting LightGBM reliability estimator
exp(001): configure baseline matrix B0 through B7 for Exp 001
```

---

## 4. Pull Request (PR) Workflow

```
1. Create Branch        git checkout -b feature/my-feature
2. Implement & Test     pytest -v && ruff check .
3. Commit               git commit -m "feat(scope): description"
4. Push & Open PR       git push origin feature/my-feature
5. CI & Peer Review     Pass CI + Receive 1 approval
6. Merge (Squash/Merge) Squash and merge into main
```

### PR Description Checklist:
Every PR must state:
- [ ] **Objective:** What scientific or engineering requirement is addressed?
- [ ] **Changes:** Summary of code modified/added.
- [ ] **Tests:** Which pytest tests were executed?
- [ ] **Scientific Impact:** Does this affect any baseline, feature definition, or label? (Yes/No with explanation)
- [ ] **Leakage Check:** Are all causal filtration guarantees preserved?

---

## 5. Development Environment Setup

```bash
# Clone repository
git clone <repo-url>
cd Aether

# Initialize virtual environment with uv
uv venv aethervenv
.\aethervenv\Scripts\activate  # Windows PowerShell

# Install in editable mode with development dependencies
uv pip install -e ".[dev]"

# Verify test suite
pytest -v
ruff check .
```
