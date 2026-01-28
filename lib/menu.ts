import recipes from "@/data/recipes.json";
import { MenuResult, Recipe, StockItem } from "./types";

const normalizeName = (name: string) => name.trim().toLowerCase();

const scoreRecipe = (recipe: Recipe, inventoryMap: Map<string, number>) => {
  let hits = 0;
  recipe.ingredients.forEach((ingredient) => {
    if (inventoryMap.has(normalizeName(ingredient.name))) {
      hits += 1;
    }
  });
  return hits;
};

const buildShoppingList = (selected: Recipe[], inventoryMap: Map<string, number>) => {
  const list: Record<string, { name: string; qty: number; unit: string }> = {};
  selected.forEach((recipe) => {
    recipe.ingredients.forEach((ingredient) => {
      const key = normalizeName(ingredient.name);
      if (!inventoryMap.has(key)) {
        if (!list[key]) {
          list[key] = {
            name: ingredient.name,
            qty: ingredient.qty,
            unit: ingredient.unit
          };
        } else {
          list[key].qty += ingredient.qty;
        }
      }
    });
  });
  return Object.values(list);
};

const summarizeNutrition = (selected: Recipe[]) => {
  const totals = selected.reduce(
    (acc, recipe) => {
      acc.proteinCoverage += recipe.nutritionProfile.proteinScore;
      acc.vegServings += recipe.nutritionProfile.vegServings;
      acc.carbServings += recipe.nutritionProfile.carbServings;
      acc.fiberScore += recipe.nutritionProfile.fiberScore;
      return acc;
    },
    { proteinCoverage: 0, vegServings: 0, carbServings: 0, fiberScore: 0 }
  );

  return {
    proteinCoverage: Math.min(100, totals.proteinCoverage * 10),
    vegServings: Math.min(6, totals.vegServings),
    carbServings: Math.min(4, totals.carbServings),
    fiberScore: Math.min(100, totals.fiberScore * 10)
  };
};

export const generateMenu = (inventory: StockItem[]): MenuResult => {
  const inventoryMap = new Map<string, number>();
  inventory.forEach((item) => {
    inventoryMap.set(normalizeName(item.name), item.qty);
  });

  const sorted = [...(recipes as Recipe[])].sort(
    (a, b) => scoreRecipe(b, inventoryMap) - scoreRecipe(a, inventoryMap)
  );

  const proteinDish = sorted.find((recipe) => recipe.nutritionProfile.proteinScore >= 7);
  const vegDish = sorted.find((recipe) => recipe.nutritionProfile.vegServings >= 1);
  const carbOrSoup = sorted.find((recipe) => recipe.nutritionProfile.carbServings >= 1);

  const menu = [proteinDish, vegDish, carbOrSoup]
    .filter((item, index, self) => item && self.indexOf(item) === index)
    .slice(0, 3) as Recipe[];

  const explanation = [
    "优先选择库存中已有食材命中率高的菜谱，减少浪费。",
    "确保至少一个高蛋白菜和一个蔬菜菜，补足蛋白与纤维。",
    "补充主食或汤品，让一餐更均衡。"
  ];

  return {
    menu,
    nutrition: summarizeNutrition(menu),
    shoppingList: buildShoppingList(menu, inventoryMap),
    explanation
  };
};
