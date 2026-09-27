from urllib.parse import quote_plus

def platform_links(query: str, platforms: list[str]) -> list[dict]:
    q = quote_plus(query)
    base = {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/search?query={q}",
        "OYO": f"https://www.oyorooms.com/search?location={q}",
    }
    return [{"platform": p, "url": base[p]} for p in platforms if p in base]
def mock_platform_products(query: str, platform: str) -> list[dict]:
    """Simulated product data for development/testing."""

    return [
        {
            "platform": platform,
            "product_name": f"Sample {query.title()}",
            "estimated_price": 999,
            "currency": "INR",
            "availability": "Simulated",
            "source": "Mock API"
        },
        {
            "platform": platform,
            "product_name": f"Premium {query.title()}",
            "estimated_price": 1499,
            "currency": "INR",
            "availability": "Simulated",
            "source": "Mock API"
        }
    ]