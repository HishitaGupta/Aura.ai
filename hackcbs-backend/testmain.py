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
sarvam_api = os.getenv("SARVAM_API_KEY")

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
    
    print(f"Cleaned text saved to {output_file}")

# save the cleaned text to a new file
cleaned_text_path=r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\cleaned.txt"
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
language = "English"  # Specify the language, e.g., "English", "Spanish", etc.
llm_prompt_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\llm_prompt.txt"

# Call the function and get the generated script
script_text = generate_script(cleaned_text_path, video_length, language, llm_prompt_path)

