import { DetectedIngredient } from "./types";

const mockIngredients = [
  { name: "鸡蛋", unit: "个", category: "protein" },
  { name: "牛奶", unit: "盒", category: "dairy" },
  { name: "番茄", unit: "个", category: "veg" },
  { name: "菠菜", unit: "把", category: "veg" },
  { name: "鸡胸肉", unit: "块", category: "protein" },
  { name: "大米", unit: "杯", category: "carb" },
  { name: "洋葱", unit: "个", category: "veg" },
  { name: "酸奶", unit: "杯", category: "dairy" },
  { name: "黄瓜", unit: "根", category: "veg" },
  { name: "土豆", unit: "个", category: "carb" },
  { name: "胡萝卜", unit: "根", category: "veg" }
] as const;

const randomBetween = (min: number, max: number) =>
  Math.round((min + Math.random() * (max - min)) * 100) / 100;

const mockDetect = (imageName: string): DetectedIngredient[] => {
  const seed = imageName.length % mockIngredients.length;
  const count = 6 + (seed % 5);
  const selected = [...mockIngredients]
    .sort((a, b) => (a.name > b.name ? 1 : -1))
    .slice(seed, seed + count);

  return selected.map((item, index) => ({
    name: item.name,
    qtyGuess: index % 3 === 0 ? 1 : index % 3 === 1 ? 2 : 3,
    unitGuess: item.unit,
    categoryGuess: item.category,
    confidence: randomBetween(0.55, 0.95)
  }));
};

const realDetect = async (imageName: string) => {
  const endpoint = process.env.REAL_VISION_ENDPOINT;
  if (!endpoint) {
    return null;
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ imageName })
    });
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as DetectedIngredient[];
    return data;
  } catch {
    return null;
  }
};

export const detectIngredients = async (imageName: string) => {
  const real = await realDetect(imageName);
  if (real && real.length > 0) {
    return real;
  }
  return mockDetect(imageName);
};
