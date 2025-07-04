import base64
import json
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
class AnalyzeImageView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            image_data = data.get('image')  # base64 encoded image
            prompt = data.get('prompt', 'Analyze this image for rizz content and provide a detailed analysis.')
            
            if not image_data:
                return JsonResponse({'error': 'No image provided'}, status=400)
            
            # Call OpenAI vision API
            analysis_result = self.analyze_image_with_openai(image_data, prompt)
            
            return JsonResponse({
                'success': True,
                'analysis': analysis_result,
                'prompt_used': prompt
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def analyze_image_with_openai(self, image_data, prompt):
        """
        Helper function to call OpenAI Vision API for rizz analysis
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
            
            # Create a rizz-specific prompt
            rizz_prompt = f"""
            {prompt}
            
            Please analyze this image for "rizz" content - meaning charisma, charm, or romantic appeal. Consider:
            1. Body language and confidence
            2. Style and presentation
            3. Facial expressions and eye contact
            4. Overall attractiveness and appeal
            5. Any text or context that shows social skills
            
            Provide a detailed analysis with a rizz score out of 10 and specific suggestions for improvement.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": rizz_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_rizz_text(request):
    """
    Alternative endpoint for text-based rizz analysis
    """
    try:
        text_content = request.data.get('text', '')
        
        if not text_content:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call OpenAI for text analysis
        client = openai.OpenAI(
            api_key=getattr(settings, 'OPENAI_API_KEY', None)
        )
        
        rizz_prompt = f"""
        Analyze the following text for "rizz" content - meaning charisma, charm, or romantic appeal:
        
        "{text_content}"
        
        Please provide:
        1. A rizz score out of 10
        2. What works well in the text
        3. Specific suggestions for improvement
        4. Alternative phrasings that would be more charming
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": rizz_prompt}
            ],
            max_tokens=800
        )
        
        return Response({
            'success': True,
            'analysis': response.choices[0].message.content,
            'original_text': text_content
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
