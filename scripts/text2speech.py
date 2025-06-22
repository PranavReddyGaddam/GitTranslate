import asyncio
import uuid
from typing import List

import aiohttp
import io
from pydub import AudioSegment
import boto3

# ------------------ CONFIG ------------------
LMNT_API_KEY = "ak_GkxGopYg9FwhJaQkJ9huMC"
LMNT_API_URL = "https://api.lmnt.com/v1/ai/speech/bytes"

AWS_S3_BUCKET = "github-podcasts"  # 🟡 Replace with your bucket

from dotenv import load_dotenv
load_dotenv()



# Alternate voices: host = 'ava', expert = 'clio'
def get_voice(index):
    return "brandon" if index % 2 == 0 else "juniper"

# ------------------ ASYNC LMNT REQUEST ------------------
async def fetch_tts(session, text, voice):
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
        "X-API-Key": LMNT_API_KEY,
    }

    async with session.post(LMNT_API_URL, json=payload, headers=headers) as response:
        print(LMNT_API_URL, payload, headers)
        response.raise_for_status()
        return await response.read()

# ------------------ MAIN ASYNC LOGIC ------------------
async def process_conversation(conversation):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_tts(session, text, get_voice(i))
            for i, text in enumerate(conversation)
        ]
        print("⏳ Sending LMNT requests asynchronously...")
        responses = await asyncio.gather(*tasks)
        print("✅ Received all audio clips.")
        return responses

# ------------------ MERGE + UPLOAD ------------------
def merge_and_upload(audio_chunks):

    merged = AudioSegment.empty()
    for i, chunk in enumerate(audio_chunks):
        audio = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
        merged += audio

    buffer = io.BytesIO()
    merged.export(buffer, format="mp3")
    buffer.seek(0)

    s3 = boto3.client("s3")
    AWS_S3_KEY = str(uuid.uuid4())
    s3.upload_fileobj(buffer, AWS_S3_BUCKET, AWS_S3_KEY, ExtraArgs={"ContentType": "audio/mpeg"})

    print(f"🚀 Uploaded podcast to s3://{AWS_S3_BUCKET}/{AWS_S3_KEY}")
    return f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{AWS_S3_KEY}"

# ------------------ ENTRY POINT ------------------
def text2speech(conversation:List[str]):
    try:
        audio_results = asyncio.run(process_conversation(conversation))
        final_url = merge_and_upload(audio_results)
        print(f"\n🎧 Final podcast audio: {final_url}")
    except Exception as e:
        print(f"❌ Error: {e}")

    return final_url


# from typing import List
#
#
# def part_summary():
#     ...
#
# def text2audio(summary: List[str]):
#     ...
#
#
#
#
# def merge_audio():
#     ...
#
#
# import boto3
# from botocore.exceptions import NoCredentialsError
#
# def upload_to_s3(file_name, bucket_name, object_name=None):
#     """
#     Uploads a file to an S3 bucket and returns the public URL.
#
#     :param file_name: File to upload
#     :param bucket_name: S3 bucket name
#     :param object_name: S3 object name. If not specified, file_name is used
#     :return: Public URL if file was uploaded, else None
#     """
#     # If S3 object_name was not specified, use file_name
#     if object_name is None:
#         object_name = file_name
#
#     # Create an S3 client
#     s3_client = boto3.client('s3')
#
#     try:
#         s3_client.upload_file(file_name, bucket_name, object_name)
#         print(f"File {file_name} uploaded to {bucket_name}/{object_name}")
#         public_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
#         return public_url
#     except FileNotFoundError:
#         print("The file was not found")
#         return None
#     except NoCredentialsError:
#         print("Credentials not available")
#         return None