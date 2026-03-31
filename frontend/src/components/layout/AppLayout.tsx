import { Outlet } from "react-router";
import { Header } from "./Header";
import { Footer } from "./Footer";

export function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-[#F7F7F7]">
      <Header />
      <main className="mx-auto w-full max-w-[1200px] flex-1 px-4 py-6">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
