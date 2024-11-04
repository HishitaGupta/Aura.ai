# def generate_video_with_subtitles(audio_path, llm_prompt_path, output_video_path, font_size=16):
#     # Load the audio file
#     audio = AudioFileClip(audio_path)
#     audio_duration = audio.duration  # Duration in seconds

#     # Read subtitle text from llm_prompt_path
#     try:
#         with open(llm_prompt_path, "r", encoding="utf-8") as file:
#             subtitle_text = file.read()
#     except FileNotFoundError:
#         print(f"Error: The file {llm_prompt_path} does not exist.")
#         return
#     except Exception as e:
#         print(f"An error occurred while reading the file: {e}")
#         return

#     # Define the video resolution and background color
#     video_width, video_height = 1280, 720  # HD resolution
#     subtitle_bg_color = (255, 255, 0)  # Yellow background for subtitle
#     font_color = 'black'  # Black font color for subtitle text

#     # Initialize video background
#     video_bg = ColorClip(size=(video_width, video_height), color=(255, 255, 255)).set_duration(audio_duration)

#     # Split subtitle text into chunks
#     words = subtitle_text.split()
#     max_words_per_line = 10  # Limit words per line to avoid very long subtitles
#     subtitle_chunks = []
#     current_chunk = ""

#     for word in words:
#         if len(current_chunk.split()) < max_words_per_line:
#             current_chunk += f"{word} "
#         else:
#             subtitle_chunks.append(current_chunk.strip())
#             current_chunk = f"{word} "
#     subtitle_chunks.append(current_chunk.strip())  # Add the last chunk

#     # Calculate the display duration for each chunk based on audio length
#     chunk_duration = audio_duration / len(subtitle_chunks)

#     # Create subtitle clips and position them with a yellow background
#     subtitle_clips = []
#     for i, chunk in enumerate(subtitle_chunks):
#         # Create the subtitle text
#         subtitle = TextClip(chunk, fontsize=font_size, color=font_color, font="Arial", size=(video_width - 40, None), method="caption")
        
#         # Add background behind the subtitle text
#         subtitle_bg = ColorClip(size=(subtitle.w + 10, subtitle.h + 10), color=subtitle_bg_color)
        
#         # Overlay text on background
#         subtitle_with_bg = CompositeVideoClip([subtitle_bg.set_position(("center", "bottom")), subtitle.set_position(("center", "bottom"))], 
#                                             size=(video_width, video_height)).set_duration(chunk_duration)
        
#         # Set the start time for each subtitle clip
#         subtitle_clips.append(subtitle_with_bg.set_start(i * chunk_duration))

#     # Composite the video with background, audio, and subtitles
#     final_video = CompositeVideoClip([video_bg, *subtitle_clips])
#     final_video = final_video.set_audio(audio)  # Attach the audio to the video

#     # Export the video
#     final_video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
#     print(f"Video with subtitles saved to '{output_video_path}'")

# # Example usage
# output_video_path = r"C:\Users\Happy yadav\Desktop\aura.ai\hackcbs-backend\output_with_subtitles.mp4"

# generate_video_with_subtitles(final_output_path, llm_prompt_path, output_video_path)