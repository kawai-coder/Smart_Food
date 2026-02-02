"use client";

import { useEffect, useState } from "react";
import { StockItem } from "@/lib/types";

const getStatus = (item: StockItem) => {
  if (!item.expiresAt) return "fresh";
  const now = new Date();
  const expires = new Date(item.expiresAt);
  const diff = expires.getTime() - now.getTime();
  if (diff < 0) return "expired";
  if (diff <= 7 * 24 * 60 * 60 * 1000) return "need_soon";
  return "fresh";
};

export default function InventoryPage() {
  const [items, setItems] = useState<StockItem[]>([]);

  const load = async () => {
    const response = await fetch("/api/inventory");
    const data = (await response.json()) as StockItem[];
    setItems(data);
  };

  useEffect(() => {
    load();
  }, []);

  const updateLocal = (id: string, patch: Partial<StockItem>) => {
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, ...patch } : item)));
  };

  const saveRow = async (item: StockItem) => {
    await fetch("/api/inventory", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: item.id, patch: item })
    });
    await load();
  };

  const removeRow = async (id: string) => {
    await fetch(`/api/inventory?id=${id}`, { method: "DELETE" });
    await load();
  };

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">库存列表</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left text-slate-600">
            <tr>
              <th className="px-3 py-2">食材</th>
              <th className="px-3 py-2">类别</th>
              <th className="px-3 py-2">数量</th>
              <th className="px-3 py-2">单位</th>
              <th className="px-3 py-2">到期日</th>
              <th className="px-3 py-2">状态</th>
              <th className="px-3 py-2">备注</th>
              <th className="px-3 py-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b">
                <td className="px-3 py-2 font-medium">{item.name}</td>
                <td className="px-3 py-2 text-slate-600">{item.category}</td>
                <td className="px-3 py-2">
                  <input
                    type="number"
                    value={item.qty}
                    onChange={(event) => updateLocal(item.id, { qty: Number(event.target.value) })}
                    className="w-20 rounded border border-slate-200 px-2 py-1"
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    value={item.unit}
                    onChange={(event) => updateLocal(item.id, { unit: event.target.value })}
                    className="w-16 rounded border border-slate-200 px-2 py-1"
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    type="date"
                    value={item.expiresAt?.slice(0, 10) ?? ""}
                    onChange={(event) => updateLocal(item.id, { expiresAt: event.target.value })}
                    className="rounded border border-slate-200 px-2 py-1"
                  />
                </td>
                <td className="px-3 py-2">
                  <span
                    className={`rounded-full px-2 py-1 text-xs ${
                      getStatus(item) === "fresh"
                        ? "bg-emerald-50 text-emerald-600"
                        : getStatus(item) === "need_soon"
                          ? "bg-amber-50 text-amber-600"
                          : "bg-rose-50 text-rose-600"
                    }`}
                  >
                    {getStatus(item)}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <input
                    value={item.note ?? ""}
                    onChange={(event) => updateLocal(item.id, { note: event.target.value })}
                    className="w-40 rounded border border-slate-200 px-2 py-1"
                  />
                </td>
                <td className="px-3 py-2">
                  <div className="flex gap-2">
                    <button
                      onClick={() => saveRow(item)}
                      className="text-xs text-slate-600"
                    >
                      保存
                    </button>
                    <button
                      onClick={() => removeRow(item.id)}
                      className="text-xs text-rose-500"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={8} className="px-3 py-6 text-center text-slate-400">
                  暂无库存，请先从添加页面导入。
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
