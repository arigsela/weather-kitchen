#!/usr/bin/env python3
"""
fetch_recipes.py — Fetch all recipes from TheMealDB free API and transform
them into the Weather Kitchen JSON schema.

Usage:
    python scripts/fetch_recipes.py

Output:
    backend/app/seed/data/recipes_mealdb.json
"""

from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

# On macOS with the python.org framework build the bundled cert.pem may be
# empty.  Build an SSL context that falls back to the system trust store so
# we can still validate HTTPS without disabling verification entirely.
def _make_ssl_context() -> ssl.SSLContext:
    """Return an SSL context that uses macOS system certificates when available."""
    try:
        # Prefer certifi if installed in the active environment
        import certifi  # type: ignore[import]
        ctx = ssl.create_default_context(cafile=certifi.where())
        return ctx
    except ImportError:
        pass

    # Try the macOS system keychain via the 'ssl' module's built-in helper
    ctx = ssl.create_default_context()
    if ctx.verify_mode == ssl.CERT_REQUIRED:
        # Attempt to load the macOS system roots
        try:
            import subprocess
            result = subprocess.run(
                ["security", "find-certificate", "-a", "-p",
                 "/System/Library/Keychains/SystemRootCertificates.keychain"],
                capture_output=True, text=True, check=True,
            )
            if result.stdout:
                import tempfile, os
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".pem", delete=False
                ) as tmp:
                    tmp.write(result.stdout)
                    tmp_path = tmp.name
                ctx = ssl.create_default_context(cafile=tmp_path)
                os.unlink(tmp_path)
                return ctx
        except Exception:
            pass
    return ctx


_SSL_CTX = _make_ssl_context()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
OUTPUT_PATH = Path(__file__).parent.parent / "backend" / "app" / "seed" / "data" / "recipes_mealdb.json"
REQUEST_DELAY = 0.5  # seconds between API calls — be polite

# ---------------------------------------------------------------------------
# Mapping tables  (all deterministic, no randomness)
# ---------------------------------------------------------------------------

# MealDB category → app category
CATEGORY_MAP: dict[str, str] = {
    "Beef": "dinner",
    "Chicken": "lunch",
    "Dessert": "snack",
    "Goat": "dinner",
    "Lamb": "dinner",
    "Miscellaneous": "lunch",
    "Pasta": "lunch",
    "Pork": "dinner",
    "Seafood": "lunch",
    "Side": "lunch",
    "Starter": "snack",
    "Vegan": "lunch",
    "Vegetarian": "lunch",
    "Breakfast": "breakfast",
}

# Keywords in the meal name / category / tags → weather
# Rules are checked in order; first match wins.
WEATHER_RULES: list[tuple[str, list[str]]] = [
    # snowy — hot, hearty, warming
    ("snowy", [
        "stew", "broth", "chowder", "pudding", "crumble", "pie", "cobbler",
        "bake", "baked", "roast", "roasted", "casserole", "dhal", "dal",
        "curry", "mulled", "hotpot", "hot pot", "braised", "braise",
        "warming", "dumpling", "dumplings", "goulash",
    ]),
    # rainy — soups, comfort, heavy
    ("rainy", [
        "soup", "bisque", "chili", "chilli", "stew", "sausage", "meatball",
        "meatloaf", "pasta bake", "lasagna", "lasagne", "shepherd", "cottage",
        "ratatouille", "tagine", "moussaka", "burger", "beef",
    ]),
    # windy — one-pot, easy indoors
    ("windy", [
        "one-pot", "one pot", "frittata", "quiche", "omelette", "omelet",
        "scrambled", "fried rice", "noodle", "noodles", "pho", "ramen",
        "yakisoba", "udon", "lo mein", "pad thai", "bibimbap",
    ]),
    # cloudy — moderate, stir-fry, wraps, rice bowls
    ("cloudy", [
        "sandwich", "wrap", "burrito", "quesadilla", "taco", "stir", "stir-fry",
        "rice", "bowl", "pilaf", "pilaf", "risotto", "stuffed", "kebab",
        "skewer", "satay", "falafel", "hummus",
    ]),
    # sunny — salads, grilled, seafood, fresh, BBQ, light pasta
    ("sunny", [
        "salad", "grill", "grilled", "bbq", "barbecue", "fish", "prawn",
        "shrimp", "salmon", "tuna", "crab", "lobster", "sushi", "sashimi",
        "ceviche", "gazpacho", "bruschetta", "caprese", "pasta", "spaghetti",
        "penne", "fettuccine", "carbonara", "pesto", "vegetarian", "vegan",
        "fresh", "light", "citrus", "lemon", "lime",
    ]),
]

# Fallback weather per app-category if no keyword matched
CATEGORY_WEATHER_FALLBACK: dict[str, str] = {
    "breakfast": "sunny",
    "lunch": "sunny",
    "dinner": "rainy",
    "snack": "cloudy",
}

# Emoji assignment — checked against lowercased name / category
EMOJI_RULES: list[tuple[str, list[str]]] = [
    ("🍝", ["pasta", "spaghetti", "penne", "fettuccine", "tagliatelle", "linguine", "carbonara", "lasagna", "lasagne"]),
    ("🥗", ["salad", "slaw", "coleslaw", "caprese"]),
    ("🍗", ["chicken"]),
    ("🥩", ["beef", "steak", "lamb", "goat", "veal"]),
    ("🐷", ["pork", "bacon", "ham", "sausage"]),
    ("🐟", ["fish", "salmon", "tuna", "cod", "tilapia", "trout", "halibut", "seafood"]),
    ("🦐", ["prawn", "shrimp", "lobster", "crab", "scallop"]),
    ("🍕", ["pizza"]),
    ("🍔", ["burger", "sandwich", "wrap", "burrito", "taco"]),
    ("🍜", ["soup", "ramen", "pho", "noodle", "udon", "broth", "bisque", "chowder"]),
    ("🍛", ["curry", "korma", "tikka", "masala", "dhal", "dal", "biryani"]),
    ("🥘", ["stew", "casserole", "tagine", "goulash", "hotpot", "braise"]),
    ("🥚", ["egg", "omelette", "omelet", "frittata", "quiche", "scrambled"]),
    ("🥞", ["pancake", "waffle", "crepe", "crêpe"]),
    ("🧇", ["waffle"]),
    ("🍰", ["cake", "tart", "gateau", "cheesecake", "torte"]),
    ("🍩", ["donut", "doughnut", "churro", "beignet"]),
    ("🍮", ["pudding", "custard", "mousse", "panna cotta", "crème brûlée"]),
    ("🍪", ["cookie", "biscuit", "brownie", "flapjack"]),
    ("🫙", ["jam", "preserve", "pickle", "chutney"]),
    ("🥙", ["kebab", "skewer", "satay", "falafel"]),
    ("🍱", ["rice", "risotto", "pilaf", "bibimbap", "fried rice"]),
    ("🫕", ["fondue", "raclette", "dip"]),
    ("🥦", ["vegetarian", "vegan", "vegetable", "veggie"]),
    ("🎂", ["dessert", "sweet", "ice cream", "sorbet"]),
    ("🥐", ["breakfast", "pastry", "croissant", "muffin", "scone"]),
]

DEFAULT_EMOJI = "🍽️"

# Pre-built weather why-sentences: (weather, app_category) → why text
WHY_MAP: dict[tuple[str, str], str] = {
    ("sunny", "breakfast"): "A bright, cheerful start that matches sunny morning vibes",
    ("sunny", "lunch"):     "Light and fresh — perfect for eating outside on a sunny day",
    ("sunny", "dinner"):    "A lighter dinner that won't weigh you down on warm evenings",
    ("sunny", "snack"):     "A fun, fresh bite to enjoy in the sunshine",
    ("rainy", "breakfast"): "A cosy, warming breakfast to brighten up a rainy morning",
    ("rainy", "lunch"):     "Comforting and hearty — exactly what you crave on a grey, rainy day",
    ("rainy", "dinner"):    "Rich and warming, ideal for a rainy evening at home",
    ("rainy", "snack"):     "A warm little treat to cheer you up when it's drizzling outside",
    ("snowy", "breakfast"): "A hot, hearty breakfast to fuel you before heading out in the snow",
    ("snowy", "lunch"):     "A filling, warming lunch to beat the winter chill",
    ("snowy", "dinner"):    "The ultimate snow-day dinner — hot, hearty, and totally cosy",
    ("snowy", "snack"):     "A warm, sweet pick-me-up on a cold, snowy day",
    ("cloudy", "breakfast"): "A satisfying breakfast for a laid-back cloudy morning",
    ("cloudy", "lunch"):     "A balanced, easy lunch that suits any kind of cloudy afternoon",
    ("cloudy", "dinner"):    "A no-fuss dinner that hits the spot on a mild, overcast evening",
    ("cloudy", "snack"):     "A simple, tasty snack for in-between weather",
    ("windy", "breakfast"):  "Easy to make and eat indoors while the wind howls outside",
    ("windy", "lunch"):      "A one-pot wonder — minimal washing up while it's blustery outside",
    ("windy", "dinner"):     "A cosy, all-in-one dinner perfect for staying indoors on a windy night",
    ("windy", "snack"):      "Quick and easy to eat inside while the wind does its thing",
}

# Kid-friendly tips keyed on the first matched keyword — fallback by app_category
KID_TIPS: dict[str, str] = {
    # ingredient / technique keywords
    "pasta":       "Did you know pasta doubles in size when it cooks? It's like magic in a pot! Make sure the water is REALLY bubbly before you add it. 🍝",
    "spaghetti":   "Twirling spaghetti on a fork is an art form — practice makes perfect and delicious! 🍝",
    "lasagna":     "Lasagna is basically a delicious pasta sandwich. Layer it up and let the oven do all the hard work! 🧀",
    "lasagne":     "Lasagne is basically a delicious pasta sandwich. Layer it up and let the oven do all the hard work! 🧀",
    "chicken":     "Always ask a grown-up to check chicken is cooked all the way through — no pink bits! Then dig in! 🍗",
    "beef":        "Browned meat = flavour! Let the pan get nice and hot before adding the beef. It'll smell SO good! 🥩",
    "lamb":        "Lamb loves herbs like rosemary. Rub them in like you're giving the lamb a little massage! 🌿",
    "pork":        "Pork is super flavourful — season it well and let it sizzle! Your nose will tell you when it smells amazing! 🐷",
    "fish":        "Fish cooks really fast — blink and it's done! Watch it carefully and you'll be a fish-cooking superstar! 🐟",
    "salmon":      "Salmon turns from dark pink to light pink as it cooks. It's like watching a sunset in your pan! 🐟",
    "shrimp":      "Shrimp cook SO fast — as soon as they curl into a little C-shape, they're ready! ⏱️🦐",
    "prawn":       "Prawns turn pink and curl up when cooked — they're doing a little dance to tell you they're ready! 🦐",
    "salad":       "Shake the dressing in a jar with the lid on — it mixes way better AND you get to pretend you're a mixologist! 🥗",
    "soup":        "Soup is basically a hug in a bowl. Stir it every few minutes and it'll taste even more amazing! 🍲",
    "stew":        "The longer a stew cooks, the better it tastes. It's the one time being slow is actually a superpower! ⏳",
    "curry":       "Toasting spices for 30 seconds before adding anything else makes the flavour go BOOM! 💥🌶️",
    "rice":        "Measure your rice, then use TWICE as much water. Rice maths is easy and the result is fluffy perfection! 🍚",
    "egg":         "Crack eggs on a flat surface, not the bowl edge — it keeps shell bits out and makes you look super pro! 🥚",
    "omelette":    "Keep the heat low and be patient — a slow omelette is a brilliant omelette! You've got this! 🥚",
    "pancake":     "The first pancake is ALWAYS a test pancake — eat it and keep quiet about it. That's the chef's rule! 🥞",
    "pizza":       "Press the dough gently from the centre out like you're giving it a little tummy rub! 🍕",
    "burger":      "Don't press the burger down while it cooks — all the yummy juices will escape! Let it be free! 🍔",
    "cake":        "Always measure ingredients exactly when baking — baking is edible science! ⚗️🎂",
    "cookie":      "Chill the dough for 30 minutes before baking for thicker, chewier cookies. Worth the wait! 🍪",
    "brownie":     "Underbake brownies by just 2 minutes and they'll be perfectly fudgy in the middle. Trust the process! 🍫",
    "pudding":     "Use a skewer to check if a baked pudding is done — if it comes out clean, it's ready to party! 🎉",
    "bread":       "Bread dough should feel like a soft earlobe when it's ready to bake. Yes really — try it! 🍞",
    "dough":       "Kneading dough is like giving it a workout. Push, fold, turn, repeat! Feel those imaginary muscles! 💪",
    "garlic":      "More garlic = more delicious. That's just science. Never apologise for extra garlic! 🧄",
    "onion":       "Onions make you cry because they release a tiny bit of gas when cut. Wear swimming goggles — totally works! 😂",
    "cheese":      "Freshly grated cheese melts WAY better than pre-grated. Grab the grater and go! 🧀",
    "chocolate":   "Melt chocolate slowly over low heat — if it gets too hot it goes grainy and sad. Be patient! 🍫",
    "bbq":         "BBQ smells amazing from miles away. That's not an accident — it's science AND magic! 🔥",
    "grill":       "Grill marks make food look AND taste epic. Press gently for those beautiful lines! 🔥",
    "grilled":     "Pat meat dry before grilling — damp meat steams instead of searing. Dry = crispy! 🔥",
    "stir":        "Stir-frying is all about speed! Have everything chopped and ready BEFORE you turn the heat on! ⚡",
    "noodle":      "Don't rinse noodles after cooking — the starchy surface helps sauce stick to every strand! 🍜",
    "wrap":        "Warm your wrap for 10 seconds before filling it — it won't crack and it tastes SO much better! 🌯",
    "sandwich":    "Toast the bread for any cold sandwich — it adds crunch and stops the filling making it soggy! 🥪",
    "kebab":       "If using wooden skewers, soak them in water for 30 minutes first so they don't burn. Safety first! 🔥",
    "falafel":     "Squeeze out as much liquid as possible from the chickpeas — drier mix = crispier falafel! 🧆",
}

# Fallback tips by app_category
CATEGORY_TIPS: dict[str, str] = {
    "breakfast": "Breakfast is the most important meal of the day AND the most delicious. Set out everything you need before you start — then cooking is easy-peasy! ☀️",
    "lunch":     "Prep your ingredients first and cooking will feel like a breeze! The secret word is MISE EN PLACE — it's French for 'get your stuff ready'. Fancy! 👩‍🍳",
    "dinner":    "Taste as you go! Every great chef does it. One little spoonful and you'll know exactly what it needs! 😋",
    "snack":     "Snacks are basically tiny meals and they deserve just as much love. Make it look pretty on the plate — you eat with your eyes first! 🎨",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Print progress message to stderr so stdout stays clean for JSON."""
    print(message, file=sys.stderr, flush=True)


def fetch_json(url: str) -> Any:
    """Fetch JSON from a URL using only stdlib.  Raises on HTTP errors."""
    with urllib.request.urlopen(url, timeout=15, context=_SSL_CTX) as response:
        return json.loads(response.read().decode("utf-8"))


def _lower_tokens(text: str) -> str:
    """Return lowercased text."""
    return text.lower()


def pick_weather(name: str, mealdb_category: str, tags: list[str]) -> str:
    """
    Determine weather from meal name, category, and tags.
    Rules are checked in WEATHER_RULES order; first keyword match wins.
    Falls back to CATEGORY_WEATHER_FALLBACK.
    """
    search_text = _lower_tokens(
        f"{name} {mealdb_category} {' '.join(tags)}"
    )
    for weather, keywords in WEATHER_RULES:
        if any(kw in search_text for kw in keywords):
            return weather
    app_cat = CATEGORY_MAP.get(mealdb_category, "lunch")
    return CATEGORY_WEATHER_FALLBACK.get(app_cat, "sunny")


def pick_emoji(name: str, mealdb_category: str) -> str:
    """Assign emoji based on first matching keyword in name/category."""
    search_text = _lower_tokens(f"{name} {mealdb_category}")
    for emoji, keywords in EMOJI_RULES:
        if any(kw in search_text for kw in keywords):
            return emoji
    return DEFAULT_EMOJI


def build_why(weather: str, app_category: str) -> str:
    """Return the why sentence from the WHY_MAP lookup."""
    return WHY_MAP.get(
        (weather, app_category),
        "A great recipe for any kind of weather day!",
    )


def build_tip(name: str, mealdb_category: str, ingredients: list[str]) -> str:
    """
    Return a kid-friendly tip.
    First scans meal name + category + first few ingredients for keyword matches
    from KID_TIPS, then falls back to CATEGORY_TIPS.
    """
    search_parts = [name.lower(), mealdb_category.lower()] + [
        ing.lower() for ing in ingredients[:5]
    ]
    search_text = " ".join(search_parts)
    for keyword, tip in KID_TIPS.items():
        if keyword in search_text:
            return tip
    app_cat = CATEGORY_MAP.get(mealdb_category, "lunch")
    return CATEGORY_TIPS.get(app_cat, CATEGORY_TIPS["lunch"])


def extract_ingredients(meal: dict[str, Any]) -> list[str]:
    """
    Combine strIngredient1-20 and strMeasure1-20 into 'measure ingredient'
    strings, filtering out empty / whitespace-only pairs.
    """
    ingredients: list[str] = []
    for i in range(1, 21):
        ingredient = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if ingredient:
            combined = f"{measure} {ingredient}".strip() if measure else ingredient
            ingredients.append(combined)
    return ingredients


def split_instructions(raw: str) -> list[str]:
    """
    Split the raw instructions blob into individual step strings.

    Strategy (in order):
    1. If numbered steps are present (e.g. '1. ' or '1) ') use those.
    2. Otherwise split on \\r\\n or \\n paragraph breaks.
    3. Return non-empty, stripped strings only.
    """
    if not raw:
        return []

    import re

    # Try numbered steps: lines starting with a digit followed by . or )
    numbered = re.split(r"\r?\n(?=\d+[\.\)])", raw.strip())
    if len(numbered) > 2:
        # Strip leading "1. " prefixes and clean up
        cleaned = []
        for step in numbered:
            step = re.sub(r"^\d+[\.\)]\s*", "", step.strip())
            step = step.replace("\r\n", " ").replace("\n", " ").strip()
            if step:
                cleaned.append(step)
        if cleaned:
            return cleaned

    # Fall back: split on blank lines or double newlines
    paragraphs = re.split(r"\r?\n\r?\n|\r\n", raw.strip())
    steps: list[str] = []
    for para in paragraphs:
        para = para.replace("\r\n", " ").replace("\n", " ").strip()
        # Remove leading numbering if present
        para = re.sub(r"^\d+[\.\)]\s*", "", para)
        if para:
            steps.append(para)
    return steps if steps else [raw.strip()]


def extract_tags(meal: dict[str, Any]) -> list[str]:
    """
    Build tags from strTags (comma-separated) and strArea (cuisine).
    Returns lowercased, deduplicated list.
    """
    tags: list[str] = []
    raw_tags = (meal.get("strTags") or "").strip()
    if raw_tags:
        tags.extend(t.strip().lower() for t in raw_tags.split(",") if t.strip())
    area = (meal.get("strArea") or "").strip().lower()
    if area and area != "unknown":
        tags.append(area)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result


def transform_meal(meal: dict[str, Any]) -> dict[str, Any]:
    """Transform a raw MealDB meal dict into the Weather Kitchen recipe schema."""
    name: str = meal.get("strMeal", "Unknown Recipe")
    mealdb_category: str = meal.get("strCategory", "Miscellaneous")
    app_category: str = CATEGORY_MAP.get(mealdb_category, "lunch")

    ingredients = extract_ingredients(meal)
    raw_tags = extract_tags(meal)
    weather = pick_weather(name, mealdb_category, raw_tags)
    emoji = pick_emoji(name, mealdb_category)
    why = build_why(weather, app_category)
    tip = build_tip(name, mealdb_category, ingredients)
    steps = split_instructions(meal.get("strInstructions", ""))

    return {
        "name": name,
        "emoji": emoji,
        "why": why,
        "tip": tip,
        "weather": weather,
        "category": app_category,
        "serves": 4,  # MealDB doesn't provide servings — default to 4
        "ingredients": ingredients,
        "steps": steps,
        "tags": raw_tags,
    }


# ---------------------------------------------------------------------------
# API fetching logic
# ---------------------------------------------------------------------------


def fetch_all_meal_ids() -> dict[str, list[str]]:
    """
    Return {category_name: [meal_id, ...]} for every MealDB category.
    """
    log("Fetching category list…")
    data = fetch_json(f"{BASE_URL}/categories.php")
    categories = [c["strCategory"] for c in data.get("categories", [])]
    log(f"  Found {len(categories)} categories: {', '.join(categories)}")

    category_ids: dict[str, list[str]] = {}
    for cat in categories:
        log(f"  Fetching meal list for category: {cat}")
        time.sleep(REQUEST_DELAY)
        try:
            result = fetch_json(f"{BASE_URL}/filter.php?c={urllib.request.quote(cat)}")
            meals = result.get("meals") or []
            ids = [m["idMeal"] for m in meals]
            category_ids[cat] = ids
            log(f"    → {len(ids)} meals")
        except Exception as exc:
            log(f"    WARNING: Failed to fetch meals for {cat}: {exc}")
            category_ids[cat] = []

    return category_ids


def fetch_meal_details(
    category_ids: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """
    Fetch full meal details for every unique meal ID.
    Returns a list of raw MealDB meal dicts (one dict per meal),
    with the MealDB category attached as 'strCategory'.
    """
    # Build a mapping id → first category (for the category field)
    id_to_category: dict[str, str] = {}
    for cat, ids in category_ids.items():
        for mid in ids:
            if mid not in id_to_category:
                id_to_category[mid] = cat

    total = len(id_to_category)
    log(f"\nFetching full details for {total} unique meals…")

    meals: list[dict[str, Any]] = []
    for idx, (meal_id, category) in enumerate(id_to_category.items(), 1):
        log(f"  [{idx}/{total}] Meal ID {meal_id} ({category})")
        time.sleep(REQUEST_DELAY)
        try:
            result = fetch_json(f"{BASE_URL}/lookup.php?i={meal_id}")
            meal_list = result.get("meals") or []
            if meal_list:
                meal = meal_list[0]
                # Ensure the category from our map is used (more reliable)
                meal["strCategory"] = category
                meals.append(meal)
        except Exception as exc:
            log(f"    WARNING: Failed to fetch details for meal {meal_id}: {exc}")

    return meals


# ---------------------------------------------------------------------------
# Summary reporting
# ---------------------------------------------------------------------------


def print_summary(recipes: list[dict[str, Any]]) -> None:
    """Print a breakdown of recipes by weather and category to stderr."""
    weather_counts: dict[str, int] = defaultdict(int)
    category_counts: dict[str, int] = defaultdict(int)
    weather_category: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for r in recipes:
        w = r["weather"]
        c = r["category"]
        weather_counts[w] += 1
        category_counts[c] += 1
        weather_category[w][c] += 1

    log("\n" + "=" * 60)
    log(f"TOTAL RECIPES FETCHED: {len(recipes)}")
    log("=" * 60)

    log("\nBy weather:")
    for weather in ("sunny", "rainy", "snowy", "cloudy", "windy"):
        count = weather_counts.get(weather, 0)
        bar = "#" * (count // 2)
        log(f"  {weather:<8} {count:>4}  {bar}")

    log("\nBy category:")
    for cat in ("breakfast", "lunch", "dinner", "snack"):
        count = category_counts.get(cat, 0)
        bar = "#" * (count // 2)
        log(f"  {cat:<10} {count:>4}  {bar}")

    log("\nCross-table (weather × category):")
    header = f"{'':10}" + "".join(f"{c:>12}" for c in ("breakfast", "lunch", "dinner", "snack"))
    log(header)
    for weather in ("sunny", "rainy", "snowy", "cloudy", "windy"):
        row = f"  {weather:<8}"
        for cat in ("breakfast", "lunch", "dinner", "snack"):
            row += f"{weather_category[weather].get(cat, 0):>12}"
        log(row)
    log("=" * 60)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    log("=" * 60)
    log("Weather Kitchen — MealDB Recipe Fetcher")
    log("=" * 60)

    # 1. Discover all meals per category
    category_ids = fetch_all_meal_ids()

    # 2. Fetch full details for every unique meal
    raw_meals = fetch_meal_details(category_ids)

    # 3. Transform into app schema
    log(f"\nTransforming {len(raw_meals)} meals into app schema…")
    recipes = [transform_meal(meal) for meal in raw_meals]
    log(f"  Done. {len(recipes)} recipes transformed.")

    # 4. Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(recipes, fh, ensure_ascii=False, indent=2)
    log(f"\nOutput written to: {OUTPUT_PATH}")

    # 5. Print summary
    print_summary(recipes)


if __name__ == "__main__":
    main()
