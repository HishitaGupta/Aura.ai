# -*- coding: utf-8 -*-
import requests
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
from transformers import pipeline
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, TextClip, ColorClip, AudioFileClip
from moviepy.editor import *
from moviepy.video.fx.all import crop, loop
from moviepy.video.tools.drawing import circle
import json
import pysrt
import numpy as np
from gtts import gTTS
from googletrans import Translator
from pydub import AudioSegment
from moviepy.video.fx.all import colorx
from moviepy.video.tools.subtitles import SubtitlesClip
import base64
from docx import Document
from pptx import Presentation

# Load environment variables
load_dotenv()

# Constants
pictures_folder = "pictures"
videos_folder = "videos"
output_video_path = "final_slideshow.mp4"
audio_output_path = "final_audio.mp3"
audio_output_speedup_path = "final_audio_speeded_up.mp3"
srt_file_path = "subtitles.srt"
output_folder = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\pdf_images"

# Create folders if they don't exist
os.makedirs(pictures_folder, exist_ok=True)
os.makedirs(videos_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

#initialize sarvam api key
sarvam_api_key = os.getenv("SARVAM_API_KEY")

# Initialize Gemini API
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Set path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Extract images from PDF
def extract_images_from_pdf(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_path = os.path.join(output_folder, f"page_{page_num}_img_{img_index}.png")
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            yield image_path  # Yield each saved image path for OCR processing

# OCR on images in folder
def ocr_images_in_folder(folder_path):
    text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            try:
                image = Image.open(image_path)
                text += pytesseract.image_to_string(image) + "\n"
            except Exception as e:
                print(f"Error OCR processing {filename}: {e}")
    return text

# Extract text from images and save them
def extract_text_from_pdf_images(pdf_path, output_folder, output_path):
    print("extract_text_from_pdf_images TRIGGERED")
    text = ""
    for image_path in extract_images_from_pdf(pdf_path, output_folder):
        try:
            image = Image.open(image_path)
            text += pytesseract.image_to_string(image) + "\n"
        except Exception as e:
            print(f"Error OCR processing {image_path}: {e}")

    # Save OCR text from images to file
    with open(output_path, "a", encoding="utf-8") as file:  # Append to include both PDF text and image text
        file.write(text)
    print(f"OCR text from images extracted and saved to {output_path}")

# Extract text from txt file
def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

# Extract text from docx file
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract text from pptx file
def extract_text_from_pptx(file_path):
    prs = Presentation(file_path)
    text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)

# Extract text from pdf file
def extract_text_from_pdf(pdf_path, output_path):
    print("extract_text_from_pdf TRIGGERED")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    # Save extracted text to file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)
    return text

# Function to handle all file types
def extract_text_from_file(file_path, output_path):
    if file_path.endswith('.pdf'):
        # Extract text from both PDF content and images
        text = extract_text_from_pdf(file_path, output_path)
        extract_text_from_pdf_images(file_path, output_folder, output_path)  # Append OCR text from images
    elif file_path.endswith('.txt'):
        text = extract_text_from_txt(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith('.pptx'):
        text = extract_text_from_pptx(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    # Write text to output file if not already saved within specific functions
    if text:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Text extracted and saved to {output_path}")

# paths to the pdf file and the output text file
pdf_path = r"C:\Users\Happy yadav\Desktop\aura.ai\test\doc\pdf1.pdf"
output_text_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\extracted.txt"
cleaned_text_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\cleaned.txt"

extract_text_from_file(pdf_path, output_text_path)

# Clean the extracted text
def clean_text(text):
    """Cleans the given text by removing extra spaces and special characters."""
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^a-zA-Z0-9\s.,]', '', text)  # Remove unwanted characters
    return text.strip()  # Remove leading and trailing spaces

# Remove UIN and CIN numbers from the text
def remove_uin_cin(text):
    # Pattern for UIN codes, assuming they start with 'UIN' followed by an alphanumeric string
    text = re.sub(r'\bUIN\s+[A-Z0-9]+\b', '', text)

    # Pattern for CIN codes, assuming they start with 'CIN' followed by an alphanumeric string
    text = re.sub(r'\bCIN\s+[A-Z0-9]+\b', '', text)

    # Remove extra spaces left after deletion
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# SingleFunction calling the above functions
def clean_extracted_text(input_file, output_file):
    """Cleans the text from the input file and saves it to the output file."""
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Clean the text
    cleaned_text = clean_text(text)
    cleaned_text = remove_uin_cin(cleaned_text)

    # Save the cleaned text to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)
    
    print(f"Cleaned text saved to '{output_file}'")

# save the cleaned text to a new file
clean_extracted_text(output_text_path, cleaned_text_path)

#if numerical data is present in the text, we can remove it using the below function

#insert the function if required

# calling the gemini api ffor script calling
def generate_script(cleaned_txt_path, video_length, language, llm_prompt_path):

    # Read cleaned text from the specified path
    with open(cleaned_txt_path, "r", encoding="utf-8") as file:
        cleaned_text = file.read()

    # Prepare the prompt
    llm_prompt = f"""
        <prompt>
            <step1>Extract the key information from the document and identify the main points that need to be discussed.</step1>
            <step2>Break down these main points into smaller subtopics that can be explained sequentially.</step2>
            <step3>For each subtopic, construct a simple and engaging explanation that fits naturally into a continuous narrative.</step3>
            <step4>Ensure that each subtopic flows logically into the next, maintaining coherence and a clear structure.</step4>
            <step5>Use simple and concise language, keeping the audience's attention with relatable examples or anecdotes where necessary.</step5>
            <step6>Review the entire monologue to make sure it includes all the important information from the original document.</step6>
            <step7>Don't include anything related to QR code or any link.</step7>
            <step8>Return the script only. The response should start with the script and end with it.</step8>
            <step9>Response should not contain anything like Script:</step9>
        </prompt>

        <!-- Text from cleaned.txt for reference -->
        {cleaned_text}
        
        <!-- Please make the script approximately {video_length} seconds long. -->
    """
    
    # Add language to the prompt if it's not English
    if language != "English":
        llm_prompt += f"\n\n<!-- Please make the script in {language}. -->"

    # Generate the content with Gemini API
    response = model.generate_content([llm_prompt])

    # Save the response to 'llm_prompt.txt'
    with open(llm_prompt_path, "w", encoding="utf-8") as output_file:
        output_file.write(response.text)
    print("Script generated successfully and saved to '{llm_prompt_path}'")
    
    return response.text

video_length = 60  # Example: 120 seconds for a 2-minute video
language = "Hindi"  # Specify the language, e.g., "English", "Spanish", etc.
llm_prompt_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\llm_prompt.txt"

# Call the function and get the generated script
script_text = generate_script(cleaned_text_path, video_length, language, llm_prompt_path)

# Questions generation from the text
def generate_quiz_from_text(cleaned_text):
    quiz_string = ""
    try:
        # Define the prompt to generate quiz questions with different types, difficulties, and explanations
        llm_prompt = f"""
        You are provided with the following text: 

        {cleaned_text}

        Based on this text, generate a pool of 10 questions that include a variety of question types:
        - Multiple-choice (MCQ)
        - True/false
        - Fill in the blanks (with options)

        For each question, output the response in the following JSON format:

        [
            {{
            "question": "Question 1 text here?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correctAnswer": "Correct option here",
            "explanation": "Explanation for the answer here",
            "type": "mcq" or "true-false" or "fill-in-the-blank",
            "difficulty": "Easy" or "Medium" or "Hard",
            "use": "normal"
            }},
            {{
            "question": "Question 2 text here?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correctAnswer": "Correct option here",
            "explanation": "Explanation for the answer here",
            "type": "mcq" or "true-false" or "fill-in-the-blank",
            "difficulty": "Easy" or "Medium" or "Hard",
            "use": "substitute"
            }},
            ...
        ]

        Ensure:
        - The correct answers are accurate and based on the provided text.
        - The questions are a mix of different types (multiple-choice, true/false, fill-in-the-blanks).
        - Each question is labeled with the appropriate difficulty level: "Easy," "Medium," or "Hard". 
        - In total, there must be 20 questions. All types: true-false, MCQs, and fill-in-the-blanks (with 3 options) must be present.
        - I need 5 questions for the quiz and 5 substitutes of only easy and medium type. 
        - Provide detailed explanations for each correct answer.

        Reply with just the JSON response and nothing else.
        """

        # Generate content using the model
        response = model.generate_content([llm_prompt])
        quiz_string = response.text
    except Exception as e:
        print(f"Error generating quiz: {e}")
    
    return quiz_string

def save_quiz_to_json(quiz_string, output_file):
    # Clean up any code block formatting from the response
    cleaned_string = quiz_string.replace('```json', '').replace('```', '').strip()

    try:
        # Parse the cleaned string as JSON
        quiz_json = json.loads(cleaned_string)
        
        # Save to specified output file
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(quiz_json, json_file, indent=4)
        
        print(f"Quiz data saved successfully to '{questions_file_path}'")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

questions_file_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\questions.json"


# Load cleaned text
with open(llm_prompt_path, "r", encoding="utf-8") as file:
    cleaned_text = file.read()

# Generate quiz questions and save to JSON
quiz_string = generate_quiz_from_text(cleaned_text)
save_quiz_to_json(quiz_string, questions_file_path)

def chunk_text(text, max_length=500):
    """Splits text into chunks of a maximum length."""
    words = text.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += (word + " ")
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_audio_with_background(llm_prompt_path, output_audio_path, background_music_path, final_output_path, language_code="hi-IN", speaker="meera", pitch=0.1, pace=1, loudness=1, music_volume=-20):
    try:
        # Read text from llm_prompt_path
        with open(llm_prompt_path, "r", encoding="utf-8") as file:
            text_content = file.read()
        
        # Split text into chunks within the 500 character limit
        text_chunks = chunk_text(text_content)
        
        # List to hold audio segments
        audio_segments = []

        # Process each chunk with the Sarvam API
        url = "https://api.sarvam.ai/text-to-speech"
        headers = {
            "api-subscription-key": sarvam_api_key,
            "Content-Type": "application/json"
        }
        
        for chunk in text_chunks:
            payload = {
                "target_language_code": language_code,
                "speaker": speaker,
                "pitch": pitch,
                "pace": pace,
                "loudness": loudness,
                "enable_preprocessing": True,
                "model": "bulbul:v1",
                "inputs": [chunk]
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            # Check if the response is successful
            if response.status_code == 200:
                audio_data = response.json().get('audios')[0]
                audio_bytes = base64.b64decode(audio_data)
                
                # Load audio segment and append to list
                with open("temp_chunk.wav", "wb") as audio_file:
                    audio_file.write(audio_bytes)
                
                audio_segment = AudioSegment.from_file("temp_chunk.wav")
                audio_segments.append(audio_segment)
                os.remove("temp_chunk.wav")  # Clean up temp file
            else:
                print(f"Error processing chunk: {response.status_code} - {response.text}")
                return
        
        # Concatenate all audio segments
        main_audio = sum(audio_segments)
        main_audio.export(output_audio_path, format="wav")
        print(f"Concatenated audio saved to {output_audio_path}")

        # Process and mix audio with background music
        # Load the main audio
        main_audio = AudioSegment.from_file(output_audio_path)
        
        # Load the background music and adjust volume
        background_music = AudioSegment.from_file(background_music_path)
        background_music = background_music - abs(music_volume)  # Lower the volume

        # Loop background music to match the length of the main audio
        if len(background_music) < len(main_audio):
            loop_count = len(main_audio) // len(background_music) + 1
            background_music = background_music * loop_count
        background_music = background_music[:len(main_audio)]
        
        # Overlay main audio on background music
        final_audio = main_audio.overlay(background_music)

        # Export the final mixed audio
        final_audio.export(final_output_path, format="mp3")
        print(f"Final audio with background music saved to {final_output_path}")

        # Delete the intermediate audio file
        os.remove(output_audio_path)
        print(f"Intermediate file '{output_audio_path}' deleted successfully.")

    except Exception as e:
        print(f"Error generating audio with background music: {e}")

# Static Paths for the function
output_audio_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\sarvam_generated_audio.wav"
background_music_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\background.mp3"
final_output_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\sarvam_output_audio_music.mp3"

generate_audio_with_background(
    llm_prompt_path=llm_prompt_path,
    output_audio_path=output_audio_path,
    background_music_path=background_music_path,
    final_output_path=final_output_path,
    language_code="hi-IN",
    speaker="meera",
    pitch=0.1,
    pace=1,
    loudness=1,
    music_volume=-20  # Adjust background music volume
)



def get_text_from_txt(file_path):
    """Reads text from a given file path."""
    try:
        with open(file_path, "r", encoding="utf-8") as text_file:
            text = text_file.read()
        return text
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def ask_aura_question(user_question, txt_file_path, model):
    """Answers the user's question using text from cleaned.txt or provides a general response."""
    answer = ""
    try:
        # Retrieve the extracted text from the txt file
        extracted_text = get_text_from_txt(txt_file_path)
        
        if not extracted_text:
            return "Error: Could not retrieve text from file."
        
        # Create a prompt asking Gemini to answer based on `cleaned.txt`
        prompt = f"Based on the following text, try to answer the question:\n\n'{extracted_text}'\n\nQuestion: {user_question}"
        response = model.generate_content(prompt)
        print("Initial answer response: ", response.text)  # Debug print for checking response
        answer = response.text

        # Check if the answer is relevant to the knowledge base
        if "I don't know" in answer or "I'm not sure" in answer or len(answer.strip()) < 5:
            # Provide a fallback response from Gemini's general knowledge if the response is inadequate
            fallback_prompt = f"I don't have specific knowledge about this part of your query based on the provided text, but I can answer from general knowledge.\n\nQuestion: {user_question}"
            fallback_response = model.generate_content(fallback_prompt)
            print("Fallback answer response: ", fallback_response.text)  # Debug print for checking fallback response
            answer = "I don’t have detailed information from the provided knowledge base, but here’s what I can tell you: " + fallback_response.text
    except Exception as e:
        print(f"Error while asking Gemini AI: {e}")
        return f"Error: {e}"
    
    return answer

# Main code to test the function
if __name__ == "__main__":
    # cleaned_text_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\cleaned.txt"
    
    while True:
        # Take user input for the question
        user_query = input("Enter your question (or type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break
        
        # Assume 'model' is your Gemini API client or instance capable of generating responses
        # Example usage:
        response = ask_aura_question(user_query, cleaned_text_path, model)
        print("Answer:", response)




