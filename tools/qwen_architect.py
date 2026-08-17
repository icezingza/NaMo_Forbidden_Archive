"""
Qwen Architect - Code Refactoring, Analysis & Test Generation CLI Tool
Uses Qwen 2.5 Coder via OpenAI-compatible DashScope API.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

DEFAULT_BASE_URL = os.getenv(
    "QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
DEFAULT_MODEL = os.getenv("QWEN_MODEL", "qwen2.5-coder-32b-instruct")


def get_api_key() -> str:
    key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        print(
            "[Error]: Missing API key! Please set DASHSCOPE_API_KEY or QWEN_API_KEY environment variable.",
            file=sys.stderr,
        )
        print("Example: $env:DASHSCOPE_API_KEY='sk-...' or set it in .env file.", file=sys.stderr)
        sys.exit(1)
    return key


def analyze_code(
    file_path: str, instruction: str, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL
) -> str:
    path = Path(file_path)
    if not path.exists():
        print(f"[Error]: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    code_content = path.read_text(encoding="utf-8", errors="replace")
    api_key = get_api_key()

    system_prompt = (
        "You are Qwen 2.5 Coder, an expert senior AI software architect. "
        "Your task is to analyze code, provide high-quality refactoring, detect bugs/security issues, "
        "or generate comprehensive test suites in Python / TypeScript based strictly on user instructions. "
        "Keep your output clean, precise, and practical."
    )

    user_prompt = (
        f"Target File: {file_path}\n\n```\n{code_content}\n```\n\nInstruction: {instruction}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    print(f"[*] Analyzing '{file_path}' using {model}...")
    with httpx.Client(timeout=90.0) as client:
        res = client.post(f"{base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
        if res.status_code != 200:
            print(f"[Error {res.status_code}]: {res.text}", file=sys.stderr)
            sys.exit(1)
        data = res.json()
        return data["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(
        description="Qwen Architect - AI Code Assistant for NaMo Project"
    )
    parser.add_argument("file", help="Path to the file to analyze or improve")
    parser.add_argument(
        "instruction",
        help="Instruction (e.g. 'Add unit tests', 'Find security vulnerabilities', 'Refactor for speed')",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API Base URL")
    parser.add_argument("--output", "-o", help="Optional output file path to save the result")

    args = parser.parse_args()
    result = analyze_code(args.file, args.instruction, model=args.model, base_url=args.base_url)

    print("\n" + "=" * 50)
    print(result)
    print("=" * 50 + "\n")

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(result, encoding="utf-8")
        print(f"[+] Result successfully saved to: {args.output}")


if __name__ == "__main__":
    main()
