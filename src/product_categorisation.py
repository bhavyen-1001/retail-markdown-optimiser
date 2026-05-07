import pandas as pd


CATEGORY_KEYWORDS = {
    "Party & Celebrations": [
        "party", "honeycomb", "confetti", "paper chain", "paper fan",
        "paper parasol", "invite", "popcorn holder", "party pizza",
        "garland",
    ],

    "Seasonal & Festive": [
        "christmas", "xmas", "easter", "halloween", "valentine",
        "advent", "nativity", "snowman", "snowflake", "reindeer",
        "santa", "bauble", "wreath", "tinsel",
    ],

    "Candles & Lighting": [
        "candle", "tealight", "tea light", "t-light", "lantern", "lamp",
        "nightlight", "night light", "candleholder", "candle holder",
        "holder", "sconce", "torch", "fairy light",
    ],

    "Kitchen & Dining": [
        "mug", "cup", "plate", "bowl", "glass", "teapot", "jug",
        "jar", "bottle", "cake", "baking", "cutlery", "spoon",
        "fork", "knife", "tin", "colander", "cafetiere", "tray",
        "chopping board", "kitchen", "dining", "napkin", "coaster",
        "placemat", "tea towel", "oven glove", "apron", "tablecloth",
        "table cloth", "food cover", "frying pan", "milk pan", "enamel",
        "biscuit bin", "bread bin", "utensil holder", "washing up",
        "scrubbing brush",
    ],

    "Jewellery & Personal Accessories": [
        "necklace", "bracelet", "earring", "bangle", "brooch", "ring",
        "pendant", "hair slide", "hairslide", "hair grip", "hair clip",
        "hairband", "hair comb", "phone charm", "passport cover", "keyring",
    ],

    "Home Decor & Accessories": [
        "frame", "sign", "clock", "plaque", "cushion", "vase",
        "ornament", "figurine", "mirror", "bunting", "banner",
        "print", "poster", "wall", "door", "doorstop", "hook",
        "peg", "hanger", "drawer", "knob",
        "trinket box", "cabinet", "parasol", "umbrella", "wicker",
        "incense", "photo album", "memory box", "hammock",
        "string curtain", "sewing box", "jewellery stand", "dress stand",
        "paperweight", "doily", "tissue box", "ironing board", "shoe tidy",
        "letter rack", "soap dish", "soap holder",
    ],

    "Bags & Totes": [
        "bag", "tote", "shopper", "purse", "pouch", "backpack",
        "satchel", "holdall",
    ],

    "Stationery & Cards": [
        "card", "notebook", "diary", "pen", "pencil", "calendar",
        "wrap", "ribbon", "tag", "sticker", "label", "envelope",
        "notepad", "rubber", "ruler", "stamp",
    ],

    "Toys, Games & Craft": [
        "puppet", "feltcraft", "dollcraft", "jigsaw", "puzzle",
        "top trump", "stencil", "tattoo", "magic slate", "soft toy",
        "stuffed", "knitted", "crochet", "doll", "game", "windmill",
        "sewing kit", "craft kit",
    ],

    "Garden & Outdoor": [
        "garden", "bird", "plant", "pot", "outdoor", "watering",
        "seed", "trowel", "fence", "hedgehog", "bee", "butterfly",
        "floral", "flower", "botanical",
    ],
}


def assign_category(description: str) -> str:
    """
    Assigns a retail category to a product based on keyword matching.

    Priority order is deliberate and must not be changed without reviewing
    inline collision notes in CATEGORY_KEYWORDS. First match wins.

    Args:
        description: Raw product description string from the Description column.

    Returns:
        Category name as a string. Returns 'Other' if no keywords match.
    """
    if not isinstance(description, str):
        return "Other"

    desc = description.lower()

    priority_order = [
        "Party & Celebrations",
        "Seasonal & Festive",
        "Candles & Lighting",
        "Kitchen & Dining",
        "Jewellery & Personal Accessories",
        "Home Decor & Accessories",
        "Bags & Totes",
        "Stationery & Cards",
        "Toys, Games & Craft",
        "Garden & Outdoor",
    ]

    for category in priority_order:
        keywords = CATEGORY_KEYWORDS[category]
        if any(kw in desc for kw in keywords):
            return category

    return "Other"


def resolve_category_conflicts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resolves SKUs assigned to more than one category across their transactions
    by replacing all assignments with the modal (most frequent) category.

    This can occur when the same StockCode appears under slightly different
    Description strings that match different keyword groups.

    Args:
        df: DataFrame with a 'category' column already populated by assign_category().

    Returns:
        DataFrame with conflicts resolved -- each StockCode maps to exactly one category.
    """
    sku_modal_category = (
        df.groupby("StockCode")["category"]
        .agg(lambda x: x.mode()[0])
        .rename("modal_category")
        .reset_index()
    )

    df = df.merge(sku_modal_category, on="StockCode", how="left")
    df["category"] = df["modal_category"]
    df = df.drop(columns=["modal_category"])

    return df


def categorise_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns a retail product category to every row in the cleaned dataset.

    Applies keyword-based category matching on the Description column, then
    resolves any StockCodes that were assigned conflicting categories across
    their transactions using modal assignment.

    Intended to be called on the output of clean_data() from data_cleaning.py.

    Args:
        df: Cleaned DataFrame as returned by clean_data().

    Returns:
        DataFrame with an additional 'category' column. All other columns
        are unchanged.
    """
    df_categorised = df.copy()

    df_categorised["category"] = df_categorised["Description"].apply(assign_category)
    df_categorised = resolve_category_conflicts(df_categorised)

    return df_categorised