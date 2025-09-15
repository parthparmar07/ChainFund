import { Outlet } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Header } from "@/components/Header";
import { useWalletStore } from "@/stores/walletStore";

export function Layout() {
  const { isAuthenticated } = useWalletStore();

  // If not authenticated, render without sidebar
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen w-full">
        <Header />
        <main className="w-full">
          <Outlet />
        </main>
      </div>
    );
  }

  // Authenticated users get sidebar layout
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}