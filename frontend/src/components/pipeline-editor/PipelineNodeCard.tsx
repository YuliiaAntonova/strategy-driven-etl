import type { NodeProps } from "reactflow";
import { Handle, Position } from "reactflow";

type PipelineNodeData = {
  label: string;
  type: string;
  status?: string;
};

function getStatusClass(status?: string): string {
  switch (status) {
    case "succeeded":
      return "node-card succeeded";
    case "failed":
      return "node-card failed";
    case "running":
      return "node-card running";
    default:
      return "node-card";
  }
}

export default function PipelineNodeCard({ data }: NodeProps<PipelineNodeData>) {
  return (
    <div className={getStatusClass(data.status)}>
      <Handle type="target" position={Position.Left} />
      <div className="node-type">{data.type}</div>
      <div className="node-label">{data.label}</div>
      <div className="node-status">Status: {data.status ?? "idle"}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
