"""FastAPI entrypoint for the budget web app."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    """Return the web app landing text."""
    return "<h1>가계부 웹</h1>"


def main() -> None:
    """Run the app with uvicorn."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
