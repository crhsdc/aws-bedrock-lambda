import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function that demonstrates using Amazon Polly to convert text to speech.
    
    This function:
    1. Takes text input from the event
    2. Converts it to speech using Amazon Polly
    3. Saves the audio file to S3
    4. Returns the S3 URL of the generated audio

    The Lambda function requires these permissions:
    polly:SynthesizeSpeech
    s3:PutObject (for storing the audio file)
    """
    # Initialize the Polly client
    polly = boto3.client('polly')
    s3 = boto3.client('s3')
    
    # Get parameters from the event
    text = event.get('text', 'Hola, esta es una prueba de Amazon Polly.')
    voice_id = event.get('voiceId', 'Mia')
    output_format = event.get('outputFormat', 'mp3')
    language_code = event.get('languageCode', 'es-MX')
    bucket = event.get('bucket')
    
    if not bucket:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'S3 bucket name is required'
            })
        }
    
    # Generate a unique filename
    filename = f"polly-{context.aws_request_id}.{output_format}"
    s3_key = f"polly-audio/{filename}"
    
    try:
        # Request speech synthesis with Generative Engine
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat=output_format,
            VoiceId=voice_id,
            Engine='generative',
            LanguageCode=language_code
        )
        
        # Access the audio stream from the response
        if "AudioStream" in response:
            audio_stream = response["AudioStream"].read()
            
            # Upload the audio file to S3
            s3.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=audio_stream,
                ContentType=f'audio/{output_format}'
            )
            
            # Generate a pre-signed URL (valid for 1 hour)
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_key},
                ExpiresIn=3600
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Text-to-speech conversion successful',
                    's3Uri': f"s3://{bucket}/{s3_key}",
                    'presignedUrl': url
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Speech synthesis failed - no AudioStream in response'
                })
            }
            
    except ClientError as e:
        print(f"Error in Polly synthesis: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error in speech synthesis',
                'error': str(e)
            })
        }