import type { PipelineRunRecord, ValidationResponse } from "../../types/pipeline";

type Props = {
  latestRun: PipelineRunRecord | null;
  lastValidation: ValidationResponse | null;
  onRun: () => void;
  onValidate: () => void;
  isRunning: boolean;
};

export default function RunPanel({ latestRun, lastValidation, onRun, onValidate, isRunning }: Props) {
  return (
    <div className="panel-content run-panel">
      <div className="toolbar-row">
        <button className="primary-button" onClick={onValidate}>Validate</button>
        <button className="primary-button" onClick={onRun} disabled={isRunning}>
          {isRunning ? "Running..." : "Run pipeline"}
        </button>
      </div>

      <h3>Pipeline status</h3>

      {lastValidation ? (
        <div className="panel-section">
          <strong>Validation:</strong> {lastValidation.valid ? "valid" : "invalid"}
          {!lastValidation.valid && lastValidation.issues.length > 0 ? (
            <ul className="issue-list">
              {lastValidation.issues.map((issue, index) => (
                <li key={`${issue.message}-${index}`}>{issue.message}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {!latestRun ? (
        <p className="muted">No runs yet.</p>
      ) : (
        <div>
          <div><strong>Status:</strong> {latestRun.status}</div>
          <div><strong>Started:</strong> {latestRun.started_at}</div>
          <div><strong>Finished:</strong> {latestRun.finished_at ?? "-"}</div>

          <div className="panel-section">
            <strong>Logs</strong>
            <pre className="terminal-block">{latestRun.logs.join("\n")}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
