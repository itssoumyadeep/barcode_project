from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_prompts():
    with open(os.path.join(os.path.dirname(__file__), "prompts.json"), "r") as f:
        return json.load(f)

@csrf_exempt  # For demo; use proper CSRF in production
def scan_barcode(request):
    return render(request, "index.html")
def scanner_home(request):
    summary = ""
    recommendation = ""
    prompts = load_prompts()
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