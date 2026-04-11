# Frontend editor architecture

## Components
- `PipelineCanvas.tsx`: renders nodes and edges
- `NodePalette.tsx`: node catalog grouped by category
- `NodeSettingsPanel.tsx`: edits node config
- `RunPanel.tsx`: shows validation, run history, and logs

## State slices
- editor state: nodes, edges, selected node
- server state: pipeline definitions, node types, runs
- validation state: current validation issues

## UX goal
The backend remains the source of truth for definitions and validation.
The frontend only edits the visual model and sends it back through the API.
