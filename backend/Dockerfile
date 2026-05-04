FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 依存関係のみ先にインストール（レイヤキャッシュ最大化）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# アプリ本体
COPY . .
RUN uv sync --frozen --no-dev

# venv の bin を PATH に通す（uvicorn を直接起動するため）
ENV PATH="/app/.venv/bin:$PATH"

# Cloud Run はポート8080を使用
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
