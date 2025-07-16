from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# For future: barcode image processing
# from pyzbar.pyzbar import decode
# from PIL import Image

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_prompts():
    with open(os.path.join(os.path.dirname(__file__), "prompts.json"), "r") as f:
        return json.load(f)

@csrf_exempt  # For demo; use proper CSRF in production
def scan_barcode(request):
    summary = ""
    recommendations = ""
    prompts = load_prompts()
    if request.method == "POST":
        barcode = request.POST.get("barcode")
        image = request.FILES.get("barcode_image")
        model = genai.GenerativeModel('gemini-1.5-flash')
        if image:
            prompt = prompts["image"].replace("{barcode}", barcode if barcode else "")
            image_bytes = image.read()
            response = model.generate_content([
                {"text": prompt},
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            summary = response.text.split("\n")[0]  # Assuming the first line is the summary
            recommendations=response.text.split("\n")[1] if len(response.text.split("\n")) > 1 else ""
        elif barcode:
            prompt = prompts["barcode"].replace("{barcode}", barcode)
            response = model.generate_content([prompt])
            summary = response.text.split("\n")[0]  # Assuming the first line is the summary
            recommendations = response.text.split("\n")[1] if len(response.text.split("\n")) > 1 else ""
        print(f"Generated summary: {summary}")
    return render(request, "scanner/index.html", 
                  {"summary": summary,"recommendations": recommendations})