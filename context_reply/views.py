import base64
import json
import os
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import openai
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@method_decorator(csrf_exempt, name='dispatch')
class ContextReplyImageView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            image_data = data.get('image')  # base64 encoded image
            prompt = data.get('prompt', 'Analyze this image and provide a contextual reply.')
            mood = data.get('mood', 'sweet').lower()  # Default to sweet mood
            spice_level = data.get('spice_level', 5)  # Default spice level 5/10
            
            if not image_data:
                return JsonResponse({'error': 'No image provided'}, status=400)
            
            # Validate mood
            valid_moods = ['flirty', 'funny', 'sweet', 'mysterious', 'sarcastic', 'romantic']
            if mood not in valid_moods:
                return JsonResponse({'error': f'Invalid mood. Must be one of: {valid_moods}'}, status=400)
            
            # Validate spice level
            try:
                spice_level = int(spice_level)
                if spice_level < 1 or spice_level > 10:
                    return JsonResponse({'error': 'Spice level must be between 1 and 10'}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Spice level must be a valid integer'}, status=400)
            
            # Call OpenAI vision API
            analysis_result = self.analyze_image_with_openai(image_data, prompt, mood, spice_level)
            
            return JsonResponse({
                'success': True,
                'reply': analysis_result,
                'mood': mood,
                'spice_level': spice_level,
                'prompt_used': prompt
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def analyze_image_with_openai(self, image_data, prompt, mood, spice_level):
        """
        Helper function to call OpenAI Vision API for contextual image analysis
        """
        try:
            # Set up OpenAI client
            client = openai.OpenAI(
                api_key=getattr(settings, 'OPENAI_API_KEY', None)
            )
            
            # Prepare the image for OpenAI API
            # Remove data:image/jpeg;base64, prefix if present
            if image_data.startswith('data:'):
                image_data = image_data.split(',')[1]
            
            # Read the mood-specific prompt from file
            prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompts', f'{mood}_prompt.txt')
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                context_prompt_template = file.read()
            
            # Replace the placeholders with user's custom prompt and spice level
            context_prompt = context_prompt_template.replace('{user_prompt}', prompt)
            context_prompt = context_prompt.replace('{spice_level}', str(spice_level))
            context_prompt = context_prompt.replace('{image_data}', image_data)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": context_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500
            )
            
            # Get the response content as simple text
            response_content = response.choices[0].message.content
            
            # Return the text response directly
            return response_content.strip()
            
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return f"Error analyzing image: {str(e)}"


