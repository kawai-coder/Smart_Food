import { NextResponse } from "next/server";
import { detectIngredients } from "@/lib/ai";

export const POST = async (request: Request) => {
  const body = (await request.json()) as { imageName?: string };
  const imageName = body.imageName ?? "fridge.jpg";
  const result = await detectIngredients(imageName);
  return NextResponse.json(result);
};
