import AppShell from "./components/layout/AppShell";
import PipelineEditorPage from "./components/pipeline-editor/PipelineEditorPage";

export default function App() {
  return (
    <AppShell>
      <PipelineEditorPage />
    </AppShell>
  );
}
