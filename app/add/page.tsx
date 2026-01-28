"use client";

import { useMemo, useState } from "react";
import { DetectedIngredient, StockInput } from "@/lib/types";

const categories = [
  { value: "protein", label: "蛋白质" },
  { value: "veg", label: "蔬菜" },
  { value: "fruit", label: "水果" },
  { value: "carb", label: "主食" },
  { value: "dairy", label: "乳制品" },
  { value: "other", label: "其他" }
];

export default function AddPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [rows, setRows] = useState<DetectedIngredient[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  const handleFile = (selected: File | null) => {
    setFile(selected);
    setRows([]);
    setMessage(null);
    if (selected) {
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(selected);
    } else {
      setPreview(null);
    }
  };

  const detect = async () => {
    if (!file) return;
    setDetecting(true);
    setMessage(null);
    const response = await fetch("/api/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ imageName: file.name })
    });
    const data = (await response.json()) as DetectedIngredient[];
    setRows(data);
    setDetecting(false);
  };

  const updateRow = (index: number, patch: Partial<DetectedIngredient>) => {
    setRows((prev) => prev.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };

  const addRow = () => {
    setRows((prev) => [
      ...prev,
      { name: "", qtyGuess: 1, unitGuess: "个", categoryGuess: "other", confidence: 0.6 }
    ]);
  };

  const removeRow = (index: number) => {
    setRows((prev) => prev.filter((_, i) => i !== index));
  };

  const confirmInventory = async () => {
    const payload: StockInput[] = rows.map((row) => ({
      name: row.name,
      qty: row.qtyGuess,
      unit: row.unitGuess,
      category: row.categoryGuess,
      expiresAt: null,
      note: `识别置信度 ${Math.round(row.confidence * 100)}%`
    }));
    await fetch("/api/inventory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: payload })
    });
    setMessage("已入库，可前往库存或生成菜单。");
  };

  const canConfirm = useMemo(() => rows.length > 0, [rows]);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">上传冰箱照片</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="flex flex-col gap-3">
            <label className="flex h-40 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 text-sm text-slate-500">
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(event) => handleFile(event.target.files?.[0] ?? null)}
              />
              <span>拖拽或点击选择图片</span>
              <span className="text-xs text-slate-400">支持 jpg/png/webp</span>
            </label>
            <button
              className="w-fit rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={!file || detecting}
              onClick={detect}
            >
              {detecting ? "识别中..." : "识别食材"}
            </button>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            {preview ? (
              <img src={preview} alt="预览" className="h-40 w-full rounded-lg object-cover" />
            ) : (
              <div className="flex h-40 items-center justify-center text-sm text-slate-400">
                图片预览
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">识别结果（可编辑）</h2>
          <button
            onClick={addRow}
            className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
          >
            + 添加行
          </button>
        </div>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-100 text-left text-slate-600">
              <tr>
                <th className="px-3 py-2">食材</th>
                <th className="px-3 py-2">数量</th>
                <th className="px-3 py-2">单位</th>
                <th className="px-3 py-2">类别</th>
                <th className="px-3 py-2">置信度</th>
                <th className="px-3 py-2">操作</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.name}-${index}`} className="border-b">
                  <td className="px-3 py-2">
                    <input
                      value={row.name}
                      onChange={(event) => updateRow(index, { name: event.target.value })}
                      className="w-32 rounded border border-slate-200 px-2 py-1"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      value={row.qtyGuess}
                      onChange={(event) => updateRow(index, { qtyGuess: Number(event.target.value) })}
                      className="w-20 rounded border border-slate-200 px-2 py-1"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      value={row.unitGuess}
                      onChange={(event) => updateRow(index, { unitGuess: event.target.value })}
                      className="w-20 rounded border border-slate-200 px-2 py-1"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <select
                      value={row.categoryGuess}
                      onChange={(event) =>
                        updateRow(index, { categoryGuess: event.target.value as DetectedIngredient["categoryGuess"] })
                      }
                      className="rounded border border-slate-200 px-2 py-1"
                    >
                      {categories.map((category) => (
                        <option key={category.value} value={category.value}>
                          {category.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-3 py-2 text-slate-500">
                    {Math.round(row.confidence * 100)}%
                  </td>
                  <td className="px-3 py-2">
                    <button
                      onClick={() => removeRow(index)}
                      className="text-xs text-rose-500"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-3 py-6 text-center text-slate-400">
                    尚未识别，点击“识别食材”获取列表。
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={confirmInventory}
            disabled={!canConfirm}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-emerald-300"
          >
            确认入库
          </button>
          {message && <span className="text-sm text-emerald-600">{message}</span>}
        </div>
      </section>
    </div>
  );
}
