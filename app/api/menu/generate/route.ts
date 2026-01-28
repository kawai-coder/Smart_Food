import { NextResponse } from "next/server";
import { generateMenu } from "@/lib/menu";
import { getInventory } from "@/lib/storage";

export const POST = async () => {
  const inventory = await getInventory();
  const menu = generateMenu(inventory);
  return NextResponse.json(menu);
};
