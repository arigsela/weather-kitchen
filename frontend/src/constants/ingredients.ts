export interface IngredientCategory {
  name: string;
  emoji: string;
  tags: string[];
}

export const INGREDIENT_CATEGORIES: IngredientCategory[] = [
  {
    name: "Fruits",
    emoji: "🍎",
    tags: [
      "apple",
      "banana",
      "orange",
      "lemon",
      "lime",
      "berries",
      "mango",
      "pineapple",
      "grapes",
      "watermelon",
    ],
  },
  {
    name: "Vegetables",
    emoji: "🥦",
    tags: [
      "carrot",
      "potato",
      "onion",
      "garlic",
      "tomato",
      "broccoli",
      "spinach",
      "pepper",
      "corn",
      "peas",
    ],
  },
  {
    name: "Dairy",
    emoji: "🧀",
    tags: ["milk", "cheese", "butter", "yogurt", "cream", "eggs"],
  },
  {
    name: "Grains",
    emoji: "🌾",
    tags: ["rice", "pasta", "bread", "flour", "oats", "cereal", "tortilla"],
  },
  {
    name: "Protein",
    emoji: "🍗",
    tags: ["chicken", "beef", "pork", "fish", "shrimp", "tofu", "beans", "lentils"],
  },
  {
    name: "Pantry",
    emoji: "🫙",
    tags: [
      "oil",
      "salt",
      "pepper",
      "sugar",
      "honey",
      "soy sauce",
      "vinegar",
      "ketchup",
      "mustard",
      "mayo",
    ],
  },
];
