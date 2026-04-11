export type Position = {
  x: number;
  y: number;
};

export type PipelineNode = {
  id: string;
  type: string;
  name: string;
  position: Position;
  config: Record<string, unknown>;
};

export type PipelineEdge = {
  source: string;
  target: string;
};

export type PipelineDefinition = {
  id: string;
  name: string;
  description?: string | null;
  version: number;
  nodes: PipelineNode[];
  edges: PipelineEdge[];
  tags?: string[];
  created_at?: string;
  updated_at?: string;
};

export type PipelineListItem = {
  id: string;
  name: string;
  description?: string | null;
  version: number;
  node_count: number;
  edge_count: number;
  updated_at?: string | null;
};

export type PipelineListResponse = {
  items: PipelineListItem[];
};

export type ValidationIssue = {
  message: string;
  node_id?: string | null;
};

export type ValidationResponse = {
  valid: boolean;
  issues: ValidationIssue[];
};

export type RunResponse = {
  run_id: string;
  status: string;
};

export type NodeRun = {
  node_id: string;
  node_type: string;
  status: string;
  started_at?: string | null;
  finished_at?: string | null;
  output: Record<string, unknown>;
  error_message?: string | null;
  logs: string[];
};

export type PipelineRunRecord = {
  id: string;
  pipeline_id: string;
  status: string;
  started_at: string;
  finished_at?: string | null;
  logs: string[];
  triggered_by?: string | null;
  error_message?: string | null;
  node_runs: NodeRun[];
};

export type PipelineRunsResponse = {
  items: PipelineRunRecord[];
};

export type NodeFieldOption =
  | string
  | {
      value: string;
      label?: string;
    };

export type NodeConfigField = {
  name: string;
  type: string;
  required: boolean;
  default?: unknown;
  description?: string | null;
  options?: NodeFieldOption[];
};

export type NodeTypeDefinition = {
  type: string;
  label: string;
  category: string;
  description?: string | null;
  config_fields: NodeConfigField[];
};

export type NodeTypesResponse = {
  items: NodeTypeDefinition[];
};
