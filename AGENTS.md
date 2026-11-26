# Repository instructions: Agent设计模式课程

## Source of truth
- Follow `docs/00_课程内容生成规范.md` and the style established by Chapters 1–3.
- Preserve approved content. Do not rewrite, expand, or alter unrelated files unless explicitly requested.
- Do not append chapter exercises by default.

## Workflow
- For new chapter text, produce the draft first and wait for approval.
- Do not automatically create PPTs, demos, exercises, or commit changes before the user asks or approves the next stage.
- After approval, create chapter-aligned demos and README; self-check, and test where feasible.
- Only sync GitHub when requested. Verify actual files and commit details before reporting.

## Teaching content
- Keep explanations systematic: context, concepts, mechanisms, execution flow, architecture, code, practical applications, engineering considerations, summary and optional further reading as appropriate.
- Add useful Mermaid diagrams where they improve understanding; explain them and keep them consistent with prose and code.
- Avoid repetitive filler, unsupported technical claims, and scope creep.

## Code
- Python is the default for Agent demos unless the chapter specifies otherwise.
- Every Python module and textbook Python snippet must contain explanatory comments for functions and key logic.
- Keep examples readable and demonstration-focused; avoid unnecessary abstraction, excessive validation, or unrelated dependencies.
- Clearly label simulated or simplified behavior.
- Use DeepSeek via OpenAI-compatible client and python-dotenv by default:
  ```python
  import os
  from dotenv import load_dotenv
  from openai import OpenAI

  load_dotenv()

  client = OpenAI(
      api_key=os.getenv("DEEPSEEK_API_KEY"),
      base_url="https://api.deepseek.com/v1"
  )

  MODEL = os.getenv("DEEPSEEK_MODEL")
  ```
- Never hardcode API keys or model names. Provide `.env.example`; exclude real `.env` from Git.
- Prefer standalone modules with direct client setup unless modularization is part of the lesson.

## Structure
- Textbooks: `docs/`
- Demo code: `examples/chapterXX/`
- Each demo chapter should include a README describing setup, environment variables, run commands, and modules.
- Follow existing naming and repository conventions; do not relocate or delete unrelated files.

## Quality and reporting
- Check alignment between chapter text, diagrams, code, and README.
- Perform syntax checks or runtime tests where feasible; distinguish what was actually tested.
- Never claim tests succeeded unless executed.
