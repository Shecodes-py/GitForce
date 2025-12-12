from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from rest_framework import status
from rest_framework import generics 
from .serializers import CustomUserSerializer 


import os
import requests
import google.generativeai as genai


from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from twilio.twiml.messaging_response import MessagingResponse

from dotenv import load_dotenv

load_dotenv()


# Create your views here.
class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer  

genai.configure(api_key=os.getenv("google_api_key"))

class WhatsAppBotView(APIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        incoming_msg = request.data.get('Body', '').strip()
        num_media = request.data.get('NumMedia', '0')
        sender_number = request.data.get('From')
        
        resp = MessagingResponse()
        msg = resp.message()

        print(f"📩 Message from {sender_number}")

        if int(num_media) > 0:
            image_url = request.data.get('MediaUrl0')
            print(f"🖼 Image URL: {image_url}")

            try:
                # 1. Download the image from Twilio
                # Twilio URLs sometimes require auth, but usually public in sandbox.
                # If it fails, we might need basic auth (Account SID + Token)
                img_data = requests.get(image_url).content

                # 2. Setup Gemini Model (Use Flash for speed!)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # 3. The Prompt (Be specific!)
                prompt = (
                    "Analyze this crop image. "
                    "1. Identify the crop. "
                    "2. Grade its quality (Grade A, B, or C). "
                    "3. Estimate a fair market price in Nigerian Naira (NGN) per kg. "
                    "4. Keep it very short and concise for a WhatsApp message."
                    "5. If it isn't a crop, ask for a crop photo."
                )

                # 4. Generate Content
                # We pass the prompt AND the image data
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": img_data}
                ])

                ai_analysis = response.text
                print(f"🧠 Gemini Says: {ai_analysis}")

                # 5. Send the Analysis back to WhatsApp
                msg.body(
                    f"🤖 *Gemini Analysis:*\n{ai_analysis}\n\n"
                    f"👇 *Sell this crop:* \n"
                    f"https://your-webapp.com/mint"
                )

            except Exception as e:
                print(f"❌ Error: {e}")
                msg.body("Sorry, I couldn't analyze that image. Please try again.")

        else:
            msg.body("📸 Send me a photo of your harvest to analyze!")

        return HttpResponse(str(resp), content_type='text/xml')
