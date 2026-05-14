# PDF Bot Architecture

## Goals

- Mention-prefixed invocation only through `@pdf`
- Async-first execution with no blocking work on the event loop
- Session isolation by `(chat_id, user_id)`
- Queue-based PDF processing with retries and cancellation
- Production-ready logging, cleanup, and deployment

## Core Flow

1. Telegram message arrives.
2. `handlers/router_handler.py` routes only text that can be parsed by `core/prefix_parser.py`.
3. `core/command_router.py` validates middleware, resolves the command, and dispatches it.
4. `handlers/pdf_handler.py` creates or resumes an isolated session.
5. `core/task_manager.py` pushes the job to an async queue and worker pool.
6. `services/dispatcher.py` maps the logical service to the PDF implementation.
7. `services/*` performs the actual work using `asyncio.to_thread()` for CPU-heavy operations.
8. Results are uploaded back to Telegram and temporary files are cleaned up.

## Major Components

### Command Engine

- `core/prefix_parser.py`
- `core/command_router.py`
- `handlers/router_handler.py`

Responsibilities:

- Parse mention-style activation.
- Validate the prefix token.
- Resolve `merge`, `split`, `compress`, `extract`, `ocr`, `queue`, `settings`, `lang`, `cancel`, and `help`.
- Keep group chats quiet unless the bot is explicitly addressed.

### Session System

- `core/session_manager.py`
- `handlers/pdf_handler.py`

Responsibilities:

- Key sessions by `(chat_id, user_id)`.
- Track per-user flow state and pending inputs.
- Prevent cross-user collisions in groups and supergroups.

### Queue and Workers

- `core/task_manager.py`
- `workers/`

Responsibilities:

- Async queue with worker pool.
- Timeout and retry policy.
- Progress updates and cancellation hooks.
- Redis-ready boundary: queue abstraction can be replaced later without changing handlers.

### OCR and PDF Services

- `services/extract_service.py`
- `services/merge_service.py`
- `services/split_service.py`
- `services/compress_service.py`
- `services/security_service.py`
- `services/convert_service.py`

Responsibilities:

- PDF manipulation, OCR, extraction, conversion, and secure transformations.
- Heavy operations run off-thread.
- OCR preprocessing uses OpenCV when available.

### Database

- `database/db.py`
- `repositories/`
- `models/`

Responsibilities:

- SQLite today through `aiosqlite`.
- Repository pattern keeps storage replaceable.
- PostgreSQL migration can be added behind the same interface.

### Middleware and Security

- `core/middleware.py`
- `middleware/`
- `services/security_service.py`

Responsibilities:

- Rate limiting.
- Ban checks.
- File and resource safety.
- Defensive handling for malformed PDFs and dangerous inputs.

### Deployment

- `Dockerfile`
- `docker-compose.yml`
- `Procfile`
- `.env.example`

Responsibilities:

- Python 3.11 runtime.
- Tesseract and language packs.
- Repeatable local and container deployment.
- Environment-driven configuration.

## Operational Rules

- Do not respond to ordinary messages.
- Do not use slash commands in group flows.
- Only route messages that activate with `@pdf`.
- Keep uploads and processing replies scoped to the caller.
- Clean temporary files automatically.

## Production Optimizations

- `asyncio.to_thread()` for CPU-heavy code.
- Structured logging with rotation.
- Queue-based backpressure.
- Safe temp filenames via UUIDs.
- Optional OCR toggle through environment settings.
- Ready for future Redis-backed queue and PostgreSQL persistence.
