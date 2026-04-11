type Props = {
  label: string;
  value: string;
};

export default function StatusBadge({ label, value }: Props) {
  return (
    <div className="status-badge">
      <span className="muted small">{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
