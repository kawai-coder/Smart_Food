"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { StockItem } from "@/lib/types";

const countExpiring = (items: StockItem[]) => {
  const now = new Date();
  const soon = new Date();
  soon.setDate(now.getDate() + 7);
  return items.filter((item) => item.expiresAt && new Date(item.expiresAt) <= soon).length;
};

export default function DashboardPage() {
  const [inventory, setInventory] = useState<StockItem[]>([]);

  useEffect(() => {
    const load = async () => {
      const response = await fetch("/api/inventory");
      const data = (await response.json()) as StockItem[];
      setInventory(data);
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">库存数量</p>
          <p className="mt-2 text-3xl font-semibold">{inventory.length}</p>
        </div>
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">7天内到期</p>
          <p className="mt-2 text-3xl font-semibold">{countExpiring(inventory)}</p>
        </div>
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">AI 识别</p>
          <p className="mt-2 text-3xl font-semibold">Mock 模式</p>
        </div>
      </section>

      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">快速操作</h2>
        <p className="mt-2 text-sm text-slate-600">
          上传冰箱照片，一键识别并确认入库，然后生成今日菜单和购物清单。
        </p>
        <div className="mt-4 flex gap-3">
          <Link
            href="/add"
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            添加照片识别
          </Link>
          <Link
            href="/menu"
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700"
          >
            生成今日菜单
          </Link>
        </div>
      </section>
    </div>
  );
}
