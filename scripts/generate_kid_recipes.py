#!/usr/bin/env python3
"""
Generate kid-friendly recipes for Weather Kitchen.
Uses compact template data expanded programmatically.
"""

import json
import sys
from pathlib import Path

# ── Weather config ──────────────────────────────────────────────────────────

WHY = {
    "sunny": [
        "Perfect for a warm sunny day!",
        "Light and refreshing when the sun is shining",
        "A cool treat for hot sunny weather",
        "Great for a sunny picnic outside",
        "Bright and cheerful like the sunshine",
        "Easy to enjoy on a beautiful sunny day",
        "Fresh flavors for sunny afternoons",
        "Sun's out, yum's out!",
        "A sunny day classic the whole family loves",
        "Nothing tastes better on a sunny day",
    ],
    "rainy": [
        "Warm and cozy for a rainy day inside",
        "Nothing beats comfort food on a rainy day",
        "Perfect rainy day cooking project",
        "Curl up and enjoy on a rainy afternoon",
        "Warm your tummy on a chilly rainy day",
        "The ultimate rainy day treat",
        "Makes a rainy day feel like a warm hug",
        "Cozy kitchen vibes for rainy weather",
        "Rainy days are made for cooking!",
        "Stay warm and full on a rainy day",
    ],
    "snowy": [
        "Hearty and warming for cold snowy weather",
        "The perfect treat after playing in the snow",
        "Warm up after a snowy adventure!",
        "Cozy comfort for snowy days",
        "Hot and delicious for freezing cold days",
        "Snow day special treat!",
        "Warming you from the inside out",
        "A snow day isn't complete without this",
        "Bundle up and dig in on a snowy day",
        "Perfect fuel for snow fort building",
    ],
    "cloudy": [
        "A tasty pick-me-up for a cloudy day",
        "Brightens up any gloomy afternoon",
        "Makes a cloudy day so much better",
        "Easy comfort for overcast days",
        "A little sunshine on your plate for cloudy days",
        "Perfect for a laid-back cloudy day",
        "Cloudy days call for yummy food",
        "Turn a gray day into a great day",
        "Simple and satisfying for cloudy weather",
        "The best thing about a cloudy day",
    ],
    "windy": [
        "Easy to make and enjoy on a blustery day",
        "Cozy indoor cooking for windy weather",
        "Stay inside and cook on a windy day",
        "Hearty enough to keep you going on windy days",
        "A blustery day calls for good food",
        "Wind outside, warmth inside!",
        "Perfect indoor project for windy weather",
        "Let the wind blow while you cook something great",
        "Windy day? Stay in and make this!",
        "Blustery weather comfort food",
    ],
}

TIPS = {
    "baking": [
        "Ask a grown-up to help with the oven, but YOU get to do all the mixing! That's the fun part! 🥄",
        "Always preheat the oven first — it needs to warm up just like you do in the morning! 🌡️",
        "Use a toothpick to check if it's done — if it comes out clean, you're a baking genius! ✨",
        "Measure carefully! Baking is like a science experiment — every bit matters! 🔬",
        "Room temperature ingredients mix better — take the butter out early! 🧈",
        "Don't open the oven too much — peeking lets the heat escape! 👀",
        "Sift your flour for the fluffiest results ever! It's like making flour clouds! ☁️",
        "Let it cool before frosting or it'll be a melty mess — patience, young chef! ⏰",
    ],
    "mixing": [
        "If you can stir, you can cook! Start slow and speed up — you're basically a human mixer! 🌀",
        "Mix dry ingredients first, then add wet — it's the chef's secret! 🤫",
        "Fold gently for fluffy results — pretend you're tucking the batter into bed! 🛏️",
        "Stir in one direction for the smoothest mix ever! Round and round you go! 🔄",
        "Crack eggs on a flat surface, not the bowl edge — keeps shell bits out! 🥚",
        "Taste as you go! Every great chef does it (with clean spoons of course)! 👅",
    ],
    "safety": [
        "Wash your hands first — chef rule #1! Clean hands make the best food! 🧼",
        "Always ask a grown-up to help with sharp knives and hot stoves! Safety first, chef! 🔪",
        "Use oven mitts every single time — your hands will thank you! 🧤",
        "Turn pot handles inward so nobody bumps them — smart chefs think ahead! 🍳",
        "Hot things stay hot for a while — let it cool before touching! 🌡️",
        "Keep a clean kitchen — wipe spills right away so nobody slips! 🧹",
    ],
    "fun": [
        "Make it your own! Add your favorite toppings and be creative! 🎨",
        "Cooking is like art — there's no wrong way to do it! 🖌️",
        "Get the whole family involved — cooking is more fun together! 👨‍👩‍👧‍👦",
        "Take a picture of your creation before eating it — chef's portfolio! 📸",
        "Put on your favorite music while cooking — kitchen dance party! 💃",
        "Wear an apron so your clothes stay clean for the taste test! 👨‍🍳",
        "The secret ingredient is always love (and maybe extra cheese)! ❤️",
        "Give your creation a silly name — food tastes better with a fun name! 😄",
    ],
    "technique": [
        "The secret to perfect pancakes? Don't flip until you see bubbles! 🫧",
        "Let the pan get hot before adding food — sizzle means it's ready! 🔥",
        "Pat meat dry before cooking for the crispiest outside! 🥩",
        "Don't squish your burger — all the juicy goodness will escape! 🍔",
        "Pasta water should be salty like the ocean — that's where the flavor starts! 🌊",
        "Let meat rest after cooking — it gets even juicier! ⏳",
        "Toast your bread or buns for extra crunch — trust me on this one! 🍞",
        "Shred cheese yourself — it melts way better than the pre-shredded stuff! 🧀",
    ],
    "cold": [
        "Freeze fruit ahead of time for the thickest, creamiest smoothie ever! 🧊",
        "Use frozen bananas for ice cream texture without the ice cream! 🍌",
        "Blend in stages — liquids first, frozen stuff last! 🥤",
        "Chill your bowl for extra cold treats! Pop it in the freezer for 10 minutes! ❄️",
    ],
    "no_cook": [
        "No cooking needed! Just mix, layer, or assemble — easy peasy! 🙌",
        "This one's so easy you could almost make it with your eyes closed! (Don't though!) 😆",
        "No oven, no stove, no problem! Just your hands and some yummy ingredients! 👐",
        "The fridge does all the work while you play — come back to deliciousness! 🎮",
    ],
}

# ── Emoji map ───────────────────────────────────────────────────────────────

EMOJI_MAP = {
    "pancake": "🥞", "waffle": "🧇", "french toast": "🥞", "egg": "🍳",
    "oatmeal": "🥣", "smoothie": "🥤", "yogurt": "🥣", "muffin": "🧁",
    "crepe": "🥞", "granola": "🥣", "hash brown": "🥔", "toast": "🍞",
    "pizza": "🍕", "pasta": "🍝", "spaghetti": "🍝", "mac": "🧀",
    "grilled cheese": "🧀", "sandwich": "🍔", "burger": "🍔",
    "taco": "🌮", "burrito": "🌯", "wrap": "🌯", "quesadilla": "🌮",
    "chicken": "🍗", "nugget": "🍗", "fish": "🐟", "salmon": "🐟",
    "shrimp": "🦐", "steak": "🥩", "beef": "🥩", "pork": "🍖",
    "rib": "🍖", "meatball": "🍝", "meatloaf": "🥩", "lamb": "🥩",
    "soup": "🍜", "stew": "🍜", "chili": "🌶️", "ramen": "🍜",
    "noodle": "🍜", "rice": "🍚", "fried rice": "🍳",
    "salad": "🥗", "corn": "🌽", "potato": "🥔",
    "cookie": "🍪", "brownie": "🍫", "cupcake": "🧁", "cake": "🍰",
    "muffin_snack": "🧁", "bread": "🍞", "donut": "🍩",
    "ice cream": "🍦", "sundae": "🍦", "milkshake": "🥤",
    "hot chocolate": "☕", "s'more": "🍫", "pudding": "🍮",
    "popcorn": "🍿", "pretzel": "🥨", "popsicle": "🍧",
    "fruit": "🍓", "apple": "🍎", "banana": "🍌",
    "trail mix": "🥜", "energy": "⚡", "chip": "🍟",
    "nachos": "🌮", "dip": "🫕", "roll": "🥟",
    "casserole": "🥘", "pie": "🥧", "lasagna": "🍝",
    "fajita": "🌮", "enchilada": "🌯", "curry": "🍛",
    "stir fry": "🥘", "kabob": "🍢", "skewer": "🍢",
}


def get_emoji(name):
    nl = name.lower()
    for key, emoji in EMOJI_MAP.items():
        if key in nl:
            return emoji
    return "🍽️"


def get_tip(category, name, idx):
    nl = name.lower()
    if any(w in nl for w in ["cookie", "brownie", "cake", "cupcake", "muffin", "bread", "bar", "pie", "donut", "churro", "eclair", "cream puff"]):
        pool = TIPS["baking"]
    elif any(w in nl for w in ["smoothie", "popsicle", "slushie", "ice cream", "frozen", "milkshake"]):
        pool = TIPS["cold"]
    elif any(w in nl for w in ["trail mix", "fruit", "parfait", "crackers", "nachos", "dip"]):
        pool = TIPS["no_cook"]
    elif any(w in nl for w in ["stir", "fry", "grill", "bake", "roast", "sear", "crispy"]):
        pool = TIPS["technique"]
    elif category == "snack":
        pool = TIPS["fun"]
    elif any(w in nl for w in ["stove", "hot", "boil", "oven"]):
        pool = TIPS["safety"]
    else:
        pools = [TIPS["mixing"], TIPS["fun"], TIPS["technique"], TIPS["safety"]]
        pool = pools[idx % len(pools)]
    return pool[idx % len(pool)]


# ── Recipe templates ────────────────────────────────────────────────────────
# Format: (name, weather, category, ingredients, steps, tags)
# This is the compact data. We define all 500 recipes as tuples.

RECIPES = []


def R(name, weather, category, ingredients, steps, tags):
    RECIPES.append((name, weather, category, ingredients, steps, tags))


# ═══════════════════════ BREAKFAST ═══════════════════════════════════════════

R("Blueberry Pancakes", "sunny", "breakfast",
  ["1½ cups flour", "1 cup milk", "1 egg", "1 cup fresh blueberries", "2 tbsp sugar", "1 tsp baking powder", "2 tbsp butter (melted)"],
  ["Mix flour, sugar, and baking powder in a bowl", "Whisk egg, milk, and melted butter together", "Combine wet and dry ingredients until just mixed", "Fold in blueberries gently", "Pour batter onto a buttered griddle over medium heat", "Flip when bubbles form on top, cook until golden", "Serve with maple syrup and extra blueberries"],
  ["easy", "vegetarian", "sweet"])

R("Chocolate Chip Pancakes", "cloudy", "breakfast",
  ["1½ cups flour", "1 cup milk", "1 egg", "½ cup chocolate chips", "2 tbsp sugar", "1 tsp baking powder", "2 tbsp butter"],
  ["Mix flour, sugar, and baking powder", "Whisk egg, milk, and melted butter", "Combine wet and dry ingredients", "Stir in chocolate chips", "Cook on a buttered griddle until bubbles form", "Flip and cook until golden brown", "Stack and serve with whipped cream"],
  ["easy", "vegetarian", "sweet", "fun"])

R("Banana Pancakes", "cloudy", "breakfast",
  ["1½ cups flour", "1 ripe banana", "1 cup milk", "1 egg", "1 tsp baking powder", "1 tsp cinnamon", "2 tbsp butter"],
  ["Mash banana in a bowl", "Mix in egg and milk", "Add flour, baking powder, and cinnamon", "Stir until just combined", "Cook on a buttered griddle over medium heat", "Flip when edges look set and bubbles pop", "Top with sliced bananas and honey"],
  ["easy", "vegetarian", "healthy"])

R("Classic Buttermilk Pancakes", "sunny", "breakfast",
  ["2 cups flour", "1½ cups buttermilk", "2 eggs", "3 tbsp sugar", "1 tsp baking soda", "3 tbsp melted butter", "Pinch of salt"],
  ["Mix flour, sugar, baking soda, and salt", "Whisk buttermilk, eggs, and butter separately", "Pour wet into dry and stir gently", "Let batter rest for 5 minutes", "Cook on medium heat until bubbly on top", "Flip and cook 2 more minutes", "Serve in a tall stack with syrup"],
  ["easy", "vegetarian", "30-minute"])

R("Strawberry Pancakes", "sunny", "breakfast",
  ["1½ cups flour", "1 cup milk", "1 egg", "1 cup diced strawberries", "2 tbsp sugar", "1 tsp baking powder", "Whipped cream"],
  ["Mix dry ingredients together", "Whisk wet ingredients", "Combine and stir until just mixed", "Fold in diced strawberries", "Cook on griddle until golden", "Flip carefully and finish cooking", "Top with whipped cream and fresh strawberries"],
  ["easy", "vegetarian", "sweet", "fun"])

R("Pumpkin Spice Pancakes", "rainy", "breakfast",
  ["1½ cups flour", "½ cup pumpkin puree", "1 cup milk", "1 egg", "1 tsp pumpkin pie spice", "2 tbsp brown sugar", "1 tsp baking powder"],
  ["Mix flour, spice, brown sugar, and baking powder", "Whisk pumpkin, milk, and egg together", "Combine wet and dry ingredients", "Cook on buttered griddle over medium heat", "Flip when edges are set", "Cook until golden on both sides", "Drizzle with maple syrup"],
  ["easy", "vegetarian", "comfort-food"])

R("Apple Cinnamon Pancakes", "rainy", "breakfast",
  ["1½ cups flour", "1 apple (peeled and diced)", "1 cup milk", "1 egg", "1 tsp cinnamon", "2 tbsp sugar", "1 tsp baking powder"],
  ["Mix flour, cinnamon, sugar, and baking powder", "Whisk milk and egg together", "Combine and fold in diced apple", "Cook on medium heat griddle", "Flip when bubbles appear", "Cook until both sides are golden", "Serve with cinnamon sugar on top"],
  ["easy", "vegetarian", "comfort-food"])

R("Classic Waffles", "sunny", "breakfast",
  ["2 cups flour", "1¾ cups milk", "2 eggs", "½ cup melted butter", "2 tbsp sugar", "1 tbsp baking powder", "1 tsp vanilla"],
  ["Preheat waffle iron", "Mix flour, sugar, and baking powder", "Whisk milk, eggs, butter, and vanilla", "Combine wet and dry ingredients", "Pour batter into hot waffle iron", "Cook until golden and crispy", "Serve with butter and syrup"],
  ["easy", "vegetarian", "sweet"])

R("Chocolate Waffles", "cloudy", "breakfast",
  ["2 cups flour", "¼ cup cocoa powder", "1¾ cups milk", "2 eggs", "½ cup melted butter", "3 tbsp sugar", "1 tbsp baking powder"],
  ["Preheat waffle iron", "Mix flour, cocoa, sugar, and baking powder", "Whisk milk, eggs, and melted butter", "Combine and stir until smooth", "Pour into waffle iron", "Cook until firm and crispy", "Top with whipped cream and strawberries"],
  ["easy", "vegetarian", "sweet", "fun"])

R("Berry Waffles", "sunny", "breakfast",
  ["2 cups flour", "1¾ cups milk", "2 eggs", "½ cup mixed berries", "½ cup melted butter", "2 tbsp sugar", "1 tbsp baking powder"],
  ["Preheat waffle iron", "Mix dry ingredients in a bowl", "Whisk wet ingredients separately", "Combine and fold in berries", "Cook in waffle iron until golden", "Serve with extra berries on top", "Drizzle with honey or syrup"],
  ["easy", "vegetarian", "healthy"])

R("French Toast Sticks", "rainy", "breakfast",
  ["4 thick bread slices", "2 eggs", "½ cup milk", "1 tsp cinnamon", "1 tsp vanilla", "2 tbsp butter", "Maple syrup for dipping"],
  ["Cut bread into thick sticks", "Whisk eggs, milk, cinnamon, and vanilla", "Dip each stick in egg mixture", "Melt butter in a pan over medium heat", "Cook sticks until golden on all sides", "Turn them gently with tongs", "Serve with maple syrup for dipping"],
  ["easy", "vegetarian", "fun", "30-minute"])

R("Classic French Toast", "rainy", "breakfast",
  ["6 bread slices", "3 eggs", "¾ cup milk", "1 tsp cinnamon", "1 tsp vanilla", "2 tbsp butter", "Powdered sugar"],
  ["Whisk eggs, milk, cinnamon, and vanilla", "Melt butter in a large pan", "Dip each bread slice in egg mixture", "Cook on medium heat for 2-3 minutes per side", "Flip when golden brown", "Dust with powdered sugar", "Serve with fruit and syrup"],
  ["easy", "vegetarian", "comfort-food"])

R("Berry Oatmeal Bowl", "rainy", "breakfast",
  ["1 cup rolled oats", "2 cups milk", "1 cup mixed berries", "2 tbsp honey", "1 tsp cinnamon", "Pinch of salt"],
  ["Bring milk to a simmer in a pot", "Stir in oats and salt", "Cook for 5 minutes, stirring often", "Add cinnamon and honey", "Pour into bowls", "Top with fresh berries", "Drizzle extra honey on top"],
  ["easy", "healthy", "vegetarian", "15-minute"])

R("Maple Brown Sugar Oatmeal", "snowy", "breakfast",
  ["1 cup rolled oats", "2 cups milk", "2 tbsp brown sugar", "2 tbsp maple syrup", "1 tsp cinnamon", "2 tbsp butter"],
  ["Heat milk in a pot until simmering", "Stir in oats and cook 5 minutes", "Add brown sugar and cinnamon", "Stir in butter until melted", "Pour into bowls", "Drizzle maple syrup on top"],
  ["easy", "vegetarian", "comfort-food", "15-minute"])

R("Tropical Smoothie Bowl", "sunny", "breakfast",
  ["1 frozen banana", "1 cup frozen mango", "½ cup coconut milk", "¼ cup granola", "Fresh fruit for topping", "1 tbsp honey"],
  ["Blend banana, mango, and coconut milk until thick", "Pour into a bowl", "Top with granola", "Add fresh fruit slices", "Drizzle with honey", "Eat with a spoon like ice cream!"],
  ["easy", "healthy", "vegetarian", "no-cook"])

R("Chocolate Banana Smoothie Bowl", "sunny", "breakfast",
  ["2 frozen bananas", "2 tbsp cocoa powder", "½ cup milk", "2 tbsp peanut butter", "Granola and banana slices for topping"],
  ["Blend frozen bananas, cocoa, milk, and PB until thick", "Pour into a bowl", "Top with granola", "Add banana slices", "Sprinkle with chocolate chips if you want!"],
  ["easy", "healthy", "vegetarian", "no-cook", "fun"])

R("Breakfast Burrito Supreme", "windy", "breakfast",
  ["4 flour tortillas", "4 eggs", "½ cup shredded cheese", "4 slices bacon (cooked)", "¼ cup salsa", "2 tbsp butter"],
  ["Scramble eggs in butter over medium heat", "Chop cooked bacon into bits", "Warm tortillas in microwave for 15 seconds", "Fill each tortilla with eggs, bacon, and cheese", "Add a spoonful of salsa", "Roll up tightly, tucking in the sides", "Cut in half and enjoy"],
  ["easy", "protein", "30-minute"])

R("Cheesy Egg Muffins", "cloudy", "breakfast",
  ["6 eggs", "½ cup shredded cheddar", "¼ cup diced ham", "¼ cup diced peppers", "Salt and pepper", "Cooking spray"],
  ["Preheat oven to 375°F", "Spray muffin tin with cooking spray", "Whisk eggs with salt and pepper", "Divide ham and peppers into muffin cups", "Pour egg mixture over the fillings", "Sprinkle cheese on top", "Bake for 15-18 minutes until set"],
  ["easy", "protein", "make-ahead", "30-minute"])

R("Yogurt Berry Parfait", "sunny", "breakfast",
  ["2 cups vanilla yogurt", "1 cup granola", "1 cup mixed berries", "2 tbsp honey"],
  ["Spoon yogurt into the bottom of glasses", "Add a layer of granola", "Add a layer of berries", "Repeat layers until glasses are full", "Drizzle honey on top", "Serve immediately"],
  ["easy", "healthy", "vegetarian", "no-cook", "15-minute"])

R("Avocado Toast Faces", "sunny", "breakfast",
  ["2 slices bread", "1 ripe avocado", "Cherry tomatoes", "Cucumber slices", "Salt and pepper", "Lemon juice"],
  ["Toast the bread until golden", "Mash avocado with lemon juice, salt, and pepper", "Spread avocado on toast", "Use cherry tomatoes for eyes", "Use cucumber for a mouth", "Get creative with your face design!"],
  ["easy", "vegetarian", "healthy", "fun", "15-minute"])

R("PB&J French Toast Roll-Ups", "cloudy", "breakfast",
  ["4 slices white bread (crusts removed)", "2 tbsp peanut butter", "2 tbsp jelly", "2 eggs", "¼ cup milk", "1 tsp cinnamon", "2 tbsp butter"],
  ["Flatten bread slices with a rolling pin", "Spread PB on two slices and jelly on the others", "Roll each slice up tightly", "Whisk eggs, milk, and cinnamon", "Dip each roll in egg mixture", "Cook in butter over medium heat until golden all around", "Slice in half and serve"],
  ["easy", "fun", "sweet", "30-minute"])

R("Blueberry Muffins", "rainy", "breakfast",
  ["2 cups flour", "¾ cup sugar", "1 cup blueberries", "½ cup milk", "⅓ cup vegetable oil", "2 eggs", "2 tsp baking powder"],
  ["Preheat oven to 375°F", "Mix flour, sugar, and baking powder", "Whisk milk, oil, and eggs together", "Combine wet and dry — don't overmix!", "Fold in blueberries gently", "Fill muffin cups ¾ full", "Bake 20-25 minutes until golden on top"],
  ["easy", "vegetarian", "baking", "sweet"])

R("Banana Chocolate Chip Muffins", "rainy", "breakfast",
  ["2 ripe bananas", "1½ cups flour", "½ cup sugar", "½ cup chocolate chips", "⅓ cup oil", "1 egg", "1 tsp baking soda"],
  ["Preheat oven to 350°F", "Mash bananas in a large bowl", "Stir in oil, egg, and sugar", "Add flour and baking soda, mix gently", "Fold in chocolate chips", "Spoon into lined muffin tin", "Bake for 20 minutes until a toothpick comes out clean"],
  ["easy", "vegetarian", "baking", "sweet"])

R("Overnight Oats", "sunny", "breakfast",
  ["1 cup rolled oats", "1 cup milk", "½ cup yogurt", "2 tbsp honey", "½ cup berries", "1 tsp chia seeds"],
  ["Mix oats, milk, yogurt, and honey in a jar", "Stir in chia seeds", "Cover and put in the fridge overnight", "In the morning, stir it up", "Top with fresh berries", "Eat cold right from the jar!"],
  ["easy", "healthy", "vegetarian", "no-cook", "make-ahead"])

R("Mini Cinnamon Rolls", "snowy", "breakfast",
  ["1 can crescent roll dough", "3 tbsp butter (softened)", "¼ cup brown sugar", "1 tbsp cinnamon", "½ cup powdered sugar", "1 tbsp milk"],
  ["Preheat oven to 375°F", "Unroll dough and spread with soft butter", "Mix brown sugar and cinnamon, sprinkle over dough", "Roll up tightly and slice into 1-inch pieces", "Place in a greased muffin tin", "Bake 12-15 minutes until golden", "Mix powdered sugar and milk for glaze and drizzle on top"],
  ["easy", "sweet", "baking", "fun"])

R("Sunrise Mango Smoothie", "sunny", "breakfast",
  ["1 cup frozen mango", "1 banana", "1 cup orange juice", "½ cup yogurt", "1 tbsp honey"],
  ["Add all ingredients to a blender", "Blend on high until smooth and creamy", "Pour into a tall glass", "Add a straw and enjoy!", "Garnish with a mango slice if you're fancy"],
  ["easy", "healthy", "15-minute", "no-cook"])

R("Berry Banana Power Smoothie", "sunny", "breakfast",
  ["1 cup mixed frozen berries", "1 banana", "1 cup milk", "2 tbsp honey", "1 tbsp peanut butter"],
  ["Put all ingredients in a blender", "Blend until completely smooth", "Pour into your favorite cup", "Drink up for super power energy!"],
  ["easy", "healthy", "15-minute", "no-cook", "protein"])

R("Egg in a Hole Toast", "cloudy", "breakfast",
  ["2 slices bread", "2 eggs", "2 tbsp butter", "Salt and pepper"],
  ["Cut a circle out of each bread slice with a cup", "Melt butter in a pan over medium heat", "Place bread in the pan", "Crack an egg into each hole", "Cook until the egg white sets, about 3 minutes", "Carefully flip and cook 1 more minute", "Season with salt and pepper"],
  ["easy", "protein", "15-minute", "fun"])

R("Cheesy Scrambled Eggs", "windy", "breakfast",
  ["4 eggs", "¼ cup shredded cheese", "2 tbsp milk", "1 tbsp butter", "Salt and pepper", "Chives for topping"],
  ["Whisk eggs, milk, salt, and pepper", "Melt butter in a pan over medium-low heat", "Pour in egg mixture", "Stir slowly with a spatula as they cook", "When almost set, stir in cheese", "Remove from heat while still slightly soft", "Top with chives and serve"],
  ["easy", "protein", "15-minute"])

R("Mini Breakfast Pizzas", "cloudy", "breakfast",
  ["4 English muffins (halved)", "4 eggs (scrambled)", "½ cup shredded cheese", "¼ cup diced ham", "2 tbsp butter", "Ketchup (optional)"],
  ["Preheat oven to broil", "Toast English muffin halves", "Scramble eggs in butter", "Top each muffin half with scrambled eggs", "Sprinkle ham and cheese on top", "Broil for 2 minutes until cheese melts", "Serve with ketchup if you like!"],
  ["easy", "fun", "protein", "15-minute"])

# ═══════════════════════ LUNCH ═══════════════════════════════════════════════

R("Classic Mac and Cheese", "rainy", "lunch",
  ["2 cups elbow macaroni", "2 cups shredded cheddar", "2 tbsp butter", "2 tbsp flour", "2 cups milk", "Salt and pepper"],
  ["Cook macaroni according to package, drain", "Melt butter in the pot over medium heat", "Stir in flour and cook 1 minute", "Slowly pour in milk, stirring constantly", "Cook until thickened, about 5 minutes", "Stir in cheese until melted and smooth", "Add pasta back and stir to coat"],
  ["easy", "vegetarian", "comfort-food", "30-minute"])

R("Bacon Mac and Cheese", "rainy", "lunch",
  ["2 cups elbow macaroni", "2 cups shredded cheddar", "6 slices bacon (cooked, crumbled)", "2 tbsp butter", "2 tbsp flour", "2 cups milk"],
  ["Cook macaroni and drain", "Melt butter, stir in flour, cook 1 minute", "Add milk slowly, stir until thick", "Melt in cheese until creamy", "Stir in cooked pasta", "Top with crumbled bacon", "Stir and serve hot"],
  ["easy", "comfort-food", "protein"])

R("BBQ Chicken Mac", "windy", "lunch",
  ["2 cups elbow macaroni", "1 cup shredded cooked chicken", "½ cup BBQ sauce", "2 cups shredded cheddar", "2 cups milk", "2 tbsp butter", "2 tbsp flour"],
  ["Cook and drain macaroni", "Make cheese sauce: melt butter, add flour, add milk, add cheese", "Toss chicken with BBQ sauce", "Combine pasta with cheese sauce", "Top with BBQ chicken", "Stir gently to combine", "Serve warm"],
  ["easy", "comfort-food", "protein"])

R("Classic Grilled Cheese", "rainy", "lunch",
  ["2 slices bread", "2 slices cheddar cheese", "1 tbsp butter"],
  ["Butter one side of each bread slice", "Place one slice butter-side down in a pan", "Layer cheese on top", "Put second slice on top, butter-side up", "Cook over medium heat until golden, about 3 minutes", "Flip carefully and cook the other side", "Cut in half and serve with tomato soup"],
  ["easy", "vegetarian", "15-minute", "comfort-food"])

R("Pizza Grilled Cheese", "rainy", "lunch",
  ["2 slices bread", "2 slices mozzarella", "2 tbsp marinara sauce", "6 mini pepperoni slices", "1 tbsp butter"],
  ["Butter one side of each bread slice", "Spread marinara on the inside of one slice", "Layer mozzarella and pepperoni", "Top with second slice, butter-side out", "Cook over medium heat until golden", "Flip and cook until cheese is melty", "Dip in extra marinara sauce"],
  ["easy", "fun", "15-minute"])

R("PB&J Sandwich", "sunny", "lunch",
  ["2 slices bread", "2 tbsp peanut butter", "2 tbsp jelly or jam"],
  ["Spread peanut butter on one slice of bread", "Spread jelly on the other slice", "Press the two slices together", "Cut diagonally for fancy triangles", "Serve with a glass of milk"],
  ["easy", "vegetarian", "no-cook", "15-minute"])

R("Turkey and Cheese Sandwich", "sunny", "lunch",
  ["2 slices bread", "3 slices turkey", "1 slice cheese", "Lettuce leaf", "1 tbsp mayo", "1 tbsp mustard"],
  ["Spread mayo on one slice, mustard on the other", "Layer turkey on the bottom slice", "Add cheese and lettuce", "Top with the other bread slice", "Cut in half", "Serve with chips or fruit"],
  ["easy", "protein", "no-cook", "15-minute"])

R("Cheese Quesadilla", "sunny", "lunch",
  ["2 flour tortillas", "1 cup shredded cheese", "1 tbsp butter", "Salsa for dipping"],
  ["Sprinkle cheese on one tortilla", "Top with the second tortilla", "Melt butter in a pan over medium heat", "Cook quesadilla 2-3 minutes per side", "Press down with a spatula", "Cut into wedges", "Serve with salsa"],
  ["easy", "vegetarian", "15-minute"])

R("Chicken Quesadilla", "sunny", "lunch",
  ["2 flour tortillas", "1 cup shredded cheese", "½ cup cooked shredded chicken", "2 tbsp salsa", "1 tbsp butter"],
  ["Mix chicken with salsa", "Sprinkle cheese on one tortilla", "Add chicken mixture", "Top with more cheese and second tortilla", "Cook in buttered pan 3 minutes per side", "Cut into triangles", "Serve with sour cream"],
  ["easy", "protein", "15-minute"])

R("Spaghetti and Marinara", "windy", "lunch",
  ["8 oz spaghetti", "2 cups marinara sauce", "2 tbsp parmesan cheese", "1 tbsp olive oil", "Salt"],
  ["Boil water with a pinch of salt", "Cook spaghetti according to package", "Drain and toss with olive oil", "Heat marinara sauce in a pan", "Pour sauce over spaghetti", "Sprinkle parmesan on top", "Twirl with a fork and enjoy!"],
  ["easy", "vegetarian", "30-minute"])

R("Butter Noodles with Parmesan", "cloudy", "lunch",
  ["8 oz egg noodles", "3 tbsp butter", "¼ cup parmesan cheese", "Salt and pepper", "Fresh parsley"],
  ["Cook noodles according to package", "Drain, saving ¼ cup pasta water", "Toss hot noodles with butter", "Add parmesan and a splash of pasta water", "Stir until creamy", "Season with salt and pepper", "Sprinkle parsley on top"],
  ["easy", "vegetarian", "15-minute", "comfort-food"])

R("Creamy Alfredo Pasta", "rainy", "lunch",
  ["8 oz fettuccine", "2 tbsp butter", "1 cup heavy cream", "1 cup parmesan cheese", "2 cloves garlic", "Salt and pepper"],
  ["Cook fettuccine and drain", "Melt butter in a pan, add minced garlic", "Cook garlic 1 minute until fragrant", "Pour in cream and bring to a simmer", "Stir in parmesan until melted", "Toss pasta in the sauce", "Season and serve immediately"],
  ["easy", "vegetarian", "comfort-food", "30-minute"])

R("Crispy Chicken Nuggets", "sunny", "lunch",
  ["1 lb chicken breast", "1 cup breadcrumbs", "½ cup flour", "2 eggs", "1 tsp garlic powder", "Salt and pepper", "Cooking spray"],
  ["Preheat oven to 400°F", "Cut chicken into bite-sized pieces", "Set up breading: flour, beaten eggs, breadcrumbs", "Dip each piece in flour, then egg, then breadcrumbs", "Place on a baking sheet lined with parchment", "Spray with cooking spray", "Bake 15-18 minutes, flipping halfway"],
  ["easy", "protein", "30-minute", "fun"])

R("Classic Hot Dogs", "sunny", "lunch",
  ["4 hot dogs", "4 hot dog buns", "Ketchup", "Mustard", "Relish"],
  ["Boil water in a pot", "Cook hot dogs for 5 minutes", "Toast buns in the oven or on a pan", "Place hot dogs in buns", "Add ketchup, mustard, and relish", "Serve with chips"],
  ["easy", "quick", "15-minute", "fun"])

R("Cheeseburger Sliders", "sunny", "lunch",
  ["1 lb ground beef", "4 slider buns", "4 slices American cheese", "Ketchup and mustard", "Lettuce and tomato", "Salt and pepper"],
  ["Mix ground beef with salt and pepper", "Form into 4 small patties", "Cook in a pan over medium-high heat, 3-4 min per side", "Add cheese on top, cover to melt", "Toast the buns", "Assemble with lettuce, tomato, and condiments", "Serve with pickles on the side"],
  ["easy", "protein", "30-minute"])

R("Chicken Tacos", "sunny", "lunch",
  ["1 lb cooked shredded chicken", "8 taco shells", "1 cup shredded cheese", "1 cup lettuce (shredded)", "½ cup salsa", "Sour cream"],
  ["Warm taco shells in the oven for 2 minutes", "Heat shredded chicken with a splash of salsa", "Fill each shell with chicken", "Top with cheese and lettuce", "Add a dollop of sour cream", "Squeeze lime juice on top if you like"],
  ["easy", "protein", "15-minute", "fun"])

R("Bean and Cheese Burritos", "windy", "lunch",
  ["4 flour tortillas", "1 can refried beans", "1 cup shredded cheese", "½ cup salsa", "Sour cream", "Hot sauce (optional)"],
  ["Warm refried beans in a pan", "Heat tortillas in microwave 15 seconds each", "Spread beans down the center of each tortilla", "Add cheese and salsa", "Fold in sides and roll up tightly", "Cut in half to serve", "Dip in sour cream"],
  ["easy", "vegetarian", "15-minute", "protein"])

R("Mini Pepperoni Pizzas", "windy", "lunch",
  ["4 English muffins (halved)", "½ cup pizza sauce", "1 cup shredded mozzarella", "Mini pepperoni slices", "Italian seasoning"],
  ["Preheat oven to 400°F", "Place muffin halves on a baking sheet", "Spread pizza sauce on each half", "Sprinkle with mozzarella", "Add pepperoni on top", "Sprinkle Italian seasoning", "Bake 8-10 minutes until cheese is bubbly"],
  ["easy", "fun", "15-minute"])

R("Tomato Basil Soup", "rainy", "lunch",
  ["1 can crushed tomatoes", "1 cup chicken broth", "½ cup heavy cream", "2 cloves garlic", "1 tbsp butter", "Fresh basil", "Salt and pepper"],
  ["Melt butter and cook minced garlic for 1 minute", "Add crushed tomatoes and broth", "Simmer for 15 minutes", "Stir in heavy cream", "Season with salt and pepper", "Blend until smooth (ask a grown-up to help!)", "Top with fresh basil leaves"],
  ["easy", "vegetarian", "comfort-food", "30-minute"])

R("Chicken Noodle Soup", "snowy", "lunch",
  ["2 chicken breasts", "8 cups chicken broth", "2 cups egg noodles", "2 carrots (diced)", "2 celery stalks (diced)", "1 onion (diced)", "Salt and pepper"],
  ["Bring broth to a boil with chicken breasts", "Cook chicken 15 minutes, then shred with forks", "Add carrots, celery, and onion to the broth", "Simmer 10 minutes until veggies are soft", "Add egg noodles and cook 8 minutes", "Return shredded chicken to the pot", "Season with salt and pepper"],
  ["easy", "protein", "comfort-food", "one-pot"])

R("Broccoli Cheese Soup", "snowy", "lunch",
  ["4 cups broccoli florets", "2 cups chicken broth", "2 cups shredded cheddar", "1 cup milk", "2 tbsp butter", "2 tbsp flour", "Salt and pepper"],
  ["Cook broccoli in broth until tender, about 10 minutes", "In another pot, melt butter and stir in flour", "Add milk slowly, stirring until thick", "Add cheese and stir until melted", "Pour cheese sauce into broccoli pot", "Stir everything together", "Blend partially if you like it chunky or fully for smooth"],
  ["easy", "vegetarian", "comfort-food"])

R("Ramen Noodle Bowl", "snowy", "lunch",
  ["2 packets ramen noodles (discard seasoning)", "4 cups chicken broth", "2 soft-boiled eggs", "1 cup corn kernels", "2 green onions (sliced)", "1 tbsp soy sauce", "1 tsp sesame oil"],
  ["Bring broth to a boil", "Add ramen noodles and cook 3 minutes", "Stir in soy sauce and sesame oil", "Divide into bowls", "Top each with a halved soft-boiled egg", "Add corn and green onions", "Slurp away!"],
  ["easy", "protein", "15-minute", "comfort-food"])

R("Veggie Fried Rice", "cloudy", "lunch",
  ["3 cups cooked rice (cold)", "2 eggs", "1 cup mixed frozen veggies", "2 tbsp soy sauce", "1 tbsp sesame oil", "2 green onions", "1 clove garlic"],
  ["Heat sesame oil in a large pan or wok", "Cook frozen veggies and garlic 3 minutes", "Push veggies to the side, scramble eggs", "Add cold rice and stir everything together", "Pour soy sauce over and toss well", "Cook 3-4 more minutes until rice is crispy", "Top with sliced green onions"],
  ["easy", "vegetarian", "30-minute"])

R("Chicken Fried Rice", "cloudy", "lunch",
  ["3 cups cooked rice", "1 cup diced cooked chicken", "2 eggs", "1 cup frozen peas and carrots", "3 tbsp soy sauce", "1 tbsp sesame oil", "2 green onions"],
  ["Heat sesame oil in a wok or large pan", "Cook peas, carrots, and chicken 3 minutes", "Push to the side and scramble eggs", "Add cold rice and toss everything together", "Pour soy sauce over and stir well", "Cook until rice starts to get crispy", "Garnish with green onions"],
  ["easy", "protein", "30-minute"])

R("Baked Fish Sticks", "cloudy", "lunch",
  ["1 lb white fish fillets", "1 cup panko breadcrumbs", "½ cup flour", "2 eggs", "1 tsp garlic powder", "Salt and pepper", "Lemon wedges"],
  ["Preheat oven to 425°F", "Cut fish into thick sticks", "Set up breading: flour, beaten eggs, seasoned panko", "Coat each stick in flour, egg, then panko", "Place on a greased baking sheet", "Bake 12-15 minutes until golden and crispy", "Serve with tartar sauce and lemon"],
  ["easy", "protein", "30-minute", "healthy"])

R("Loaded Potato Soup", "snowy", "lunch",
  ["4 large potatoes (diced)", "4 cups chicken broth", "1 cup shredded cheddar", "½ cup sour cream", "4 slices bacon (cooked)", "2 green onions", "Salt and pepper"],
  ["Boil diced potatoes in broth until tender", "Mash some potatoes for thickness, leave some chunky", "Stir in sour cream and half the cheese", "Season with salt and pepper", "Ladle into bowls", "Top with bacon crumbles, cheese, and green onions"],
  ["easy", "comfort-food", "one-pot"])

R("Lo Mein Noodles", "cloudy", "lunch",
  ["8 oz lo mein noodles or spaghetti", "1 cup mixed vegetables", "2 tbsp soy sauce", "1 tbsp sesame oil", "1 tbsp oyster sauce", "1 clove garlic", "1 tsp ginger"],
  ["Cook noodles and drain", "Heat sesame oil in a wok", "Cook garlic, ginger, and veggies 3 minutes", "Add noodles to the wok", "Pour soy sauce and oyster sauce over", "Toss everything together with tongs", "Serve hot"],
  ["easy", "vegetarian", "30-minute"])

R("Corn Dogs", "sunny", "lunch",
  ["4 hot dogs", "1 cup cornmeal", "1 cup flour", "1 egg", "1 cup milk", "Oil for frying", "Wooden sticks"],
  ["Mix cornmeal, flour, egg, and milk into a thick batter", "Insert sticks into hot dogs", "Heat oil to 350°F (grown-up job!)", "Dip each hot dog into batter to coat", "Carefully lower into hot oil", "Fry 3-4 minutes until golden brown", "Serve with ketchup and mustard"],
  ["fun", "30-minute"])

R("Turkey Meatball Subs", "windy", "lunch",
  ["1 lb ground turkey", "¼ cup breadcrumbs", "1 egg", "4 sub rolls", "1 cup marinara sauce", "½ cup mozzarella", "Italian seasoning"],
  ["Mix turkey, breadcrumbs, egg, and Italian seasoning", "Roll into golf ball-sized meatballs", "Bake at 400°F for 15 minutes", "Heat marinara sauce in a pan", "Toss meatballs in sauce", "Fill sub rolls with meatballs", "Top with mozzarella and broil 2 minutes"],
  ["easy", "protein", "30-minute"])

R("Sloppy Joes", "rainy", "lunch",
  ["1 lb ground beef", "1 cup ketchup", "2 tbsp brown sugar", "1 tbsp mustard", "1 tbsp Worcestershire sauce", "4 hamburger buns", "1 small onion (diced)"],
  ["Cook ground beef and onion until browned", "Drain excess grease", "Add ketchup, brown sugar, mustard, and Worcestershire", "Stir and simmer 10 minutes", "Spoon onto toasted buns", "Serve with napkins — it's gonna be messy!"],
  ["easy", "protein", "30-minute", "messy", "fun"])

R("Pretzel Bites with Cheese Dip", "windy", "lunch",
  ["1 can refrigerated pizza dough", "4 cups water", "¼ cup baking soda", "Coarse salt", "1 cup cheese sauce"],
  ["Preheat oven to 425°F", "Cut dough into small pieces", "Boil water with baking soda", "Drop dough pieces in for 30 seconds, remove", "Place on greased baking sheet, sprinkle with salt", "Bake 12-15 minutes until golden", "Serve with warm cheese dip"],
  ["fun", "vegetarian", "30-minute"])

R("Mozzarella Sticks", "rainy", "lunch",
  ["8 mozzarella string cheese sticks", "1 cup breadcrumbs", "½ cup flour", "2 eggs", "1 tsp Italian seasoning", "Marinara for dipping"],
  ["Cut string cheese in half", "Freeze for 30 minutes", "Set up breading: flour, beaten eggs, seasoned breadcrumbs", "Coat each stick: flour, egg, breadcrumbs, egg, breadcrumbs", "Place on baking sheet, freeze 15 more minutes", "Bake at 400°F for 8-10 minutes", "Serve with marinara sauce"],
  ["fun", "vegetarian", "party"])

R("Sweet Potato Fries", "sunny", "lunch",
  ["2 large sweet potatoes", "2 tbsp olive oil", "1 tsp paprika", "½ tsp garlic powder", "Salt", "Ketchup for dipping"],
  ["Preheat oven to 425°F", "Cut sweet potatoes into thin fry shapes", "Toss with olive oil, paprika, garlic, and salt", "Spread in a single layer on a baking sheet", "Bake 20-25 minutes, flipping halfway", "Let cool slightly", "Dip in ketchup and enjoy"],
  ["easy", "vegetarian", "healthy", "30-minute"])

R("Caprese Pasta Salad", "sunny", "lunch",
  ["8 oz rotini pasta", "1 cup cherry tomatoes (halved)", "1 cup mozzarella balls", "¼ cup basil (chopped)", "3 tbsp olive oil", "1 tbsp balsamic vinegar", "Salt and pepper"],
  ["Cook pasta and drain", "Rinse with cold water until cool", "Toss with cherry tomatoes and mozzarella", "Add chopped basil", "Drizzle with olive oil and balsamic", "Season with salt and pepper", "Chill before serving"],
  ["easy", "vegetarian", "healthy", "make-ahead"])

# ═══════════════════════ DINNER ═══════════════════════════════════════════════

R("Crispy Baked Chicken Drumsticks", "rainy", "dinner",
  ["8 chicken drumsticks", "1 cup breadcrumbs", "½ cup parmesan cheese", "1 tsp garlic powder", "1 tsp paprika", "2 tbsp olive oil", "Salt and pepper"],
  ["Preheat oven to 400°F", "Mix breadcrumbs, parmesan, garlic, paprika, salt, and pepper", "Brush drumsticks with olive oil", "Roll each drumstick in the coating", "Place on a baking rack over a baking sheet", "Bake 35-40 minutes until golden and cooked through", "Let cool slightly before eating"],
  ["easy", "protein", "30-minute"])

R("Honey Mustard Chicken Thighs", "cloudy", "dinner",
  ["6 chicken thighs", "3 tbsp honey", "2 tbsp mustard", "1 tbsp olive oil", "1 tsp garlic powder", "Salt and pepper"],
  ["Preheat oven to 400°F", "Mix honey, mustard, olive oil, and garlic", "Season chicken with salt and pepper", "Brush honey mustard mixture all over chicken", "Place on a baking sheet", "Bake 30-35 minutes until golden", "Brush with extra sauce before serving"],
  ["easy", "protein"])

R("Chicken Parmesan", "rainy", "dinner",
  ["4 chicken breasts", "1 cup breadcrumbs", "½ cup parmesan", "2 eggs", "1 cup marinara sauce", "1 cup mozzarella", "Spaghetti for serving"],
  ["Preheat oven to 400°F", "Pound chicken to even thickness", "Dip in beaten eggs, then breadcrumb-parmesan mix", "Pan-fry in oil 3 minutes per side until golden", "Place on baking sheet, top with marinara and mozzarella", "Bake 15 minutes until cheese is bubbly", "Serve over spaghetti"],
  ["protein", "comfort-food"])

R("Chicken Stir Fry", "cloudy", "dinner",
  ["1 lb chicken breast (sliced)", "2 cups mixed vegetables", "3 tbsp soy sauce", "1 tbsp honey", "1 tsp cornstarch", "1 tbsp sesame oil", "Rice for serving"],
  ["Mix soy sauce, honey, and cornstarch for sauce", "Heat sesame oil in a wok over high heat", "Cook chicken 5-6 minutes until done, remove", "Add vegetables and stir fry 3 minutes", "Return chicken to the wok", "Pour sauce over and toss to coat", "Serve over steamed rice"],
  ["easy", "healthy", "protein", "30-minute"])

R("Chicken Pot Pie", "snowy", "dinner",
  ["2 cups cooked shredded chicken", "1 cup mixed frozen veggies", "1 can cream of chicken soup", "½ cup milk", "2 refrigerated pie crusts", "Salt and pepper"],
  ["Preheat oven to 375°F", "Mix chicken, veggies, soup, milk, salt, and pepper", "Press one pie crust into a pie dish", "Pour filling into the crust", "Place second crust on top and crimp edges", "Cut slits in the top for steam", "Bake 35-40 minutes until golden brown"],
  ["comfort-food", "protein"])

R("Chicken Enchiladas", "windy", "dinner",
  ["2 cups shredded cooked chicken", "8 flour tortillas", "1 can enchilada sauce", "2 cups shredded cheese", "½ cup sour cream", "1 can diced green chiles"],
  ["Preheat oven to 375°F", "Mix chicken, half the cheese, sour cream, and chiles", "Spread some enchilada sauce in a baking dish", "Fill each tortilla with chicken mixture, roll up", "Place seam-side down in the dish", "Cover with remaining sauce and cheese", "Bake 20-25 minutes until bubbly"],
  ["easy", "protein", "comfort-food"])

R("Classic Spaghetti and Meatballs", "windy", "dinner",
  ["1 lb ground beef", "¼ cup breadcrumbs", "1 egg", "8 oz spaghetti", "2 cups marinara sauce", "¼ cup parmesan", "Italian seasoning"],
  ["Mix beef, breadcrumbs, egg, and Italian seasoning", "Roll into golf ball-sized meatballs", "Brown meatballs in a pan on all sides", "Simmer meatballs in marinara sauce for 15 minutes", "Cook spaghetti according to package", "Serve meatballs and sauce over spaghetti", "Sprinkle parmesan on top"],
  ["protein", "comfort-food", "30-minute"])

R("Swedish Meatballs", "snowy", "dinner",
  ["1 lb ground beef", "¼ cup breadcrumbs", "1 egg", "2 tbsp butter", "2 tbsp flour", "1½ cups beef broth", "½ cup sour cream"],
  ["Mix beef, breadcrumbs, and egg, form meatballs", "Brown meatballs in butter, set aside", "Add flour to the pan drippings, stir 1 minute", "Pour in broth and whisk until smooth", "Simmer until thickened", "Stir in sour cream", "Add meatballs back, simmer 5 minutes, serve over noodles"],
  ["comfort-food", "protein"])

R("Baked Lasagna", "snowy", "dinner",
  ["9 lasagna noodles", "1 lb ground beef", "2 cups ricotta", "2 cups mozzarella", "2 cups marinara", "1 egg", "½ cup parmesan"],
  ["Preheat oven to 375°F", "Cook noodles and brown beef, drain both", "Mix ricotta, egg, and half the parmesan", "Layer: sauce, noodles, ricotta mix, beef, mozzarella", "Repeat layers twice", "Top with remaining mozzarella and parmesan", "Cover with foil, bake 25 min, uncover, bake 15 more"],
  ["comfort-food", "protein"])

R("Shepherd's Pie", "snowy", "dinner",
  ["1 lb ground beef", "4 large potatoes (peeled, diced)", "1 cup frozen peas and carrots", "1 cup beef gravy", "½ cup shredded cheddar", "3 tbsp butter", "½ cup milk"],
  ["Boil potatoes until tender, mash with butter and milk", "Brown ground beef, drain grease", "Stir gravy and frozen veggies into beef", "Pour into a baking dish", "Spread mashed potatoes on top", "Sprinkle with cheddar", "Bake at 400°F for 20 minutes until golden"],
  ["comfort-food", "protein", "one-pot"])

R("Baked Salmon with Honey Glaze", "cloudy", "dinner",
  ["4 salmon fillets", "3 tbsp honey", "2 tbsp soy sauce", "1 tbsp olive oil", "1 clove garlic (minced)", "Lemon wedges"],
  ["Preheat oven to 400°F", "Mix honey, soy sauce, olive oil, and garlic", "Place salmon on a lined baking sheet", "Brush glaze generously over each fillet", "Bake 12-15 minutes until flaky", "Squeeze lemon juice on top", "Serve with rice and veggies"],
  ["easy", "healthy", "protein", "30-minute"])

R("Teriyaki Salmon", "cloudy", "dinner",
  ["4 salmon fillets", "¼ cup soy sauce", "2 tbsp honey", "1 tbsp rice vinegar", "1 tsp sesame oil", "1 tsp ginger", "Sesame seeds"],
  ["Mix soy sauce, honey, vinegar, sesame oil, and ginger", "Marinate salmon for 15 minutes", "Preheat oven to 400°F", "Bake salmon 12-15 minutes", "Brush with extra teriyaki sauce", "Sprinkle sesame seeds on top", "Serve with steamed rice"],
  ["healthy", "protein", "30-minute"])

R("Beef Tacos Supreme", "sunny", "dinner",
  ["1 lb ground beef", "1 packet taco seasoning", "8 taco shells", "1 cup shredded cheese", "1 cup lettuce", "1 tomato (diced)", "Sour cream and salsa"],
  ["Brown ground beef and drain", "Add taco seasoning and ¾ cup water", "Simmer 5 minutes until thick", "Warm taco shells in the oven", "Fill shells with seasoned beef", "Top with cheese, lettuce, tomato", "Add sour cream and salsa"],
  ["easy", "protein", "30-minute", "fun"])

R("Beef Stew", "snowy", "dinner",
  ["1½ lbs beef stew meat", "4 potatoes (diced)", "3 carrots (diced)", "1 onion (diced)", "4 cups beef broth", "2 tbsp tomato paste", "2 tbsp flour"],
  ["Coat beef in flour and brown in a large pot", "Add onion and cook 3 minutes", "Stir in tomato paste", "Pour in beef broth and bring to a boil", "Add potatoes and carrots", "Reduce heat and simmer 1-2 hours", "Season with salt and pepper, serve in bowls"],
  ["comfort-food", "protein", "one-pot"])

R("Beef Chili", "snowy", "dinner",
  ["1 lb ground beef", "1 can kidney beans", "1 can diced tomatoes", "1 cup beef broth", "2 tbsp chili powder", "1 tsp cumin", "1 onion (diced)"],
  ["Brown beef and onion in a large pot", "Drain excess grease", "Add beans, tomatoes, broth, and spices", "Stir everything together", "Bring to a boil, then reduce to a simmer", "Cook 30-45 minutes until thick", "Serve with cheese and sour cream on top"],
  ["protein", "comfort-food", "one-pot"])

R("Meatloaf with Ketchup Glaze", "rainy", "dinner",
  ["1½ lbs ground beef", "½ cup breadcrumbs", "1 egg", "¼ cup milk", "½ cup ketchup", "1 tbsp Worcestershire sauce", "1 tsp onion powder"],
  ["Preheat oven to 350°F", "Mix beef, breadcrumbs, egg, milk, and seasonings", "Shape into a loaf on a baking sheet", "Mix ketchup with Worcestershire for glaze", "Spread glaze on top of meatloaf", "Bake 45-55 minutes until cooked through", "Let rest 10 minutes before slicing"],
  ["comfort-food", "protein"])

R("BBQ Baby Back Ribs", "sunny", "dinner",
  ["2 racks baby back ribs", "1 cup BBQ sauce", "2 tbsp brown sugar", "1 tsp garlic powder", "1 tsp paprika", "Salt and pepper"],
  ["Preheat oven to 300°F", "Remove membrane from back of ribs", "Mix brown sugar, garlic, paprika, salt, and pepper", "Rub seasoning all over ribs", "Wrap tightly in foil and bake 2.5 hours", "Unwrap, brush with BBQ sauce", "Broil 5 minutes until caramelized"],
  ["protein", "savory"])

R("Stuffed Bell Peppers", "cloudy", "dinner",
  ["4 bell peppers", "1 lb ground beef", "1 cup cooked rice", "1 cup marinara sauce", "1 cup shredded cheese", "1 tsp Italian seasoning", "Salt and pepper"],
  ["Preheat oven to 375°F", "Cut tops off peppers and remove seeds", "Brown beef with Italian seasoning, drain", "Mix beef with rice and half the marinara", "Stuff peppers with the mixture", "Place in a baking dish, top with remaining sauce and cheese", "Bake 30-35 minutes until peppers are tender"],
  ["protein", "healthy", "30-minute"])

R("One Pot Chicken and Rice", "windy", "dinner",
  ["4 chicken thighs", "1½ cups rice", "3 cups chicken broth", "1 cup frozen peas", "2 tbsp butter", "1 tsp garlic powder", "Salt and pepper"],
  ["Season chicken with garlic, salt, and pepper", "Brown chicken in butter in a large pot, set aside", "Add rice to the pot and toast 2 minutes", "Pour in broth and bring to a boil", "Place chicken on top of rice", "Cover and simmer 20 minutes", "Stir in peas, cover 5 more minutes, serve"],
  ["easy", "protein", "one-pot"])

R("Sheet Pan Chicken and Veggies", "cloudy", "dinner",
  ["4 chicken thighs", "2 cups broccoli florets", "1 cup cherry tomatoes", "1 bell pepper (sliced)", "3 tbsp olive oil", "1 tsp Italian seasoning", "Salt and pepper"],
  ["Preheat oven to 400°F", "Toss veggies with olive oil, salt, and Italian seasoning", "Season chicken with same seasonings", "Arrange chicken and veggies on a large baking sheet", "Bake 25-30 minutes until chicken is cooked", "Everything cooks together — easy cleanup!", "Serve right from the pan"],
  ["easy", "healthy", "protein", "30-minute"])

R("Homemade Pizza Night", "windy", "dinner",
  ["1 lb pizza dough", "½ cup pizza sauce", "2 cups mozzarella", "Your favorite toppings", "1 tbsp olive oil", "Flour for rolling"],
  ["Preheat oven to 475°F", "Stretch dough on a floured surface", "Place on an oiled baking sheet or pizza stone", "Spread sauce, leaving an edge for crust", "Sprinkle mozzarella all over", "Add your favorite toppings", "Bake 12-15 minutes until crust is golden"],
  ["fun", "vegetarian", "party", "30-minute"])

R("Slow Cooker Chili", "snowy", "dinner",
  ["1 lb ground beef (browned)", "2 cans diced tomatoes", "2 cans beans (kidney and black)", "1 cup beef broth", "2 tbsp chili powder", "1 tsp cumin", "1 onion (diced)"],
  ["Brown ground beef and onion, drain", "Add everything to the slow cooker", "Stir to combine", "Cover and cook on low for 6-8 hours", "Stir before serving", "Top with cheese, sour cream, and crackers"],
  ["comfort-food", "protein", "one-pot", "make-ahead"])

R("Veggie Stir Fry with Tofu", "cloudy", "dinner",
  ["1 block firm tofu (cubed)", "2 cups mixed vegetables", "3 tbsp soy sauce", "1 tbsp honey", "1 tbsp cornstarch", "1 tbsp sesame oil", "Rice for serving"],
  ["Press tofu for 15 minutes, then cube", "Mix soy sauce, honey, and cornstarch for sauce", "Heat sesame oil in a wok", "Cook tofu until crispy on all sides, set aside", "Stir fry vegetables 3-4 minutes", "Return tofu, pour sauce over", "Toss and serve over rice"],
  ["healthy", "vegetarian", "30-minute"])

R("Black Bean Tacos", "sunny", "dinner",
  ["2 cans black beans (drained)", "8 taco shells", "1 cup shredded cheese", "1 avocado", "1 cup salsa", "Lime juice", "Cilantro"],
  ["Heat black beans with a pinch of cumin", "Warm taco shells", "Mash avocado with lime juice and salt", "Fill shells with beans", "Top with cheese and salsa", "Add a dollop of smashed avocado", "Sprinkle cilantro on top"],
  ["easy", "vegetarian", "healthy", "15-minute"])

R("Garlic Butter Shrimp Pasta", "rainy", "dinner",
  ["8 oz linguine", "1 lb large shrimp (peeled)", "4 cloves garlic (minced)", "3 tbsp butter", "¼ cup white wine or broth", "Red pepper flakes", "Parsley"],
  ["Cook linguine and drain", "Melt butter in a large pan", "Cook garlic 30 seconds until fragrant", "Add shrimp, cook 2-3 minutes per side", "Pour in wine/broth and simmer 2 minutes", "Toss pasta with the shrimp and sauce", "Garnish with parsley and pepper flakes"],
  ["protein", "30-minute"])

R("Pork Chops with Applesauce", "rainy", "dinner",
  ["4 pork chops", "1 cup applesauce", "2 tbsp olive oil", "1 tsp garlic powder", "1 tsp thyme", "Salt and pepper"],
  ["Season pork chops with garlic, thyme, salt, and pepper", "Heat olive oil in a pan over medium-high heat", "Cook pork chops 5 minutes per side", "Let them rest for 5 minutes", "Warm applesauce in a small pot", "Serve pork chops with applesauce on the side", "Add mashed potatoes for a complete meal"],
  ["protein", "comfort-food", "30-minute"])

R("Creamy Tomato Basil Pasta", "rainy", "dinner",
  ["8 oz penne", "1 can crushed tomatoes", "½ cup heavy cream", "2 cloves garlic", "Fresh basil", "2 tbsp olive oil", "Parmesan cheese"],
  ["Cook penne and drain", "Sauté garlic in olive oil 1 minute", "Add crushed tomatoes and simmer 10 minutes", "Stir in heavy cream", "Toss with cooked pasta", "Top with fresh basil and parmesan", "Serve hot"],
  ["easy", "vegetarian", "comfort-food", "30-minute"])

# ═══════════════════════ SNACKS ═══════════════════════════════════════════════

R("Strawberry Banana Smoothie", "sunny", "snack",
  ["1 cup frozen strawberries", "1 banana", "1 cup milk", "½ cup yogurt", "1 tbsp honey"],
  ["Add all ingredients to a blender", "Blend on high until smooth", "Pour into a glass", "Add a straw and enjoy!"],
  ["easy", "healthy", "15-minute", "no-cook"])

R("Mango Pineapple Smoothie", "sunny", "snack",
  ["1 cup frozen mango", "½ cup pineapple chunks", "1 cup orange juice", "½ cup yogurt"],
  ["Combine everything in a blender", "Blend until smooth and creamy", "Pour into a tall glass", "Taste the tropical paradise!"],
  ["easy", "healthy", "15-minute", "no-cook"])

R("Berry Blast Smoothie", "sunny", "snack",
  ["1 cup mixed frozen berries", "1 banana", "1 cup milk", "1 tbsp honey", "½ cup yogurt"],
  ["Put all ingredients in the blender", "Blend until completely smooth", "Pour into your favorite glass", "Drink up all those vitamins!"],
  ["easy", "healthy", "15-minute", "no-cook"])

R("Rainbow Fruit Popsicles", "sunny", "snack",
  ["1 cup strawberry yogurt", "1 cup mango chunks", "1 cup blueberries", "1 cup kiwi (diced)", "½ cup orange juice"],
  ["Layer strawberry yogurt in popsicle molds", "Add a layer of mango chunks", "Add blueberries", "Top with kiwi mixed with OJ", "Insert sticks and freeze 4+ hours", "Run warm water on mold to release"],
  ["easy", "healthy", "fun", "no-cook"])

R("Classic Chocolate Chip Cookies", "rainy", "snack",
  ["2¼ cups flour", "1 cup butter (softened)", "¾ cup sugar", "¾ cup brown sugar", "2 eggs", "1 tsp vanilla", "2 cups chocolate chips"],
  ["Preheat oven to 375°F", "Cream butter and both sugars until fluffy", "Beat in eggs and vanilla", "Mix in flour gradually", "Fold in chocolate chips", "Drop rounded spoonfuls onto baking sheets", "Bake 9-11 minutes until edges are golden"],
  ["baking", "sweet", "fun", "vegetarian"])

R("Oatmeal Raisin Cookies", "rainy", "snack",
  ["1½ cups flour", "1 cup oats", "1 cup raisins", "½ cup butter", "¾ cup brown sugar", "1 egg", "1 tsp cinnamon"],
  ["Preheat oven to 350°F", "Cream butter and brown sugar", "Beat in egg", "Mix in flour, oats, and cinnamon", "Fold in raisins", "Scoop onto baking sheets", "Bake 10-12 minutes until lightly browned"],
  ["baking", "sweet", "vegetarian"])

R("Sugar Cookies with Sprinkles", "cloudy", "snack",
  ["2¾ cups flour", "1 cup butter (softened)", "1½ cups powdered sugar", "1 egg", "1 tsp vanilla", "Sprinkles", "Food coloring (optional)"],
  ["Cream butter and powdered sugar", "Beat in egg and vanilla", "Mix in flour until dough forms", "Chill dough 1 hour", "Roll out and cut with cookie cutters", "Bake at 350°F for 8-10 minutes", "Decorate with frosting and sprinkles"],
  ["baking", "sweet", "fun", "party"])

R("Peanut Butter Cookies", "cloudy", "snack",
  ["1 cup peanut butter", "1 cup sugar", "1 egg", "1 tsp vanilla", "½ tsp baking soda"],
  ["Preheat oven to 350°F", "Mix all ingredients until smooth", "Roll into balls and place on baking sheet", "Press each ball with a fork in a criss-cross pattern", "Bake 10-12 minutes", "Let cool on the pan for 5 minutes", "These are SO easy — only 5 ingredients!"],
  ["baking", "sweet", "easy"])

R("Fudgy Brownies", "rainy", "snack",
  ["½ cup butter", "1 cup sugar", "2 eggs", "⅓ cup cocoa powder", "½ cup flour", "1 tsp vanilla", "¼ tsp salt"],
  ["Preheat oven to 350°F", "Melt butter and stir in sugar", "Beat in eggs and vanilla", "Mix in cocoa, flour, and salt", "Pour into a greased 8x8 pan", "Bake 25-30 minutes — don't overbake!", "Let cool before cutting into squares"],
  ["baking", "sweet", "vegetarian"])

R("Chocolate Cupcakes", "rainy", "snack",
  ["1½ cups flour", "¾ cup cocoa powder", "1½ cups sugar", "2 eggs", "½ cup oil", "1 cup milk", "1 tsp vanilla"],
  ["Preheat oven to 350°F", "Mix dry ingredients in a bowl", "Whisk wet ingredients separately", "Combine and mix until smooth", "Fill cupcake liners ⅔ full", "Bake 18-20 minutes until a toothpick comes out clean", "Cool completely before frosting"],
  ["baking", "sweet", "fun", "party"])

R("Vanilla Cupcakes", "cloudy", "snack",
  ["1½ cups flour", "1 cup sugar", "½ cup butter (softened)", "2 eggs", "½ cup milk", "2 tsp vanilla", "1½ tsp baking powder"],
  ["Preheat oven to 350°F", "Cream butter and sugar", "Beat in eggs and vanilla", "Alternate adding flour and milk", "Fill cupcake liners ⅔ full", "Bake 18-22 minutes", "Frost with your favorite frosting and sprinkles"],
  ["baking", "sweet", "fun", "party"])

R("Classic Banana Bread", "rainy", "snack",
  ["3 ripe bananas", "⅓ cup melted butter", "¾ cup sugar", "1 egg", "1 tsp vanilla", "1½ cups flour", "1 tsp baking soda"],
  ["Preheat oven to 350°F", "Mash bananas in a bowl", "Mix in melted butter, sugar, egg, and vanilla", "Stir in flour and baking soda until just combined", "Pour into a greased loaf pan", "Bake 55-60 minutes until golden", "Let cool before slicing"],
  ["baking", "sweet", "vegetarian", "easy"])

R("Apple Slices with Peanut Butter", "sunny", "snack",
  ["2 apples", "¼ cup peanut butter", "Granola for sprinkling", "Honey for drizzling"],
  ["Wash and slice apples", "Spread peanut butter on each slice", "Sprinkle granola on top", "Drizzle with honey", "Arrange on a plate and enjoy!"],
  ["easy", "healthy", "no-cook", "15-minute"])

R("Ants on a Log", "sunny", "snack",
  ["4 celery stalks", "¼ cup peanut butter", "¼ cup raisins"],
  ["Wash celery and cut into sticks", "Fill the groove with peanut butter", "Place raisins on top of the peanut butter", "The raisins are the ants! The celery is the log!", "Line them up on a plate"],
  ["easy", "healthy", "no-cook", "15-minute", "fun"])

R("Classic Trail Mix", "sunny", "snack",
  ["1 cup mixed nuts", "1 cup pretzels", "½ cup chocolate chips", "½ cup raisins", "½ cup cereal"],
  ["Pour all ingredients into a big bowl", "Toss everything together", "Divide into small bags or cups", "Perfect for on-the-go snacking!"],
  ["easy", "no-cook", "15-minute", "make-ahead"])

R("Buttery Popcorn", "cloudy", "snack",
  ["½ cup popcorn kernels", "3 tbsp butter", "Salt to taste"],
  ["Pop kernels in a pot with a lid over medium heat", "Shake the pot every few seconds", "When popping slows down, remove from heat", "Melt butter and drizzle over popcorn", "Sprinkle with salt", "Toss and enjoy movie night!"],
  ["easy", "vegetarian", "15-minute", "fun"])

R("Rice Crispy Treats", "cloudy", "snack",
  ["6 cups rice cereal", "4 cups mini marshmallows", "3 tbsp butter", "1 tsp vanilla"],
  ["Melt butter in a large pot", "Add marshmallows and stir until melted", "Stir in vanilla", "Remove from heat and add cereal", "Stir until all cereal is coated", "Press into a greased 9x13 pan", "Let cool and cut into squares"],
  ["easy", "sweet", "fun", "15-minute"])

R("Rainbow Fruit Salad", "sunny", "snack",
  ["1 cup strawberries", "1 cup mandarin oranges", "1 cup pineapple", "1 cup kiwi", "1 cup blueberries", "1 cup grapes", "2 tbsp honey"],
  ["Wash and cut all fruit", "Arrange in rainbow order in a big bowl", "Drizzle honey on top", "Gently toss together", "Serve in cups for individual portions"],
  ["easy", "healthy", "no-cook", "15-minute", "fun"])

R("Frozen Yogurt Bark", "sunny", "snack",
  ["2 cups vanilla yogurt", "1 cup mixed berries", "¼ cup granola", "2 tbsp honey", "1 tbsp chocolate chips"],
  ["Line a baking sheet with parchment paper", "Spread yogurt in an even layer", "Sprinkle berries, granola, and chocolate chips on top", "Drizzle with honey", "Freeze for 3-4 hours until solid", "Break into pieces like bark", "Eat quickly before it melts!"],
  ["easy", "healthy", "fun", "no-cook"])

R("Granola Bars", "cloudy", "snack",
  ["2 cups oats", "½ cup honey", "½ cup peanut butter", "½ cup chocolate chips", "¼ cup brown sugar", "2 tbsp butter"],
  ["Melt butter, honey, brown sugar, and PB together", "Stir in oats until coated", "Fold in chocolate chips", "Press firmly into a lined 8x8 pan", "Refrigerate 2 hours until firm", "Cut into bars", "Wrap individually for grab-and-go snacks"],
  ["easy", "make-ahead", "sweet"])

R("Peanut Butter Energy Bites", "windy", "snack",
  ["1 cup oats", "½ cup peanut butter", "⅓ cup honey", "½ cup chocolate chips", "1 tsp vanilla"],
  ["Mix all ingredients in a bowl", "Stir until everything is combined", "Chill mixture 30 minutes", "Roll into small balls", "Place on a lined tray", "Refrigerate until firm", "Store in the fridge for snacking all week"],
  ["easy", "healthy", "no-cook", "make-ahead"])

R("Vanilla Ice Cream Sundae", "sunny", "snack",
  ["Vanilla ice cream", "Chocolate sauce", "Whipped cream", "Sprinkles", "Cherry on top", "Chopped nuts (optional)"],
  ["Scoop ice cream into a bowl", "Drizzle chocolate sauce on top", "Add a mountain of whipped cream", "Cover in sprinkles", "Place a cherry on the very top", "Eat immediately!"],
  ["easy", "sweet", "fun", "no-cook"])

R("Cookies and Cream Milkshake", "sunny", "snack",
  ["3 scoops vanilla ice cream", "1 cup milk", "4 Oreo cookies", "Whipped cream"],
  ["Add ice cream and milk to blender", "Break cookies into pieces and add them", "Blend until smooth and thick", "Pour into a tall glass", "Top with whipped cream and cookie crumbles"],
  ["easy", "sweet", "fun", "no-cook"])

R("Chocolate Milkshake", "sunny", "snack",
  ["3 scoops chocolate ice cream", "1 cup milk", "2 tbsp chocolate syrup", "Whipped cream"],
  ["Combine ice cream, milk, and syrup in blender", "Blend until thick and creamy", "Pour into a glass", "Top with whipped cream and a drizzle of syrup"],
  ["easy", "sweet", "fun", "no-cook"])

R("Classic Hot Chocolate", "snowy", "snack",
  ["2 cups milk", "2 tbsp cocoa powder", "2 tbsp sugar", "½ tsp vanilla", "Marshmallows", "Whipped cream"],
  ["Heat milk in a saucepan (don't boil!)", "Whisk in cocoa powder and sugar", "Stir until smooth and steamy", "Add vanilla and stir", "Pour into mugs", "Top with marshmallows AND whipped cream"],
  ["easy", "sweet", "15-minute", "comfort-food"])

R("Peppermint Hot Chocolate", "snowy", "snack",
  ["2 cups milk", "2 tbsp cocoa powder", "2 tbsp sugar", "¼ tsp peppermint extract", "Whipped cream", "Crushed candy canes"],
  ["Heat milk over medium heat", "Whisk in cocoa and sugar until smooth", "Add peppermint extract and stir", "Pour into mugs", "Top with whipped cream", "Sprinkle crushed candy cane on top"],
  ["easy", "sweet", "15-minute", "comfort-food"])

R("Campfire S'mores", "windy", "snack",
  ["Graham crackers", "Marshmallows", "Chocolate bars"],
  ["Break graham crackers in half", "Place chocolate on one half", "Toast marshmallow over a fire or under a broiler", "Squish marshmallow onto the chocolate", "Top with the other graham cracker half", "Squeeze together and enjoy the gooey goodness!"],
  ["easy", "sweet", "fun"])

R("Indoor S'mores Dip", "snowy", "snack",
  ["2 cups chocolate chips", "1 bag mini marshmallows", "Graham crackers for dipping", "1 tbsp butter"],
  ["Preheat oven to 450°F", "Spread chocolate chips in a cast iron skillet", "Cover with mini marshmallows", "Bake 5-7 minutes until marshmallows are golden", "Dip graham crackers right into the skillet!", "Careful — it's hot!"],
  ["easy", "sweet", "fun", "party"])

R("Chocolate Pudding Cups", "rainy", "snack",
  ["2 cups milk", "⅓ cup sugar", "3 tbsp cocoa powder", "3 tbsp cornstarch", "1 tsp vanilla", "Whipped cream"],
  ["Whisk sugar, cocoa, and cornstarch in a pot", "Gradually stir in milk", "Cook over medium heat, stirring constantly", "Keep stirring until thick and bubbly", "Remove from heat, stir in vanilla", "Pour into cups and chill 2 hours", "Top with whipped cream"],
  ["sweet", "comfort-food", "make-ahead"])

R("Dirt Cup Dessert", "cloudy", "snack",
  ["1 box chocolate pudding mix", "2 cups milk", "1 cup Oreo crumbs", "Gummy worms", "Whipped cream"],
  ["Make pudding according to package", "Chill until set", "Spoon pudding into clear cups", "Top with Oreo crumbs (the dirt!)", "Stick gummy worms poking out of the top", "Add whipped cream clouds"],
  ["easy", "sweet", "fun", "party", "no-cook"])

R("Frozen Banana Pops", "sunny", "snack",
  ["4 bananas", "1 cup chocolate chips (melted)", "Sprinkles", "Crushed peanuts", "Popsicle sticks"],
  ["Peel bananas and cut in half", "Insert popsicle sticks into flat ends", "Dip in melted chocolate", "Roll in sprinkles or crushed peanuts", "Place on parchment-lined tray", "Freeze 2 hours until solid"],
  ["easy", "sweet", "fun", "no-cook"])

R("Chocolate Covered Strawberries", "sunny", "snack",
  ["1 lb fresh strawberries", "1 cup chocolate chips", "1 tbsp coconut oil", "Sprinkles (optional)"],
  ["Wash and dry strawberries completely", "Melt chocolate chips with coconut oil", "Hold each strawberry by the stem and dip", "Let excess chocolate drip off", "Add sprinkles while chocolate is wet", "Place on parchment paper", "Chill until chocolate is set"],
  ["easy", "sweet", "fun", "no-cook"])

R("Fruit and Cheese Kabobs", "sunny", "snack",
  ["Strawberries", "Grapes", "Cheese cubes", "Pineapple chunks", "Wooden skewers"],
  ["Wash all fruit", "Cut strawberries in half", "Thread fruit and cheese onto skewers", "Alternate colors for a rainbow look", "Arrange on a plate", "Dip in yogurt if you want!"],
  ["easy", "healthy", "no-cook", "15-minute", "fun", "party"])

R("Soft Pretzels", "windy", "snack",
  ["1 packet active dry yeast", "1½ cups warm water", "1 tbsp sugar", "4 cups flour", "¼ cup baking soda", "Coarse salt", "Melted butter"],
  ["Dissolve yeast and sugar in warm water, wait 5 min", "Mix in flour to form dough, knead 5 minutes", "Divide into 8 pieces, roll into ropes, shape into pretzels", "Boil water with baking soda", "Dip each pretzel in boiling water for 30 seconds", "Place on baking sheet, sprinkle with salt", "Bake at 425°F for 12-15 minutes, brush with melted butter"],
  ["baking", "fun", "30-minute"])

R("Cinnamon Sugar Donuts", "snowy", "snack",
  ["1 can biscuit dough", "Oil for frying", "½ cup sugar", "1 tbsp cinnamon", "2 tbsp melted butter"],
  ["Cut holes in center of each biscuit (save the holes!)", "Heat oil to 350°F (grown-up job!)", "Fry donuts 1-2 minutes per side until golden", "Drain on paper towels", "Mix sugar and cinnamon in a bag", "Toss warm donuts in cinnamon sugar", "Don't forget to fry the donut holes too!"],
  ["sweet", "fun"])

R("Churro Bites", "snowy", "snack",
  ["1 can crescent roll dough", "3 tbsp melted butter", "¼ cup sugar", "1 tbsp cinnamon", "Chocolate sauce for dipping"],
  ["Preheat oven to 375°F", "Cut dough into small squares", "Roll each into a little ball", "Place on a baking sheet", "Bake 10-12 minutes until golden", "Brush with melted butter", "Roll in cinnamon sugar and serve with chocolate sauce"],
  ["easy", "sweet", "fun", "baking"])

R("Mini Corn Dogs", "cloudy", "snack",
  ["1 package cocktail sausages", "1 cup cornmeal", "1 cup flour", "1 egg", "¾ cup milk", "Oil for frying", "Toothpicks"],
  ["Mix cornmeal, flour, egg, and milk into batter", "Pat sausages dry", "Insert toothpicks into sausages", "Dip each in batter to coat", "Fry in 350°F oil for 2-3 minutes", "Drain on paper towels", "Serve with ketchup and mustard"],
  ["fun", "party"])

R("Pizza Rolls", "windy", "snack",
  ["1 can crescent roll dough", "¼ cup pizza sauce", "½ cup shredded mozzarella", "Mini pepperoni slices", "Italian seasoning"],
  ["Preheat oven to 375°F", "Unroll dough and cut into small squares", "Place a bit of sauce, cheese, and pepperoni on each", "Roll up each square tightly", "Place seam-side down on baking sheet", "Sprinkle with Italian seasoning", "Bake 12-15 minutes until golden"],
  ["easy", "fun", "30-minute"])

R("Loaded Potato Skins", "windy", "snack",
  ["4 baked potatoes", "1 cup shredded cheddar", "4 slices bacon (cooked, crumbled)", "¼ cup sour cream", "2 green onions", "2 tbsp butter"],
  ["Cut potatoes in half, scoop out centers", "Brush insides with melted butter", "Bake at 400°F for 10 minutes until crispy", "Fill with shredded cheese and bacon", "Return to oven until cheese melts", "Top with sour cream and green onions"],
  ["easy", "savory", "fun", "party"])

R("Kale Chips", "sunny", "snack",
  ["1 bunch kale", "1 tbsp olive oil", "Salt", "Garlic powder"],
  ["Preheat oven to 300°F", "Wash and thoroughly dry kale", "Tear into chip-sized pieces, remove stems", "Toss with olive oil, salt, and garlic powder", "Spread in a single layer on baking sheets", "Bake 20-25 minutes until crispy", "They shrink a lot — make extra!"],
  ["easy", "healthy", "vegetarian", "vegan"])

# ═══════════════════════ MORE BREAKFAST ══════════════════════════════════════

R("Lemon Poppy Seed Pancakes", "sunny", "breakfast",
  ["1½ cups flour", "1 cup milk", "1 egg", "2 tbsp sugar", "1 tbsp poppy seeds", "Zest of 1 lemon", "1 tsp baking powder"],
  ["Mix flour, sugar, baking powder, and poppy seeds", "Whisk milk, egg, and lemon zest", "Combine wet and dry ingredients", "Cook on a buttered griddle", "Flip when bubbles form", "Serve with lemon glaze or powdered sugar"],
  ["easy", "vegetarian", "sweet"])

R("Red Velvet Pancakes", "cloudy", "breakfast",
  ["1½ cups flour", "1 cup buttermilk", "1 egg", "2 tbsp cocoa powder", "Red food coloring", "2 tbsp sugar", "1 tsp baking powder"],
  ["Mix flour, cocoa, sugar, and baking powder", "Whisk buttermilk, egg, and food coloring", "Combine wet and dry ingredients", "Cook on buttered griddle until set", "Flip and cook until done", "Top with cream cheese drizzle"],
  ["fun", "sweet", "vegetarian"])

R("Cinnamon Roll Waffles", "snowy", "breakfast",
  ["1 can cinnamon roll dough", "Cooking spray", "½ cup powdered sugar", "2 tbsp milk", "1 tsp vanilla"],
  ["Preheat waffle iron and spray with cooking spray", "Place one cinnamon roll in each section", "Close and cook until golden, about 3-4 minutes", "Mix powdered sugar, milk, and vanilla for glaze", "Drizzle glaze over warm waffles", "Eat immediately!"],
  ["easy", "sweet", "fun", "15-minute"])

R("Stuffed French Toast", "snowy", "breakfast",
  ["8 slices thick bread", "4 oz cream cheese", "¼ cup jam", "3 eggs", "½ cup milk", "1 tsp cinnamon", "2 tbsp butter"],
  ["Spread cream cheese and jam on 4 bread slices", "Top with remaining slices to make sandwiches", "Whisk eggs, milk, and cinnamon", "Dip each sandwich in egg mixture", "Cook in buttered pan 3 minutes per side", "Dust with powdered sugar", "Cut diagonally and serve"],
  ["sweet", "comfort-food", "vegetarian"])

R("Apple Pie Oatmeal", "rainy", "breakfast",
  ["1 cup rolled oats", "2 cups milk", "1 apple (diced)", "2 tbsp brown sugar", "1 tsp cinnamon", "¼ tsp nutmeg", "1 tbsp butter"],
  ["Cook oats in milk over medium heat", "Add diced apple and spices", "Stir for 5 minutes until apple is tender", "Stir in brown sugar and butter", "Pour into bowls", "Tastes just like apple pie for breakfast!"],
  ["easy", "vegetarian", "comfort-food", "15-minute"])

R("Chia Seed Pudding Bowl", "sunny", "breakfast",
  ["¼ cup chia seeds", "1 cup coconut milk", "1 tbsp honey", "½ tsp vanilla", "Fresh fruit for topping", "Granola"],
  ["Mix chia seeds, coconut milk, honey, and vanilla", "Stir well to prevent clumps", "Cover and refrigerate overnight", "In the morning, stir again", "Top with fresh fruit and granola", "It thickens like magic!"],
  ["easy", "healthy", "no-cook", "make-ahead", "vegetarian"])

R("Breakfast Corn Dogs", "windy", "breakfast",
  ["8 breakfast sausage links", "1 cup pancake mix", "¾ cup milk", "1 egg", "2 tbsp sugar", "Oil for frying", "Wooden sticks"],
  ["Cook sausage links and let cool", "Mix pancake mix, milk, egg, and sugar", "Insert sticks into sausages", "Dip each sausage in batter", "Fry in 350°F oil for 2-3 minutes (grown-up job!)", "Drain on paper towels", "Dip in maple syrup!"],
  ["fun", "protein"])

R("Monkey Bread Bites", "snowy", "breakfast",
  ["1 can biscuit dough", "½ cup sugar", "2 tsp cinnamon", "¼ cup butter (melted)", "¼ cup brown sugar"],
  ["Preheat oven to 350°F", "Cut each biscuit into quarters", "Mix sugar and cinnamon in a bag", "Toss dough pieces in cinnamon sugar", "Place in a greased bundt or muffin pan", "Mix melted butter and brown sugar, pour over top", "Bake 25-30 minutes until golden, flip onto a plate"],
  ["sweet", "fun", "baking"])

R("Cookie Dough Overnight Oats", "sunny", "breakfast",
  ["1 cup rolled oats", "1 cup milk", "2 tbsp peanut butter", "1 tbsp honey", "2 tbsp mini chocolate chips", "½ tsp vanilla"],
  ["Mix oats, milk, peanut butter, honey, and vanilla", "Stir until combined", "Cover and refrigerate overnight", "In the morning, stir in chocolate chips", "Eat cold — it tastes like cookie dough!"],
  ["easy", "sweet", "no-cook", "make-ahead", "fun"])

R("Strawberry Cheesecake Overnight Oats", "sunny", "breakfast",
  ["1 cup rolled oats", "1 cup milk", "2 tbsp cream cheese (softened)", "1 tbsp honey", "½ cup diced strawberries", "2 tbsp graham cracker crumbs"],
  ["Mix oats, milk, cream cheese, and honey", "Stir until cream cheese is blended in", "Fold in diced strawberries", "Refrigerate overnight", "Top with graham cracker crumbs in the morning"],
  ["easy", "sweet", "no-cook", "make-ahead"])

R("Sausage and Cheese Pinwheels", "windy", "breakfast",
  ["1 sheet puff pastry", "8 oz breakfast sausage (cooked, crumbled)", "1 cup shredded cheddar", "1 egg (beaten)", "1 tsp garlic powder"],
  ["Preheat oven to 400°F", "Unroll puff pastry on a floured surface", "Spread sausage and cheese evenly over pastry", "Roll up tightly into a log", "Slice into 1-inch pinwheels", "Place on a baking sheet, brush with beaten egg", "Bake 15-18 minutes until golden and puffed"],
  ["protein", "savory", "make-ahead"])

R("Banana Bread Oatmeal Bake", "rainy", "breakfast",
  ["2 cups rolled oats", "2 ripe bananas (mashed)", "1½ cups milk", "1 egg", "2 tbsp maple syrup", "1 tsp cinnamon", "½ cup walnuts"],
  ["Preheat oven to 375°F", "Mix oats, mashed bananas, milk, egg, syrup, and cinnamon", "Pour into a greased baking dish", "Top with walnuts", "Bake 30-35 minutes until set and golden", "Cut into squares", "Serve warm with extra maple syrup"],
  ["healthy", "baking", "make-ahead", "comfort-food"])

# ═══════════════════════ MORE LUNCH ═════════════════════════════════════════

R("Broccoli Cheddar Mac", "rainy", "lunch",
  ["2 cups elbow macaroni", "2 cups shredded cheddar", "2 cups broccoli florets", "2 tbsp butter", "2 tbsp flour", "2 cups milk"],
  ["Cook macaroni and broccoli together, drain", "Melt butter, stir in flour, cook 1 minute", "Add milk slowly, stir until thick", "Melt in cheddar until creamy", "Combine with pasta and broccoli", "Stir gently and serve hot"],
  ["easy", "vegetarian", "comfort-food"])

R("Buffalo Chicken Mac", "windy", "lunch",
  ["2 cups macaroni", "1 cup shredded chicken", "¼ cup buffalo sauce", "2 cups cheddar", "2 cups milk", "2 tbsp butter", "2 tbsp flour"],
  ["Cook and drain macaroni", "Toss chicken with buffalo sauce", "Make cheese sauce: butter, flour, milk, cheese", "Combine pasta with cheese sauce", "Top with buffalo chicken", "Sprinkle extra cheese", "Serve with celery sticks and ranch"],
  ["protein", "comfort-food"])

R("Tomato Soup Grilled Cheese", "snowy", "lunch",
  ["2 slices sourdough bread", "3 slices cheddar", "2 tbsp butter", "1 can tomato soup", "½ cup milk"],
  ["Make grilled cheese: butter bread, add cheese, cook until golden", "Heat tomato soup with milk in a pot", "Cut grilled cheese into strips", "Pour soup into a bowl", "Dunk the grilled cheese strips into the soup!", "The classic combo!"],
  ["easy", "vegetarian", "comfort-food"])

R("Ham and Swiss Grilled Cheese", "rainy", "lunch",
  ["2 slices rye bread", "2 slices Swiss cheese", "2 slices deli ham", "1 tbsp butter", "1 tsp Dijon mustard"],
  ["Butter one side of each bread slice", "Spread mustard on the inside", "Layer Swiss cheese and ham", "Cook over medium heat until golden", "Flip carefully and cook the other side", "Cut diagonally and serve"],
  ["easy", "protein", "15-minute"])

R("Chicken Salad Sandwich", "sunny", "lunch",
  ["2 cups cooked shredded chicken", "¼ cup mayo", "1 celery stalk (diced)", "¼ cup grapes (halved)", "4 bread slices", "Lettuce"],
  ["Mix chicken, mayo, celery, and grapes", "Season with salt and pepper", "Scoop onto bread slices", "Add lettuce on top", "Top with second bread slice", "Cut into halves or triangles"],
  ["easy", "protein", "no-cook", "15-minute"])

R("Tuna Melt Sandwich", "cloudy", "lunch",
  ["1 can tuna (drained)", "2 tbsp mayo", "4 bread slices", "4 slices cheddar", "1 tbsp butter", "1 celery stalk (diced)"],
  ["Mix tuna, mayo, and celery", "Spread tuna on two bread slices", "Top with cheddar cheese", "Add second bread slice", "Butter outsides and cook in a pan", "Cook 3 minutes per side until cheese melts", "Serve warm and gooey"],
  ["easy", "protein", "15-minute"])

R("Veggie Cream Cheese Wrap", "sunny", "lunch",
  ["2 flour tortillas", "4 tbsp cream cheese", "½ cucumber (sliced)", "1 carrot (shredded)", "½ cup spinach", "Salt and pepper"],
  ["Spread cream cheese over each tortilla", "Layer cucumber, carrot, and spinach", "Season with salt and pepper", "Roll up tightly", "Cut in half diagonally", "Wrap in foil for lunchbox"],
  ["easy", "vegetarian", "healthy", "no-cook", "15-minute"])

R("Chicken Caesar Wrap", "sunny", "lunch",
  ["2 flour tortillas", "1 cup grilled chicken (sliced)", "1 cup romaine lettuce (chopped)", "¼ cup parmesan", "2 tbsp Caesar dressing", "Croutons"],
  ["Lay tortillas flat", "Drizzle Caesar dressing down the middle", "Layer chicken, lettuce, and parmesan", "Add a few croutons for crunch", "Roll up tightly", "Cut in half and serve"],
  ["easy", "protein", "15-minute"])

R("BLT Wrap", "sunny", "lunch",
  ["2 flour tortillas", "6 slices bacon (cooked)", "1 cup lettuce", "1 tomato (sliced)", "2 tbsp mayo"],
  ["Spread mayo on each tortilla", "Layer bacon, lettuce, and tomato", "Roll up tightly, tucking in the sides", "Cut diagonally", "Secure with a toothpick if needed"],
  ["easy", "protein", "15-minute"])

R("Pesto Pasta Twirls", "sunny", "lunch",
  ["8 oz fusilli pasta", "½ cup basil pesto", "¼ cup parmesan", "1 cup cherry tomatoes (halved)", "1 tbsp olive oil", "Pine nuts"],
  ["Cook pasta according to package", "Drain and toss with pesto and olive oil", "Add cherry tomatoes", "Sprinkle parmesan on top", "Garnish with pine nuts", "Serve warm or cold — both are delicious!"],
  ["easy", "vegetarian", "30-minute"])

R("Baked Ziti", "rainy", "lunch",
  ["8 oz ziti pasta", "2 cups marinara sauce", "1 cup ricotta", "1½ cups mozzarella", "¼ cup parmesan", "Italian seasoning"],
  ["Preheat oven to 375°F", "Cook ziti until almost done, drain", "Mix pasta with marinara and ricotta", "Pour half into a baking dish", "Add layer of mozzarella", "Add remaining pasta, top with cheese and parmesan", "Bake 25 minutes until bubbly and golden"],
  ["vegetarian", "comfort-food", "baking"])

R("Pasta Salad Cups", "sunny", "lunch",
  ["2 cups rotini (cooked, cooled)", "½ cup cherry tomatoes", "½ cup cucumber (diced)", "¼ cup olives", "¼ cup Italian dressing", "¼ cup feta cheese"],
  ["Cook pasta and rinse with cold water", "Dice all vegetables", "Toss pasta with veggies and dressing", "Sprinkle feta on top", "Serve in individual cups", "Great for lunchboxes!"],
  ["easy", "vegetarian", "no-cook", "make-ahead"])

R("Bow Tie Pasta with Peas", "cloudy", "lunch",
  ["8 oz bow tie pasta", "1 cup frozen peas", "2 tbsp butter", "¼ cup parmesan", "1 clove garlic", "Salt and pepper"],
  ["Cook pasta, adding peas in last 2 minutes", "Drain, saving ½ cup pasta water", "Melt butter with minced garlic in the pot", "Return pasta and peas to the pot", "Add parmesan and splash of pasta water", "Toss until creamy"],
  ["easy", "vegetarian", "15-minute"])

R("Cheesy Tortellini", "rainy", "lunch",
  ["1 lb cheese tortellini", "2 cups marinara sauce", "½ cup mozzarella", "2 tbsp parmesan", "Fresh basil"],
  ["Cook tortellini according to package", "Heat marinara sauce in a pan", "Toss tortellini in sauce", "Top with mozzarella", "Cover until cheese melts", "Sprinkle parmesan and basil on top"],
  ["easy", "vegetarian", "30-minute", "comfort-food"])

R("Teriyaki Chicken Rice Bowl", "cloudy", "lunch",
  ["1 lb chicken breast (diced)", "3 tbsp teriyaki sauce", "2 cups cooked rice", "1 cup steamed broccoli", "1 tbsp sesame oil", "Sesame seeds", "Green onions"],
  ["Cook diced chicken in sesame oil until browned", "Add teriyaki sauce and cook 2 more minutes", "Divide rice into bowls", "Top with teriyaki chicken", "Add steamed broccoli", "Sprinkle sesame seeds and green onions"],
  ["easy", "protein", "30-minute", "healthy"])

R("Hawaiian Pizza Bites", "sunny", "lunch",
  ["4 English muffins (halved)", "½ cup pizza sauce", "1 cup mozzarella", "½ cup diced ham", "½ cup pineapple chunks"],
  ["Preheat oven to 400°F", "Spread sauce on each muffin half", "Top with mozzarella", "Add ham and pineapple", "Bake 8-10 minutes until bubbly", "The sweet and savory combo is amazing!"],
  ["easy", "fun", "15-minute"])

R("Minestrone Soup", "snowy", "lunch",
  ["4 cups vegetable broth", "1 can diced tomatoes", "1 cup small pasta", "1 can kidney beans", "1 cup diced zucchini", "1 cup diced carrots", "Italian seasoning"],
  ["Heat broth and tomatoes in a large pot", "Add carrots and cook 5 minutes", "Add zucchini, beans, and Italian seasoning", "Add pasta and cook until tender", "Season with salt and pepper", "Serve with crusty bread"],
  ["healthy", "vegetarian", "one-pot", "comfort-food"])

R("Veggie Spring Rolls", "sunny", "lunch",
  ["8 rice paper wrappers", "1 cup shredded carrots", "1 cup cucumber (julienned)", "1 cup lettuce", "½ cup rice noodles (cooked)", "Peanut sauce for dipping"],
  ["Soften rice paper in warm water for 10 seconds", "Lay flat and add a bit of each filling", "Fold sides in, then roll up tightly", "Repeat with remaining wrappers", "Cut in half if you want", "Serve with peanut dipping sauce"],
  ["healthy", "vegetarian", "no-cook", "fun"])

R("Chicken Lettuce Wraps", "sunny", "lunch",
  ["1 lb ground chicken", "2 tbsp soy sauce", "1 tbsp hoisin sauce", "1 tsp sesame oil", "1 can water chestnuts (diced)", "Butter lettuce leaves", "Green onions"],
  ["Cook ground chicken in sesame oil until done", "Add soy sauce, hoisin, and water chestnuts", "Cook 2 more minutes", "Spoon into lettuce cups", "Top with green onions", "Wrap and eat with your hands!"],
  ["healthy", "protein", "15-minute"])

R("Chicken Pot Pie Bites", "snowy", "lunch",
  ["1 can crescent roll dough", "1 cup cooked diced chicken", "½ cup frozen peas and carrots", "½ cup cream of chicken soup", "½ cup shredded cheddar"],
  ["Preheat oven to 375°F", "Press dough into muffin tin cups", "Mix chicken, veggies, and soup", "Spoon filling into dough cups", "Top with shredded cheddar", "Bake 15-18 minutes until golden", "Mini pot pies!"],
  ["easy", "protein", "fun", "30-minute"])

R("Philly Cheesesteak Sliders", "windy", "lunch",
  ["1 lb shaved steak", "4 slider buns", "4 slices provolone", "1 bell pepper (sliced)", "1 onion (sliced)", "2 tbsp olive oil"],
  ["Cook peppers and onions in olive oil until soft", "Add shaved steak and cook until browned", "Divide meat and veggies onto buns", "Top each with provolone", "Broil 1-2 minutes until cheese melts", "Serve immediately"],
  ["protein", "30-minute"])

R("Pulled BBQ Chicken Sandwiches", "cloudy", "lunch",
  ["2 cups shredded cooked chicken", "1 cup BBQ sauce", "4 hamburger buns", "Coleslaw", "Pickles"],
  ["Mix chicken with BBQ sauce in a pan", "Heat over medium until warmed through", "Toast hamburger buns", "Pile BBQ chicken on bottom buns", "Top with coleslaw and pickles", "Press top bun on and serve"],
  ["easy", "protein", "15-minute"])

R("Bagel Pizzas", "windy", "lunch",
  ["4 bagels (halved)", "½ cup pizza sauce", "1½ cups shredded mozzarella", "Toppings of your choice"],
  ["Preheat oven to 400°F", "Place bagel halves on a baking sheet", "Spread pizza sauce on each half", "Add mozzarella and your toppings", "Bake 10-12 minutes until cheese bubbles", "Let cool slightly before eating"],
  ["easy", "fun", "15-minute"])

R("Crispy Zucchini Sticks", "sunny", "lunch",
  ["2 large zucchini", "1 cup panko breadcrumbs", "½ cup parmesan", "2 eggs", "½ cup flour", "Marinara for dipping"],
  ["Preheat oven to 425°F", "Cut zucchini into thick sticks", "Set up breading: flour, eggs, panko mixed with parmesan", "Coat each stick", "Place on a lined baking sheet", "Bake 18-20 minutes until crispy", "Serve with marinara for dipping"],
  ["easy", "vegetarian", "healthy", "30-minute"])

R("Popcorn Chicken Bites", "sunny", "lunch",
  ["1 lb chicken breast (cubed small)", "1 cup flour", "2 eggs", "1½ cups panko", "1 tsp garlic powder", "1 tsp paprika", "Ranch for dipping"],
  ["Preheat oven to 425°F", "Season flour with garlic and paprika", "Coat chicken: flour, egg, panko", "Spread on a baking sheet", "Spray with cooking spray", "Bake 15 minutes, flip, bake 5 more", "Dip in ranch!"],
  ["protein", "fun", "30-minute"])

R("Cheese and Bean Nachos", "windy", "lunch",
  ["Tortilla chips", "1 can refried beans", "1½ cups shredded cheese", "½ cup salsa", "¼ cup sour cream", "1 avocado", "Jalapeños (optional)"],
  ["Preheat oven to 375°F", "Spread chips on a baking sheet", "Drop spoonfuls of beans over chips", "Cover with shredded cheese", "Bake 8-10 minutes until cheese melts", "Top with salsa, sour cream, and avocado", "Eat fast before they get soggy!"],
  ["easy", "fun", "vegetarian", "party", "15-minute"])

R("Orange Chicken Bites", "cloudy", "lunch",
  ["1 lb chicken breast (cubed)", "½ cup orange juice", "3 tbsp soy sauce", "2 tbsp honey", "1 tbsp cornstarch", "1 cup flour", "Oil for frying"],
  ["Coat chicken cubes in flour and fry until golden", "Mix OJ, soy sauce, honey, and cornstarch", "Heat sauce in a pan until thick", "Toss fried chicken in the sauce", "Sprinkle sesame seeds on top", "Serve over rice"],
  ["protein", "sweet", "30-minute"])

R("Honey Garlic Chicken Bites", "cloudy", "lunch",
  ["1 lb chicken breast (cubed)", "3 tbsp honey", "2 tbsp soy sauce", "2 cloves garlic (minced)", "1 tbsp butter", "Sesame seeds", "Rice for serving"],
  ["Cook chicken in butter until golden", "Add garlic and cook 30 seconds", "Pour in honey and soy sauce", "Toss to coat, cook until sauce thickens", "Sprinkle sesame seeds on top", "Serve over steamed rice"],
  ["easy", "protein", "30-minute"])

R("Sesame Noodles", "cloudy", "lunch",
  ["8 oz spaghetti", "3 tbsp soy sauce", "2 tbsp sesame oil", "1 tbsp honey", "1 tbsp rice vinegar", "1 cucumber (julienned)", "Sesame seeds"],
  ["Cook spaghetti and drain", "Whisk soy sauce, sesame oil, honey, and vinegar", "Toss noodles with sauce", "Top with cucumber", "Sprinkle sesame seeds", "Serve cold or warm"],
  ["easy", "vegetarian", "15-minute"])

R("Peanut Noodles", "cloudy", "lunch",
  ["8 oz spaghetti", "3 tbsp peanut butter", "2 tbsp soy sauce", "1 tbsp honey", "1 tbsp lime juice", "1 tsp sesame oil", "Crushed peanuts"],
  ["Cook spaghetti and drain", "Whisk PB, soy sauce, honey, lime, and sesame oil", "Add a splash of pasta water to thin the sauce", "Toss noodles in peanut sauce", "Top with crushed peanuts", "Garnish with green onions"],
  ["easy", "vegetarian", "30-minute"])

R("Garlic Bread Sticks", "rainy", "lunch",
  ["1 can refrigerated breadstick dough", "3 tbsp butter (melted)", "2 cloves garlic (minced)", "2 tbsp parmesan", "Parsley", "Marinara for dipping"],
  ["Preheat oven to 375°F", "Separate and twist dough sticks", "Place on a baking sheet", "Mix melted butter with garlic", "Brush garlic butter on each stick", "Sprinkle parmesan and parsley", "Bake 12-15 minutes, serve with marinara"],
  ["easy", "vegetarian", "30-minute"])

R("Cucumber Sushi Rolls", "sunny", "lunch",
  ["2 cups sushi rice (cooked, seasoned)", "4 nori sheets", "1 cucumber (julienned)", "1 avocado (sliced)", "1 carrot (julienned)", "Soy sauce for dipping"],
  ["Place nori on a bamboo mat or plastic wrap", "Spread rice evenly over nori", "Lay cucumber, avocado, and carrot in a line", "Roll up tightly using the mat", "Wet the edge to seal", "Slice with a wet knife into rounds", "Dip in soy sauce"],
  ["healthy", "vegetarian", "fun"])

R("Mini Shepherd's Pie Cups", "snowy", "lunch",
  ["1 lb ground beef", "1 cup frozen peas and carrots", "½ cup beef gravy", "2 cups mashed potatoes", "½ cup shredded cheddar"],
  ["Preheat oven to 375°F", "Brown beef and drain", "Mix with gravy and veggies", "Spoon into greased muffin tin", "Top each with mashed potatoes", "Sprinkle cheese on top", "Bake 20 minutes until golden"],
  ["protein", "comfort-food", "fun"])

R("White Chicken Chili", "snowy", "lunch",
  ["2 cups cooked shredded chicken", "2 cans white beans", "4 cups chicken broth", "1 can diced green chiles", "1 tsp cumin", "½ cup sour cream", "1 cup shredded Monterey Jack"],
  ["Combine chicken, beans, broth, chiles, and cumin in a pot", "Bring to a boil, then simmer 20 minutes", "Stir in sour cream", "Ladle into bowls", "Top with shredded cheese", "Serve with tortilla chips"],
  ["protein", "comfort-food", "one-pot"])

R("Corn Chowder", "snowy", "lunch",
  ["4 cups corn kernels", "3 cups chicken broth", "1 cup heavy cream", "4 slices bacon (cooked, crumbled)", "1 potato (diced)", "1 onion (diced)", "Salt and pepper"],
  ["Cook onion and potato in a pot until soft", "Add corn and broth, simmer 15 minutes", "Mash some corn against the side for thickness", "Stir in cream", "Season with salt and pepper", "Top with crumbled bacon"],
  ["comfort-food", "one-pot"])

R("Egg Drop Soup", "rainy", "lunch",
  ["4 cups chicken broth", "2 eggs", "1 tbsp cornstarch", "2 tbsp water", "1 tsp sesame oil", "Green onions", "Salt"],
  ["Bring broth to a boil", "Mix cornstarch with water, stir into broth", "Beat eggs in a small bowl", "Slowly drizzle eggs into simmering broth", "Stir gently — the eggs make pretty ribbons!", "Add sesame oil", "Top with green onions"],
  ["easy", "15-minute", "healthy"])

R("Shrimp Fried Rice", "cloudy", "lunch",
  ["3 cups cooked rice (cold)", "1 cup cooked shrimp", "2 eggs", "1 cup frozen peas and carrots", "3 tbsp soy sauce", "1 tbsp sesame oil", "Green onions"],
  ["Heat sesame oil in a wok over high heat", "Scramble eggs, set aside", "Cook veggies and shrimp 2 minutes", "Add cold rice and soy sauce", "Toss and cook 3-4 minutes", "Mix in scrambled eggs", "Top with green onions"],
  ["protein", "30-minute"])

R("Fish and Chips Bites", "rainy", "lunch",
  ["1 lb white fish fillets", "1 cup panko breadcrumbs", "½ cup flour", "2 eggs", "Frozen fries", "Tartar sauce", "Lemon wedges"],
  ["Preheat oven to 425°F", "Cut fish into bite-sized pieces", "Bread: flour, egg, panko", "Bake fish bites and fries together", "Fish needs 12-15 minutes", "Serve with tartar sauce and lemon", "Sprinkle with malt vinegar if you're fancy"],
  ["protein", "fun", "30-minute"])

# ═══════════════════════ MORE DINNER ════════════════════════════════════════

R("Lemon Herb Roasted Chicken", "cloudy", "dinner",
  ["1 whole chicken (3-4 lbs)", "2 lemons", "4 cloves garlic", "2 tbsp olive oil", "Fresh rosemary and thyme", "Salt and pepper"],
  ["Preheat oven to 425°F", "Pat chicken dry and rub with olive oil", "Season inside and out with salt, pepper, and herbs", "Stuff cavity with lemon halves and garlic", "Place in a roasting pan", "Roast 1 hour until golden and juices run clear", "Let rest 10 minutes before carving"],
  ["protein", "healthy"])

R("BBQ Glazed Chicken", "sunny", "dinner",
  ["4 chicken breasts", "1 cup BBQ sauce", "1 tbsp olive oil", "1 tsp garlic powder", "Salt and pepper"],
  ["Preheat oven to 400°F", "Season chicken with garlic, salt, and pepper", "Brush with half the BBQ sauce", "Bake 20 minutes", "Brush with remaining sauce", "Bake 10 more minutes", "Let rest before slicing"],
  ["easy", "protein", "30-minute"])

R("Teriyaki Chicken Thighs", "cloudy", "dinner",
  ["6 chicken thighs", "¼ cup soy sauce", "2 tbsp honey", "1 tbsp rice vinegar", "1 tsp ginger", "1 tsp garlic", "Sesame seeds"],
  ["Mix soy sauce, honey, vinegar, ginger, and garlic", "Marinate chicken 30 minutes", "Bake at 400°F for 30-35 minutes", "Brush with extra sauce halfway through", "Sprinkle sesame seeds on top", "Serve with rice and steamed veggies"],
  ["protein", "30-minute"])

R("Chicken Alfredo Bake", "rainy", "dinner",
  ["8 oz penne pasta", "2 cups cooked shredded chicken", "1 jar Alfredo sauce", "2 cups mozzarella", "½ cup parmesan", "Italian seasoning"],
  ["Preheat oven to 375°F", "Cook penne and drain", "Mix pasta, chicken, and Alfredo sauce", "Pour into a baking dish", "Top with mozzarella and parmesan", "Sprinkle Italian seasoning", "Bake 25 minutes until bubbly"],
  ["protein", "comfort-food", "baking"])

R("Chicken Fajitas", "sunny", "dinner",
  ["1 lb chicken breast (sliced)", "2 bell peppers (sliced)", "1 onion (sliced)", "2 tbsp fajita seasoning", "2 tbsp olive oil", "Flour tortillas", "Toppings: cheese, sour cream, salsa"],
  ["Heat olive oil in a large skillet", "Cook chicken with seasoning until done, set aside", "Cook peppers and onion until tender-crisp", "Return chicken to the pan", "Warm tortillas", "Fill with fajita mix and your favorite toppings"],
  ["protein", "healthy", "30-minute"])

R("Coconut Curry Chicken", "rainy", "dinner",
  ["1 lb chicken breast (cubed)", "1 can coconut milk", "2 tbsp curry paste (mild)", "1 cup frozen peas", "1 tbsp oil", "Salt", "Rice for serving"],
  ["Cook chicken in oil until browned", "Add curry paste and stir 1 minute", "Pour in coconut milk and stir", "Simmer 15 minutes", "Add peas and cook 5 more minutes", "Serve over steamed rice"],
  ["protein", "comfort-food", "one-pot"])

R("Butter Chicken (Mild)", "rainy", "dinner",
  ["1 lb chicken breast (cubed)", "1 cup tomato puree", "½ cup heavy cream", "2 tbsp butter", "1 tbsp garam masala", "1 tsp turmeric", "Rice or naan"],
  ["Cook chicken in butter until browned", "Add tomato puree, garam masala, and turmeric", "Simmer 15 minutes", "Stir in heavy cream", "Cook 5 more minutes until rich and creamy", "Serve over rice or with naan bread"],
  ["protein", "comfort-food"])

R("Sticky Sesame Chicken", "cloudy", "dinner",
  ["1 lb chicken breast (cubed)", "3 tbsp soy sauce", "2 tbsp honey", "1 tbsp sesame oil", "1 tbsp cornstarch", "Sesame seeds", "Green onions"],
  ["Coat chicken in cornstarch", "Cook in sesame oil until golden and crispy", "Mix soy sauce and honey", "Pour sauce over chicken", "Toss until glazed and sticky", "Top with sesame seeds and green onions", "Serve with rice"],
  ["protein", "sweet", "30-minute"])

R("Turkey Meatballs in Marinara", "windy", "dinner",
  ["1 lb ground turkey", "¼ cup breadcrumbs", "1 egg", "1 tsp Italian seasoning", "2 cups marinara sauce", "Parmesan cheese", "Spaghetti for serving"],
  ["Mix turkey, breadcrumbs, egg, and seasoning", "Form into small meatballs", "Brown in a pan on all sides", "Add marinara sauce and simmer 15 minutes", "Cook spaghetti", "Serve meatballs and sauce over pasta", "Top with parmesan"],
  ["protein", "30-minute"])

R("BBQ Meatball Sliders", "sunny", "dinner",
  ["1 lb ground beef", "¼ cup breadcrumbs", "1 egg", "1 cup BBQ sauce", "8 slider buns", "Coleslaw"],
  ["Mix beef, breadcrumbs, and egg", "Form into small meatballs", "Brown in a pan, then add BBQ sauce", "Simmer 10 minutes until glazed", "Place 2-3 meatballs on each slider bun", "Top with coleslaw", "Serve with extra sauce"],
  ["protein", "fun", "party"])

R("Veggie Lasagna", "snowy", "dinner",
  ["9 lasagna noodles", "2 cups ricotta", "3 cups spinach", "2 cups mushrooms (sliced)", "2 cups marinara", "2 cups mozzarella", "½ cup parmesan"],
  ["Preheat oven to 375°F", "Cook noodles, sauté spinach and mushrooms", "Mix ricotta with half the parmesan", "Layer: sauce, noodles, ricotta, veggies, mozzarella", "Repeat layers twice", "Top with remaining cheese", "Bake covered 25 min, uncovered 15 min"],
  ["vegetarian", "comfort-food", "baking"])

R("Cottage Pie", "snowy", "dinner",
  ["1 lb ground turkey", "1 cup frozen mixed veggies", "1 cup turkey gravy", "3 cups mashed sweet potatoes", "½ cup cheddar", "1 onion (diced)"],
  ["Brown turkey with onion, drain", "Stir in gravy and frozen veggies", "Pour into a baking dish", "Spread sweet potato mash on top", "Sprinkle with cheddar", "Bake at 400°F for 20 minutes"],
  ["protein", "comfort-food"])

R("Turkey Pot Pie", "snowy", "dinner",
  ["2 cups cooked diced turkey", "1 cup frozen mixed veggies", "1 can cream of chicken soup", "½ cup milk", "2 refrigerated pie crusts", "Salt and pepper"],
  ["Preheat oven to 375°F", "Mix turkey, veggies, soup, and milk", "Line pie dish with bottom crust", "Pour in filling", "Add top crust, crimp edges, cut slits", "Bake 35-40 minutes until golden", "Perfect for using Thanksgiving leftovers!"],
  ["protein", "comfort-food"])

R("Lemon Butter Tilapia", "sunny", "dinner",
  ["4 tilapia fillets", "3 tbsp butter", "2 cloves garlic", "Juice of 1 lemon", "Fresh parsley", "Salt and pepper"],
  ["Season tilapia with salt and pepper", "Melt butter in a pan over medium heat", "Cook garlic 30 seconds", "Add tilapia and cook 3-4 minutes per side", "Squeeze lemon juice over the fish", "Garnish with parsley", "Serve with rice and steamed veggies"],
  ["easy", "protein", "healthy", "15-minute"])

R("Baked Fish and Chips", "rainy", "dinner",
  ["4 white fish fillets", "1 cup panko breadcrumbs", "4 large potatoes", "2 eggs", "3 tbsp olive oil", "Salt and malt vinegar"],
  ["Preheat oven to 425°F", "Cut potatoes into fries, toss with oil and salt", "Bake fries 20 minutes", "Bread fish: egg then panko", "Add fish to the baking sheet", "Bake everything 15 more minutes", "Serve with malt vinegar and tartar sauce"],
  ["protein", "comfort-food"])

R("Sweet and Sour Pork", "cloudy", "dinner",
  ["1 lb pork loin (cubed)", "1 cup pineapple chunks", "1 bell pepper (diced)", "½ cup ketchup", "3 tbsp rice vinegar", "3 tbsp sugar", "1 tbsp soy sauce"],
  ["Mix ketchup, vinegar, sugar, and soy sauce for sauce", "Coat pork in cornstarch and fry until golden", "Cook bell pepper 2 minutes", "Add pineapple and sauce to the pan", "Toss pork in the sauce", "Cook until everything is glazed", "Serve over steamed rice"],
  ["protein", "sweet"])

R("Pork Fried Rice", "cloudy", "dinner",
  ["3 cups cold cooked rice", "1 cup diced pork", "2 eggs", "1 cup frozen veggies", "3 tbsp soy sauce", "1 tbsp sesame oil", "Green onions"],
  ["Heat sesame oil in a wok", "Cook pork until browned", "Add veggies, cook 2 minutes", "Push to the side, scramble eggs", "Add rice and soy sauce", "Toss everything together", "Top with green onions"],
  ["protein", "30-minute"])

R("Pork Carnitas Tacos", "sunny", "dinner",
  ["2 lbs pork shoulder", "1 cup orange juice", "4 cloves garlic", "2 tsp cumin", "Small tortillas", "Cilantro and onion", "Lime wedges"],
  ["Season pork with cumin, salt, and pepper", "Place in slow cooker with OJ and garlic", "Cook on low 8 hours until falling apart", "Shred with two forks", "Broil shredded pork 5 minutes for crispy edges", "Serve in warm tortillas", "Top with cilantro, onion, and lime"],
  ["protein"])

R("Beef Stroganoff", "snowy", "dinner",
  ["1 lb beef sirloin (sliced thin)", "8 oz egg noodles", "1 cup mushrooms (sliced)", "1 cup beef broth", "½ cup sour cream", "2 tbsp butter", "2 tbsp flour"],
  ["Cook egg noodles and drain", "Brown beef in butter, set aside", "Cook mushrooms in the same pan", "Stir in flour, then add broth", "Simmer until thickened", "Stir in sour cream and return beef", "Serve over egg noodles"],
  ["protein", "comfort-food"])

R("Cheeseburger Casserole", "rainy", "dinner",
  ["1 lb ground beef", "2 cups cooked macaroni", "1 can tomato soup", "1½ cups shredded cheddar", "1 tbsp mustard", "Pickles for topping"],
  ["Preheat oven to 375°F", "Brown beef and drain", "Mix with cooked macaroni, soup, and mustard", "Pour into a baking dish", "Top with cheddar cheese", "Bake 20-25 minutes until bubbly", "Top with pickles — it tastes like a cheeseburger!"],
  ["easy", "protein", "comfort-food", "fun"])

R("Taco Pasta Bake", "windy", "dinner",
  ["1 lb ground beef", "1 packet taco seasoning", "8 oz rotini pasta", "1 can diced tomatoes", "1½ cups shredded cheese", "½ cup sour cream"],
  ["Preheat oven to 375°F", "Cook pasta and brown beef, drain both", "Mix beef with taco seasoning and tomatoes", "Combine with pasta and sour cream", "Pour into a baking dish", "Top with cheese", "Bake 20 minutes until cheese is melted"],
  ["easy", "protein", "comfort-food"])

R("Philly Cheesesteak Stuffed Peppers", "rainy", "dinner",
  ["4 bell peppers", "1 lb shaved steak", "1 onion (sliced)", "1 cup provolone cheese", "2 tbsp olive oil", "Salt and pepper"],
  ["Preheat oven to 400°F", "Cut peppers in half, remove seeds", "Cook steak and onions in olive oil", "Season with salt and pepper", "Fill pepper halves with steak mixture", "Top with provolone", "Bake 20 minutes until peppers are tender"],
  ["protein", "healthy"])

R("Mini Meatloaves", "rainy", "dinner",
  ["1 lb ground beef", "½ cup breadcrumbs", "1 egg", "¼ cup ketchup", "1 tsp onion powder", "Salt and pepper"],
  ["Preheat oven to 375°F", "Mix beef, breadcrumbs, egg, and seasonings", "Divide into muffin tin cups", "Top each with ketchup", "Bake 25 minutes", "These cook faster than a big meatloaf!", "Serve with mashed potatoes"],
  ["easy", "protein", "fun", "30-minute"])

R("Honey BBQ Ribs", "sunny", "dinner",
  ["2 racks baby back ribs", "½ cup BBQ sauce", "¼ cup honey", "2 tbsp brown sugar", "1 tsp garlic powder", "Salt and pepper"],
  ["Mix BBQ sauce with honey for glaze", "Season ribs with brown sugar, garlic, salt, pepper", "Wrap in foil, bake at 300°F for 2.5 hours", "Unwrap and brush with honey BBQ glaze", "Broil 5 minutes until caramelized", "So sticky and good!"],
  ["protein"])

R("Taco Stuffed Peppers", "windy", "dinner",
  ["4 bell peppers", "1 lb ground beef", "1 packet taco seasoning", "1 cup cooked rice", "1 cup shredded cheese", "½ cup salsa"],
  ["Preheat oven to 375°F", "Brown beef with taco seasoning", "Mix with rice and salsa", "Cut tops off peppers, remove seeds", "Stuff peppers with taco meat mixture", "Top with cheese", "Bake 25-30 minutes until peppers are soft"],
  ["protein", "fun"])

R("Chicken and Broccoli Stir Fry", "cloudy", "dinner",
  ["1 lb chicken breast (sliced)", "3 cups broccoli florets", "3 tbsp soy sauce", "1 tbsp honey", "1 tsp cornstarch", "1 tbsp sesame oil", "Rice for serving"],
  ["Mix soy sauce, honey, and cornstarch", "Heat sesame oil in a wok", "Cook chicken until done, set aside", "Stir fry broccoli 3-4 minutes", "Return chicken, pour sauce over", "Toss until everything is coated", "Serve over rice"],
  ["protein", "healthy", "30-minute"])

R("Beef and Broccoli", "rainy", "dinner",
  ["1 lb flank steak (sliced thin)", "3 cups broccoli florets", "¼ cup soy sauce", "2 tbsp brown sugar", "1 tbsp cornstarch", "1 tbsp sesame oil", "Rice for serving"],
  ["Mix soy sauce, brown sugar, and cornstarch", "Heat sesame oil in a wok over high heat", "Sear beef until browned, set aside", "Stir fry broccoli 3 minutes", "Return beef and pour sauce over", "Toss until sauce thickens", "Serve over steamed rice"],
  ["protein", "30-minute"])

R("Chicken Lo Mein", "windy", "dinner",
  ["8 oz lo mein noodles", "1 cup cooked shredded chicken", "1 cup mixed vegetables", "3 tbsp soy sauce", "1 tbsp sesame oil", "1 tbsp oyster sauce", "Green onions"],
  ["Cook noodles and drain", "Heat sesame oil in a wok", "Cook vegetables 3 minutes", "Add chicken and noodles", "Pour soy sauce and oyster sauce over", "Toss with tongs until combined", "Top with green onions"],
  ["protein", "30-minute"])

R("Baked Ravioli", "rainy", "dinner",
  ["1 bag frozen cheese ravioli", "2 cups marinara sauce", "1½ cups mozzarella", "½ cup parmesan", "Italian seasoning"],
  ["Preheat oven to 375°F", "Spread sauce in bottom of baking dish", "Layer frozen ravioli over sauce", "Add more sauce and cheese", "Repeat layers", "Sprinkle Italian seasoning on top", "Bake 35-40 minutes until bubbly"],
  ["easy", "vegetarian", "comfort-food"])

R("Stuffed Shells", "rainy", "dinner",
  ["1 box jumbo pasta shells", "2 cups ricotta", "1 cup mozzarella", "1 egg", "2 cups marinara", "½ cup parmesan", "Fresh basil"],
  ["Preheat oven to 375°F", "Cook shells until almost done, drain", "Mix ricotta, half the mozzarella, egg, and parmesan", "Stuff each shell with cheese mixture", "Spread sauce in a baking dish", "Arrange stuffed shells in the dish", "Top with remaining mozzarella, bake 30 minutes"],
  ["vegetarian", "comfort-food", "baking"])

R("Baked Penne", "windy", "dinner",
  ["8 oz penne pasta", "1 lb Italian sausage", "2 cups marinara", "1½ cups mozzarella", "½ cup ricotta", "Italian seasoning"],
  ["Preheat oven to 375°F", "Cook penne and brown sausage separately", "Mix pasta, sausage, marinara, and ricotta", "Pour into a baking dish", "Top with mozzarella", "Bake 25 minutes until bubbly and golden"],
  ["protein", "comfort-food"])

R("Tuna Noodle Casserole", "rainy", "dinner",
  ["8 oz egg noodles", "2 cans tuna (drained)", "1 can cream of mushroom soup", "1 cup frozen peas", "1 cup shredded cheddar", "½ cup milk", "1 cup crushed potato chips"],
  ["Preheat oven to 375°F", "Cook noodles and drain", "Mix noodles, tuna, soup, peas, milk, and half the cheese", "Pour into a baking dish", "Top with remaining cheese and crushed chips", "Bake 25 minutes until golden", "Classic comfort food!"],
  ["protein", "comfort-food"])

R("Broccoli Rice Casserole", "rainy", "dinner",
  ["2 cups cooked rice", "2 cups broccoli (steamed)", "1 can cream of chicken soup", "1½ cups shredded cheddar", "½ cup milk", "½ cup crushed Ritz crackers"],
  ["Preheat oven to 350°F", "Mix rice, broccoli, soup, milk, and 1 cup cheese", "Pour into a greased baking dish", "Top with remaining cheese and cracker crumbs", "Bake 30 minutes until bubbly", "Let cool 5 minutes before serving"],
  ["easy", "vegetarian", "comfort-food"])

R("King Ranch Chicken", "windy", "dinner",
  ["3 cups cooked shredded chicken", "1 can cream of chicken soup", "1 can cream of mushroom soup", "1 can Rotel tomatoes", "12 corn tortillas", "2 cups shredded cheddar"],
  ["Preheat oven to 350°F", "Mix soups, Rotel, and chicken", "Layer tortillas, chicken mix, and cheese in a baking dish", "Repeat layers twice", "Top with remaining cheese", "Bake 30-35 minutes until bubbly"],
  ["protein", "comfort-food"])

R("Pot Roast with Vegetables", "snowy", "dinner",
  ["3 lb chuck roast", "4 potatoes (quartered)", "4 carrots (chunked)", "1 onion (quartered)", "2 cups beef broth", "1 packet onion soup mix"],
  ["Place roast in slow cooker", "Surround with potatoes, carrots, and onion", "Sprinkle onion soup mix on top", "Pour beef broth over everything", "Cook on low 8 hours", "Meat should fall apart with a fork", "Serve with the veggies and gravy"],
  ["protein", "comfort-food", "one-pot"])

R("Eggplant Parmesan", "rainy", "dinner",
  ["1 large eggplant", "1 cup breadcrumbs", "2 eggs", "2 cups marinara", "1½ cups mozzarella", "½ cup parmesan", "Fresh basil"],
  ["Preheat oven to 400°F", "Slice eggplant into ½-inch rounds", "Dip in egg, then breadcrumbs", "Bake on a sheet 20 minutes, flip halfway", "Layer in a dish: sauce, eggplant, cheese", "Repeat layers", "Bake 20 more minutes until melted and bubbly"],
  ["vegetarian", "comfort-food", "baking"])

R("Mushroom Risotto", "rainy", "dinner",
  ["1½ cups arborio rice", "4 cups chicken broth (warm)", "2 cups mushrooms (sliced)", "½ cup parmesan", "2 tbsp butter", "1 small onion (diced)", "½ cup white wine or broth"],
  ["Cook onion and mushrooms in butter", "Add rice and toast 2 minutes", "Add wine/broth and stir until absorbed", "Add warm broth one ladle at a time, stirring", "Keep stirring and adding broth for 18-20 minutes", "Stir in parmesan and extra butter", "Rice should be creamy and tender"],
  ["vegetarian", "comfort-food"])

R("Spinach and Ricotta Stuffed Shells", "snowy", "dinner",
  ["1 box jumbo shells", "2 cups ricotta", "2 cups spinach (chopped)", "1 cup mozzarella", "1 egg", "2 cups marinara", "½ cup parmesan"],
  ["Preheat oven to 375°F", "Cook shells until almost done", "Mix ricotta, spinach, half the mozzarella, and egg", "Stuff each shell", "Pour sauce in a baking dish", "Place shells in the dish", "Top with remaining cheese, bake 30 minutes"],
  ["vegetarian", "comfort-food", "baking"])

R("Hot Dog Bar Night", "sunny", "dinner",
  ["8 hot dogs", "8 hot dog buns", "Chili", "Shredded cheese", "Diced onions", "Relish, ketchup, mustard", "Sauerkraut"],
  ["Grill or boil hot dogs", "Toast buns lightly", "Set up all toppings in bowls", "Let everyone build their own dog", "Try a chili cheese dog!", "Or go classic with ketchup and mustard", "The fun is in the choosing!"],
  ["easy", "fun", "party", "15-minute"])

# ═══════════════════════ MORE SNACKS ════════════════════════════════════════

R("Green Power Smoothie", "sunny", "snack",
  ["1 cup spinach", "1 banana", "½ cup frozen mango", "1 cup apple juice", "1 tbsp honey"],
  ["Add spinach and apple juice to blender", "Blend until spinach is smooth", "Add banana, mango, and honey", "Blend until creamy", "You can't even taste the spinach!"],
  ["easy", "healthy", "15-minute", "no-cook"])

R("Chocolate PB Smoothie", "cloudy", "snack",
  ["1 frozen banana", "2 tbsp peanut butter", "1 tbsp cocoa powder", "1 cup milk", "1 tbsp honey"],
  ["Add all ingredients to blender", "Blend until thick and creamy", "Pour into a glass", "It tastes like a peanut butter cup!"],
  ["easy", "sweet", "15-minute", "no-cook"])

R("Orange Creamsicle Smoothie", "sunny", "snack",
  ["1 cup orange juice", "½ cup vanilla yogurt", "1 cup frozen mango", "1 tsp vanilla", "½ cup ice"],
  ["Combine all ingredients in blender", "Blend until smooth and frothy", "Pour into a glass", "Tastes like a creamsicle!"],
  ["easy", "sweet", "15-minute", "no-cook"])

R("Watermelon Slushie", "sunny", "snack",
  ["3 cups frozen watermelon cubes", "½ cup water", "1 tbsp lime juice", "1 tbsp honey"],
  ["Blend frozen watermelon with water", "Add lime juice and honey", "Blend until slushy consistency", "Pour into glasses and serve with a straw!"],
  ["easy", "healthy", "15-minute", "no-cook"])

R("Strawberry Lemonade Popsicles", "sunny", "snack",
  ["1 cup strawberries (pureed)", "1 cup lemonade", "2 tbsp honey"],
  ["Blend strawberries until smooth", "Mix with lemonade and honey", "Pour into popsicle molds", "Insert sticks", "Freeze 4+ hours", "Run warm water on mold to release"],
  ["easy", "healthy", "no-cook", "fun"])

R("Chocolate Banana Popsicles", "sunny", "snack",
  ["2 bananas", "1 cup chocolate milk", "2 tbsp cocoa powder", "1 tbsp honey"],
  ["Blend bananas with chocolate milk", "Add cocoa powder and honey", "Blend until smooth", "Pour into popsicle molds", "Freeze 4+ hours until solid"],
  ["easy", "sweet", "no-cook", "fun"])

R("Yogurt Berry Popsicles", "sunny", "snack",
  ["1½ cups vanilla yogurt", "1 cup mixed berries", "2 tbsp honey"],
  ["Blend yogurt, berries, and honey", "Pour into popsicle molds", "Insert sticks", "Freeze 4+ hours", "These are basically healthy ice cream!"],
  ["easy", "healthy", "no-cook"])

R("Snickerdoodle Cookies", "rainy", "snack",
  ["2¾ cups flour", "1 cup butter (softened)", "1½ cups sugar", "2 eggs", "2 tsp cream of tartar", "1 tsp baking soda", "3 tsp cinnamon"],
  ["Cream butter and 1 cup sugar", "Beat in eggs", "Mix in flour, cream of tartar, and baking soda", "Mix remaining sugar with cinnamon in a bowl", "Roll dough into balls, roll in cinnamon sugar", "Place on baking sheet", "Bake at 375°F for 10 minutes"],
  ["baking", "sweet", "fun"])

R("Double Chocolate Cookies", "rainy", "snack",
  ["1½ cups flour", "½ cup cocoa powder", "1 cup butter", "1 cup sugar", "1 egg", "1 cup chocolate chips", "1 tsp vanilla"],
  ["Cream butter and sugar", "Beat in egg and vanilla", "Mix in flour and cocoa powder", "Fold in chocolate chips", "Scoop onto baking sheets", "Bake at 350°F for 10-12 minutes", "So rich and chocolatey!"],
  ["baking", "sweet"])

R("M&M Cookies", "cloudy", "snack",
  ["2¼ cups flour", "1 cup butter", "¾ cup sugar", "¾ cup brown sugar", "2 eggs", "1 tsp vanilla", "1½ cups M&Ms"],
  ["Cream butter and both sugars", "Beat in eggs and vanilla", "Mix in flour gradually", "Fold in M&Ms", "Scoop onto baking sheets", "Press extra M&Ms on top for looks", "Bake at 375°F for 9-11 minutes"],
  ["baking", "sweet", "fun", "party"])

R("White Chocolate Macadamia Cookies", "cloudy", "snack",
  ["2 cups flour", "¾ cup butter", "¾ cup brown sugar", "½ cup sugar", "1 egg", "1 cup white chocolate chips", "½ cup macadamia nuts"],
  ["Cream butter and sugars", "Beat in egg", "Mix in flour", "Fold in white chocolate chips and nuts", "Scoop onto baking sheets", "Bake at 350°F for 10-12 minutes", "Let cool — they firm up as they cool"],
  ["baking", "sweet"])

R("Gingerbread Cookies", "snowy", "snack",
  ["3 cups flour", "¾ cup brown sugar", "½ cup butter", "½ cup molasses", "1 egg", "2 tsp ginger", "1 tsp cinnamon"],
  ["Mix butter, brown sugar, and molasses", "Beat in egg", "Add flour, ginger, and cinnamon", "Chill dough 1 hour", "Roll out and cut with cookie cutters", "Bake at 350°F for 8-10 minutes", "Decorate with icing!"],
  ["baking", "sweet", "fun", "party"])

R("Blondie Bars", "cloudy", "snack",
  ["½ cup butter (melted)", "1 cup brown sugar", "1 egg", "1 tsp vanilla", "1 cup flour", "½ cup chocolate chips", "½ cup butterscotch chips"],
  ["Preheat oven to 350°F", "Mix melted butter and brown sugar", "Beat in egg and vanilla", "Stir in flour", "Fold in chocolate and butterscotch chips", "Spread in a greased 8x8 pan", "Bake 25 minutes — don't overbake!"],
  ["baking", "sweet", "easy"])

R("Lemon Bars", "sunny", "snack",
  ["1 cup flour", "½ cup butter", "¼ cup powdered sugar", "2 eggs", "¾ cup sugar", "3 tbsp lemon juice", "1 tbsp lemon zest"],
  ["Mix flour, butter, and powdered sugar for crust", "Press into a 8x8 pan, bake at 350°F for 15 min", "Whisk eggs, sugar, lemon juice, and zest", "Pour over hot crust", "Bake 20 more minutes until set", "Cool completely", "Dust with powdered sugar and cut into bars"],
  ["baking", "sweet"])

R("Funfetti Cupcakes", "cloudy", "snack",
  ["1½ cups flour", "1 cup sugar", "½ cup butter", "2 eggs", "½ cup milk", "2 tsp vanilla", "⅓ cup rainbow sprinkles"],
  ["Preheat oven to 350°F", "Cream butter and sugar", "Beat in eggs and vanilla", "Alternate adding flour and milk", "Fold in sprinkles gently", "Fill cupcake liners ⅔ full", "Bake 18-22 minutes, frost with vanilla and more sprinkles"],
  ["baking", "sweet", "fun", "party"])

R("Red Velvet Cupcakes", "rainy", "snack",
  ["1½ cups flour", "1 cup sugar", "2 tbsp cocoa powder", "2 eggs", "½ cup buttermilk", "½ cup oil", "Red food coloring"],
  ["Preheat oven to 350°F", "Mix dry ingredients", "Whisk wet ingredients with food coloring", "Combine and mix until smooth", "Fill cupcake liners ⅔ full", "Bake 18-20 minutes", "Frost with cream cheese frosting"],
  ["baking", "sweet", "fun"])

R("Pumpkin Muffins", "rainy", "snack",
  ["1½ cups flour", "1 cup canned pumpkin", "¾ cup sugar", "⅓ cup oil", "2 eggs", "1 tsp pumpkin pie spice", "1 tsp baking soda"],
  ["Preheat oven to 350°F", "Mix pumpkin, sugar, oil, and eggs", "Add flour, spice, and baking soda", "Stir until just combined", "Fill muffin cups ¾ full", "Bake 20-22 minutes", "The house will smell amazing!"],
  ["baking", "sweet", "comfort-food"])

R("Cinnamon Apple Muffins", "rainy", "snack",
  ["1½ cups flour", "1 apple (diced small)", "¾ cup sugar", "⅓ cup oil", "1 egg", "½ cup milk", "2 tsp cinnamon"],
  ["Preheat oven to 375°F", "Mix flour, sugar, and cinnamon", "Whisk oil, egg, and milk", "Combine wet and dry", "Fold in diced apple", "Fill muffin cups ¾ full", "Bake 18-20 minutes until golden"],
  ["baking", "sweet", "easy"])

R("Chocolate Chip Banana Bread", "snowy", "snack",
  ["3 ripe bananas", "⅓ cup melted butter", "¾ cup sugar", "1 egg", "1½ cups flour", "1 tsp baking soda", "½ cup chocolate chips"],
  ["Preheat oven to 350°F", "Mash bananas in a bowl", "Mix in butter, sugar, and egg", "Add flour and baking soda", "Fold in chocolate chips", "Pour into a greased loaf pan", "Bake 55-60 minutes until done"],
  ["baking", "sweet", "easy"])

R("Zucchini Bread", "rainy", "snack",
  ["1½ cups flour", "1 cup shredded zucchini", "¾ cup sugar", "⅓ cup oil", "1 egg", "1 tsp cinnamon", "1 tsp baking soda"],
  ["Preheat oven to 350°F", "Mix flour, sugar, cinnamon, and baking soda", "Squeeze excess water from zucchini", "Mix oil, egg, and zucchini", "Combine wet and dry ingredients", "Pour into a greased loaf pan", "Bake 50-55 minutes until toothpick comes out clean"],
  ["baking", "healthy", "vegetarian"])

R("Caramel Popcorn", "windy", "snack",
  ["8 cups popped popcorn", "½ cup brown sugar", "¼ cup butter", "2 tbsp corn syrup", "¼ tsp baking soda", "Pinch of salt"],
  ["Preheat oven to 250°F", "Cook brown sugar, butter, and corn syrup until boiling", "Boil 4 minutes without stirring", "Remove from heat, stir in baking soda (it'll foam!)", "Pour over popcorn and toss to coat", "Spread on a baking sheet", "Bake 45 minutes, stirring every 15"],
  ["sweet", "fun", "party"])

R("Chocolate Rice Crispy Treats", "cloudy", "snack",
  ["6 cups rice cereal", "4 cups mini marshmallows", "3 tbsp butter", "½ cup chocolate chips"],
  ["Melt butter in a large pot", "Add marshmallows, stir until melted", "Stir in chocolate chips until swirled", "Add cereal and mix well", "Press into a greased pan", "Let cool and cut into squares"],
  ["easy", "sweet", "fun", "15-minute"])

R("Veggie Sticks with Ranch", "sunny", "snack",
  ["1 cup carrot sticks", "1 cup celery sticks", "1 cup cucumber slices", "1 cup cherry tomatoes", "½ cup ranch dressing"],
  ["Wash and cut all vegetables", "Arrange on a plate around a small bowl", "Fill bowl with ranch dressing", "Dip and crunch!", "Try to eat a rainbow of veggies!"],
  ["easy", "healthy", "no-cook", "15-minute"])

R("Hummus and Pita Chips", "sunny", "snack",
  ["1 can chickpeas", "2 tbsp tahini", "2 tbsp lemon juice", "1 clove garlic", "2 tbsp olive oil", "Pita bread"],
  ["Blend chickpeas, tahini, lemon juice, garlic, and oil", "Add water a tablespoon at a time until smooth", "Cut pita into triangles", "Brush with oil and bake at 375°F for 8 minutes", "Scoop hummus with crispy pita chips"],
  ["healthy", "vegetarian", "30-minute"])

R("Guacamole and Chips", "sunny", "snack",
  ["3 ripe avocados", "1 lime (juiced)", "¼ cup diced tomato", "¼ cup diced onion", "Salt", "Tortilla chips"],
  ["Cut avocados in half and remove pit", "Scoop into a bowl and mash with a fork", "Mix in lime juice, tomato, onion, and salt", "Keep it chunky or smooth — your choice!", "Serve with tortilla chips", "Eat immediately — it turns brown if you wait!"],
  ["easy", "healthy", "vegetarian", "no-cook", "15-minute"])

R("Apple Nachos", "sunny", "snack",
  ["2 apples (sliced thin)", "2 tbsp peanut butter (melted)", "2 tbsp caramel sauce", "2 tbsp mini chocolate chips", "2 tbsp granola"],
  ["Spread apple slices on a plate", "Drizzle melted peanut butter over them", "Drizzle caramel sauce", "Sprinkle chocolate chips and granola", "Eat like nachos — grab and go!"],
  ["easy", "fun", "sweet", "no-cook", "15-minute"])

R("Salted Caramel Hot Chocolate", "snowy", "snack",
  ["2 cups milk", "2 tbsp cocoa powder", "2 tbsp sugar", "2 tbsp caramel sauce", "Whipped cream", "Sea salt flakes"],
  ["Heat milk in a saucepan", "Whisk in cocoa and sugar until smooth", "Stir in caramel sauce", "Pour into mugs", "Top with whipped cream and caramel drizzle", "Sprinkle a few sea salt flakes on top"],
  ["easy", "sweet", "comfort-food"])

R("White Hot Chocolate", "snowy", "snack",
  ["2 cups milk", "½ cup white chocolate chips", "½ tsp vanilla", "Whipped cream", "Sprinkles"],
  ["Heat milk in a saucepan (don't boil!)", "Add white chocolate chips", "Stir until completely melted and smooth", "Add vanilla", "Pour into mugs", "Top with whipped cream and sprinkles"],
  ["easy", "sweet", "comfort-food"])

R("S'mores Bars", "windy", "snack",
  ["1½ cups graham cracker crumbs", "½ cup butter (melted)", "1 cup chocolate chips", "1½ cups mini marshmallows"],
  ["Preheat oven to 350°F", "Mix graham crumbs and butter, press into 8x8 pan", "Sprinkle chocolate chips evenly over crust", "Top with marshmallows", "Bake 15 minutes until marshmallows are golden", "Let cool slightly before cutting", "Gooey and amazing!"],
  ["easy", "sweet", "fun", "baking"])

R("Butterscotch Pudding", "rainy", "snack",
  ["2 cups milk", "½ cup brown sugar", "3 tbsp cornstarch", "2 tbsp butter", "1 tsp vanilla", "Pinch of salt"],
  ["Whisk brown sugar and cornstarch in a pot", "Gradually stir in milk", "Cook over medium heat, stirring constantly", "Keep going until thick and bubbly", "Remove from heat, stir in butter and vanilla", "Pour into cups and chill 2 hours"],
  ["sweet", "comfort-food", "make-ahead"])

R("Fruit Jello Cups", "sunny", "snack",
  ["1 box Jello (any flavor)", "1 cup boiling water", "1 cup cold water", "1 cup fresh fruit (diced)", "Whipped cream"],
  ["Dissolve Jello in boiling water", "Stir in cold water", "Pour into cups", "Drop fruit pieces into each cup", "Refrigerate 3-4 hours until firm", "Top with whipped cream"],
  ["easy", "fun", "sweet", "no-cook"])

R("Candy Apples", "windy", "snack",
  ["6 apples", "2 cups sugar", "½ cup corn syrup", "1 cup water", "Red food coloring", "Wooden sticks"],
  ["Insert sticks into apples", "Cook sugar, corn syrup, and water to 300°F (grown-up job!)", "Add food coloring", "Quickly dip each apple, twirling to coat", "Place on parchment paper to cool", "These are beautiful and delicious!"],
  ["sweet", "fun", "party"])

R("Caramel Apple Slices", "windy", "snack",
  ["2 apples (sliced)", "½ cup caramel sauce", "2 tbsp chopped peanuts", "Mini chocolate chips"],
  ["Slice apples and arrange on a plate", "Drizzle caramel sauce over slices", "Sprinkle chopped peanuts", "Add mini chocolate chips", "Eat with your hands!"],
  ["easy", "sweet", "fun", "no-cook", "15-minute"])

R("Yogurt Covered Pretzels", "cloudy", "snack",
  ["2 cups pretzel twists", "1 cup yogurt chips (melted)", "Sprinkles"],
  ["Line a baking sheet with parchment", "Dip each pretzel in melted yogurt", "Place on parchment", "Add sprinkles while still wet", "Refrigerate until coating is set", "Store in an airtight container"],
  ["easy", "sweet", "fun", "no-cook"])

R("Chocolate Dipped Pretzels", "snowy", "snack",
  ["2 cups pretzel rods", "1 cup chocolate chips (melted)", "Sprinkles", "Crushed nuts"],
  ["Melt chocolate chips in microwave in 30-second bursts", "Dip each pretzel rod halfway into chocolate", "Roll in sprinkles or crushed nuts", "Place on parchment paper", "Refrigerate until chocolate is set", "Wrap in cellophane for gifts!"],
  ["easy", "sweet", "fun", "no-cook", "party"])

R("Puppy Chow Snack Mix", "cloudy", "snack",
  ["9 cups rice cereal", "1 cup chocolate chips", "½ cup peanut butter", "¼ cup butter", "1½ cups powdered sugar"],
  ["Melt chocolate, PB, and butter together", "Pour over cereal in a big bowl, stir gently", "Pour powdered sugar into a large bag", "Add coated cereal to the bag", "Shake shake shake until coated!", "Spread on parchment to cool"],
  ["easy", "sweet", "fun", "party", "no-cook"])

R("Strawberry Shortcake Cups", "sunny", "snack",
  ["2 cups strawberries (diced)", "2 tbsp sugar", "1 cup whipped cream", "4 shortcake biscuits (or angel food cake)"],
  ["Mix strawberries with sugar, let sit 15 minutes", "Crumble biscuits into cups", "Spoon juicy strawberries over", "Top with whipped cream", "Repeat layers if cups are big enough", "Summer in a cup!"],
  ["easy", "sweet", "fun", "no-cook"])

R("Cinnamon Sugar Donut Holes", "snowy", "snack",
  ["1 can biscuit dough", "Oil for frying", "½ cup sugar", "1 tbsp cinnamon"],
  ["Cut each biscuit into quarters and roll into balls", "Heat oil to 350°F (grown-up job!)", "Fry dough balls 1-2 minutes until golden", "Drain on paper towels", "Mix sugar and cinnamon", "Roll warm donut holes in cinnamon sugar", "Pop 'em like candy!"],
  ["sweet", "fun"])

R("Cheese Stuffed Breadsticks", "windy", "snack",
  ["1 can refrigerated pizza dough", "8 mozzarella string cheese sticks", "2 tbsp butter (melted)", "1 tsp garlic powder", "2 tbsp parmesan", "Marinara for dipping"],
  ["Preheat oven to 425°F", "Cut dough into 8 strips", "Wrap each strip around a cheese stick", "Place on a baking sheet", "Brush with garlic butter", "Sprinkle parmesan on top", "Bake 10-12 minutes until golden"],
  ["easy", "fun", "savory", "30-minute"])

R("Sweet Potato Chips", "sunny", "snack",
  ["2 sweet potatoes", "2 tbsp olive oil", "Salt", "Cinnamon (optional)"],
  ["Preheat oven to 375°F", "Slice sweet potatoes paper-thin (use a mandoline with help!)", "Toss with olive oil and salt", "Lay in a single layer on baking sheets", "Bake 15-20 minutes, watching carefully", "They crisp up more as they cool", "Try with a sprinkle of cinnamon!"],
  ["easy", "healthy", "vegetarian", "vegan"])

R("Banana Split", "sunny", "snack",
  ["1 banana", "3 scoops ice cream (vanilla, chocolate, strawberry)", "Chocolate sauce", "Whipped cream", "Sprinkles", "Cherries"],
  ["Split banana in half lengthwise", "Place in a long dish", "Add one scoop of each flavor between banana halves", "Drizzle with chocolate sauce", "Top with whipped cream and sprinkles", "Put a cherry on each scoop!"],
  ["easy", "sweet", "fun", "no-cook"])

R("Strawberry Milkshake", "sunny", "snack",
  ["3 scoops vanilla ice cream", "1 cup milk", "1 cup frozen strawberries", "Whipped cream"],
  ["Add ice cream, milk, and strawberries to blender", "Blend until smooth and thick", "Pour into a glass", "Top with whipped cream and a strawberry"],
  ["easy", "sweet", "fun", "no-cook"])


# ── Build JSON ──────────────────────────────────────────────────────────────

def build():
    out = []
    seen = set()
    for idx, (name, weather, category, ingredients, steps, tags) in enumerate(RECIPES):
        if name in seen:
            print(f"DUPLICATE SKIPPED: {name}", file=sys.stderr)
            continue
        seen.add(name)
        out.append({
            "name": name,
            "emoji": get_emoji(name),
            "why": WHY[weather][idx % len(WHY[weather])],
            "tip": get_tip(category, name, idx),
            "weather": weather,
            "category": category,
            "serves": 4,
            "version_added": "2.0.0",
            "ingredients": ingredients,
            "steps": steps,
            "tags": tags,
        })
    return out


def main():
    recipes = build()
    out_path = Path(__file__).parent.parent / "backend" / "app" / "seed" / "data" / "recipes.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(recipes, f, indent=2)

    print(f"Generated {len(recipes)} recipes -> {out_path}", file=sys.stderr)

    from collections import Counter
    wc = Counter(r["weather"] for r in recipes)
    cc = Counter(r["category"] for r in recipes)
    print("\nBy weather:", file=sys.stderr)
    for w, c in sorted(wc.items(), key=lambda x: -x[1]):
        print(f"  {w:8s} {c:4d}  ({c*100//len(recipes)}%)", file=sys.stderr)
    print("\nBy category:", file=sys.stderr)
    for cat, c in sorted(cc.items(), key=lambda x: -x[1]):
        print(f"  {cat:12s} {c:4d}", file=sys.stderr)


if __name__ == "__main__":
    main()
