"use client";

import { useState } from "react";
import { MenuResult } from "@/lib/types";

const NutritionBar = ({ label, value, max = 100 }: { label: string; value: number; max?: number }) => {
  const percent = Math.round((value / max) * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-500">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-emerald-500" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
};

export default function MenuPage() {
  const [result, setResult] = useState<MenuResult | null>(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    const response = await fetch("/api/menu/generate", { method: "POST" });
    const data = (await response.json()) as MenuResult;
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">今日菜单</h2>
            <p className="text-sm text-slate-500">自动根据库存匹配 2 菜 1 汤</p>
          </div>
          <button
            onClick={generate}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            {loading ? "生成中..." : "生成今日菜单"}
          </button>
        </div>
        {result && (
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {result.menu.map((recipe) => (
              <div key={recipe.title} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <h3 className="font-semibold">{recipe.title}</h3>
                <p className="mt-2 text-xs text-slate-500">
                  {recipe.ingredients.map((item) => item.name).join("、")}
                </p>
                <ul className="mt-3 space-y-1 text-xs text-slate-600">
                  {recipe.steps.map((step) => (
                    <li key={step}>• {step}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </section>

      {result && (
        <section className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold">营养均衡指标</h3>
            <div className="mt-4 space-y-3">
              <NutritionBar label="蛋白质覆盖" value={result.nutrition.proteinCoverage} />
              <NutritionBar label="蔬菜份数" value={result.nutrition.vegServings} max={6} />
              <NutritionBar label="主食份数" value={result.nutrition.carbServings} max={4} />
              <NutritionBar label="纤维评分" value={result.nutrition.fiberScore} />
            </div>
          </div>
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold">搭配说明</h3>
            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              {result.explanation.map((line) => (
                <li key={line}>• {line}</li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {result && (
        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold">购物清单</h3>
          <p className="text-sm text-slate-500">缺少的食材会出现在此处，可勾选。</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {result.shoppingList.length > 0 ? (
              result.shoppingList.map((item) => (
                <label key={item.name} className="flex items-center gap-2 rounded-lg border p-3">
                  <input type="checkbox" className="h-4 w-4" />
                  <span className="text-sm text-slate-700">
                    {item.name} {item.qty}
                    {item.unit}
                  </span>
                </label>
              ))
            ) : (
              <div className="text-sm text-emerald-600">库存足够，无需补货。</div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
