import { promises as fs } from "fs";
import path from "path";
import { StockInput, StockItem } from "./types";

const storagePath = path.join(process.cwd(), "data", "inventory.json");
let inMemory: StockItem[] | null = null;

const readFileSafe = async () => {
  try {
    const data = await fs.readFile(storagePath, "utf8");
    return JSON.parse(data) as StockItem[];
  } catch {
    if (inMemory) {
      return inMemory;
    }
    return [] as StockItem[];
  }
};

const writeFileSafe = async (rows: StockItem[]) => {
  try {
    await fs.writeFile(storagePath, JSON.stringify(rows, null, 2));
  } catch {
    inMemory = rows;
  }
};

export const getInventory = async () => {
  return readFileSafe();
};

export const addInventory = async (items: StockInput[]) => {
  const current = await readFileSafe();
  const now = new Date().toISOString();
  const next = current.concat(
    items.map((item) => ({
      ...item,
      id: crypto.randomUUID(),
      createdAt: now
    }))
  );
  await writeFileSafe(next);
  return next;
};

export const updateInventory = async (id: string, patch: Partial<StockItem>) => {
  const current = await readFileSafe();
  const next = current.map((row) => (row.id === id ? { ...row, ...patch } : row));
  await writeFileSafe(next);
  return next;
};

export const deleteInventory = async (id: string) => {
  const current = await readFileSafe();
  const next = current.filter((row) => row.id !== id);
  await writeFileSafe(next);
  return next;
};
