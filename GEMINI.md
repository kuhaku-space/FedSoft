## 開発環境 (Development Environment)

このプロジェクトでは、ツール管理に **mise**、Python のパッケージ管理に **uv** を使用しています。

- **Tool Manager:** [mise](https://mise.jdx.description/)
- **Python Package Manager:** [uv](https://github.com/astral-sh/uv)
- **Configuration Files:** `mise.toml`, `pyproject.toml`, `uv.lock`

## コーディング・実行ルール

1. **ツールの実行:**
   - ツール（uv, python, ruff 等）を実行する際は、原則として `mise exec -- <command>` を使用してください。
   - 例: `mise exec -- uv sync`
2. **Python スクリプトの実行:**
   - Python を実行する場合は、uv で作成された仮想環境を利用するため `uv run` を優先してください。
   - 例: `mise exec -- uv run main.py`
3. **パッケージの追加・更新:**
   - パッケージをインストールする際は `uv add <package>` を提案してください。
4. **タスク実行:**
   - `mise.toml` の `[tasks]` に定義されたタスクがある場合は、`mise run <task>` を優先してください。
