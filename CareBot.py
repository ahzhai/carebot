

# Required Libraries
# To install the libraries, run the following commands:
# pip install openai
# pip install requests
# pip install boto3

import os
import json
import openai
from openai import OpenAI
import requests
import boto3
import argparse

# Initialize Constants
TRANSCRIPTION_ENDPOINT = 'https://api.openai.com/v1/audio/transcriptions'
CHAT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AUDIO_FILE_PATH = "toohot.m4a"
AWS_KEY = ""
AWS_SECRET_KEY = ""


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

few_shot_examples = [
    # Set the behavior of the assistant
    {"role": "system", "content": "You are a helpful assistant who communicates with people who have dementia. Give short, one sentence explanations. Repeat instructions or sentences exactly the same way. Avoid insistence. Try again later. Agree with them or distract them to a different subject or activity. Accept the blame when something’s wrong (even if it’s fantasy). Respond to the feelings rather than the words. Be patient and cheerful and reassuring. Go with the flow. Here are some specific Do's and Don'ts to follow."},

    # First Example
    {"role": "user", "content": "The person with dementia says: 'What doctor’s appointment? There’s nothing wrong with me.' How should I respond?"},
    {"role": "assistant", "content": "Do: (short explanation) 'It’s just a regular checkup.'\n(accept blame) 'I’m sorry if I forgot to tell you.'\nDon’t: (reason) 'You’ve been seeing the doctor every three months for the last two years. It’s written on the calendar and I told you about it yesterday and this morning.'"},

    # Second Example
    {"role": "user", "content": "The person with dementia says: 'I didn’t write this check for $500. Someone at the bank is forging my signature.' How should I respond?"},
    {"role": "assistant", "content": "Do: (respond to feelings) 'That’s a scary thought.'\n(reassure) 'I’ll make sure they don’t do that.'\n(distract) 'Would you help me fold the towels?'\nDon’t: (argue) 'What? Don’t be silly! The bank wouldn’t be forging your signature.'"},

    # Third Example
    {"role": "user", "content": "The person with dementia says: 'Nobody’s going to make decisions for me. You can go now…and don’t come back!' How should I respond?"},
    {"role": "assistant", "content": "Do: (accept blame or respond to feelings) 'I’m sorry this is a tough time.'\n(reassure) 'I love you and we’re going to get through this together.'\n(distract) 'You know what? Don has a new job. He’s really excited about it.'\nDon’t: (confront) 'I’m not going anywhere and you can’t remember enough to make your own decisions.'"},

    # Fourth Example
    {"role": "user", "content": "The person with dementia says: 'Joe hasn’t called for a long time. I hope he’s okay.' How should I respond?"},
    {"role": "assistant", "content": "Do: (reassure) 'You really like talking with him don’t you?'\n(distract) 'Let’s call him when we get back from our walk.'\nDon’t: (remind) 'Joe called yesterday and you talked with him for 15 minutes.'"},

    # Fifth Example
    {"role": "user", "content": "The person with dementia says: 'Who are you? Where’s my husband?' How should I respond?"},
    {"role": "assistant", "content": "Do: (go with the flow, reassure) 'He’ll be here for dinner.'\n(distract) 'How about some milk and cookies?… Would you like chocolate chip or oatmeal?'\nDon’t: (take it personally) 'What do you mean – who’s your husband? I am!'"},

    # Sixth Example
    {"role": "user", "content": "The person with dementia says: 'I don’t want to eat this! I hate chicken.' How should I respond?"},
    {"role": "assistant", "content": "Do: (accept blame) 'I’m so sorry, I forgot. I was in such a rush that it slipped my mind.'\n(respond positively) 'Let me see what else we have available.' Leave the room and try again.\nDon’t: (respond negatively) 'You just told me you wanted chicken. I’m not making you anything else, so you better eat it!'"}
]

# Function: Chat with GPT
def chat_with_gpt(prompt, patient=False):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    if patient:
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an assistant that extracts important information."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,}
    else:
        data = {
            "model": "gpt-4o-mini",
            "messages": few_shot_examples + [
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
    print(content[start_idx:end_idx])
    return json.loads(content[start_idx:end_idx])

# Function: Send SMS via AWS SNS
def send_sms_via_sns(message):
    sns = boto3.client(
        "sns",
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
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

def generate_voice_message(message, output_file):
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=message
    )
    response.stream_to_file(output_file)

def determine_severity(problem_description):
    prompt = (f"You are a liason between a dementia patient and a caregiver. "
              f"The patient is having this problem currently:{problem_description} - Dementia patients often experience frustrations "
              "that require validation and neutralization of self-deprecating emtoions. However, it is sometimes the case that their "
              "frustrations stem from stimuli that the caregiver genuinely needs to address (medical crisis, bathroom troubles, temperature, etc...). But, "
              "it is equally true that sometimes they have frustrations that don't really rise to the level of paging a busy caretaker. Given the problem description, "
              "determine whether the caretaker should be paged and place your response in a json blob where 'Page' maps to  a string version of True or False. "
              "Caregivers should always be paged if the patient is having any sort of medical issues or poses a threat to themselves or others. You should only not notify if you are sure this is a passing emotion / momentary discomfort. You can provide rationale outside the blob.")
    content = chat_with_gpt(prompt)
    print(f"Page Response: {content}")
    if not content:
        return
    json_data = extract_json(content)
    page = json_data['Page'].lower()
    return 't' in page

# Main Workflow
def main(input_file, output_file):
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    audio_response = transcribe_audio_file(input_file)
    if not audio_response:
        return

    # Step 2: Create a prompt and send it to GPT
    prompt = (f"Based on this text:'{audio_response}' - Can you provide me with a json blob response "
              "where 'Content' maps to a brief factual description of the stimulus causing the emotion? "
              "This trigger can likely be categorized as one of the following six forms of psychological "
              "stress: physical pain, full bladder, temperature, sound, light, and internal personal frustration. "
              "'Emotion' maps to a description of the emotions the person is experiencing as a result of the stimulus.")

    # print(f"Prompt to GPT: {prompt}")
    content = chat_with_gpt(prompt)
    if not content:
        return

    # Step 3: Extract JSON response
    json_data = extract_json(content)
    problem_description = json_data['Content']
    emotion_description = json_data['Emotion']
    # print(f"Problem: {problem_description}, Emotion: {emotion_description}")

    #Step 4: Determine Problem Severity
    page_bool = determine_severity(problem_description)
    
    # Step 5: Create a message for the caregiver
    if page_bool:
        caregiver_prompt = (f"Here is a description of a dementia patient's problem: {problem_description}. "
                            f"The emotion they're experiencing is {emotion_description}. Can you craft a text message "
                            "to send to the caregiver with an update and put it in a json blob with the key 'Text Response'?")
        message = chat_with_gpt(caregiver_prompt)
        if message:
            message_dict = extract_json(message)
            print(f"Caregiver Message: {message_dict['Text Response']}")
            send_sms_via_sns(message_dict['Text Response'])

    # Step 6: Create a message for the patient
    patient_prompt = (f"Here is a description of a dementia patient's problem: {problem_description}. "
                      f"The emotion they're experiencing is {emotion_description}. Can you craft a message "
                      "that will be transcribed to audio to say to the patient? Our main goal is to validate their "
                      "feelings and then deescalate any negative emotions/reinforce any positive emotions. Make sure "
                      "to not make it infantilizing - try to be specific. Put your response in a json blob with key 'Voice Response'.")
    message = chat_with_gpt(patient_prompt, patient=True)
    if message:
        voice_dict = extract_json(message)
        voice_message = voice_dict['Voice Response']
        print(f"Voice Message: {voice_message}")
        generate_voice_message(voice_message, output_file)
        

# Run the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio and generate response messages using OpenAI API.")
    parser.add_argument("input_file", help="Path to the input audio file for transcription.")
    parser.add_argument("output_file", help="Path to the output audio file where the voice message will be saved.")
    args = parser.parse_args()
    main(args.input_file, args.output_file)    
