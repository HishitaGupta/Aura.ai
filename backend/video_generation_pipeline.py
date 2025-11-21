

# import os
# import json
# import time
# import requests
# from typing import List, Optional, Dict
# from operator import add
# from pathlib import Path
# import subprocess
# import base64
# from pydub import AudioSegment
# import pysrt
# import whisper

# import cv2
# import numpy as np
# from PIL import Image, ImageDraw, ImageFont

# from langchain_core.prompts import ChatPromptTemplate
# from langgraph.graph import StateGraph, END
# from langgraph.checkpoint.memory import MemorySaver
# from langsmith import traceable
# from dotenv import load_dotenv

# from models import CompleteVideoScript
# from typing import TypedDict
# from sarvamai import SarvamAI

# load_dotenv()
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "video-gen-pipeline")

# # ==================== VIDEO COMPOSITION CONFIG ====================

# class VideoConfig:
#     """Centralized configuration for video formatting"""
#     WIDTH = 1280
#     HEIGHT = 720
#     FPS = 30
    
#     # Colors (RGB)
#     BG_COLOR = (30, 30, 40)
#     TEXT_COLOR = (255, 255, 255)
#     TITLE_COLOR = (100, 200, 255)
#     BULLET_COLOR = (220, 220, 220)
#     SUBTITLE_BG = (0, 0, 0, 180)
#     SUBTITLE_COLOR = (255, 255, 255)
    
#     # Fonts
#     TITLE_SIZE = 44
#     BULLET_SIZE = 28
#     SUBTITLE_SIZE = 24
#     HOOK_SIZE = 48
    
#     # Layout
#     TOP_MARGIN = 40
#     LEFT_MARGIN = 60
#     RIGHT_MARGIN = 60
#     BULLET_START_Y = 160
#     BULLET_GAP = 100
    
#     # Image positioning (right side)
#     IMAGE_WIDTH = 400
#     IMAGE_HEIGHT = 350
#     IMAGE_X = 820  # Position image on the right (WIDTH - IMAGE_WIDTH - margin)
#     IMAGE_Y = 180  # Vertical position for the image
    
#     # Text area constraints (left side only)
#     TEXT_AREA_WIDTH = 700  # Maximum width for text (leaves room for image)
#     TEXT_MAX_X = 750  # Text should not exceed this X position
    
#     # Durations (seconds)
#     HOOK_DURATION = 10
#     CONCLUSION_DURATION = 15
    
#     # Subtitle
#     SUBTITLE_Y_OFFSET = 30
#     SUBTITLE_PADDING = 5
#     SUBTITLE_LINE_HEIGHT = 30
    
#     @classmethod
#     def get_text_wrap_width(cls):
#         """Returns the maximum width available for text content"""
#         return cls.TEXT_AREA_WIDTH - cls.LEFT_MARGIN
    
#     @classmethod
#     def get_image_position(cls):
#         """Returns (x, y) tuple for image placement"""
#         return (cls.IMAGE_X, cls.IMAGE_Y)


# class VideoGenerationState(TypedDict):
#     complete_script: Optional[CompleteVideoScript]
#     audio_path: Optional[str]
#     srt_path: Optional[str]
#     audio_timestamps: Optional[List[Dict]]
#     images: Dict[str, str]
#     image_mapping: Dict[str, List[str]]
#     video_path: Optional[str]
#     messages: List[str]
#     current_step: str


# # ==================== AUDIO GENERATION FROM DESCRIPTIONS ====================

# @traceable(name="extract_audio_descriptions")
# def extract_audio_descriptions(script: CompleteVideoScript) -> List[Dict]:
#     """Extract audio descriptions with metadata from script"""
#     segments = []
    
#     # Hook
#     segments.append({
#         "type": "hook",
#         "text": script.hook.narration,
#         "section": "hook"
#     })
    
#     # Main topics
#     for topic in script.main_topics:
#         for part in topic.subtitle_segments:
#             segments.append({
#                 "type": "topic",
#                 "topic_number": topic.topic_number,
#                 "text": part.text,
#                 "section": f"topic_{topic.topic_number}"
#             })
    
#     # Conclusion
#     segments.append({
#         "type": "conclusion",
#         "text": script.conclusion.narration,
#         "section": "conclusion"
#     })
    
#     return segments


# @traceable(name="generate_audio_from_descriptions")
# def generate_audio_from_descriptions(
#     audio_segments: List[Dict],
#     language: str = "en-IN",
#     output_path: str = "./output/narration.wav"
# ) -> tuple[str, List[Dict]]:
#     """
#     Generate audio from audio descriptions and return timestamps
#     """
#     print(f"🎙️  Generating audio from descriptions in {language}...")

#     api_key = os.getenv("SARVAM_API_KEY")
#     if not api_key:
#         raise ValueError("SARVAM_API_KEY not set")

#     client = SarvamAI(api_subscription_key=api_key)

#     tmp_folder = "./tmp_audio_segments"
#     os.makedirs(tmp_folder, exist_ok=True)

#     final_audio = AudioSegment.silent(0)
#     timestamps = []
#     current_time_ms = 0

#     for idx, segment in enumerate(audio_segments):
#         print(f"📍 Segment {idx+1}/{len(audio_segments)}: {segment['section']}...")

#         # Generate TTS
#         response = client.text_to_speech.convert(
#             target_language_code="en-IN",
#             text=segment['text'],
#             model="bulbul:v2",
#             speaker="anushka"
#         )

#         audio_b64 = (
#             response.audios[0]
#             if hasattr(response, "audios")
#             else response["audios"][0]
#         )
#         audio_bytes = base64.b64decode(audio_b64)

#         chunk_path = f"{tmp_folder}/segment_{idx:03d}.wav"
#         with open(chunk_path, "wb") as f:
#             f.write(audio_bytes)

#         audio_segment = AudioSegment.from_wav(chunk_path)
        
#         # Add small pause between segments
#         pause = AudioSegment.silent(300)  # 300ms pause
#         audio_segment = audio_segment + pause
        
#         # Store timestamp info
#         timestamps.append({
#             "index": idx,
#             "type": segment['type'],
#             "section": segment['section'],
#             "topic_number": segment.get('topic_number'),
#             "start_ms": current_time_ms,
#             "end_ms": current_time_ms + len(audio_segment),
#             "duration_ms": len(audio_segment),
#             "text": segment['text']
#         })
        
#         final_audio += audio_segment
#         current_time_ms += len(audio_segment)

#         time.sleep(0.5)

#     # Export merged audio
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     final_audio.export(output_path, format="wav", bitrate="192k")

#     print(f"✅ Audio saved: {output_path} ({len(final_audio)/1000:.1f}s)")
    
#     # Save timestamps
#     timestamp_path = "./output/audio_timestamps.json"
#     with open(timestamp_path, "w") as f:
#         json.dump(timestamps, f, indent=2)
    
#     return output_path, timestamps


# # ==================== SUBTITLE GENERATION FROM AUDIO ====================

# @traceable(name="generate_subtitles_from_audio")
# def generate_subtitles_from_audio(
#     audio_path: str,
#     timestamps: List[Dict],
#     output_srt: str = "./output/subtitles.srt"
# ) -> str:
#     """
#     Generate SRT subtitles using Whisper or similar STT
#     Falls back to using timestamps if STT unavailable
#     """
#     print("📝 Generating subtitles from audio...")
    
#     try:
        
        
#         model = whisper.load_model("base")
#         result = model.transcribe(audio_path, word_timestamps=True)
        
#         # Create SRT from Whisper output
#         subs = pysrt.SubRipFile()
        
#         for i, segment in enumerate(result['segments']):
#             start = pysrt.SubRipTime(seconds=segment['start'])
#             end = pysrt.SubRipTime(seconds=segment['end'])
#             text = segment['text'].strip()
            
#             subs.append(pysrt.SubRipItem(
#                 index=i+1,
#                 start=start,
#                 end=end,
#                 text=text
#             ))
        
#         subs.save(output_srt, encoding='utf-8')
#         print(f"✅ Subtitles generated using Whisper: {output_srt}")
        
#     except ImportError:
#         print("⚠️  Whisper not available, using timestamp-based subtitles...")
        
#         # Fallback: Create subtitles from timestamps and original text
#         subs = pysrt.SubRipFile()
        
#         for i, ts in enumerate(timestamps):
#             start = pysrt.SubRipTime(milliseconds=ts['start_ms'])
#             end = pysrt.SubRipTime(milliseconds=ts['end_ms'])
            
#             # Split long text into chunks for readability
#             text = ts['text']
#             words = text.split()
#             chunk_size = 10
#             text_chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            
#             # Create subtitle entries for each chunk
#             chunk_duration = (ts['end_ms'] - ts['start_ms']) / len(text_chunks)
            
#             for j, chunk in enumerate(text_chunks):
#                 chunk_start_ms = ts['start_ms'] + (j * chunk_duration)
#                 chunk_end_ms = chunk_start_ms + chunk_duration
                
#                 subs.append(pysrt.SubRipItem(
#                     index=len(subs)+1,
#                     start=pysrt.SubRipTime(milliseconds=int(chunk_start_ms)),
#                     end=pysrt.SubRipTime(milliseconds=int(chunk_end_ms)),
#                     text=chunk
#                 ))
        
#         subs.save(output_srt, encoding='utf-8')
#         print(f"✅ Subtitles generated from timestamps: {output_srt}")
    
#     return output_srt


# @traceable(name="audio_generation_node")
# def audio_generation_node(state: VideoGenerationState) -> VideoGenerationState:
#     """Node: Generate audio from descriptions and create subtitles"""
    
#     print("\n🎬 Step 1: Generating Audio from Descriptions...")
    
#     script = state['complete_script']
#     language = os.getenv("AUDIO_LANGUAGE", "en-IN")
    
#     # Extract audio descriptions
#     audio_segments = extract_audio_descriptions(script)
    
#     # Generate audio
#     audio_path, timestamps = generate_audio_from_descriptions(
#         audio_segments,
#         language=language,
#         output_path="./output/narration.wav"
#     )
    
#     # Generate subtitles from audio
#     srt_path = generate_subtitles_from_audio(
#         audio_path,
#         timestamps,
#         output_srt="./output/subtitles.srt"
#     )
    
#     state["audio_path"] = audio_path
#     state["srt_path"] = srt_path
#     state["audio_timestamps"] = timestamps
#     state["current_step"] = "audio_generated"
#     state["messages"].append(f"✅ Audio generated ({language})")
#     state["messages"].append(f"✅ Subtitles generated")
    
#     return state


# # ==================== IMAGE GENERATION ====================

# @traceable(name="generate_image_pollinations")
# def generate_image_pollinations(
#     prompt: str,
#     width: int = 1280,
#     height: int = 720,
#     output_path: str = None,
#     delay: float = 5,
#     max_retries: int = 3
# ) -> str:
#     """Generate image using Pollinations AI with retry logic"""
    
#     actual_delay = delay + np.random.uniform(-0.5, 2)
#     time.sleep(actual_delay)
    
#     print(f"🎨 Generating: {prompt[:40]}...")

#     url = f"https://image.pollinations.ai/prompt/{prompt}"
    
#     params = {
#         "width": width,
#         "height": height,
#         "nologo": "true"
#     }

#     for attempt in range(1, max_retries + 1):
#         try:
#             response = requests.get(url, params=params, timeout=60)
#             response.raise_for_status()

#             if output_path:
#                 os.makedirs(os.path.dirname(output_path), exist_ok=True)
#                 with open(output_path, "wb") as f:
#                     f.write(response.content)
#                 print(f"   ✓ Saved: {output_path}")
#                 return output_path
            
#             return response.content

#         except Exception as e:
#             print(f"   ❌ Attempt {attempt}/{max_retries}: {e}")
#             if attempt < max_retries:
#                 time.sleep(2 + attempt)

#     raise Exception(f"Image generation failed: {prompt}")


# @traceable(name="image_generation_node")
# def image_generation_node(state: VideoGenerationState) -> VideoGenerationState:
#     """Node: Generate all images with mapping"""
#     print("\n🎬 Step 2: Generating Images...")
    
#     script = state['complete_script']
#     output_dir = "./output/images"
#     os.makedirs(output_dir, exist_ok=True)
    
#     image_mapping = {}
    
#     # Hook image
#     hook_path = f"{output_dir}/hook.png"
#     state["images"]["hook"] = generate_image_pollinations(
#         script.image_generation_prompts[0],
#         output_path=hook_path
#     )
    
#     # Topic images with mapping
#     prompt_idx = 1
#     for topic in script.main_topics:
#         topic_id = f"topic_{topic.topic_number}"
#         image_mapping[topic_id] = []
        
#         # Generate image for EACH visual
#         for visual_idx, visual in enumerate(topic.visuals):
#             if prompt_idx < len(script.image_generation_prompts):
#                 img_prompt = script.image_generation_prompts[prompt_idx]
#                 img_prompt = img_prompt.split(":", 1)[1].strip() if ":" in img_prompt else img_prompt
                
#                 img_path = f"{output_dir}/{topic_id}_visual_{visual_idx}.png"
#                 state["images"][f"{topic_id}_visual_{visual_idx}"] = generate_image_pollinations(
#                     img_prompt,
#                     output_path=img_path
#                 )
#                 image_mapping[topic_id].append(img_path)
#                 prompt_idx += 1
    
#     # Conclusion image
#     conclusion_path = f"{output_dir}/conclusion.png"
#     state["images"]["conclusion"] = generate_image_pollinations(
#         script.image_generation_prompts[-1],
#         output_path=conclusion_path
#     )
    
#     state["image_mapping"] = image_mapping
#     state["current_step"] = "images_generated"
#     state["messages"].append(f"✅ Generated {len(state['images'])} images")
    
#     with open("./output/image_mapping.json", "w") as f:
#         json.dump({
#             "image_paths": state["images"],
#             "topic_mapping": state["image_mapping"]
#         }, f, indent=2)
    
#     return state


# # ==================== VIDEO COMPOSITION WITH SYNC ====================

# def create_text_image(
#     text: str,
#     config: VideoConfig = VideoConfig,
#     font_size: Optional[int] = None
# ) -> Image.Image:
#     """Create image with centered text"""
#     img = Image.new("RGB", (config.WIDTH, config.HEIGHT), config.BG_COLOR)
#     draw = ImageDraw.Draw(img)
    
#     font_size = font_size or config.HOOK_SIZE
    
#     try:
#         font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
#     except:
#         font = ImageFont.load_default()
    
#     words = text.split()
#     lines = []
#     current_line = []
    
#     for word in words:
#         test_line = " ".join(current_line + [word])
#         bbox = draw.textbbox((0, 0), test_line, font=font)
#         if bbox[2] - bbox[0] <= config.WIDTH - 100:
#             current_line.append(word)
#         else:
#             if current_line:
#                 lines.append(" ".join(current_line))
#             current_line = [word]
#     if current_line:
#         lines.append(" ".join(current_line))
    
#     total_height = len(lines) * font_size * 1.3
#     y = (config.HEIGHT - total_height) // 2
    
#     for line in lines:
#         bbox = draw.textbbox((0, 0), line, font=font)
#         line_width = bbox[2] - bbox[0]
#         x = (config.WIDTH - line_width) // 2
#         draw.text((x, y), line, fill=config.TEXT_COLOR, font=font)
#         y += int(font_size * 1.3)
    
#     return img


# def create_topic_frame(
#     topic_title: str,
#     bullet_points: List[str],
#     image_path: str,
#     config: VideoConfig = VideoConfig
# ) -> Image.Image:
#     """Create frame: title center, bullets left, image right"""
#     canvas = Image.new("RGB", (config.WIDTH, config.HEIGHT), config.BG_COLOR)
#     draw = ImageDraw.Draw(canvas)
    
#     try:
#         title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", config.TITLE_SIZE)
#         bullet_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", config.BULLET_SIZE)
#     except:
#         title_font = ImageFont.load_default()
#         bullet_font = ImageFont.load_default()
    
#     # Title at top center
#     bbox = draw.textbbox((0, 0), topic_title, font=title_font)
#     title_width = bbox[2] - bbox[0]
#     x_title = (config.WIDTH - title_width) // 2
#     draw.text((x_title, config.TOP_MARGIN), topic_title, fill=config.TITLE_COLOR, font=title_font)
    
#     # Left side: bullets
#     left_y = config.BULLET_START_Y
#     for point in bullet_points[:3]:
#         draw.text((config.LEFT_MARGIN + 20, left_y), f"• {point}", fill=config.BULLET_COLOR, font=bullet_font)
#         left_y += config.BULLET_GAP
    
#     # Right side: image
#     if os.path.exists(image_path):
#         img = Image.open(image_path).convert("RGB")
#         img_height = int(config.IMAGE_WIDTH * img.height / img.width)
#         img = img.resize((config.IMAGE_WIDTH, img_height), Image.Resampling.LANCZOS)
        
#         right_x = config.WIDTH - config.IMAGE_WIDTH - config.RIGHT_MARGIN
#         right_y = (config.HEIGHT - img_height) // 2
#         canvas.paste(img, (right_x, right_y))
    
#     return canvas


# def add_subtitles_to_frame(
#     frame: Image.Image,
#     subtitle_text: str,
#     config: VideoConfig = VideoConfig
# ) -> Image.Image:
#     """Add subtitle at bottom center"""
#     draw = ImageDraw.Draw(frame)
    
#     try:
#         sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", config.SUBTITLE_SIZE)
#     except:
#         sub_font = ImageFont.load_default()
    
#     words = subtitle_text.split()
#     lines = []
#     current_line = []
    
#     for word in words:
#         test_line = " ".join(current_line + [word])
#         bbox = draw.textbbox((0, 0), test_line, font=sub_font)
#         if bbox[2] - bbox[0] <= config.WIDTH - 100:
#             current_line.append(word)
#         else:
#             if current_line:
#                 lines.append(" ".join(current_line))
#             current_line = [word]
#     if current_line:
#         lines.append(" ".join(current_line))
    
#     y = config.HEIGHT - (len(lines) * config.SUBTITLE_LINE_HEIGHT) - 30
#     for line in lines:
#         bbox = draw.textbbox((0, 0), line, font=sub_font)
#         line_width = bbox[2] - bbox[0]
#         x = (config.WIDTH - line_width) // 2
        
#         draw.rectangle(
#             [(x - config.SUBTITLE_PADDING, y - config.SUBTITLE_PADDING), 
#              (x + line_width + config.SUBTITLE_PADDING, y + 25 + config.SUBTITLE_PADDING)],
#             fill=(0, 0, 0, 128)
#         )
#         draw.text((x, y), line, fill=config.SUBTITLE_COLOR, font=sub_font)
#         y += config.SUBTITLE_LINE_HEIGHT
    
#     return frame


# @traceable(name="compose_video_node")
# def compose_video_node(state: VideoGenerationState) -> VideoGenerationState:
#     """Memory-safe and FFmpeg-safe video composer"""
#     print("\n🎬 Step 3: Composing Video (Synced with Audio)...")

#     script = state['complete_script']
#     timestamps = state['audio_timestamps']
#     config = VideoConfig

#     # Load subtitles & audio
#     subs = pysrt.open(state['srt_path'])
#     audio = AudioSegment.from_wav(state['audio_path'])

#     total_duration_ms = len(audio)
#     total_frames = int((total_duration_ms / 1000.0) * config.FPS)

#     print(f"📊 Total duration: {total_duration_ms/1000:.1f}s ({total_frames} frames)")

#     # Open Video Writer
#     video_path = "./output/video_with_visuals.mp4"
#     os.makedirs(os.path.dirname(video_path), exist_ok=True)

#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     out = cv2.VideoWriter(
#         video_path,
#         fourcc,
#         config.FPS,
#         (config.WIDTH, config.HEIGHT)
#     )

#     if not out.isOpened():
#         raise RuntimeError("❌ Could not open VideoWriter. Check FFmpeg installation and codec support.")

#     # Write frames directly – no large list in memory
#     frames_written = 0

#     for ts_idx, ts in enumerate(timestamps):
#         start_frame = int((ts['start_ms'] / 1000.0) * config.FPS)
#         end_frame = int((ts['end_ms'] / 1000.0) * config.FPS)
#         num_frames = max(1, end_frame - start_frame)

#         print(f"📽️ Segment {ts_idx+1}/{len(timestamps)}: {ts['section']} ({num_frames} frames)")

#         # Select image based on node type
#         if ts['type'] == 'hook':
#             image_path = state["images"].get("hook")
#             base_frame = create_text_image(ts['text'], config)

#         elif ts['type'] == 'topic':
#             topic = next(
#                 (t for t in script.main_topics if t.topic_number == ts['topic_number']), 
#                 None
#             )
#             topic_id = f"topic_{ts['topic_number']}"
#             topic_images = state["image_mapping"].get(topic_id, [])

#             visual_idx = sum(
#                 1 for t in timestamps[:ts_idx] 
#                 if t.get('topic_number') == ts['topic_number']
#             )

#             image_idx = (visual_idx % len(topic_images)) if topic_images else 0
#             image_path = topic_images[image_idx] if topic_images else None

#             if image_path and os.path.exists(image_path):
#                 base_frame = create_topic_frame(topic.title, topic.key_points, image_path, config)
#             else:
#                 base_frame = create_text_image(topic.title, config)

#         elif ts['type'] == 'conclusion':
#             base_frame = create_text_image(ts['text'], config)

#         else:
#             base_frame = create_text_image(ts['text'], config)

#         # Convert once to numpy
#         base_frame_np = np.array(base_frame, dtype=np.uint8)

#         # ACCURATE SUBTITLE TIMING + MEMORY-SAFE
#         for _ in range(num_frames):

#             current_time_ms = (frames_written / config.FPS) * 1000

#             # Find active subtitle
#             active_subtitle = ""
#             for sub in subs:
#                 if sub.start.ordinal <= current_time_ms < sub.end.ordinal:
#                     active_subtitle = sub.text
#                     break

#             # Add subtitles
#             frame_with_sub = add_subtitles_to_frame(
#                 Image.fromarray(base_frame_np),
#                 active_subtitle,
#                 config
#             )
#             frame_np = np.array(frame_with_sub, dtype=np.uint8)

#             # Ensure size matches video spec
#             h, w = frame_np.shape[:2]
#             if (w, h) != (config.WIDTH, config.HEIGHT):
#                 frame_np = cv2.resize(frame_np, (config.WIDTH, config.HEIGHT))

#             # Ensure proper type
#             if frame_np.dtype != np.uint8:
#                 frame_np = frame_np.astype(np.uint8)

#             # Convert RGB → BGR
#             bgr_frame = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

#             out.write(bgr_frame)
#             frames_written += 1

#             if frames_written % 300 == 0:
#                 print(f"   {frames_written}/{total_frames} frames written...")

#     # Pad end if missing frames
#     while frames_written < total_frames:
#         out.write(bgr_frame)   # last frame repeated
#         frames_written += 1

#     out.release()
#     print(f"✅ Video saved: {video_path}")

#     state["video_path"] = video_path
#     state["current_step"] = "video_composed"
#     state["messages"].append(f"🎬 Video composed ({frames_written} frames, synced)")

#     return state


# @traceable(name="merge_audio_video_node")
# def merge_audio_video_node(state: VideoGenerationState) -> VideoGenerationState:
#     """Node: Merge audio with video - perfectly synced"""
#     print("\n🎬 Step 4: Merging Audio & Video...")
    
#     output_path = "./output/final_video.mp4"
    
#     cmd = [
#         "ffmpeg",
#         "-i", state["video_path"],
#         "-i", state["audio_path"],
#         "-c:v", "libx264",
#         "-preset", "medium",
#         "-c:a", "aac",
#         "-b:a", "192k",
#         "-shortest",
#         "-y",
#         output_path
#     ]
    
#     print(f"   ⏳ FFmpeg merging...")
    
#     try:
#         subprocess.run(cmd, check=True, capture_output=True, timeout=600)
#         print(f"✅ Final video: {output_path}")
#         state["video_path"] = output_path
#     except subprocess.CalledProcessError as e:
#         print(f"⚠️  FFmpeg error: {e.stderr.decode()}")
#         raise
    
#     state["current_step"] = "complete"
#     state["messages"].append(f"✅ Final video: {output_path}")
    
#     return state


# # ==================== LANGGRAPH WORKFLOW ====================

# def create_video_generation_workflow():
#     """Create workflow with checkpoint support"""
#     workflow = StateGraph(VideoGenerationState)
    
#     workflow.add_node("generate_audio", audio_generation_node)
#     workflow.add_node("generate_images", image_generation_node)
#     workflow.add_node("compose_video", compose_video_node)
#     workflow.add_node("merge_media", merge_audio_video_node)
    
#     workflow.set_entry_point("generate_audio")
#     workflow.add_edge("generate_audio", "generate_images")
#     workflow.add_edge("generate_images", "compose_video")
#     workflow.add_edge("compose_video", "merge_media")
#     workflow.add_edge("merge_media", END)
    
#     memory = MemorySaver()
#     return workflow.compile(checkpointer=memory)


# @traceable(name="generate_complete_video")
# def generate_complete_video(
#     script_path: str = "./output/complete_script.json",
#     resume_from: Optional[str] = "video_composed"
# ) -> str:
#     """
#     Main function to generate video from script
    
#     resume_from: "audio_generated", "images_generated", "video_composed", or None
#     """
    
#     print("🚀 Starting Video Generation Pipeline (Audio-First, Fully Synced)")
#     print("=" * 60)
    
#     with open(script_path, "r") as f:
#         script_dict = json.load(f)
    
#     script = CompleteVideoScript(**script_dict)
    
#     state = VideoGenerationState(
#         complete_script=script,
#         audio_path=None,
#         srt_path=None,
#         audio_timestamps=None,
#         images={},
#         image_mapping={},
#         video_path=None,
#         messages=[],
#         current_step="initialized"
#     )
    
#     app = create_video_generation_workflow()
    
#     print("\n🎬 Running Workflow...")
#     print("=" * 60)
    
#     config = {"configurable": {"thread_id": "main"}}
#     final_state = app.invoke(state, config=config)
    
#     print("\n" + "=" * 60)
#     print("✨ Complete!")
#     print("=" * 60)
    
#     print("\n📊 Summary:")
#     for msg in final_state["messages"]:
#         print(f"  {msg}")
    
#     return final_state["video_path"]


# if __name__ == "__main__":
#     video_path = generate_complete_video()
#     print(f"\n🎉 Final: {video_path}")







import os
import json
import time
import requests
from typing import List, Optional, Dict
from operator import add
from pathlib import Path
import subprocess
import base64
from pydub import AudioSegment
import pysrt
import whisper

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from dotenv import load_dotenv

from models import CompleteVideoScript
from typing import TypedDict
from sarvamai import SarvamAI


import math


from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Dict, Optional, Tuple


load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "video-gen-pipeline")

# ==================== VIDEO COMPOSITION CONFIG ====================

class VideoConfig:
    """Centralized configuration for video formatting"""
    WIDTH = 1280
    HEIGHT = 720
    FPS = 30
    
    # Colors (RGB)
    BG_COLOR = (30, 30, 40)
    TEXT_COLOR = (255, 255, 255)
    TITLE_COLOR = (100, 200, 255)
    BULLET_COLOR = (220, 220, 220)
    ACCENT_COLOR = (255, 180, 100)
    SUBTITLE_BG = (0, 0, 0, 180)
    SUBTITLE_COLOR = (255, 255, 255)
    
    # Fonts
    TITLE_SIZE = 44
    BULLET_SIZE = 28
    SUBTITLE_SIZE = 24
    HOOK_SIZE = 48
    
    # Layout
    TOP_MARGIN = 40
    LEFT_MARGIN = 60
    RIGHT_MARGIN = 60
    BULLET_START_Y = 200
    BULLET_GAP = 85
    
    # Image positioning (right side)
    IMAGE_WIDTH = 380
    IMAGE_MAX_HEIGHT = 550
    IMAGE_X = 830
    IMAGE_Y = 170
    
    # Text area constraints (left side only)
    TEXT_AREA_WIDTH = 720
    TEXT_MAX_X = 780
    
    # Animation settings
    TYPING_SPEED = 0.5
    BULLET_DELAY_FRAMES = 10
    FADE_FRAMES = 15
    TRANSITION_FRAMES = 15
    
    # Durations (seconds)
    HOOK_DURATION = 10
    CONCLUSION_DURATION = 15
    
    # Subtitle
    SUBTITLE_Y_OFFSET = 30
    SUBTITLE_PADDING = 8
    SUBTITLE_LINE_HEIGHT = 32
    
    @classmethod
    def get_text_wrap_width(cls):
        return cls.TEXT_AREA_WIDTH - cls.LEFT_MARGIN - 40
    
    @classmethod
    def get_image_position(cls):
        return (cls.IMAGE_X, cls.IMAGE_Y)




class VideoGenerationState(TypedDict):
    complete_script: Optional[CompleteVideoScript]
    audio_path: Optional[str]
    srt_path: Optional[str]
    audio_timestamps: Optional[List[Dict]]
    images: Dict[str, str]
    image_mapping: Dict[str, List[str]]
    video_path: Optional[str]
    messages: List[str]
    current_step: str


# ==================== AUDIO GENERATION FROM DESCRIPTIONS ====================

@traceable(name="extract_audio_descriptions")
def extract_audio_descriptions(script: CompleteVideoScript) -> List[Dict]:
    """Extract audio descriptions with metadata from script"""
    segments = []
    
    # Hook
    segments.append({
        "type": "hook",
        "text": script.hook.narration,
        "section": "hook"
    })
    
    # Main topics
    for topic in script.main_topics:
        for part in topic.subtitle_segments:
            segments.append({
                "type": "topic",
                "topic_number": topic.topic_number,
                "text": part.text,
                "section": f"topic_{topic.topic_number}"
            })
    
    # Conclusion
    segments.append({
        "type": "conclusion",
        "text": script.conclusion.narration,
        "section": "conclusion"
    })
    
    return segments


@traceable(name="generate_audio_from_descriptions")
def generate_audio_from_descriptions(
    audio_segments: List[Dict],
    language: str = "en-IN",
    output_path: str = "./output/narration.wav"
) -> tuple[str, List[Dict]]:
    """
    Generate audio from audio descriptions and return timestamps
    """
    print(f"🎙️  Generating audio from descriptions in {language}...")

    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY not set")

    client = SarvamAI(api_subscription_key=api_key)

    tmp_folder = "./tmp_audio_segments"
    os.makedirs(tmp_folder, exist_ok=True)

    final_audio = AudioSegment.silent(0)
    timestamps = []
    current_time_ms = 0

    for idx, segment in enumerate(audio_segments):
        print(f"📍 Segment {idx+1}/{len(audio_segments)}: {segment['section']}...")

        # Generate TTS
        response = client.text_to_speech.convert(
            target_language_code="en-IN",
            text=segment['text'],
            model="bulbul:v2",
            speaker="anushka"
        )

        audio_b64 = (
            response.audios[0]
            if hasattr(response, "audios")
            else response["audios"][0]
        )
        audio_bytes = base64.b64decode(audio_b64)

        chunk_path = f"{tmp_folder}/segment_{idx:03d}.wav"
        with open(chunk_path, "wb") as f:
            f.write(audio_bytes)

        audio_segment = AudioSegment.from_wav(chunk_path)
        
        # Add small pause between segments
        pause = AudioSegment.silent(300)  # 300ms pause
        audio_segment = audio_segment + pause
        
        # Store timestamp info
        timestamps.append({
            "index": idx,
            "type": segment['type'],
            "section": segment['section'],
            "topic_number": segment.get('topic_number'),
            "start_ms": current_time_ms,
            "end_ms": current_time_ms + len(audio_segment),
            "duration_ms": len(audio_segment),
            "text": segment['text']
        })
        
        final_audio += audio_segment
        current_time_ms += len(audio_segment)

        time.sleep(0.5)

    # Export merged audio
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_audio.export(output_path, format="wav", bitrate="192k")

    print(f"✅ Audio saved: {output_path} ({len(final_audio)/1000:.1f}s)")
    
    # Save timestamps
    timestamp_path = "./output/audio_timestamps.json"
    with open(timestamp_path, "w") as f:
        json.dump(timestamps, f, indent=2)
    
    return output_path, timestamps


# ==================== SUBTITLE GENERATION FROM AUDIO ====================

@traceable(name="generate_subtitles_from_audio")
def generate_subtitles_from_audio(
    audio_path: str,
    timestamps: List[Dict],
    output_srt: str = "./output/subtitles.srt"
) -> str:
    """
    Generate SRT subtitles using Whisper or similar STT
    Falls back to using timestamps if STT unavailable
    """
    print("📝 Generating subtitles from audio...")
    
    try:
        
        
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        # Create SRT from Whisper output
        subs = pysrt.SubRipFile()
        
        for i, segment in enumerate(result['segments']):
            start = pysrt.SubRipTime(seconds=segment['start'])
            end = pysrt.SubRipTime(seconds=segment['end'])
            text = segment['text'].strip()
            
            subs.append(pysrt.SubRipItem(
                index=i+1,
                start=start,
                end=end,
                text=text
            ))
        
        subs.save(output_srt, encoding='utf-8')
        print(f"✅ Subtitles generated using Whisper: {output_srt}")
        
    except ImportError:
        print("⚠️  Whisper not available, using timestamp-based subtitles...")
        
        # Fallback: Create subtitles from timestamps and original text
        subs = pysrt.SubRipFile()
        
        for i, ts in enumerate(timestamps):
            start = pysrt.SubRipTime(milliseconds=ts['start_ms'])
            end = pysrt.SubRipTime(milliseconds=ts['end_ms'])
            
            # Split long text into chunks for readability
            text = ts['text']
            words = text.split()
            chunk_size = 10
            text_chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            
            # Create subtitle entries for each chunk
            chunk_duration = (ts['end_ms'] - ts['start_ms']) / len(text_chunks)
            
            for j, chunk in enumerate(text_chunks):
                chunk_start_ms = ts['start_ms'] + (j * chunk_duration)
                chunk_end_ms = chunk_start_ms + chunk_duration
                
                subs.append(pysrt.SubRipItem(
                    index=len(subs)+1,
                    start=pysrt.SubRipTime(milliseconds=int(chunk_start_ms)),
                    end=pysrt.SubRipTime(milliseconds=int(chunk_end_ms)),
                    text=chunk
                ))
        
        subs.save(output_srt, encoding='utf-8')
        print(f"✅ Subtitles generated from timestamps: {output_srt}")
    
    return output_srt


@traceable(name="audio_generation_node")
def audio_generation_node(state: VideoGenerationState) -> VideoGenerationState:
    """Node: Generate audio from descriptions and create subtitles"""
    
    print("\n🎬 Step 1: Generating Audio from Descriptions...")
    
    script = state['complete_script']
    language = os.getenv("AUDIO_LANGUAGE", "en-IN")
    
    # Extract audio descriptions
    audio_segments = extract_audio_descriptions(script)
    
    # Generate audio
    audio_path, timestamps = generate_audio_from_descriptions(
        audio_segments,
        language=language,
        output_path="./output/narration.wav"
    )
    
    # Generate subtitles from audio
    srt_path = generate_subtitles_from_audio(
        audio_path,
        timestamps,
        output_srt="./output/subtitles.srt"
    )
    
    state["audio_path"] = audio_path
    state["srt_path"] = srt_path
    state["audio_timestamps"] = timestamps
    state["current_step"] = "audio_generated"
    state["messages"].append(f"✅ Audio generated ({language})")
    state["messages"].append(f"✅ Subtitles generated")
    
    return state


# ==================== IMAGE GENERATION ====================

@traceable(name="generate_image_pollinations")
def generate_image_pollinations(
    prompt: str,
    width: int = 720,
    height: int = 720,
    output_path: str = None,
    delay: float = 5,
    max_retries: int = 3
) -> str:
    """Generate image using Pollinations AI with retry logic"""
    
    actual_delay = delay + np.random.uniform(-0.5, 2)
    time.sleep(actual_delay)
    
    print(f"🎨 Generating: {prompt[:40]}...")

    url = f"https://image.pollinations.ai/prompt/{prompt}"
    
    params = {
        "width": width,
        "height": height,
        "nologo": "true"
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"   ✓ Saved: {output_path}")
                return output_path
            
            return response.content

        except Exception as e:
            print(f"   ❌ Attempt {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(2 + attempt)

    raise Exception(f"Image generation failed: {prompt}")


@traceable(name="image_generation_node")
def image_generation_node(state: VideoGenerationState) -> VideoGenerationState:
    """Node: Generate all images with mapping"""
    print("\n🎬 Step 2: Generating Images...")
    
    script = state['complete_script']
    output_dir = "./output/images"
    os.makedirs(output_dir, exist_ok=True)
    
    image_mapping = {}
    
    # Hook image
    hook_path = f"{output_dir}/hook.png"
    state["images"]["hook"] = generate_image_pollinations(
        script.image_generation_prompts[0],
        output_path=hook_path
    )
    
    # Topic images with mapping
    prompt_idx = 1
    for topic in script.main_topics:
        topic_id = f"topic_{topic.topic_number}"
        image_mapping[topic_id] = []
        
        # Generate image for EACH visual
        for visual_idx, visual in enumerate(topic.visuals):
            if prompt_idx < len(script.image_generation_prompts):
                img_prompt = script.image_generation_prompts[prompt_idx]
                img_prompt = img_prompt.split(":", 1)[1].strip() if ":" in img_prompt else img_prompt
                
                img_path = f"{output_dir}/{topic_id}_visual_{visual_idx}.png"
                state["images"][f"{topic_id}_visual_{visual_idx}"] = generate_image_pollinations(
                    img_prompt,
                    output_path=img_path
                )
                image_mapping[topic_id].append(img_path)
                prompt_idx += 1
    
    # Conclusion image
    conclusion_path = f"{output_dir}/conclusion.png"
    state["images"]["conclusion"] = generate_image_pollinations(
        script.image_generation_prompts[-1],
        output_path=conclusion_path
    )
    
    state["image_mapping"] = image_mapping
    state["current_step"] = "images_generated"
    state["messages"].append(f"✅ Generated {len(state['images'])} images")
    
    with open("./output/image_mapping.json", "w") as f:
        json.dump({
            "image_paths": state["images"],
            "topic_mapping": state["image_mapping"]
        }, f, indent=2)
    
    return state


# ==================== HELPER FUNCTIONS ====================

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load font with fallback - works on Windows and Linux"""
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
              max_width: int) -> List[str]:
    """Wrap text to fit within max_width"""
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_text_with_shadow(draw: ImageDraw.Draw, pos: Tuple[int, int], text: str,
                          font: ImageFont.FreeTypeFont, fill: Tuple,
                          shadow_offset: Tuple[int, int] = (2, 2)):
    """Draw text with drop shadow"""
    draw.text((pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]), 
              text, fill=(0, 0, 0, 150), font=font)
    draw.text(pos, text, fill=fill, font=font)


def ease_out(t: float) -> float:
    """Ease out quad"""
    return 1 - (1 - t) ** 2


def ease_in_out(t: float) -> float:
    """Ease in-out"""
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


# ==================== IMAGE PROCESSING ====================

def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Remove white/light background from cartoon illustrations"""
    img = img.convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    data[:, :, 3] = np.where(white_mask, 0, 255)
    near_white = (r > threshold - 20) & (g > threshold - 20) & (b > threshold - 20) & ~white_mask
    if np.any(near_white):
        luminance = (r.astype(float) + g.astype(float) + b.astype(float)) / 3
        alpha_factor = np.clip((threshold - luminance) / 20, 0, 1)
        data[:, :, 3] = np.where(near_white, (alpha_factor * 255).astype(np.uint8), data[:, :, 3])
    return Image.fromarray(data, 'RGBA')


def add_drop_shadow(img: Image.Image, offset: Tuple[int, int] = (8, 8), 
                    blur: int = 15, opacity: int = 100) -> Image.Image:
    """Add drop shadow to RGBA image"""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_data = np.array(img)
    shadow_layer = np.zeros((*img.size[::-1], 4), dtype=np.uint8)
    shadow_layer[:, :, 3] = (shadow_data[:, :, 3] * (opacity / 255)).astype(np.uint8)
    shadow = Image.fromarray(shadow_layer, 'RGBA')
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    result_w = img.width + abs(offset[0]) + blur
    result_h = img.height + abs(offset[1]) + blur
    result = Image.new('RGBA', (result_w, result_h), (0, 0, 0, 0))
    shadow_pos = (blur // 2 + max(0, offset[0]), blur // 2 + max(0, offset[1]))
    img_pos = (blur // 2 + max(0, -offset[0]), blur // 2 + max(0, -offset[1]))
    result.paste(shadow, shadow_pos, shadow)
    result.paste(img, img_pos, img)
    return result


def load_and_process_image(image_path: str, config: VideoConfig) -> Optional[Image.Image]:
    """Load image, remove background, add shadow, resize"""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        img = Image.open(image_path)
        img = remove_white_background(img, threshold=242)
        aspect = img.width / img.height
        if aspect > config.IMAGE_WIDTH / config.IMAGE_MAX_HEIGHT:
            new_width = config.IMAGE_WIDTH
            new_height = int(new_width / aspect)
        else:
            new_height = config.IMAGE_MAX_HEIGHT
            new_width = int(new_height * aspect)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img = add_drop_shadow(img, offset=(8, 8), blur=12, opacity=80)
        return img
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


# ==================== BACKGROUND ====================

def create_gradient_background(config: VideoConfig) -> Image.Image:
    """Create gradient background"""
    img = Image.new("RGB", (config.WIDTH, config.HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(config.HEIGHT):
        ratio = y / config.HEIGHT
        r = int(config.BG_COLOR[0] * (1 - ratio * 0.3))
        g = int(config.BG_COLOR[1] * (1 - ratio * 0.3))
        b = int(config.BG_COLOR[2] + ratio * 15)
        draw.line([(0, y), (config.WIDTH, y)], fill=(r, g, b))
    return img


# ==================== ANIMATED FRAME GENERATORS ====================

def generate_hook_frames_animated(
    text: str,
    num_frames: int,
    config: VideoConfig = VideoConfig
) -> List[Image.Image]:
    """Generate animated hook frames with typing effect"""
    
    frames = []
    title_font = load_font(config.HOOK_SIZE, bold=True)

    # Prepare a temporary measurement surface
    temp_img = Image.new("RGB", (config.WIDTH, config.HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)

    full_lines = wrap_text(temp_draw, text, title_font, config.WIDTH - 120)
    total_text_height = len(full_lines) * int(config.HOOK_SIZE * 1.4)
    base_y = (config.HEIGHT - total_text_height) // 2

    fade_in_frames = 15
    typing_chars = len(text)

    for frame_idx in range(num_frames):

        canvas = create_gradient_background(config)
        draw = ImageDraw.Draw(canvas, 'RGBA')

        # Fade in logic
        if frame_idx < fade_in_frames:
            opacity = ease_out(frame_idx / fade_in_frames)
        else:
            opacity = 1.0

        accent_alpha = int(120 * opacity)

        # Accent side bars
        draw.rectangle(
            [(40, config.HEIGHT // 2 - 60), (45, config.HEIGHT // 2 + 60)],
            fill=(*config.ACCENT_COLOR, accent_alpha)
        )
        draw.rectangle(
            [(config.WIDTH - 45, config.HEIGHT // 2 - 60),
             (config.WIDTH - 40, config.HEIGHT // 2 + 60)],
            fill=(*config.ACCENT_COLOR, accent_alpha)
        )

        # Typing effect
        if frame_idx >= fade_in_frames:

            typing_frame = frame_idx - fade_in_frames

            # FIX → ensure integer
            chars_shown = int(
                min(typing_frame * config.TYPING_SPEED, typing_chars)
            )

            visible_text = text[:chars_shown]

            if visible_text.strip():

                lines = wrap_text(draw, visible_text, title_font, config.WIDTH - 120)
                y = base_y

                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=title_font)
                    line_width = bbox[2] - bbox[0]
                    x = (config.WIDTH - line_width) // 2
                    draw_text_with_shadow(draw, (x, y), line, title_font, config.TEXT_COLOR)
                    y += int(config.HOOK_SIZE * 1.4)

                # Blinking cursor
                if chars_shown < typing_chars and (frame_idx // 8) % 2 == 0:
                    last_line = lines[-1] if lines else ""
                    bbox = draw.textbbox((0, 0), last_line, font=title_font)
                    cursor_x = (config.WIDTH + bbox[2] - bbox[0]) // 2 + 5
                    cursor_y = y - int(config.HOOK_SIZE * 1.4)

                    draw.rectangle(
                        [(cursor_x, cursor_y), (cursor_x + 3, cursor_y + config.HOOK_SIZE)],
                        fill=config.ACCENT_COLOR
                    )

        frames.append(canvas)

    return frames


def generate_topic_frames_animated(title: str, bullet_points: List[str], image_path: str,
                                    num_frames: int, config: VideoConfig = VideoConfig) -> List[Image.Image]:
    """Generate animated topic frames with staggered bullets and image slide-in"""
    frames = []
    title_font = load_font(config.TITLE_SIZE, bold=True)
    bullet_font = load_font(config.BULLET_SIZE)
    
    topic_img = load_and_process_image(image_path, config)
    
    title_fade = 12
    image_slide = 20
    bullet_delay = config.BULLET_DELAY_FRAMES
    
    for frame_idx in range(num_frames):
        canvas = create_gradient_background(config)
        draw = ImageDraw.Draw(canvas, 'RGBA')
        
        title_opacity = min(frame_idx / title_fade, 1.0)
        title_alpha = int(255 * ease_out(title_opacity))
        
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        x_title = (config.WIDTH - title_width) // 2
        
        draw.text((x_title + 2, config.TOP_MARGIN + 2), title, 
                 fill=(0, 0, 0, int(title_alpha * 0.5)), font=title_font)
        draw.text((x_title, config.TOP_MARGIN), title,
                 fill=(*config.TITLE_COLOR, title_alpha), font=title_font)
        
        underline_width = int(title_width * ease_out(title_opacity))
        draw.rectangle([(x_title, config.TOP_MARGIN + config.TITLE_SIZE + 5),
                       (x_title + underline_width, config.TOP_MARGIN + config.TITLE_SIZE + 8)],
                      fill=(*config.ACCENT_COLOR, title_alpha))
        
        for i, point in enumerate(bullet_points[:4]):
            bullet_start_frame = title_fade + i * bullet_delay
            if frame_idx >= bullet_start_frame:
                bullet_progress = min((frame_idx - bullet_start_frame) / 15, 1.0)
                bullet_opacity = ease_out(bullet_progress)
                bullet_alpha = int(255 * bullet_opacity)
                slide_offset = int(40 * (1 - bullet_opacity))
                
                y = config.BULLET_START_Y + i * config.BULLET_GAP
                x = config.LEFT_MARGIN - slide_offset
                
                wrapped = wrap_text(draw, point, bullet_font, config.get_text_wrap_width())
                draw.text((x, y), "•", fill=(*config.ACCENT_COLOR, bullet_alpha), font=bullet_font)
                for j, line in enumerate(wrapped[:2]):
                    draw.text((x + 25, y + j * 30), line,
                             fill=(*config.BULLET_COLOR, bullet_alpha), font=bullet_font)
        
        if topic_img and frame_idx >= title_fade:
            img_frame = frame_idx - title_fade
            img_progress = min(img_frame / image_slide, 1.0)
            img_progress = ease_out(img_progress)
            
            start_x = config.WIDTH + 20
            end_x = config.IMAGE_X - 10
            current_x = int(start_x + (end_x - start_x) * img_progress)
            img_y = config.IMAGE_Y
            
            if img_progress < 1.0:
                scale = 0.7 + 0.3 * img_progress
                new_size = (int(topic_img.width * scale), int(topic_img.height * scale))
                display_img = topic_img.resize(new_size, Image.Resampling.LANCZOS)
                current_x += int((topic_img.width - new_size[0]) / 2)
                img_y += int((topic_img.height - new_size[1]) / 2)
            else:
                display_img = topic_img
            
            if display_img.mode == 'RGBA':
                canvas.paste(display_img, (current_x, img_y), display_img)
            else:
                canvas.paste(display_img, (current_x, img_y))
        
        frames.append(canvas)
    return frames


def generate_conclusion_frames_animated(text: str, num_frames: int,
                                         config: VideoConfig = VideoConfig) -> List[Image.Image]:
    """Generate animated conclusion frames with fade-in"""
    frames = []
    title_font = load_font(config.HOOK_SIZE - 4, bold=True)
    
    temp_img = Image.new("RGB", (config.WIDTH, config.HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)
    lines = wrap_text(temp_draw, text, title_font, config.WIDTH - 120)
    total_text_height = len(lines) * int(config.HOOK_SIZE * 1.3)
    
    for frame_idx in range(num_frames):
        canvas = create_gradient_background(config)
        draw = ImageDraw.Draw(canvas, 'RGBA')
        
        opacity = ease_out(min(frame_idx / config.FADE_FRAMES, 1.0))
        alpha = int(255 * opacity)
        
        box_padding = 40
        box_top = (config.HEIGHT - total_text_height) // 2 - box_padding
        box_bottom = box_top + total_text_height + box_padding * 2
        
        draw.rounded_rectangle([(80, box_top), (config.WIDTH - 80, box_bottom)],
                               radius=15, outline=(*config.ACCENT_COLOR, int(150 * opacity)), width=3)
        
        y = (config.HEIGHT - total_text_height) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = bbox[2] - bbox[0]
            x = (config.WIDTH - line_width) // 2
            draw.text((x, y), line, fill=(*config.TEXT_COLOR, alpha), font=title_font)
            y += int(config.HOOK_SIZE * 1.3)
        
        frames.append(canvas)
    return frames


# ==================== SUBTITLE RENDERING ====================

def add_animated_subtitle(frame: Image.Image, text: str, anim_frame: int,
                          config: VideoConfig = VideoConfig) -> Image.Image:
    """Add subtitle with fade-in animation"""
    if not text.strip():
        return frame
    
    frame = frame.copy()
    draw = ImageDraw.Draw(frame, 'RGBA')
    sub_font = load_font(config.SUBTITLE_SIZE)
    
    fade_progress = min(anim_frame / 10, 1.0)
    alpha = int(255 * ease_out(fade_progress))
    bg_alpha = int(180 * ease_out(fade_progress))
    
    lines = wrap_text(draw, text, sub_font, config.WIDTH - 100)
    y = config.HEIGHT - (len(lines) * config.SUBTITLE_LINE_HEIGHT) - 35
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=sub_font)
        line_width = bbox[2] - bbox[0]
        x = (config.WIDTH - line_width) // 2
        padding = config.SUBTITLE_PADDING
        draw.rectangle([(x - padding - 5, y - padding),
                       (x + line_width + padding + 5, y + 28 + padding)],
                      fill=(0, 0, 0, bg_alpha))
        draw.text((x, y), line, fill=(*config.SUBTITLE_COLOR, alpha), font=sub_font)
        y += config.SUBTITLE_LINE_HEIGHT
    
    return frame


# ==================== TRANSITIONS ====================

def create_fade_transition(from_frame: Image.Image, to_frame: Image.Image, 
                           num_frames: int) -> List[Image.Image]:
    """Create fade transition between two frames"""
    frames = []
    for i in range(num_frames):
        progress = ease_in_out(i / max(num_frames - 1, 1))
        blended = Image.blend(from_frame.convert('RGBA'), to_frame.convert('RGBA'), progress)
        frames.append(blended.convert('RGB'))
    return frames


# ==================== VIDEO COMPOSITION ====================

@traceable(name="compose_video_node")
def compose_video_node(state) -> dict:
    """Animated video composer with transitions"""
    print("\n🎬 Step 3: Composing Animated Video...")

    script = state['complete_script']
    timestamps = state['audio_timestamps']
    config = VideoConfig

    subs = pysrt.open(state['srt_path'])
    audio = AudioSegment.from_wav(state['audio_path'])

    total_duration_ms = len(audio)
    total_frames = int((total_duration_ms / 1000.0) * config.FPS)

    print(f"📊 Total duration: {total_duration_ms/1000:.1f}s ({total_frames} frames)")

    video_path = "./output/video_with_visuals.mp4"
    os.makedirs(os.path.dirname(video_path), exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, config.FPS, (config.WIDTH, config.HEIGHT))

    if not out.isOpened():
        raise RuntimeError("❌ Could not open VideoWriter")

    frames_written = 0
    last_segment_frame = None
    subtitle_start_times = {}

    for ts_idx, ts in enumerate(timestamps):
        start_frame = int((ts['start_ms'] / 1000.0) * config.FPS)
        end_frame = int((ts['end_ms'] / 1000.0) * config.FPS)
        num_frames = max(1, end_frame - start_frame)

        print(f"📽️ [{ts_idx+1}/{len(timestamps)}] {ts['section']} ({num_frames} frames)")

        # Generate animated frames based on segment type
        if ts['type'] == 'hook':
            segment_frames = generate_hook_frames_animated(ts['text'], num_frames, config)
        
        elif ts['type'] == 'topic':
            topic = next((t for t in script.main_topics if t.topic_number == ts['topic_number']), None)
            if topic:
                topic_id = f"topic_{ts['topic_number']}"
                topic_images = state["image_mapping"].get(topic_id, [])
                visual_idx = sum(1 for t in timestamps[:ts_idx] if t.get('topic_number') == ts['topic_number'])
                image_idx = (visual_idx % len(topic_images)) if topic_images else 0
                image_path = topic_images[image_idx] if topic_images else None
                segment_frames = generate_topic_frames_animated(
                    topic.title, topic.key_points, image_path, num_frames, config
                )
            else:
                segment_frames = generate_hook_frames_animated(ts['text'], num_frames, config)
        
        elif ts['type'] == 'conclusion':
            segment_frames = generate_conclusion_frames_animated(ts['text'], num_frames, config)
        
        else:
            segment_frames = generate_hook_frames_animated(ts['text'], num_frames, config)

        # Add transition from previous segment
        if last_segment_frame is not None and ts_idx > 0:
            prev_type = timestamps[ts_idx - 1]['type']
            if prev_type != ts['type'] or (prev_type == 'topic' and 
                timestamps[ts_idx-1].get('topic_number') != ts.get('topic_number')):
                transition_frames = create_fade_transition(
                    last_segment_frame, segment_frames[0], config.TRANSITION_FRAMES
                )
                for trans_frame in transition_frames:
                    current_time_ms = (frames_written / config.FPS) * 1000
                    active_subtitle, sub_anim = get_active_subtitle(subs, current_time_ms, subtitle_start_times, frames_written)
                    if active_subtitle:
                        trans_frame = add_animated_subtitle(trans_frame, active_subtitle, sub_anim, config)
                    write_frame(out, trans_frame, config)
                    frames_written += 1

        # Write segment frames with subtitles
        for frame in segment_frames:
            current_time_ms = (frames_written / config.FPS) * 1000
            active_subtitle, sub_anim = get_active_subtitle(subs, current_time_ms, subtitle_start_times, frames_written)
            if active_subtitle:
                frame = add_animated_subtitle(frame, active_subtitle, sub_anim, config)
            write_frame(out, frame, config)
            frames_written += 1
            
            if frames_written % 300 == 0:
                print(f"   ✓ {frames_written}/{total_frames} frames")

        last_segment_frame = segment_frames[-1] if segment_frames else None

    # Pad if needed
    while frames_written < total_frames:
        write_frame(out, last_segment_frame, config)
        frames_written += 1

    out.release()
    print(f"✅ Video saved: {video_path}")

    state["video_path"] = video_path
    state["current_step"] = "video_composed"
    state["messages"].append(f"🎬 Video composed ({frames_written} frames)")

    return state


def get_active_subtitle(subs, current_time_ms: float, subtitle_start_times: dict, 
                        frames_written: int) -> Tuple[str, int]:
    """Get active subtitle and its animation frame"""
    for sub in subs:
        if sub.start.ordinal <= current_time_ms < sub.end.ordinal:
            sub_key = f"{sub.start.ordinal}"
            if sub_key not in subtitle_start_times:
                subtitle_start_times[sub_key] = frames_written
            return sub.text, frames_written - subtitle_start_times[sub_key]
    return "", 999


def write_frame(out: cv2.VideoWriter, frame: Image.Image, config: VideoConfig):
    """Convert PIL Image and write to video"""
    frame_np = np.array(frame, dtype=np.uint8)
    if frame_np.shape[-1] == 4:
        bg = np.full_like(frame_np[:, :, :3], config.BG_COLOR)
        alpha = frame_np[:, :, 3:4] / 255.0
        frame_np = (frame_np[:, :, :3] * alpha + bg * (1 - alpha)).astype(np.uint8)
    h, w = frame_np.shape[:2]
    if (w, h) != (config.WIDTH, config.HEIGHT):
        frame_np = cv2.resize(frame_np, (config.WIDTH, config.HEIGHT))
    bgr_frame = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
    out.write(bgr_frame)


@traceable(name="merge_audio_video_node")
def merge_audio_video_node(state) -> dict:
    """Node: Merge audio with video"""
    print("\n🎬 Step 4: Merging Audio & Video...")
    
    output_path = "./output/final_video.mp4"
    
    cmd = [
        "ffmpeg", "-i", state["video_path"], "-i", state["audio_path"],
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", output_path
    ]
    
    print("   ⏳ FFmpeg merging...")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=600)
        print(f"✅ Final video: {output_path}")
        state["video_path"] = output_path
    except subprocess.CalledProcessError as e:
        print(f"⚠️ FFmpeg error: {e.stderr.decode()}")
        raise
    
    state["current_step"] = "complete"
    state["messages"].append(f"✅ Final video: {output_path}")
    
    return state


# ==================== LANGGRAPH WORKFLOW ====================

def create_video_generation_workflow():
    """Create workflow with checkpoint support"""
    workflow = StateGraph(VideoGenerationState)
    
    workflow.add_node("generate_audio", audio_generation_node)
    workflow.add_node("generate_images", image_generation_node)
    workflow.add_node("compose_video", compose_video_node)
    workflow.add_node("merge_media", merge_audio_video_node)
    
    workflow.set_entry_point("generate_audio")
    workflow.add_edge("generate_audio", "generate_images")
    workflow.add_edge("generate_images", "compose_video")
    workflow.add_edge("compose_video", "merge_media")
    workflow.add_edge("merge_media", END)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


@traceable(name="generate_complete_video")
def generate_complete_video(
    script_path: str = "./output/complete_script.json",
    resume_from: Optional[str] = "video_composed"
) -> str:
    """
    Main function to generate video from script
    
    resume_from: "audio_generated", "images_generated", "video_composed", or None
    """
    
    print("🚀 Starting Video Generation Pipeline (Audio-First, Fully Synced)")
    print("=" * 60)
    
    with open(script_path, "r") as f:
        script_dict = json.load(f)
    
    script = CompleteVideoScript(**script_dict)
    
    state = VideoGenerationState(
        complete_script=script,
        audio_path=None,
        srt_path=None,
        audio_timestamps=None,
        images={},
        image_mapping={},
        video_path=None,
        messages=[],
        current_step="initialized"
    )
    
    app = create_video_generation_workflow()
    
    print("\n🎬 Running Workflow...")
    print("=" * 60)
    
    config = {"configurable": {"thread_id": "main"}}
    final_state = app.invoke(state, config=config)
    
    print("\n" + "=" * 60)
    print("✨ Complete!")
    print("=" * 60)
    
    print("\n📊 Summary:")
    for msg in final_state["messages"]:
        print(f"  {msg}")
    
    return final_state["video_path"]


if __name__ == "__main__":
    video_path = generate_complete_video()
    print(f"\n🎉 Final: {video_path}")