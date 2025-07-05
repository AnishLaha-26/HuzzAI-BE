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
            
            # Read the prompt from file
            prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompts', 'rizz_analysis_prompt.txt')
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                rizz_prompt_template = file.read()
            
            # Replace the placeholder with user's custom prompt (avoiding format() conflicts with JSON)
            rizz_prompt = rizz_prompt_template.replace('{user_prompt}', prompt)
            
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
                max_tokens=3000  # Increased for detailed JSON response
            )
            
            # Get the response content
            response_content = response.choices[0].message.content
            
            # Debug logging to see what's failing
            print("=== DEBUG RAW RESPONSE ===")
            print(repr(response_content))
            print("=== END RAW RESPONSE ===")
            
            # Strip markdown code blocks if present
            if response_content.startswith('```json'):
                response_content = response_content[7:]  # Remove ```json
            if response_content.startswith('```'):
                response_content = response_content[3:]  # Remove ```
            if response_content.endswith('```'):
                response_content = response_content[:-3]  # Remove closing ```
            
            # Clean up whitespace
            response_content = response_content.strip()
            
            # Try to parse as JSON, fallback to plain text if it fails
            try:
                import json
                print("=== ATTEMPTING INITIAL JSON PARSE ===")
                print(f"Content to parse: {repr(response_content[:500])}...")
                parsed_json = json.loads(response_content)
                print("=== INITIAL PARSE SUCCESSFUL ===")
                return parsed_json.get('data', parsed_json)
            except json.JSONDecodeError as e:
                print(f"=== INITIAL PARSE FAILED: {str(e)} ===")
                # Instead of repairing, let's extract the data and rebuild perfect JSON
                try:
                    import re
                    print("=== REBUILDING JSON FROM CONTENT ===")
                    
                    # Extract key-value pairs using regex
                    def extract_value(pattern, content, default=None):
                        match = re.search(pattern, content, re.DOTALL)
                        return match.group(1) if match else default
                    
                    def extract_number(pattern, content, default=0):
                        match = re.search(pattern, content)
                        return int(match.group(1)) if match else default
                    
                    def extract_array(pattern, content, default=None):
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            items = re.findall(r'"([^"]+)"', match.group(1))
                            return items
                        return default or []
                    
                    # Build perfect JSON structure
                    perfect_json = {
                        "rizzScore": extract_number(r'"rizzScore":\s*(\d+)', response_content, 0),
                        "engagement": {
                            "huzzPercentage": extract_number(r'"huzzPercentage":\s*(\d+)', response_content, 0),
                            "youPercentage": extract_number(r'"youPercentage":\s*(\d+)', response_content, 0),
                            "summary": extract_value(r'"summary":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "interestLevel": {
                            "huzzPercentage": extract_number(r'"interestLevel"[^}]+"huzzPercentage":\s*(\d+)', response_content, 0),
                            "youPercentage": extract_number(r'"interestLevel"[^}]+"youPercentage":\s*(\d+)', response_content, 0),
                            "summary": extract_value(r'"interestLevel"[^}]+"summary":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "tone": {
                            "you": extract_value(r'"tone"[^}]+"you":\s*"([^"]+)"', response_content, "unknown"),
                            "huzz": extract_value(r'"tone"[^}]+"huzz":\s*"([^"]+)"', response_content, "unknown"),
                            "summary": extract_value(r'"tone"[^}]+"summary":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "compatibilityScore": extract_number(r'"compatibilityScore":\s*(\d+)', response_content, 0),
                        "compatibilitySummary": extract_value(r'"compatibilitySummary":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                        "strengths": extract_array(r'"strengths":\s*\[([^\]]+)\]', response_content, ["Analysis unavailable"]),
                        "improvements": extract_array(r'"improvements":\s*\[([^\]]+)\]', response_content, ["Analysis unavailable"]),
                        "conversationTips": [{
                            "tip": "Analysis unavailable",
                            "example": "Please try again"
                        }],
                        "suggestedResponses": extract_array(r'"suggestedResponses":\s*\[([^\]]+)\]', response_content, ["Analysis unavailable"]),
                        "redFlags": extract_array(r'"redFlags":\s*\[([^\]]+)\]', response_content, ["No red flags detected"]),
                        "nextSteps": extract_array(r'"nextSteps":\s*\[([^\]]+)\]', response_content, ["Continue conversation"]),
                        "openingLineAnalysis": {
                            "strength": extract_value(r'"openingLineAnalysis"[^}]+"strength":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "weakness": extract_value(r'"openingLineAnalysis"[^}]+"weakness":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "suggestion": extract_value(r'"openingLineAnalysis"[^}]+"suggestion":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "emojiUsage": {
                            "yourUsage": extract_value(r'"emojiUsage"[^}]+"yourUsage":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "theirUsage": extract_value(r'"emojiUsage"[^}]+"theirUsage":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "suggestion": extract_value(r'"emojiUsage"[^}]+"suggestion":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "responseTime": {
                            "yourAverage": extract_value(r'"responseTime"[^}]+"yourAverage":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "theirAverage": extract_value(r'"responseTime"[^}]+"theirAverage":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "suggestion": extract_value(r'"responseTime"[^}]+"suggestion":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "conversationFlow": {
                            "assessment": extract_value(r'"conversationFlow"[^}]+"assessment":\s*"([^"]+)"', response_content, "Analysis unavailable"),
                            "suggestion": extract_value(r'"conversationFlow"[^}]+"suggestion":\s*"([^"]+)"', response_content, "Analysis unavailable")
                        },
                        "iceBreakerIdeas": extract_array(r'"iceBreakerIdeas":\s*\[([^\]]+)\]', response_content, ["What's new with you?"]),
                        "escalationTips": extract_array(r'"escalationTips":\s*\[([^\]]+)\]', response_content, ["Keep the conversation flowing"]),
                        "analysisTimestamp": "2023-10-09T12:00:00Z",
                        "version": "1.0"
                    }
                    
                    print("=== PERFECT JSON REBUILT SUCCESSFULLY ===")
                    return perfect_json
                    
                except Exception as rebuild_error:
                    # If JSON repair also fails, return a structured fallback response
                    # Return a structured fallback that won't break the frontend
                    return {
                        "rizzScore": 0,
                        "engagement": {
                            "huzzPercentage": 0,
                            "youPercentage": 0,
                            "summary": "Unable to analyze due to parsing error"
                        },
                        "interestLevel": {
                            "huzzPercentage": 0,
                            "youPercentage": 0,
                            "summary": "Unable to analyze due to parsing error"
                        },
                        "tone": {
                            "you": "unknown",
                            "huzz": "unknown",
                            "summary": "Unable to analyze due to parsing error"
                        },
                        "compatibilityScore": 0,
                        "compatibilitySummary": "Unable to analyze due to parsing error",
                        "strengths": ["Unable to analyze - please try again"],
                        "improvements": ["Unable to analyze - please try again"],
                        "conversationTips": [{
                            "tip": "Unable to analyze - please try again",
                            "example": "Technical error occurred"
                        }],
                        "suggestedResponses": ["Unable to analyze - please try again"],
                        "redFlags": ["Technical parsing error"],
                        "nextSteps": ["Try uploading the image again"],
                        "openingLineAnalysis": {
                            "strength": "Unable to analyze",
                            "weakness": "Unable to analyze",
                            "suggestion": "Please try again"
                        },
                        "emojiUsage": {
                            "yourUsage": "Unable to analyze",
                            "theirUsage": "Unable to analyze",
                            "suggestion": "Please try again"
                        },
                        "responseTime": {
                            "yourAverage": "Unable to analyze",
                            "theirAverage": "Unable to analyze",
                            "suggestion": "Please try again"
                        },
                        "conversationFlow": {
                            "assessment": "Unable to analyze",
                            "suggestion": "Please try again"
                        },
                        "iceBreakerIdeas": ["Unable to analyze - please try again"],
                        "escalationTips": ["Unable to analyze - please try again"],
                        "analysisTimestamp": "2023-10-09T12:00:00Z",
                        "version": "1.0",
                        "_parseError": {
                            "message": "JSON parsing failed",
                            "originalError": str(e),
                            "repairError": str(repair_error)
                        }
                    }
            
        except Exception as e:
            return {"error": f"Error analyzing image: {str(e)}"}


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


