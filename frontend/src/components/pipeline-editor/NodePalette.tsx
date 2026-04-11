import type { NodeTypeDefinition } from "../../types/pipeline";

type Props = {
  nodeTypes: NodeTypeDefinition[];
  onAddNode?: (nodeType: NodeTypeDefinition) => void;
};

const DND_NODE_TYPE = "application/strategy-driven-etl/node-type";

export default function NodePalette({ nodeTypes, onAddNode }: Props) {
  const grouped = nodeTypes.reduce<Record<string, NodeTypeDefinition[]>>((acc, nodeType) => {
    acc[nodeType.category] ??= [];
    acc[nodeType.category].push(nodeType);
    return acc;
  }, {});

  return (
    <div className="panel-content">
      <h3>Node palette</h3>
      {Object.entries(grouped).map(([category, items]) => (
        <div key={category} className="palette-group">
          <div className="palette-group-title">{category}</div>
          {items.map((item) => (
            <div
              key={item.type}
              className="palette-item"
              draggable
              onDragStart={(event) => {
                event.dataTransfer.setData(DND_NODE_TYPE, item.type);
                event.dataTransfer.effectAllowed = "move";
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
                <div>
                  <strong>{item.label}</strong>
                  <div className="muted small">{item.type}</div>
                </div>
                <button
                  type="button"
                  className="btn secondary"
                  style={{ padding: "6px 10px", minWidth: "unset" }}
                  onClick={() => onAddNode?.(item)}
                >
                  + Add
                </button>
              </div>
              {item.description ? <div className="small">{item.description}</div> : null}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
