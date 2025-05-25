import json
import boto3

def lambda_handler(event, context):
    """
    Lambda function that demonstrates using Amazon Translate to translate text.
    
    This function:
    1. Takes text input from the event
    2. Translates the text from source language to target language
    3. Returns the translated text
    
    The Lambda function requires these permissions:
    translate:TranslateText
    
    Example test event:
    {
      "text": "Hello, how are you today?",
      "sourceLanguage": "en",
      "targetLanguage": "es"
    }
    """
    # Initialize the Translate client
    translate = boto3.client('translate')
    
    # Get parameters from the event
    text = event.get('text', 'Hello, world!')
    source_language = event.get('sourceLanguage', 'auto')
    target_language = event.get('targetLanguage', 'es')
    
    try:
        # Call Amazon Translate to translate the text
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )
        
        # Return the translated text
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Translation successful',
                'sourceLanguage': response['SourceLanguageCode'],
                'targetLanguage': response['TargetLanguageCode'],
                'originalText': text,
                'translatedText': response['TranslatedText']
            })
        }
        
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error translating text',
                'error': str(e)
            })
        }