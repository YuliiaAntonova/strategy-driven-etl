# Strategy-Driven ETL frontend

This frontend is a React Flow scaffold for a Mage-style pipeline editor over the FastAPI backend.

## Stack

- React
- TypeScript
- Vite
- React Flow
- Axios

## Start

From the `frontend` folder:

```bash
npm install
npm run dev
```

The app runs on `http://127.0.0.1:5173` by default.

## API base URL

By default the frontend talks to:

```text
http://127.0.0.1:8000/api
```

To override it, create a `.env` file inside `frontend`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Required backend routes

- `GET /api/pipelines`
- `GET /api/pipelines/{id}`
- `GET /api/pipelines/meta/node-types`
- `POST /api/pipelines/{id}/validate`
- `POST /api/pipelines/{id}/run`
- `GET /api/pipelines/{id}/runs`

## Notes

This is an MVP editor shell. It already supports:

- pipeline selection
- React Flow canvas rendering
- node selection
- config panel
- validation
- run action
- latest run status and logs
- node coloring based on latest run

The next step would be editable nodes and save/update endpoints.

uvicorn src.entrypoints.api:app --reload

cd frontend
npm install
npm run dev

http://127.0.0.1:5173

