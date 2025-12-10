# Marco - Habit Tracker Project Guide

This document provides guidance for AI assistants (like Claude) working on the Marco habit tracker application.

## Project Overview

Marco is a full-stack habit tracking application that helps users build and maintain daily routines. The project consists of:
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: SvelteKit 2.0 + Svelte 5 (with Runes) + Tailwind CSS 4
- **Language**: Spanish (UI text and comments)

## Project Structure

```
marco/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI entry point with CORS
│   │   ├── config.py         # App configuration
│   │   ├── database.py       # Async SQLite connection
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic v2 schemas
│   │   └── routers/          # API endpoints
│   │       ├── usuarios.py
│   │       ├── categorias.py
│   │       ├── habitos.py
│   │       ├── registros.py
│   │       └── habito_dias.py
│   ├── pyproject.toml        # UV dependencies
│   └── app.db                # SQLite database
│
└── frontend/          # SvelteKit frontend
    ├── src/
    │   ├── lib/
    │   │   ├── api.ts                # API client
    │   │   └── components/           # Reusable components
    │   └── routes/                   # SvelteKit routes
    │       ├── +page.svelte          # Daily progress view
    │       ├── +layout.svelte        # Main layout with nav
    │       ├── habitos/              # Habit management
    │       ├── charts/               # Visualizations
    │       ├── progreso/             # Progress details
    │       └── settings/             # User settings
    ├── package.json
    ├── svelte.config.js
    └── vite.config.ts
```

## Technology Stack

### Backend
- Python 3.12+
- FastAPI (web framework)
- SQLAlchemy (async ORM with aiosqlite)
- Pydantic v2 (data validation)
- Uvicorn (ASGI server)
- UV package manager

### Frontend
- SvelteKit 2.0
- Svelte 5 with Runes (`$state`, `$effect`, `$derived`)
- Tailwind CSS 4
- TypeScript
- Vite 6

### Database
- SQLite (app.db)
- Tables: usuarios, categorias, habitos, registros, progreso_habitos

## Key Features

1. **Habit Management**: Create, edit, delete habits with colors and weekly schedules
2. **Daily Tracking**: Mark habits complete, record values, view progress
3. **Progress Visualization**: Animated progress bar with neon gradient effect when 100% complete
4. **Date Navigation**: Navigate between days to review history
5. **Future Lock**: Option to disable viewing/editing future dates
6. **Cascading Deletes**: Deleting a habit removes all associated records

## Development Commands

### Backend
```bash
cd backend
uv sync                                      # Install dependencies
uv run uvicorn app.main:app --reload --port 8000   # Start dev server
```
- Backend runs on: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

### Frontend
```bash
cd frontend
pnpm install              # Install dependencies
pnpm dev                  # Start dev server
pnpm build                # Build for production
```
- Frontend runs on: http://localhost:5173

## Code Conventions

### Backend
- Use async/await for all database operations
- Follow FastAPI dependency injection patterns
- Use Pydantic v2 schemas for validation
- CORS enabled for frontend communication
- Spanish naming for API responses and error messages

### Frontend
- Use Svelte 5 Runes syntax (`$state`, `$effect`, `$derived`)
- TypeScript for type safety
- Tailwind CSS for styling (utility-first approach)
- Spanish text for all UI elements
- API calls through centralized `lib/api.ts`

### Styling
- Dark theme with colors:
  - Background: `#0E0D0D`
  - Border: `#533483`
  - Accent: `#e94560`
  - Success: `#00ff88`
  - Text: `#FFFFFF` / `#A0A0A0`
- Smooth animations and transitions
- Responsive design (mobile-first)

## Database Schema

Key relationships:
- `usuarios` → `habitos` (one-to-many)
- `usuarios` → `registros` (one-to-many)
- `categorias` → `habitos` (one-to-many)
- `registros` → `progreso_habitos` (one-to-many)
- `habitos` → `progreso_habitos` (one-to-many)

Important fields:
- `habitos.dias`: String of day letters (e.g., "LMXJVSD")
- `habitos.color`: Hex color code for UI
- `usuarios.ver_futuro`: Boolean to allow/block future dates
- `progreso_habitos.completado`: Boolean completion status

## Common Tasks

### Adding a New API Endpoint
1. Define Pydantic schemas in `backend/app/schemas.py`
2. Create router function in appropriate file under `backend/app/routers/`
3. Use async database sessions
4. Add endpoint to router in `backend/app/main.py` if new router file
5. Test at http://127.0.0.1:8000/docs

### Adding a New Frontend Page
1. Create `+page.svelte` in `frontend/src/routes/[route-name]/`
2. Use Svelte 5 Runes for state management
3. Import API functions from `lib/api.ts`
4. Style with Tailwind CSS
5. Add navigation link in `+layout.svelte` if needed

### Working with the Database
- Direct SQLite access: View `backend/app.db` with SQLite browser
- Migrations: Not currently using Alembic (direct schema changes)
- Reset database: Delete `app.db` and restart backend (auto-creates tables)

## Important Notes

- **No Git Repository**: Project currently has `.git` folder but not actively using version control
- **Single User**: Currently designed for single-user local use
- **Spanish Language**: All UI text, comments, and user-facing content in Spanish
- **Modern Stack**: Uses latest versions (Svelte 5, Tailwind 4, FastAPI, Pydantic v2)
- **Animations**: Heavy use of CSS transitions and Svelte transitions

## API Patterns

All endpoints follow RESTful conventions:
- `GET /api/{resource}/` - List all
- `GET /api/{resource}/{id}` - Get by ID
- `POST /api/{resource}/` - Create
- `PUT /api/{resource}/{id}/` - Update
- `DELETE /api/{resource}/{id}` - Delete

Special endpoints:
- `GET /api/habitos/usuario/{usuario_id}` - Get user's habits
- `GET /api/registros/usuario/{usuario_id}/fecha/{fecha}` - Get/create daily record

## Testing

Currently no automated tests. Manual testing through:
- FastAPI Swagger UI: http://127.0.0.1:8000/docs
- Browser interface: http://localhost:5173

## Known Limitations

- Single-user application (no authentication)
- No real-time sync (refresh required)
- SQLite (not suitable for high concurrency)
- No data export/import functionality
- No backup mechanism

## When Making Changes

1. **Backend changes**: Restart uvicorn server to apply
2. **Frontend changes**: Hot module reload (HMR) enabled
3. **Schema changes**: May require database recreation
4. **New dependencies**: Run `uv sync` (backend) or `pnpm install` (frontend)

## Design Philosophy

- **Simplicity**: Keep features focused and intuitive
- **Visual Appeal**: Smooth animations and modern dark theme
- **Performance**: Async operations, minimal re-renders
- **User Experience**: Clear feedback, confirmation modals for destructive actions
- **Maintainability**: Clean separation of concerns, typed interfaces

## Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com
- SvelteKit Docs: https://kit.svelte.dev
- Svelte 5 Runes: https://svelte.dev/docs/svelte/what-are-runes
- Tailwind CSS: https://tailwindcss.com
- SQLAlchemy: https://docs.sqlalchemy.org

---

Last Updated: 2025-12-10
