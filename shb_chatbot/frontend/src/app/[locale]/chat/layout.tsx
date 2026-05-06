import { Header, Sidebar } from "@/components/layout";
import { PageTransition } from "@/components/layout/page-transition";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen flex-col">
      <Header />
      <Sidebar />
      <main className="flex min-h-0 flex-1 flex-col overflow-auto p-3 sm:p-6">
        <PageTransition>{children}</PageTransition>
      </main>
    </div>
  );
}
