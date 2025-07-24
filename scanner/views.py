from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_json(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name), "r") as f:
        return json.load(f)
def get_ingredients_list(food_item):
    prompts = load_json("prompts.json")
    prompt = prompts["getting_ingredients"].replace("{food_item}", food_item
    )
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt])
    # Clean and parse the response to get a Python list
    import ast, re
    cleaned = re.sub(r'```python|```', '', response.text).strip()
    try:
        ingredients = ast.literal_eval(cleaned)
        if isinstance(ingredients, list):
            return ingredients
    except Exception:
        pass
    return []

@csrf_exempt  # For demo; use proper CSRF in production
def scan_barcode(request):
    ingredients = None
    #define item_price as a list to hold ingredients and total price
    item_price = {"ingredients": [], "total_price": 0, "available": {}, "not_available": []}
    query = request.GET.get('q')
    if query:
        ingredients = get_ingredients_list(query)
        pricelist = load_json("pricelist.json")
        #get total pricing for the ingredients
        if ingredients and isinstance(ingredients, list):
            total_price = sum(pricelist.get(ingredient, 0) for ingredient in ingredients)
            #ingredients.append(f"Total Price: ${total_price:.2f}")
            item_price["ingredients"] = ingredients
            item_price["total_price"] = total_price
        else:
            ingredients = ["No ingredients found or invalid input."]
        #prompts = load_json()
        #prompt = prompts["getting_ingredients"]
        print(ingredients)
        
        #get not available ingredients
        item_price["not_available"] = [ingredient for ingredient in ingredients if ingredient not in pricelist]
        #get available ingredients and it's price
        item_price["available"] = {ingredient: pricelist[ingredient] for ingredient in ingredients if ingredient in pricelist}
        #print the item_price using for loop
        print("Available ingredients and their prices:")
        for item, price in item_price["available"].items():
            print(f"{item}: ${price:.2f}")
        print("Not available ingredients:")
        print(item_price)
        return render(request, "checkout.html", {"ingredients": ingredients, "item_price": item_price})
    return render(request, "index.html")

def scanner_home(request):
    summary = ""
    recommendation = ""
    prompts = load_json("prompts.json")
    if request.method == "POST":
        barcode = request.POST.get("barcode")
        image = request.FILES.get("barcode_image")
        data =""
        model = genai.GenerativeModel('gemini-1.5-flash')
        if image:
            prompt = prompts["image"].replace("{barcode}", barcode if barcode else "")
            image_bytes = image.read()
            response = model.generate_content([
                {"text": prompt},
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            cleaned = re.sub(r'```json|```|Response:\s*', '', response.text).strip()
            try:
                data = json.loads(cleaned)
                summary = data.get("summary", "")
                recommendation = data.get("recommendation", "")
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
                summary = "Could not parse summary."
                recommendation = "Could not parse recommendation."

            print(f"Data: {summary}")
            print(f"Recommendation: {recommendation}")
        elif barcode:
            prompt = prompts["barcode"].replace("{barcode}", barcode)
            response = model.generate_content([prompt])
            cleaned = re.sub(r'```json|```|Response:\s*', '', response.text).strip()
            try:
                data = json.loads(cleaned)
                summary = data.get("summary", "")
                recommendation = data.get("recommendation", "")
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
                summary = "Could not parse summary."
                recommendation = "Could not parse recommendation."


        print(f"Generated summary: {summary}")
        print(f"Generated recommendations: {recommendation}")
    return render(request, "scanner/scanner_home.html", 
                  {"summary": summary,"recommendations": recommendation})