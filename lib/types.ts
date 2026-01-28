export type Category = "protein" | "veg" | "fruit" | "carb" | "dairy" | "other";

export type DetectedIngredient = {
  name: string;
  qtyGuess: number;
  unitGuess: string;
  categoryGuess: Category;
  confidence: number;
};

export type StockItem = {
  id: string;
  name: string;
  category: Category;
  qty: number;
  unit: string;
  expiresAt?: string | null;
  note?: string | null;
  createdAt: string;
};

export type StockInput = Omit<StockItem, "id" | "createdAt">;

export type Recipe = {
  title: string;
  ingredients: Array<{
    name: string;
    qty: number;
    unit: string;
    optional?: boolean;
  }>;
  nutritionProfile: {
    proteinScore: number;
    vegServings: number;
    carbServings: number;
    fiberScore: number;
  };
  steps: string[];
};

export type MenuResult = {
  menu: Recipe[];
  nutrition: {
    proteinCoverage: number;
    vegServings: number;
    carbServings: number;
    fiberScore: number;
  };
  shoppingList: Array<{ name: string; qty: number; unit: string }>;
  explanation: string[];
};
