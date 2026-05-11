# Development Workflow

## Branch Strategy

This coursework uses a lightweight GitHub Flow:

- `main` contains stable, verified coursework code.
- `feature/high-score-workflow` documents the professional workflow and research basis.
- `feature/test-quality-gates` strengthens automated testing and CI.
- `feature/advanced-ranking` adds TF-IDF, BM25, explain, and benchmark features using TDD.
- `feature/evidence-and-coverage` expands evidence and coverage.
- `feature/extreme-case-hardening` covers malformed input and empty benchmark cases.
- `feature/algorithm-comparison-evidence` adds benchmark comparison evidence.
- `feature/release-quality-hardening` records engineering practice and release quality.
- `feature/readme-open-source-polish` improves the repository entrypoint.
- `feature/documentation-tone-review` checks project documentation tone and modern search practice evidence.
- `release/v1.0.0` is used for final release checks, index refresh, and tag preparation.

Each feature branch is merged back with a merge commit so the branch history remains visible in `git log --graph --decorate --all`.

## Semantic Commits

Commit messages follow Conventional Commits:

- `docs:` documentation and coursework evidence.
- `test:` automated tests and fixtures.
- `feat:` user-facing functionality.
- `perf:` benchmark and performance-related work.
- `ci:` automated test pipeline.
- `fix:` defect fixes.
- `data:` generated index file.

This makes the development history easy to explain in the video and demonstrates incremental work across separate commits.

## TDD Workflow

Algorithm and CLI behavior changes follow test-driven development:

1. Write a failing test for the intended behavior.
2. Run the narrow test and confirm it fails for the expected reason.
3. Implement the smallest code change that passes the test.
4. Run the narrow test again.
5. Run the full suite with coverage.
6. Commit tests separately from implementation when the history benefits from showing the red-green order.

The advanced ranking branch intentionally commits ranking tests before the ranking implementation to make the TDD process visible.

## Quality Gates

Before merging or tagging a release, run:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
python3 -m compileall src tests
python3 -m src.main load
python3 -m src.main print nonsense
python3 -m src.main find good friends
```

The local target is at least 90% coverage, with the current project aiming higher. The CI workflow runs the same test and compile checks automatically.

## Release Process

Major submission checkpoints use release tags:

1. Re-run the full verification suite.
2. Refresh `data/index.json` with `python3 -m src.main build`.
3. Update `README.md`, `docs/VIDEO_SCRIPT.md`, and `docs/BENCHMARKS.md`.
4. Merge the feature or release branch into `main`.
5. Tag the checkpoint:

```bash
git tag -a v1.0.6 -m "Release documentation tone review"
```

This provides explicit evidence for branch strategy, semantic commits, and a release tag.
