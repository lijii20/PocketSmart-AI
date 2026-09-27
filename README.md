# PocketSmart AI

A FastAPI + Jinja2 + SQLite Generative-AI budget recommendation assistant based on the supplied project document.

## Features
- User registration/login with JWT authentication
- Home Interior Planner
- Party Budget Planner
- Jewelry Planner with optional outfit image
- Gemini multimodal recommendation generation
- SQLite recommendation history
- Deterministic fallback recommendations when Gemini is unavailable
- Responsive HTML/CSS/JS UI
- Platform search links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO

## Important implementation note
The supplied document names third-party platforms but does not provide API credentials, endpoints, schemas, or affiliate access. This implementation therefore generates search links to those platforms rather than scraping them or claiming live inventory/prices. Replace `app/services/platform_links.py` with approved partner APIs later if required.

## Quick start
1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Create a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your Gemini API key.
6. Run: `uvicorn app.main:app --reload`
7. Open http://127.0.0.1:8000

If `GEMINI_API_KEY` is empty or invalid, the app still works using its fallback recommendation engine.
