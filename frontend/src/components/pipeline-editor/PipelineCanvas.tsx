import { useCallback, useMemo, useRef } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Connection,
  type Edge,
  type OnConnect,
  type Node,
  type ReactFlowInstance,
} from "reactflow";
import "reactflow/dist/style.css";
import type { NodeTypeDefinition, PipelineDefinition, PipelineRunRecord } from "../../types/pipeline";
import PipelineNodeCard from "./PipelineNodeCard";

type Props = {
  pipeline: PipelineDefinition | null;
  nodeTypesCatalog: NodeTypeDefinition[];
  latestRun: PipelineRunRecord | null;
  selectedNodeId?: string | null;
  onSelectNode?: (nodeId: string) => void;
  onChange?: (next: Pick<PipelineDefinition, "nodes" | "edges">) => void;
};

const DND_NODE_TYPE = "application/strategy-driven-etl/node-type";

const nodeTypes = {
  pipelineNode: PipelineNodeCard,
};

function buildInitialConfig(nodeType: NodeTypeDefinition | undefined): Record<string, unknown> {
  if (!nodeType) return {};

  return nodeType.config_fields.reduce<Record<string, unknown>>((acc, field) => {
    if (field.default !== undefined) {
      acc[field.name] = field.default;
    }
    return acc;
  }, {});
}

export default function PipelineCanvas({
  pipeline,
  nodeTypesCatalog,
  latestRun,
  selectedNodeId,
  onSelectNode,
  onChange,
}: Props) {
  const nodeRunMap = useMemo(() => {
    const map = new Map<string, string>();
    latestRun?.node_runs.forEach((run) => {
      map.set(run.node_id, run.status);
    });
    return map;
  }, [latestRun]);

  const nodeTypesMap = useMemo(
    () => new Map(nodeTypesCatalog.map((item) => [item.type, item])),
    [nodeTypesCatalog]
  );

  const reactFlowWrapperRef = useRef<HTMLDivElement | null>(null);
  const reactFlowInstanceRef = useRef<ReactFlowInstance | null>(null);

  const handleConnect: OnConnect = useCallback(
    (connection: Connection) => {
      if (!pipeline) return;
      if (!connection.source || !connection.target) return;

      const exists = pipeline.edges.some(
        (edge) => edge.source === connection.source && edge.target === connection.target
      );
      if (exists) return;

      const nextEdges = [...pipeline.edges, { source: connection.source, target: connection.target }];
      onChange?.({ nodes: pipeline.nodes, edges: nextEdges });
    },
    [onChange, pipeline]
  );

  const handleNodeDragStop = useCallback(
    (_: unknown, node: Node) => {
      if (!pipeline) return;
      const nextNodes = pipeline.nodes.map((existing) =>
        existing.id === node.id ? { ...existing, position: node.position } : existing
      );
      onChange?.({ nodes: nextNodes, edges: pipeline.edges });
    },
    [onChange, pipeline]
  );

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      if (!pipeline) return;

      const type = event.dataTransfer.getData(DND_NODE_TYPE);
      if (!type) return;

      const wrapperBounds = reactFlowWrapperRef.current?.getBoundingClientRect();
      if (!wrapperBounds) return;

      const instance = reactFlowInstanceRef.current;
      if (!instance) return;

      const position = instance.screenToFlowPosition({
        x: event.clientX - wrapperBounds.left,
        y: event.clientY - wrapperBounds.top,
      });

      const newId =
        typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `node_${Date.now().toString(16)}`;

      const definition = nodeTypesMap.get(type);
      const nextNodes = [
        ...pipeline.nodes,
        {
          id: newId,
          type,
          name: definition?.label ?? type,
          position,
          config: buildInitialConfig(definition),
        },
      ];

      onChange?.({ nodes: nextNodes, edges: pipeline.edges });
      onSelectNode?.(newId);
    },
    [nodeTypesMap, onChange, onSelectNode, pipeline]
  );

  const nodes: Node[] = useMemo(() => {
    if (!pipeline) return [];

    return pipeline.nodes.map((node) => ({
      id: node.id,
      type: "pipelineNode",
      position: node.position,
      selected: selectedNodeId === node.id,
      data: {
        label: node.name,
        type: node.type,
        status: nodeRunMap.get(node.id),
      },
    }));
  }, [pipeline, nodeRunMap, selectedNodeId]);

  const edges: Edge[] = useMemo(() => {
    if (!pipeline) return [];

    return pipeline.edges.map((edge, index) => ({
      id: `${edge.source}-${edge.target}-${index}`,
      source: edge.source,
      target: edge.target,
      animated: false,
    }));
  }, [pipeline]);

  return (
    <div className="canvas-shell" ref={reactFlowWrapperRef}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        onNodeClick={(_, node) => onSelectNode?.(node.id)}
        onPaneClick={() => onSelectNode?.("")}
        onInit={(instance) => {
          reactFlowInstanceRef.current = instance;
        }}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onConnect={handleConnect}
        onNodeDragStop={handleNodeDragStop}
      >
        <Background />
        <MiniMap />
        <Controls />
      </ReactFlow>
    </div>
  );
}
