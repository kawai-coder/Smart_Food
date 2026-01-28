import { NextResponse } from "next/server";
import { addInventory, deleteInventory, getInventory, updateInventory } from "@/lib/storage";
import { StockInput, StockItem } from "@/lib/types";

export const GET = async () => {
  const items = await getInventory();
  return NextResponse.json(items);
};

export const POST = async (request: Request) => {
  const body = (await request.json()) as { items: StockInput[] };
  const items = await addInventory(body.items ?? []);
  return NextResponse.json(items);
};

export const PUT = async (request: Request) => {
  const body = (await request.json()) as { id: string; patch: Partial<StockItem> };
  const items = await updateInventory(body.id, body.patch ?? {});
  return NextResponse.json(items);
};

export const DELETE = async (request: Request) => {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");
  if (!id) {
    return NextResponse.json({ error: "Missing id" }, { status: 400 });
  }
  const items = await deleteInventory(id);
  return NextResponse.json(items);
};
