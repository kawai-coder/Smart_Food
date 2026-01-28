import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "智能冰箱 Demo",
  description: "黑客松智能冰箱 Web Demo"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>
        <div className="min-h-screen">
          <header className="border-b bg-white">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <div>
                <h1 className="text-xl font-semibold">智能冰箱 Web Demo</h1>
                <p className="text-sm text-slate-500">上传照片 → 识别 → 入库 → 菜单</p>
              </div>
              <nav className="flex gap-4 text-sm font-medium text-slate-600">
                <Link href="/" className="hover:text-slate-900">
                  Dashboard
                </Link>
                <Link href="/add" className="hover:text-slate-900">
                  添加
                </Link>
                <Link href="/inventory" className="hover:text-slate-900">
                  库存
                </Link>
                <Link href="/menu" className="hover:text-slate-900">
                  菜单
                </Link>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-6 py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
