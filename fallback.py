from app.services.platform_links import platform_links

def _items(rows, budget, platforms):
    total = sum(r["estimated_total"] for r in rows)
    return {"items": rows, "estimated_total": round(total, 2), "remaining_budget": round(budget-total,2), "platforms": platforms}

def home_fallback(data):
    unit = data["budget"] / max(sum(i["quantity"] for i in data["items"]), 1)
    rows=[]
    for i in data["items"]:
        est=round(unit*i["quantity"]*0.9,2)
        rows.append({"category":i["category"],"quantity":i["quantity"],"estimated_unit_price":round(est/i["quantity"],2),"estimated_total":est,"reason":f"Balanced {data['style']} option for {data['room_type']}","links":platform_links(i["category"], ["Amazon","IKEA","Flipkart"])})
    return {"title":"Home Budget Plan","summary":"A balanced starter plan generated without live product inventory.",**_items(rows,data["budget"],["Amazon","IKEA","Flipkart"])}

def party_fallback(data):
    b=data["budget"]
    alloc=[("Catering",.50,"Swiggy"),("Decoration",.20,"Amazon"),("Venue / stay",.20,"OYO"),("Entertainment",.10,"Amazon")]
    rows=[]
    for cat,p,plat in alloc:
        amt=round(b*p,2); q=data["event_type"] if cat!="Catering" else f"{data['guests']} guests"
        rows.append({"category":cat,"quantity":1,"estimated_unit_price":amt,"estimated_total":amt,"reason":f"{q}; {data['preferences']}","links":platform_links(cat,[plat])})
    return {"title":"Party Budget Plan","summary":f"Starter allocation for {data['guests']} guests and a {data['event_type']} event.",**_items(rows,b,["Swiggy","Zomato","OYO","Amazon"])}

def jewelry_fallback(data):
    rows=[]
    for cat,p in [("Earrings",.25),("Necklace",.50),("Bracelet",.25)]:
        amt=round(data["budget"]*p,2)
        rows.append({"category":cat,"quantity":1,"estimated_unit_price":amt,"estimated_total":amt,"reason":f"{data['style']} style for {data['occasion']}; coordinate with {data['outfit_description']}","links":platform_links(cat,["Amazon","Flipkart"])})
    return {"title":"Jewelry Budget Plan","summary":"Starter style-matched allocation; upload an outfit for Gemini visual analysis.",**_items(rows,data["budget"],["Amazon","Flipkart"])}
