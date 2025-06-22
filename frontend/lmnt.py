import requests
import json

def text_to_speech(text, voice="ava", output_file="output.mp3"):
    url = "https://api.lmnt.com/v1/ai/speech/bytes"
    
    payload = {
        "voice": voice,
        "text": text,
        "model": "blizzard",
        "language": "auto",
        "format": "mp3",
        "sample_rate": 24000,
        "seed": 123,
        "top_p": 0.8,
        "temperature": 1
    }
    
    headers = {
        "X-API-Key": "ak_GkxGopYg9FwhJaQkJ9huMC",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the audio data from the response
        audio_data = response.content
        
        # Save the audio file
        with open(output_file, 'wb') as f:
            f.write(audio_data)
            
        print(f"Successfully saved audio to {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        if response.text:
            try:
                error_details = json.loads(response.text)
                print(f"API Error details: {error_details}")
            except json.JSONDecodeError:
                print(f"Raw error response: {response.text}")

# Example usage
if __name__ == "__main__":
    text_to_speech("Hello! This is a test of the LMNT text-to-speech API.")