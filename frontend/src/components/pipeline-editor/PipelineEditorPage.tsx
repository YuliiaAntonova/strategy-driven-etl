import { useEffect, useMemo, useRef, useState } from "react";
import {
  fetchNodeTypes,
  fetchPipeline,
  fetchPipelineRuns,
  fetchPipelines,
  runPipeline,
  updatePipeline,
  validatePipeline,
} from "../../api/pipelines";
import type {
  NodeConfigField,
  NodeTypeDefinition,
  PipelineDefinition,
  PipelineListItem,
  PipelineRunRecord,
  ValidationResponse,
} from "../../types/pipeline";
import PipelineCanvas from "./PipelineCanvas";
import NodePalette from "./NodePalette";
import ConfigPanel from "./ConfigPanel";
import RunPanel from "./RunPanel";
import StatusBadge from "./StatusBadge";

function buildDefaultConfig(fields: NodeConfigField[]): Record<string, unknown> {
  return fields.reduce<Record<string, unknown>>((acc, field) => {
    if (field.default !== undefined) {
      acc[field.name] = field.default;
    }
    return acc;
  }, {});
}

export default function PipelineEditorPage() {
  const [pipelines, setPipelines] = useState<PipelineListItem[]>([]);
  const [selectedPipelineId, setSelectedPipelineId] = useState<string>("jobs_visual_sample");
  const [pipeline, setPipeline] = useState<PipelineDefinition | null>(null);
  const [nodeTypes, setNodeTypes] = useState<NodeTypeDefinition[]>([]);
  const [runs, setRuns] = useState<PipelineRunRecord[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [lastValidation, setLastValidation] = useState<ValidationResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const autosaveTimerRef = useRef<number | null>(null);
  const isHydratingRef = useRef(false);

  function buildSavePayload(definition: PipelineDefinition) {
    return {
      name: definition.name,
      description: definition.description ?? null,
      version: definition.version,
      nodes: definition.nodes,
      edges: definition.edges,
      tags: definition.tags ?? [],
    };
  }

  async function handleSave(reason: "manual" | "autosave" = "manual") {
    if (!pipeline) return;
    if (!selectedPipelineId) return;
    if (!isDirty) return;
    if (isRunning) return;

    if (autosaveTimerRef.current) {
      window.clearTimeout(autosaveTimerRef.current);
      autosaveTimerRef.current = null;
    }

    try {
      setIsSaving(true);
      setErrorMessage(null);
      const payload = buildSavePayload(pipeline);
      const updated = await updatePipeline(selectedPipelineId, payload as unknown as PipelineDefinition);
      setPipeline(updated);
      setIsDirty(false);
      setLastSavedAt(new Date());
      if (reason === "manual") {
        setLastValidation(null);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Save failed.");
    } finally {
      setIsSaving(false);
    }
  }

  function updateNodeConfig(nodeId: string, key: string, value: unknown) {
    setPipeline((current) => {
      if (!current) return current;
      if (!isHydratingRef.current) setIsDirty(true);
      return {
        ...current,
        nodes: current.nodes.map((node) => {
          if (node.id !== nodeId) return node;

          if (key === "__node_name__") {
            return {
              ...node,
              name: String(value ?? ""),
            };
          }

          return {
            ...node,
            config: {
              ...(node.config ?? {}),
              [key]: value,
            },
          };
        }),
      };
    });
  }

  function updateLayout(next: Pick<PipelineDefinition, "nodes" | "edges">) {
    if (!isHydratingRef.current) setIsDirty(true);
    setPipeline((current) => (current ? { ...current, nodes: next.nodes, edges: next.edges } : current));
  }

  function handleAddNode(nodeType: NodeTypeDefinition) {
    setPipeline((current) => {
      if (!current) return current;

      const newId =
        typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `node_${Date.now().toString(16)}`;

      const nextNode = {
        id: newId,
        type: nodeType.type,
        name: nodeType.label,
        position: {
          x: 120 + (current.nodes.length % 3) * 220,
          y: 120 + Math.floor(current.nodes.length / 3) * 140,
        },
        config: buildDefaultConfig(nodeType.config_fields),
      };

      if (!isHydratingRef.current) setIsDirty(true);
      setSelectedNodeId(newId);

      return {
        ...current,
        nodes: [...current.nodes, nextNode],
      };
    });
  }

  function handleDeleteNode(nodeId: string) {
    setPipeline((current) => {
      if (!current) return current;
      if (!current.nodes.some((node) => node.id === nodeId)) return current;

      if (!isHydratingRef.current) setIsDirty(true);

      const nextNodes = current.nodes.filter((node) => node.id !== nodeId);
      const nextEdges = current.edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId);

      const nextSelectedNodeId = selectedNodeId === nodeId ? nextNodes[0]?.id ?? null : selectedNodeId;
      setSelectedNodeId(nextSelectedNodeId);

      return {
        ...current,
        nodes: nextNodes,
        edges: nextEdges,
      };
    });
  }

  useEffect(() => {
    void (async () => {
      try {
        const [pipelineList, types] = await Promise.all([fetchPipelines(), fetchNodeTypes()]);
        setPipelines(pipelineList.items);
        setNodeTypes(types.items);

        if (pipelineList.items.length > 0 && !pipelineList.items.some((item) => item.id === selectedPipelineId)) {
          setSelectedPipelineId(pipelineList.items[0].id);
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to load pipeline list.");
      }
    })();
  }, [selectedPipelineId]);

  useEffect(() => {
    if (!selectedPipelineId) return;

    void (async () => {
      try {
        setErrorMessage(null);
        isHydratingRef.current = true;
        const [definition, pipelineRuns] = await Promise.all([
          fetchPipeline(selectedPipelineId),
          fetchPipelineRuns(selectedPipelineId),
        ]);
        setPipeline(definition);
        setRuns(pipelineRuns.items);
        setSelectedNodeId(definition.nodes[0]?.id ?? null);
        setIsDirty(false);
        setLastSavedAt(null);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to load pipeline.");
      } finally {
        window.setTimeout(() => {
          isHydratingRef.current = false;
        }, 0);
      }
    })();
  }, [selectedPipelineId]);

  useEffect(() => {
    if (!pipeline) return;
    if (!selectedPipelineId) return;
    if (!isDirty) return;
    if (isSaving || isRunning) return;

    if (autosaveTimerRef.current) window.clearTimeout(autosaveTimerRef.current);

    autosaveTimerRef.current = window.setTimeout(() => {
      void handleSave("autosave");
    }, 800);

    return () => {
      if (autosaveTimerRef.current) {
        window.clearTimeout(autosaveTimerRef.current);
        autosaveTimerRef.current = null;
      }
    };
  }, [pipeline, isDirty, isSaving, isRunning, selectedPipelineId]);

  const latestRun = useMemo(() => runs[0] ?? null, [runs]);

  async function handleValidate() {
    if (!selectedPipelineId) return;
    try {
      const result = await validatePipeline(selectedPipelineId);
      setLastValidation(result);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Validation failed.");
    }
  }

  async function handleRun() {
    if (!selectedPipelineId) return;

    try {
      setIsRunning(true);
      await runPipeline(selectedPipelineId);
      const refreshedRuns = await fetchPipelineRuns(selectedPipelineId);
      setRuns(refreshedRuns.items);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Run failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="editor-page">
      <section className="editor-header card">
        <div>
          <div className="eyebrow">Pipeline editor</div>
          <h2>{pipeline?.name ?? "Loading..."}</h2>
          <p className="muted">{pipeline?.description ?? "React Flow editor scaffold over the FastAPI visual runtime."}</p>
        </div>
        <div className="header-controls">
          <label className="muted small" htmlFor="pipeline-select">Pipeline</label>
          <select
            id="pipeline-select"
            value={selectedPipelineId}
            onChange={(event) => setSelectedPipelineId(event.target.value)}
          >
            {pipelines.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>

          <button
            type="button"
            className="btn"
            onClick={() => void handleSave("manual")}
            disabled={!pipeline || !isDirty || isSaving || isRunning}
            title={isRunning ? "Cannot save while pipeline is running" : "Save pipeline"}
          >
            {isSaving ? "Saving..." : "Save"}
          </button>

          <div className="muted small" style={{ textAlign: "right" }}>
            {isDirty ? "Unsaved changes" : lastSavedAt ? `Saved ${lastSavedAt.toLocaleTimeString()}` : ""}
          </div>
        </div>
      </section>

      <section className="editor-metrics">
        <StatusBadge label="Nodes" value={String(pipeline?.nodes.length ?? 0)} />
        <StatusBadge label="Edges" value={String(pipeline?.edges.length ?? 0)} />
        <StatusBadge label="Latest run" value={latestRun?.status ?? "idle"} />
      </section>

      {errorMessage ? <div className="error-banner">{errorMessage}</div> : null}

      <section className="editor-grid">
        <aside className="card sidebar-left">
          <NodePalette nodeTypes={nodeTypes} onAddNode={handleAddNode} />
        </aside>

        <div className="card canvas-card">
          <PipelineCanvas
            pipeline={pipeline}
            nodeTypesCatalog={nodeTypes}
            latestRun={latestRun}
            selectedNodeId={selectedNodeId}
            onSelectNode={(nodeId) => setSelectedNodeId(nodeId || null)}
            onChange={updateLayout}
          />
        </div>

        <aside className="card sidebar-right top">
          <ConfigPanel
            pipeline={pipeline}
            nodeTypes={nodeTypes}
            selectedNodeId={selectedNodeId}
            onChange={updateNodeConfig}
            onDeleteNode={handleDeleteNode}
          />
        </aside>

        <aside className="card sidebar-right bottom">
          <RunPanel
            latestRun={latestRun}
            lastValidation={lastValidation}
            onRun={handleRun}
            onValidate={handleValidate}
            isRunning={isRunning}
          />
        </aside>
      </section>
    </div>
  );
}
