import type { PropsWithChildren } from "react";
import TopBar from "./TopBar";

export default function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <TopBar />
      <main className="app-main">{children}</main>
    </div>
  );
}
