import { useMemo } from "react";
import type {
  NodeConfigField,
  NodeFieldOption,
  NodeTypeDefinition,
  PipelineDefinition,
  PipelineNode,
} from "../../types/pipeline";

type Props = {
  pipeline: PipelineDefinition | null;
  nodeTypes: NodeTypeDefinition[];
  selectedNodeId: string | null;
  onChange: (nodeId: string, key: string, value: unknown) => void;
  onDeleteNode?: (nodeId: string) => void;
};

type SelectOption = {
  value: string;
  label: string;
};

function getDefaultValue(field: NodeConfigField): unknown {
  if (field.default !== undefined) return field.default;
  if (field.type === "boolean") return false;
  if (field.type === "integer" || field.type === "number") return "";
  if (field.type === "string[]") return [];
  return "";
}

function normalizeInputValue(field: NodeConfigField, rawValue: string | boolean): unknown {
  if (field.type === "boolean") return Boolean(rawValue);
  if (typeof rawValue !== "string") return rawValue;

  if (field.type === "integer") {
    if (rawValue.trim() === "") return "";
    const parsed = Number.parseInt(rawValue, 10);
    return Number.isNaN(parsed) ? rawValue : parsed;
  }

  if (field.type === "number") {
    if (rawValue.trim() === "") return "";
    const parsed = Number(rawValue);
    return Number.isNaN(parsed) ? rawValue : parsed;
  }

  if (field.type === "string[]") {
    return rawValue
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return rawValue;
}

function formatValue(field: NodeConfigField, value: unknown): string | boolean {
  if (field.type === "boolean") return Boolean(value);
  if (field.type === "string[]") return Array.isArray(value) ? value.join(", ") : "";
  if (value === null || value === undefined) return "";
  return String(value);
}

function normalizeOption(option: NodeFieldOption): SelectOption {
  if (typeof option === "string") {
    return { value: option, label: option };
  }

  return {
    value: option.value,
    label: option.label ?? option.value,
  };
}

function matchesCategory(nodeType: string, prefixes: string[]): boolean {
  return prefixes.some((prefix) => nodeType.toLowerCase().startsWith(prefix));
}

function buildNodeReferenceOptions(
  field: NodeConfigField,
  pipeline: PipelineDefinition,
  nodeTypes: NodeTypeDefinition[],
  currentNode: PipelineNode
): SelectOption[] {
  const fieldName = field.name.toLowerCase();
  const fieldType = field.type.toLowerCase();

  let allowedPrefixes: string[] = [];

  if (fieldName.includes("extractor") || fieldType.includes("extractor")) {
    allowedPrefixes = ["extractor."];
  } else if (fieldName.includes("loader") || fieldType.includes("loader")) {
    allowedPrefixes = ["loader."];
  } else if (fieldName.includes("transform") || fieldType.includes("transform")) {
    allowedPrefixes = ["transformer."];
  } else if (fieldType.includes("node_ref") || fieldName.endsWith("_node_id") || fieldName.endsWith("node_id")) {
    allowedPrefixes = [];
  } else {
    return [];
  }

  const nodeTypeMap = new Map(nodeTypes.map((item) => [item.type, item]));

  return pipeline.nodes
    .filter((node) => node.id !== currentNode.id)
    .filter((node) => {
      if (allowedPrefixes.length === 0) return true;
      return matchesCategory(node.type, allowedPrefixes);
    })
    .map((node) => {
      const definition = nodeTypeMap.get(node.type);
      const suffix = definition?.label ?? node.type;
      return {
        value: node.id,
        label: `${node.name} (${suffix})`,
      };
    });
}

function getSelectOptions(
  field: NodeConfigField,
  pipeline: PipelineDefinition,
  nodeTypes: NodeTypeDefinition[],
  currentNode: PipelineNode
): SelectOption[] {
  if (Array.isArray(field.options) && field.options.length > 0) {
    return field.options.map(normalizeOption);
  }

  return buildNodeReferenceOptions(field, pipeline, nodeTypes, currentNode);
}

export default function ConfigPanel({
  pipeline,
  nodeTypes,
  selectedNodeId,
  onChange,
  onDeleteNode,
}: Props) {
  const node = pipeline?.nodes.find((n) => n.id === selectedNodeId) ?? null;

  const nodeType = useMemo(
    () => nodeTypes.find((item) => item.type === node?.type) ?? null,
    [node?.type, nodeTypes]
  );

  if (!pipeline || !node) return <div style={{ padding: 16 }}>Select node</div>;

  const configFields = nodeType?.config_fields ?? [];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: 12, marginBottom: 16 }}>
        <div>
          <h3 style={{ marginBottom: 4 }}>{nodeType?.label ?? node.name}</h3>
          <div className="muted small">{node.type}</div>
        </div>
        <button
          type="button"
          className="btn secondary"
          onClick={() => onDeleteNode?.(node.id)}
          disabled={!onDeleteNode}
        >
          Delete
        </button>
      </div>

      <div style={{ marginBottom: 16 }}>
        <label htmlFor="node-name" style={{ display: "block", marginBottom: 6 }}>Name</label>
        <input
          id="node-name"
          value={node.name}
          onChange={(e) => onChange(node.id, "__node_name__", e.target.value)}
          style={{ width: "100%" }}
        />
      </div>

      {configFields.length === 0 ? (
        <div className="muted small">This node has no configurable fields.</div>
      ) : (
        configFields.map((field) => {
          const currentValue = node.config?.[field.name] ?? getDefaultValue(field);
          const formattedValue = formatValue(field, currentValue);
          const selectOptions = getSelectOptions(field, pipeline, nodeTypes, node);
          const shouldRenderSelect = selectOptions.length > 0;

          return (
            <div key={field.name} style={{ marginBottom: 12 }}>
              <label htmlFor={`field-${field.name}`} style={{ display: "block", marginBottom: 6 }}>
                {field.name} {field.required ? "*" : ""}
              </label>

              {field.type === "boolean" ? (
                <input
                  id={`field-${field.name}`}
                  type="checkbox"
                  checked={Boolean(formattedValue)}
                  onChange={(e) => onChange(node.id, field.name, normalizeInputValue(field, e.target.checked))}
                />
              ) : shouldRenderSelect ? (
                <select
                  id={`field-${field.name}`}
                  value={String(formattedValue)}
                  onChange={(e) => onChange(node.id, field.name, normalizeInputValue(field, e.target.value))}
                  style={{ width: "100%" }}
                >
                  <option value="">Select...</option>
                  {selectOptions.map((option) => (
                    <option key={`${field.name}-${option.value}`} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  id={`field-${field.name}`}
                  value={String(formattedValue)}
                  onChange={(e) => onChange(node.id, field.name, normalizeInputValue(field, e.target.value))}
                  placeholder={field.default !== undefined ? String(formatValue(field, field.default)) : undefined}
                  style={{ width: "100%" }}
                />
              )}

              <div className="muted small" style={{ marginTop: 4 }}>
                {field.description ?? field.type}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
