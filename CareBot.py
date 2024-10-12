

# Required Libraries
# To install the libraries, run the following commands:
# pip install openai
# pip install requests
# pip install boto3

import os
import json
import openai
import requests
import boto3

# Initialize Constants
TRANSCRIPTION_ENDPOINT = 'https://api.openai.com/v1/audio/transcriptions'
CHAT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "open-ai-key")
AUDIO_FILE_PATH = "drive/MyDrive/CS329T/data/Schizo.m4a"
AWS_KEY = "aws-key"
AWS_SECRET_KEY = "secret-key"


# Function: Transcribe Audio File
def transcribe_audio_file(audio_file_path):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
    }
    data = {
        'model': 'whisper-1',
        'prompt': 'You are transcribing the text of a dementia patient. '
    }
    with open(audio_file_path, 'rb') as audio_file:
        files = {'file': audio_file}
        response = requests.post(TRANSCRIPTION_ENDPOINT, headers=headers, data=data, files=files)

    if response.status_code == 200:
        transcript = response.json()
        return transcript['text']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Function: Chat with GPT
def chat_with_gpt(prompt):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an assistant that extracts important information."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
    }

    response = requests.post(CHAT_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Function: Extract JSON from GPT Response
def extract_json(content):
    start_idx = content.find("{")
    end_idx = content.find("}") + 1
    return json.loads(content[start_idx:end_idx])

# Function: Send SMS via AWS SNS
def send_sms_via_sns(message):
    sns = boto3.client(
        "sns",
        aws_access_key_id="your-aws-access-key-id-here",
        aws_secret_access_key="your-aws-secret-access-key-here",
        region_name="us-east-2"
    )
    text_response = sns.publish(
        PhoneNumber="+18043056660",
        Message=message,
        MessageAttributes={
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Transactional'
            }
        }
    )
    print(f"Message sent! Message ID: {text_response['MessageId']}")

# Main Workflow
def main():
    # Step 1: Transcribe the audio file
    audio_response = transcribe_audio_file(AUDIO_FILE_PATH)
    if not audio_response:
        return

    # Step 2: Create a prompt and send it to GPT
    prompt = (f"Based on this text:'{audio_response}' - Can you provide me with a json blob response "
              "where 'Content' maps to a brief factual description of the stimulus causing the emotion? "
              "This trigger can likely be categorized as one of the following six forms of psychological "
              "stress: physical pain, full bladder, temperature, sound, light, and internal personal frustration. "
              "'Emotion' maps to a description of the emotions the person is experiencing as a result of the stimulus.")

    print(f"Prompt to GPT: {prompt}")
    content = chat_with_gpt(prompt)
    if not content:
        return

    # Step 3: Extract JSON response
    json_data = extract_json(content)
    problem_description = json_data['Content']
    emotion_description = json_data['Emotion']
    print(f"Problem: {problem_description}, Emotion: {emotion_description}")

    # Step 4: Create a message for the caregiver
    caregiver_prompt = (f"Here is a description of a dementia patient's problem: {problem_description}. "
                        f"The emotion they're experiencing is {emotion_description}. Can you craft a text message "
                        "to send to the caregiver with an update and put it in a json blob with the key 'Text Response'?")
    message = chat_with_gpt(caregiver_prompt)
    if message:
        message_dict = extract_json(message)
        print(f"Caregiver Message: {message_dict['Text Response']}")
        send_sms_via_sns(message_dict['Text Response'])

    # Step 5: Create a message for the patient
    patient_prompt = (f"Here is a description of a dementia patient's problem: {problem_description}. "
                      f"The emotion they're experiencing is {emotion_description}. Can you craft a message "
                      "that will be transcribed to audio to say to the patient? Our main goal is to validate their "
                      "feelings and then deescalate any negative emotions/reinforce any positive emotions. Make sure "
                      "to not make it infantilizing - try to be specific.")
    message = chat_with_gpt(patient_prompt)
    if message:
        voice_dict = extract_json(message)
        print(f"Voice Message: {voice_dict['Voice Response']}")

# Run the main function
if __name__ == "__main__":
    main()
