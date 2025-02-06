# Sign Language Video Generation

This project converts audio speech into sign language animations using a combination of frontend and backend technologies. Below is a detailed explanation of how the system works.

## Table of Contents
1. [Overview](#overview)
2. [Technologies Used](#technologies-used)
3. [Workflow](#workflow)
4. [Detailed Process](#detailed-process)
   - [Frontend](#frontend)
   - [Speech Recognition](#speech-recognition)
   - [Backend](#backend)
   - [Text Processing](#text-processing)
   - [Animation Generation](#animation-generation)
   - [Storage and Retrieval](#storage-and-retrieval)
5. [Handling Missing Words](#handling-missing-words)
6. [3D Model Animation](#3d-model-animation)

## Overview
This project aims to convert spoken language into sign language animations. It involves recording audio, processing the text, and playing corresponding sign language videos.

## Technologies Used
- **Frontend**: React
- **Backend**: Django (Python)
- **Speech Recognition**: Web Speech API
- **Text Processing**: NLTK (Natural Language Toolkit)
- **Database**: SQLite

## Workflow
1. User visits the home page.
2. User records speech using the microphone button.
3. Speech is converted to text and displayed in an input field.
4. User submits the text.
5. Text is processed (tokenization, POS tagging, lemmatization, stop words removal).
6. Mapped videos are played in sequence to show the sign language animation.

## Detailed Process

### Speech Recognition
- **Recording Audio**: The `record()` function uses the `webkitSpeechRecognition` API to capture and convert spoken words into text.
- **Storing Text**: The recognized text is stored in an input field (`speechToText`).

### Backend
- **Views**: Django views (`views.py`) handle requests and render the appropriate templates.
  - `home_view`, `about_view`, `contact_view`, `signup_view`, `login_view`, `logout_view`, and `animation_view` manage different pages and functionalities.
- **User Authentication**: Managed using Django's built-in authentication system.

### Text Processing
- **Tokenization**: The input text is tokenized into words using `word_tokenize`.
- **POS Tagging**: Parts of speech are tagged using `nltk.pos_tag`.
- **Lemmatization**: Words are lemmatized using `WordNetLemmatizer`.
- **Stop Words Removal**: Common stop words are removed from the text.

### Animation Generation
- **Word Mapping**: Each word is mapped to a corresponding video file (e.g., `word.mp4`).
- **Video Playback**: The `play()` function in `animation.html` dynamically sets the source of the video player to the appropriate video files based on the processed text.

### Storage and Retrieval
- **Static Files**: Video files are stored in the `static` directory and are served by Django's static file handling.
- **Database**: User data and other necessary information are stored in a SQLite database (`db.sqlite3`).

## Handling Missing Words
If a word does not have a corresponding video file, the system handles it by playing a default video (`default.mp4`). This ensures that the animation continues smoothly even if specific word videos are missing.

### 3D Model Animation
The 3D model works by mapping each processed word to a pre-recorded animation clip that shows the corresponding sign language gesture. The JavaScript code dynamically sets the video source to these clips, ensuring that the correct gestures are shown in sequence. If a specific word does not have a corresponding animation, a default video is played.

### Example Workflow for 3D Model Animation
Word Splitting: The processedText is split into individual words.
Video Path: For each word, the corresponding video path is constructed.
Fetch Video: The code attempts to fetch the video file for the current word.
Response Handling:
If the video file exists (response.ok), it sets the video source to the corresponding video file.
If the video file does not exist, it sets the video source to a default video (default.mp4).
Error Handling: If there is an error in fetching the video file, it also sets the video source to the default video.
Playback: The video is played, and the next word is processed when the current video ends.

### Run:
python manage.py runserver [ "port no. of your choice" { say : 4000} ]