# """
# temp.py - Video Experimentation File
# =====================================
# Test and tweak video frames without running the full pipeline.
# Once satisfied, copy the functions to your main.py

# Usage:
#     python temp.py

# Outputs:
#     - test_outputs/hook_frame.png
#     - test_outputs/topic_frame.png
#     - test_outputs/conclusion_frame.png
#     - test_outputs/hook_animated.gif
#     - test_outputs/topic_animated.gif
#     - test_outputs/test_video.mp4 (if enabled)
# """

# import os
# import math
# import numpy as np
# from PIL import Image, ImageDraw, ImageFont, ImageFilter
# from typing import List, Tuple, Optional
# import cv2

# # Create output directory
# os.makedirs("test_outputs", exist_ok=True)

# # ==================== VIDEO CONFIG ====================

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
#     ACCENT_COLOR = (255, 180, 100)
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
#     BULLET_START_Y = 140
#     BULLET_GAP = 85
    
#     # Image positioning (right side)
#     IMAGE_WIDTH = 380
#     IMAGE_MAX_HEIGHT = 400
#     IMAGE_X = 830
#     IMAGE_Y = 170
    
#     # Text area constraints (left side only)
#     TEXT_AREA_WIDTH = 720
#     TEXT_MAX_X = 780
    
#     # Animation settings
#     TYPING_SPEED = 2  # chars per frame
#     BULLET_DELAY_FRAMES = 10  # delay between bullets
#     FADE_FRAMES = 15
    
#     # Subtitle
#     SUBTITLE_Y_OFFSET = 30
#     SUBTITLE_PADDING = 8
#     SUBTITLE_LINE_HEIGHT = 32
    
#     @classmethod
#     def get_text_wrap_width(cls):
#         return cls.TEXT_AREA_WIDTH - cls.LEFT_MARGIN - 40


# # ==================== FONT HELPER ====================

# def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
#     """Load font with fallback - works on Windows and Linux"""
#     font_paths = [
#         # Windows
#         "C:/Windows/Fonts/arial.ttf",
#         "C:/Windows/Fonts/arialbd.ttf",
#         "C:/Windows/Fonts/segoeui.ttf",
#         # Linux
#         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
#         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
#     ]
    
#     for path in font_paths:
#         try:
#             return ImageFont.truetype(path, size)
#         except:
#             continue
    
#     return ImageFont.load_default()


# # ==================== IMAGE PROCESSING ====================

# def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
#     """Remove white/light background from cartoon illustrations"""
#     img = img.convert("RGBA")
#     data = np.array(img)
    
#     r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    
#     # Make white pixels transparent
#     white_mask = (r > threshold) & (g > threshold) & (b > threshold)
#     data[:, :, 3] = np.where(white_mask, 0, 255)
    
#     # Gradual transparency for near-white pixels
#     near_white = (r > threshold - 20) & (g > threshold - 20) & (b > threshold - 20) & ~white_mask
#     if np.any(near_white):
#         luminance = (r.astype(float) + g.astype(float) + b.astype(float)) / 3
#         alpha_factor = np.clip((threshold - luminance) / 20, 0, 1)
#         data[:, :, 3] = np.where(near_white, (alpha_factor * 255).astype(np.uint8), data[:, :, 3])
    
#     return Image.fromarray(data, 'RGBA')


# def add_drop_shadow(img: Image.Image, offset: Tuple[int, int] = (8, 8), 
#                     blur: int = 15, opacity: int = 100) -> Image.Image:
#     """Add drop shadow to RGBA image"""
#     if img.mode != 'RGBA':
#         img = img.convert('RGBA')
    
#     # Create shadow from alpha channel
#     shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
#     shadow_data = np.array(img)
    
#     shadow_layer = np.zeros((*img.size[::-1], 4), dtype=np.uint8)
#     shadow_layer[:, :, 3] = (shadow_data[:, :, 3] * (opacity / 255)).astype(np.uint8)
    
#     shadow = Image.fromarray(shadow_layer, 'RGBA')
#     shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    
#     # Combine with offset
#     result_w = img.width + abs(offset[0]) + blur
#     result_h = img.height + abs(offset[1]) + blur
#     result = Image.new('RGBA', (result_w, result_h), (0, 0, 0, 0))
    
#     shadow_pos = (blur // 2 + max(0, offset[0]), blur // 2 + max(0, offset[1]))
#     img_pos = (blur // 2 + max(0, -offset[0]), blur // 2 + max(0, -offset[1]))
    
#     result.paste(shadow, shadow_pos, shadow)
#     result.paste(img, img_pos, img)
    
#     return result


# def load_and_process_image(image_path: str, config: VideoConfig) -> Optional[Image.Image]:
#     """Load image, remove background, add shadow, resize"""
#     if not image_path or not os.path.exists(image_path):
#         return None
    
#     try:
#         img = Image.open(image_path)
        
#         # Remove white background
#         img = remove_white_background(img, threshold=242)
        
#         # Resize maintaining aspect ratio
#         aspect = img.width / img.height
#         if aspect > config.IMAGE_WIDTH / config.IMAGE_MAX_HEIGHT:
#             new_width = config.IMAGE_WIDTH
#             new_height = int(new_width / aspect)
#         else:
#             new_height = config.IMAGE_MAX_HEIGHT
#             new_width = int(new_height * aspect)
        
#         img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
#         # Add shadow
#         img = add_drop_shadow(img, offset=(8, 8), blur=12, opacity=80)
        
#         return img
#     except Exception as e:
#         print(f"Error processing image: {e}")
#         return None


# # ==================== TEXT HELPERS ====================

# def wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
#               max_width: int) -> List[str]:
#     """Wrap text to fit within max_width"""
#     words = text.split()
#     lines = []
#     current = []
    
#     for word in words:
#         test = " ".join(current + [word])
#         bbox = draw.textbbox((0, 0), test, font=font)
#         if bbox[2] - bbox[0] <= max_width:
#             current.append(word)
#         else:
#             if current:
#                 lines.append(" ".join(current))
#             current = [word]
#     if current:
#         lines.append(" ".join(current))
    
#     return lines


# def draw_text_with_shadow(draw: ImageDraw.Draw, pos: Tuple[int, int], text: str,
#                           font: ImageFont.FreeTypeFont, fill: Tuple,
#                           shadow_offset: Tuple[int, int] = (2, 2)):
#     """Draw text with drop shadow"""
#     # Shadow
#     draw.text((pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]), 
#               text, fill=(0, 0, 0, 150), font=font)
#     # Main text
#     draw.text(pos, text, fill=fill, font=font)


# # ==================== EASING FUNCTIONS ====================

# def ease_out(t: float) -> float:
#     """Ease out quad - fast start, slow end"""
#     return 1 - (1 - t) ** 2


# def ease_in_out(t: float) -> float:
#     """Ease in-out - smooth start and end"""
#     return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


# # ==================== BACKGROUND ====================

# def create_gradient_background(config: VideoConfig) -> Image.Image:
#     """Create gradient background"""
#     img = Image.new("RGB", (config.WIDTH, config.HEIGHT))
#     draw = ImageDraw.Draw(img)
    
#     for y in range(config.HEIGHT):
#         ratio = y / config.HEIGHT
#         r = int(config.BG_COLOR[0] * (1 - ratio * 0.3))
#         g = int(config.BG_COLOR[1] * (1 - ratio * 0.3))
#         b = int(config.BG_COLOR[2] + ratio * 15)
#         draw.line([(0, y), (config.WIDTH, y)], fill=(r, g, b))
    
#     return img


# # ==================== STATIC FRAME GENERATORS ====================

# def create_text_image(text: str, config: VideoConfig = VideoConfig,
#                       font_size: Optional[int] = None) -> Image.Image:
#     """Create image with centered text (STATIC - no animation)"""
#     img = create_gradient_background(config)
#     draw = ImageDraw.Draw(img)
    
#     font_size = font_size or config.HOOK_SIZE
#     font = load_font(font_size, bold=True)
    
#     lines = wrap_text(draw, text, font, config.WIDTH - 120)
    
#     total_height = len(lines) * int(font_size * 1.4)
#     y = (config.HEIGHT - total_height) // 2
    
#     for line in lines:
#         bbox = draw.textbbox((0, 0), line, font=font)
#         line_width = bbox[2] - bbox[0]
#         x = (config.WIDTH - line_width) // 2
#         draw_text_with_shadow(draw, (x, y), line, font, config.TEXT_COLOR)
#         y += int(font_size * 1.4)
    
#     return img


# def create_topic_frame(topic_title: str, bullet_points: List[str], image_path: str,
#                        config: VideoConfig = VideoConfig) -> Image.Image:
#     """Create topic frame: title top, bullets left, image right (STATIC)"""
#     canvas = create_gradient_background(config)
#     draw = ImageDraw.Draw(canvas, 'RGBA')
    
#     title_font = load_font(config.TITLE_SIZE, bold=True)
#     bullet_font = load_font(config.BULLET_SIZE)
    
#     # Title centered at top
#     bbox = draw.textbbox((0, 0), topic_title, font=title_font)
#     title_width = bbox[2] - bbox[0]
#     x_title = (config.WIDTH - title_width) // 2
#     draw_text_with_shadow(draw, (x_title, config.TOP_MARGIN), topic_title, 
#                           title_font, config.TITLE_COLOR)
    
#     # Accent underline
#     draw.rectangle(
#         [(x_title, config.TOP_MARGIN + config.TITLE_SIZE + 5),
#          (x_title + title_width, config.TOP_MARGIN + config.TITLE_SIZE + 8)],
#         fill=config.ACCENT_COLOR
#     )
    
#     # Bullets on left
#     y = config.BULLET_START_Y
#     for i, point in enumerate(bullet_points[:4]):
#         wrapped = wrap_text(draw, point, bullet_font, config.get_text_wrap_width())
        
#         # Bullet marker
#         draw.text((config.LEFT_MARGIN, y), "•", fill=config.ACCENT_COLOR, font=bullet_font)
        
#         # Bullet text (wrapped)
#         for j, line in enumerate(wrapped[:2]):
#             draw.text((config.LEFT_MARGIN + 25, y + j * 30), line, 
#                      fill=config.BULLET_COLOR, font=bullet_font)
        
#         y += config.BULLET_GAP
    
#     # Image on right
#     topic_img = load_and_process_image(image_path, config)
#     if topic_img:
#         # Center image in right area
#         img_x = config.IMAGE_X - 10
#         img_y = config.IMAGE_Y
        
#         if topic_img.mode == 'RGBA':
#             canvas.paste(topic_img, (img_x, img_y), topic_img)
#         else:
#             canvas.paste(topic_img, (img_x, img_y))
    
#     return canvas


# def add_subtitles_to_frame(frame: Image.Image, subtitle_text: str,
#                            config: VideoConfig = VideoConfig) -> Image.Image:
#     """Add subtitle at bottom center"""
#     if not subtitle_text.strip():
#         return frame
    
#     frame = frame.copy()
#     draw = ImageDraw.Draw(frame, 'RGBA')
#     sub_font = load_font(config.SUBTITLE_SIZE)
    
#     lines = wrap_text(draw, subtitle_text, sub_font, config.WIDTH - 100)
    
#     y = config.HEIGHT - (len(lines) * config.SUBTITLE_LINE_HEIGHT) - 35
    
#     for line in lines:
#         bbox = draw.textbbox((0, 0), line, font=sub_font)
#         line_width = bbox[2] - bbox[0]
#         x = (config.WIDTH - line_width) // 2
        
#         # Background box with rounded corners feel
#         padding = config.SUBTITLE_PADDING
#         draw.rectangle(
#             [(x - padding - 5, y - padding),
#              (x + line_width + padding + 5, y + 28 + padding)],
#             fill=(0, 0, 0, 180)
#         )
#         draw.text((x, y), line, fill=config.SUBTITLE_COLOR, font=sub_font)
#         y += config.SUBTITLE_LINE_HEIGHT
    
#     return frame


# # ==================== ANIMATED FRAME GENERATORS ====================

# def generate_hook_frames_animated(text: str, num_frames: int,
#                                    config: VideoConfig = VideoConfig) -> List[Image.Image]:
#     """Generate animated hook frames with typing effect"""
#     frames = []
#     title_font = load_font(config.HOOK_SIZE, bold=True)
    
#     # Pre-calculate for consistent positioning
#     temp_img = Image.new("RGB", (config.WIDTH, config.HEIGHT))
#     temp_draw = ImageDraw.Draw(temp_img)
#     full_lines = wrap_text(temp_draw, text, title_font, config.WIDTH - 120)
#     total_text_height = len(full_lines) * int(config.HOOK_SIZE * 1.4)
#     base_y = (config.HEIGHT - total_text_height) // 2
    
#     # Animation phases
#     fade_in_frames = 15
#     typing_chars = len(text)
    
#     for frame_idx in range(num_frames):
#         canvas = create_gradient_background(config)
#         draw = ImageDraw.Draw(canvas, 'RGBA')
        
#         # Fade in decorative elements
#         if frame_idx < fade_in_frames:
#             opacity = ease_out(frame_idx / fade_in_frames)
#         else:
#             opacity = 1.0
        
#         accent_alpha = int(120 * opacity)
        
#         # Side accent bars
#         draw.rectangle(
#             [(40, config.HEIGHT // 2 - 60), (45, config.HEIGHT // 2 + 60)],
#             fill=(*config.ACCENT_COLOR, accent_alpha)
#         )
#         draw.rectangle(
#             [(config.WIDTH - 45, config.HEIGHT // 2 - 60),
#              (config.WIDTH - 40, config.HEIGHT // 2 + 60)],
#             fill=(*config.ACCENT_COLOR, accent_alpha)
#         )
        
#         # Typing animation
#         if frame_idx >= fade_in_frames:
#             typing_frame = frame_idx - fade_in_frames
#             chars_shown = min(typing_frame * config.TYPING_SPEED, typing_chars)
#             visible_text = text[:chars_shown]
            
#             if visible_text.strip():
#                 lines = wrap_text(draw, visible_text, title_font, config.WIDTH - 120)
#                 y = base_y
                
#                 for line in lines:
#                     bbox = draw.textbbox((0, 0), line, font=title_font)
#                     line_width = bbox[2] - bbox[0]
#                     x = (config.WIDTH - line_width) // 2
#                     draw_text_with_shadow(draw, (x, y), line, title_font, config.TEXT_COLOR)
#                     y += int(config.HOOK_SIZE * 1.4)
                
#                 # Blinking cursor
#                 if chars_shown < typing_chars and (frame_idx // 8) % 2 == 0:
#                     last_line = lines[-1] if lines else ""
#                     bbox = draw.textbbox((0, 0), last_line, font=title_font)
#                     cursor_x = (config.WIDTH + bbox[2] - bbox[0]) // 2 + 5
#                     cursor_y = y - int(config.HOOK_SIZE * 1.4)
#                     draw.rectangle(
#                         [(cursor_x, cursor_y), (cursor_x + 3, cursor_y + config.HOOK_SIZE)],
#                         fill=config.ACCENT_COLOR
#                     )
        
#         frames.append(canvas)
    
#     return frames


# def generate_topic_frames_animated(title: str, bullet_points: List[str], image_path: str,
#                                     num_frames: int, config: VideoConfig = VideoConfig) -> List[Image.Image]:
#     """Generate animated topic frames with staggered bullets and image slide-in"""
#     frames = []
    
#     title_font = load_font(config.TITLE_SIZE, bold=True)
#     bullet_font = load_font(config.BULLET_SIZE)
    
#     # Load and process image once
#     topic_img = load_and_process_image(image_path, config)
    
#     # Animation timing
#     title_fade = 12
#     image_slide = 20
#     bullet_delay = config.BULLET_DELAY_FRAMES
    
#     for frame_idx in range(num_frames):
#         canvas = create_gradient_background(config)
#         draw = ImageDraw.Draw(canvas, 'RGBA')
        
#         # ===== TITLE with fade =====
#         title_opacity = min(frame_idx / title_fade, 1.0)
#         title_alpha = int(255 * ease_out(title_opacity))
        
#         bbox = draw.textbbox((0, 0), title, font=title_font)
#         title_width = bbox[2] - bbox[0]
#         x_title = (config.WIDTH - title_width) // 2
        
#         # Title
#         draw.text((x_title + 2, config.TOP_MARGIN + 2), title, 
#                  fill=(0, 0, 0, int(title_alpha * 0.5)), font=title_font)
#         draw.text((x_title, config.TOP_MARGIN), title,
#                  fill=(*config.TITLE_COLOR, title_alpha), font=title_font)
        
#         # Underline animation
#         underline_width = int(title_width * ease_out(title_opacity))
#         draw.rectangle(
#             [(x_title, config.TOP_MARGIN + config.TITLE_SIZE + 5),
#              (x_title + underline_width, config.TOP_MARGIN + config.TITLE_SIZE + 8)],
#             fill=(*config.ACCENT_COLOR, title_alpha)
#         )
        
#         # ===== BULLETS with stagger =====
#         for i, point in enumerate(bullet_points[:4]):
#             bullet_start_frame = title_fade + i * bullet_delay
            
#             if frame_idx >= bullet_start_frame:
#                 bullet_progress = min((frame_idx - bullet_start_frame) / 15, 1.0)
#                 bullet_opacity = ease_out(bullet_progress)
#                 bullet_alpha = int(255 * bullet_opacity)
                
#                 # Slide in from left
#                 slide_offset = int(40 * (1 - bullet_opacity))
                
#                 y = config.BULLET_START_Y + i * config.BULLET_GAP
#                 x = config.LEFT_MARGIN - slide_offset
                
#                 wrapped = wrap_text(draw, point, bullet_font, config.get_text_wrap_width())
                
#                 # Bullet marker
#                 draw.text((x, y), "•", fill=(*config.ACCENT_COLOR, bullet_alpha), font=bullet_font)
                
#                 # Text
#                 for j, line in enumerate(wrapped[:2]):
#                     draw.text((x + 25, y + j * 30), line,
#                              fill=(*config.BULLET_COLOR, bullet_alpha), font=bullet_font)
        
#         # ===== IMAGE with slide-in =====
#         if topic_img and frame_idx >= title_fade:
#             img_frame = frame_idx - title_fade
#             img_progress = min(img_frame / image_slide, 1.0)
#             img_progress = ease_out(img_progress)
            
#             # Slide from right
#             start_x = config.WIDTH + 20
#             end_x = config.IMAGE_X - 10
#             current_x = int(start_x + (end_x - start_x) * img_progress)
            
#             img_y = config.IMAGE_Y
            
#             # Scale effect during slide
#             if img_progress < 1.0:
#                 scale = 0.7 + 0.3 * img_progress
#                 new_size = (int(topic_img.width * scale), int(topic_img.height * scale))
#                 display_img = topic_img.resize(new_size, Image.Resampling.LANCZOS)
#                 # Adjust position for smaller image
#                 current_x += int((topic_img.width - new_size[0]) / 2)
#                 img_y += int((topic_img.height - new_size[1]) / 2)
#             else:
#                 display_img = topic_img
            
#             if display_img.mode == 'RGBA':
#                 canvas.paste(display_img, (current_x, img_y), display_img)
#             else:
#                 canvas.paste(display_img, (current_x, img_y))
        
#         frames.append(canvas)
    
#     return frames


# # ==================== TEST FUNCTIONS ====================

# def test_static_frames():
#     """Test static frame generation"""
#     print("📸 Generating static frames...")
#     config = VideoConfig
    
#     # Test hook
#     hook = create_text_image("Welcome to Our Amazing Video!", config)
#     hook.save("test_outputs/hook_frame.png")
#     print("   ✓ hook_frame.png")
    
#     # Test topic (with or without image)
#     test_image = "test_image.png"  # Change to your test image path
#     topic = create_topic_frame(
#         "Understanding Machine Learning",
#         [
#             "Neural networks mimic brain structure",
#             "Training requires large datasets for accuracy",
#             "Applications in healthcare and finance",
#             "Deep learning enables complex pattern recognition"
#         ],
#         test_image,
#         config
#     )
#     topic.save("test_outputs/topic_frame.png")
#     print("   ✓ topic_frame.png")
    
#     # Test conclusion
#     conclusion = create_text_image("Thanks for Watching!", config, font_size=44)
#     conclusion.save("test_outputs/conclusion_frame.png")
#     print("   ✓ conclusion_frame.png")
    
#     # Test with subtitle
#     with_sub = add_subtitles_to_frame(topic, "This is a sample subtitle text for testing purposes")
#     with_sub.save("test_outputs/topic_with_subtitle.png")
#     print("   ✓ topic_with_subtitle.png")


# def test_animated_frames():
#     """Test animated frame generation and save as GIF"""
#     print("\n🎬 Generating animated frames...")
#     config = VideoConfig
    
#     # Animated hook
#     hook_frames = generate_hook_frames_animated(
#         "Welcome to Our Amazing Video!",
#         num_frames=90,  # 3 seconds
#         config=config
#     )
#     hook_frames[0].save(
#         "test_outputs/hook_animated.gif",
#         save_all=True,
#         append_images=hook_frames[1:],
#         duration=33,
#         loop=0
#     )
#     print(f"   ✓ hook_animated.gif ({len(hook_frames)} frames)")
    
#     # Animated topic
#     test_image = "test_image.png"  # Change to your test image path
#     topic_frames = generate_topic_frames_animated(
#         "Understanding Machine Learning",
#         [
#             "Neural networks mimic brain structure",
#             "Training requires large datasets",
#             "Applications in healthcare and finance",
#             "Enables complex pattern recognition"
#         ],
#         test_image,
#         num_frames=120,  # 4 seconds
#         config=config
#     )
#     topic_frames[0].save(
#         "test_outputs/topic_animated.gif",
#         save_all=True,
#         append_images=topic_frames[1:],
#         duration=33,
#         loop=0
#     )
#     print(f"   ✓ topic_animated.gif ({len(topic_frames)} frames)")


# def test_video_output():
#     """Generate a test MP4 video"""
#     print("\n🎥 Generating test video...")
#     config = VideoConfig
    
#     video_path = "test_outputs/test_video.mp4"
#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     out = cv2.VideoWriter(video_path, fourcc, config.FPS, (config.WIDTH, config.HEIGHT))
    
#     if not out.isOpened():
#         print("   ✗ Could not open video writer")
#         return
    
#     # Hook section (3 seconds)
#     print("   Writing hook...")
#     hook_frames = generate_hook_frames_animated("Welcome to the Test Video!", 90, config)
#     for frame in hook_frames:
#         frame_np = np.array(frame)
#         bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
#         out.write(bgr)
    
#     # Topic section (4 seconds)
#     print("   Writing topic...")
#     topic_frames = generate_topic_frames_animated(
#         "Key Points Overview",
#         ["First important point", "Second key insight", "Third takeaway"],
#         "test_image.png",
#         120, config
#     )
#     for frame in topic_frames:
#         frame_np = np.array(frame)
#         bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
#         out.write(bgr)
    
#     # Conclusion (2 seconds)
#     print("   Writing conclusion...")
#     conclusion = create_text_image("Thanks for Watching!", config, 44)
#     for _ in range(60):
#         frame_np = np.array(conclusion)
#         bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
#         out.write(bgr)
    
#     out.release()
#     print(f"   ✓ test_video.mp4 saved")


# def test_image_processing():
#     """Test background removal on an image"""
#     print("\n🖼️ Testing image processing...")
    
#     test_path = "./output/images/topic_1_visual_1.png"  # Change to your test image
    
#     if not os.path.exists(test_path):
#         print(f"   ⚠ Test image not found: {test_path}")
#         print("   Create a test image or change the path")
#         return
    
#     img = Image.open(test_path)
#     print(f"   Original: {img.mode}, {img.size}")
    
#     # Remove background
#     no_bg = remove_white_background(img)
#     no_bg.save("test_outputs/no_background.png")
#     print("   ✓ no_background.png")
    
#     # Add shadow
#     with_shadow = add_drop_shadow(no_bg)
#     with_shadow.save("test_outputs/with_shadow.png")
#     print("   ✓ with_shadow.png")
    
#     # Full processing
#     processed = load_and_process_image(test_path, VideoConfig)
#     if processed:
#         processed.save("test_outputs/fully_processed.png")
#         print("   ✓ fully_processed.png")


# # ==================== MAIN ====================

# if __name__ == "__main__":
#     print("=" * 50)
#     print("🎬 Video Frame Experimentation")
#     print("=" * 50)
    
#     # Run tests
#     test_static_frames()
#     test_animated_frames()
    
#     # Uncomment to test video output
#     test_video_output()
    
#     # Uncomment to test image processing (needs test_image.png)
#     test_image_processing()
    
#     print("\n" + "=" * 50)
#     print("✅ Done! Check 'test_outputs/' folder")
#     print("=" * 50)


"""
temp.py - Video Experimentation File
=====================================
Test and tweak video frames without running the full pipeline.
Once satisfied, copy the functions to your main.py

Usage:
    python temp.py

Outputs:
    - test_outputs/hook_frame.png
    - test_outputs/topic_frame.png
    - test_outputs/conclusion_frame.png
    - test_outputs/hook_animated.gif
    - test_outputs/topic_animated.gif
    - test_outputs/test_video.mp4 (if enabled)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Tuple, Optional
import cv2

# Create output directory
os.makedirs("test_outputs", exist_ok=True)

# ==================== VIDEO CONFIG ====================

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
    IMAGE_MAX_HEIGHT = 400
    IMAGE_X = 830
    IMAGE_Y = 170
    
    # Text area constraints (left side only)
    TEXT_AREA_WIDTH = 720
    TEXT_MAX_X = 780
    
    # Animation settings
    TYPING_SPEED = 0.5  # chars per frame
    BULLET_DELAY_FRAMES = 10  # delay between bullets
    FADE_FRAMES = 15
    
    # Subtitle
    SUBTITLE_Y_OFFSET = 30
    SUBTITLE_PADDING = 8
    SUBTITLE_LINE_HEIGHT = 32
    
    @classmethod
    def get_text_wrap_width(cls):
        return cls.TEXT_AREA_WIDTH - cls.LEFT_MARGIN - 40


# ==================== FONT HELPER ====================

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load font with fallback - works on Windows and Linux"""
    font_paths = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    
    return ImageFont.load_default()


# ==================== IMAGE PROCESSING ====================

def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Remove white/light background from cartoon illustrations"""
    img = img.convert("RGBA")
    data = np.array(img)
    
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    
    # Make white pixels transparent
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    data[:, :, 3] = np.where(white_mask, 0, 255)
    
    # Gradual transparency for near-white pixels
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
    
    # Create shadow from alpha channel
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_data = np.array(img)
    
    shadow_layer = np.zeros((*img.size[::-1], 4), dtype=np.uint8)
    shadow_layer[:, :, 3] = (shadow_data[:, :, 3] * (opacity / 255)).astype(np.uint8)
    
    shadow = Image.fromarray(shadow_layer, 'RGBA')
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    
    # Combine with offset
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
        
        # Remove white background
        img = remove_white_background(img, threshold=242)
        
        # Resize maintaining aspect ratio
        aspect = img.width / img.height
        if aspect > config.IMAGE_WIDTH / config.IMAGE_MAX_HEIGHT:
            new_width = config.IMAGE_WIDTH
            new_height = int(new_width / aspect)
        else:
            new_height = config.IMAGE_MAX_HEIGHT
            new_width = int(new_height * aspect)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Add shadow
        img = add_drop_shadow(img, offset=(8, 8), blur=12, opacity=80)
        
        return img
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


# ==================== TEXT HELPERS ====================

def wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
              max_width: int) -> List[str]:
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current = []
    
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
    # Shadow
    draw.text((pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]), 
              text, fill=(0, 0, 0, 150), font=font)
    # Main text
    draw.text(pos, text, fill=fill, font=font)


# ==================== EASING FUNCTIONS ====================

def ease_out(t: float) -> float:
    """Ease out quad - fast start, slow end"""
    return 1 - (1 - t) ** 2


def ease_in_out(t: float) -> float:
    """Ease in-out - smooth start and end"""
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


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


# ==================== STATIC FRAME GENERATORS ====================

def create_text_image(text: str, config: VideoConfig = VideoConfig,
                      font_size: Optional[int] = None) -> Image.Image:
    """Create image with centered text (STATIC - no animation)"""
    img = create_gradient_background(config)
    draw = ImageDraw.Draw(img)
    
    font_size = font_size or config.HOOK_SIZE
    font = load_font(font_size, bold=True)
    
    lines = wrap_text(draw, text, font, config.WIDTH - 120)
    
    total_height = len(lines) * int(font_size * 1.4)
    y = (config.HEIGHT - total_height) // 2
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (config.WIDTH - line_width) // 2
        draw_text_with_shadow(draw, (x, y), line, font, config.TEXT_COLOR)
        y += int(font_size * 1.4)
    
    return img


def create_topic_frame(topic_title: str, bullet_points: List[str], image_path: str,
                       config: VideoConfig = VideoConfig) -> Image.Image:
    """Create topic frame: title top, bullets left, image right (STATIC)"""
    canvas = create_gradient_background(config)
    draw = ImageDraw.Draw(canvas, 'RGBA')
    
    title_font = load_font(config.TITLE_SIZE, bold=True)
    bullet_font = load_font(config.BULLET_SIZE)
    
    # Title centered at top
    bbox = draw.textbbox((0, 0), topic_title, font=title_font)
    title_width = bbox[2] - bbox[0]
    x_title = (config.WIDTH - title_width) // 2
    draw_text_with_shadow(draw, (x_title, config.TOP_MARGIN), topic_title, 
                          title_font, config.TITLE_COLOR)
    
    # Accent underline
    draw.rectangle(
        [(x_title, config.TOP_MARGIN + config.TITLE_SIZE + 5),
         (x_title + title_width, config.TOP_MARGIN + config.TITLE_SIZE + 8)],
        fill=config.ACCENT_COLOR
    )
    
    # Bullets on left
    y = config.BULLET_START_Y
    for i, point in enumerate(bullet_points[:4]):
        wrapped = wrap_text(draw, point, bullet_font, config.get_text_wrap_width())
        
        # Bullet marker
        draw.text((config.LEFT_MARGIN, y), "•", fill=config.ACCENT_COLOR, font=bullet_font)
        
        # Bullet text (wrapped)
        for j, line in enumerate(wrapped[:2]):
            draw.text((config.LEFT_MARGIN + 25, y + j * 30), line, 
                     fill=config.BULLET_COLOR, font=bullet_font)
        
        y += config.BULLET_GAP
    
    # Image on right
    topic_img = load_and_process_image(image_path, config)
    if topic_img:
        # Center image in right area
        img_x = config.IMAGE_X - 10
        img_y = config.IMAGE_Y
        
        if topic_img.mode == 'RGBA':
            canvas.paste(topic_img, (img_x, img_y), topic_img)
        else:
            canvas.paste(topic_img, (img_x, img_y))
    
    return canvas


def add_subtitles_to_frame(frame: Image.Image, subtitle_text: str,
                           config: VideoConfig = VideoConfig) -> Image.Image:
    """Add subtitle at bottom center"""
    if not subtitle_text.strip():
        return frame
    
    frame = frame.copy()
    draw = ImageDraw.Draw(frame, 'RGBA')
    sub_font = load_font(config.SUBTITLE_SIZE)
    
    lines = wrap_text(draw, subtitle_text, sub_font, config.WIDTH - 100)
    
    y = config.HEIGHT - (len(lines) * config.SUBTITLE_LINE_HEIGHT) - 35
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=sub_font)
        line_width = bbox[2] - bbox[0]
        x = (config.WIDTH - line_width) // 2
        
        # Background box with rounded corners feel
        padding = config.SUBTITLE_PADDING
        draw.rectangle(
            [(x - padding - 5, y - padding),
             (x + line_width + padding + 5, y + 28 + padding)],
            fill=(0, 0, 0, 180)
        )
        draw.text((x, y), line, fill=config.SUBTITLE_COLOR, font=sub_font)
        y += config.SUBTITLE_LINE_HEIGHT
    
    return frame


# ==================== ANIMATED FRAME GENERATORS ====================

def generate_hook_frames_animated(text: str, num_frames: int,
                                   config: VideoConfig = VideoConfig) -> List[Image.Image]:
    """Generate animated hook frames with typing effect"""
    frames = []
    title_font = load_font(config.HOOK_SIZE, bold=True)
    
    # Pre-calculate for consistent positioning
    temp_img = Image.new("RGB", (config.WIDTH, config.HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)
    full_lines = wrap_text(temp_draw, text, title_font, config.WIDTH - 120)
    total_text_height = len(full_lines) * int(config.HOOK_SIZE * 1.4)
    base_y = (config.HEIGHT - total_text_height) // 2
    
    # Animation phases
    fade_in_frames = 15
    typing_chars = len(text)
    
    for frame_idx in range(num_frames):
        canvas = create_gradient_background(config)
        draw = ImageDraw.Draw(canvas, 'RGBA')
        
        # Fade in decorative elements
        if frame_idx < fade_in_frames:
            opacity = ease_out(frame_idx / fade_in_frames)
        else:
            opacity = 1.0
        
        accent_alpha = int(120 * opacity)
        
        # Side accent bars
        draw.rectangle(
            [(40, config.HEIGHT // 2 - 60), (45, config.HEIGHT // 2 + 60)],
            fill=(*config.ACCENT_COLOR, accent_alpha)
        )
        draw.rectangle(
            [(config.WIDTH - 45, config.HEIGHT // 2 - 60),
             (config.WIDTH - 40, config.HEIGHT // 2 + 60)],
            fill=(*config.ACCENT_COLOR, accent_alpha)
        )
        
        # Typing animation
        if frame_idx >= fade_in_frames:
            typing_frame = frame_idx - fade_in_frames
            chars_shown = min(typing_frame * config.TYPING_SPEED, typing_chars)
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
    
    # Load and process image once
    topic_img = load_and_process_image(image_path, config)
    
    # Animation timing
    title_fade = 12
    image_slide = 20
    bullet_delay = config.BULLET_DELAY_FRAMES
    
    for frame_idx in range(num_frames):
        canvas = create_gradient_background(config)
        draw = ImageDraw.Draw(canvas, 'RGBA')
        
        # ===== TITLE with fade =====
        title_opacity = min(frame_idx / title_fade, 1.0)
        title_alpha = int(255 * ease_out(title_opacity))
        
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        x_title = (config.WIDTH - title_width) // 2
        
        # Title
        draw.text((x_title + 2, config.TOP_MARGIN + 2), title, 
                 fill=(0, 0, 0, int(title_alpha * 0.5)), font=title_font)
        draw.text((x_title, config.TOP_MARGIN), title,
                 fill=(*config.TITLE_COLOR, title_alpha), font=title_font)
        
        # Underline animation
        underline_width = int(title_width * ease_out(title_opacity))
        draw.rectangle(
            [(x_title, config.TOP_MARGIN + config.TITLE_SIZE + 5),
             (x_title + underline_width, config.TOP_MARGIN + config.TITLE_SIZE + 8)],
            fill=(*config.ACCENT_COLOR, title_alpha)
        )
        
        # ===== BULLETS with stagger =====
        for i, point in enumerate(bullet_points[:4]):
            bullet_start_frame = title_fade + i * bullet_delay
            
            if frame_idx >= bullet_start_frame:
                bullet_progress = min((frame_idx - bullet_start_frame) / 15, 1.0)
                bullet_opacity = ease_out(bullet_progress)
                bullet_alpha = int(255 * bullet_opacity)
                
                # Slide in from left
                slide_offset = int(40 * (1 - bullet_opacity))
                
                y = config.BULLET_START_Y + i * config.BULLET_GAP
                x = config.LEFT_MARGIN - slide_offset
                
                wrapped = wrap_text(draw, point, bullet_font, config.get_text_wrap_width())
                
                # Bullet marker
                draw.text((x, y), "•", fill=(*config.ACCENT_COLOR, bullet_alpha), font=bullet_font)
                
                # Text
                for j, line in enumerate(wrapped[:2]):
                    draw.text((x + 25, y + j * 30), line,
                             fill=(*config.BULLET_COLOR, bullet_alpha), font=bullet_font)
        
        # ===== IMAGE with slide-in =====
        if topic_img and frame_idx >= title_fade:
            img_frame = frame_idx - title_fade
            img_progress = min(img_frame / image_slide, 1.0)
            img_progress = ease_out(img_progress)
            
            # Slide from right
            start_x = config.WIDTH + 20
            end_x = config.IMAGE_X - 10
            current_x = int(start_x + (end_x - start_x) * img_progress)
            
            img_y = config.IMAGE_Y
            
            # Scale effect during slide
            if img_progress < 1.0:
                scale = 0.7 + 0.3 * img_progress
                new_size = (int(topic_img.width * scale), int(topic_img.height * scale))
                display_img = topic_img.resize(new_size, Image.Resampling.LANCZOS)
                # Adjust position for smaller image
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


# ==================== TEST FUNCTIONS ====================

def test_static_frames():
    """Test static frame generation"""
    print("📸 Generating static frames...")
    config = VideoConfig
    
    # Test hook
    hook = create_text_image("Welcome to Our Amazing Video!", config)
    hook.save("test_outputs/hook_frame.png")
    print("   ✓ hook_frame.png")
    
    # Test topic (with or without image)
    test_image = "test_image.png"  # Change to your test image path
    topic = create_topic_frame(
        "Understanding Machine Learning",
        [
            "Neural networks mimic brain structure",
            "Training requires large datasets for accuracy",
            "Applications in healthcare and finance",
            "Deep learning enables complex pattern recognition"
        ],
        test_image,
        config
    )
    topic.save("test_outputs/topic_frame.png")
    print("   ✓ topic_frame.png")
    
    # Test conclusion
    conclusion = create_text_image("Thanks for Watching!", config, font_size=44)
    conclusion.save("test_outputs/conclusion_frame.png")
    print("   ✓ conclusion_frame.png")
    
    # Test with subtitle
    with_sub = add_subtitles_to_frame(topic, "This is a sample subtitle text for testing purposes")
    with_sub.save("test_outputs/topic_with_subtitle.png")
    print("   ✓ topic_with_subtitle.png")


def test_animated_frames():
    """Test animated frame generation and save as GIF"""
    print("\n🎬 Generating animated frames...")
    config = VideoConfig
    
    # Animated hook
    hook_frames = generate_hook_frames_animated(
        "Welcome to Our Amazing Video!",
        num_frames=90,  # 3 seconds
        config=config
    )
    hook_frames[0].save(
        "test_outputs/hook_animated.gif",
        save_all=True,
        append_images=hook_frames[1:],
        duration=33,
        loop=0
    )
    print(f"   ✓ hook_animated.gif ({len(hook_frames)} frames)")
    
    # Animated topic
    test_image = "test_image.png"  # Change to your test image path
    topic_frames = generate_topic_frames_animated(
        "Understanding Machine Learning",
        [
            "Neural networks mimic brain structure",
            "Training requires large datasets",
            "Applications in healthcare and finance",
            "Enables complex pattern recognition"
        ],
        test_image,
        num_frames=120,  # 4 seconds
        config=config
    )
    topic_frames[0].save(
        "test_outputs/topic_animated.gif",
        save_all=True,
        append_images=topic_frames[1:],
        duration=33,
        loop=0
    )
    print(f"   ✓ topic_animated.gif ({len(topic_frames)} frames)")


def test_video_output():
    """Generate a test MP4 video"""
    print("\n🎥 Generating test video...")
    config = VideoConfig
    
    video_path = "test_outputs/test_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, config.FPS, (config.WIDTH, config.HEIGHT))
    
    if not out.isOpened():
        print("   ✗ Could not open video writer")
        return
    
    # Hook section (3 seconds)
    print("   Writing hook...")
    hook_frames = generate_hook_frames_animated("Welcome to the Test Video!", 90, config)
    for frame in hook_frames:
        frame_np = np.array(frame)
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
    
    # Topic section (4 seconds)
    print("   Writing topic...")
    topic_frames = generate_topic_frames_animated(
        "Key Points Overview",
        ["First important point", "Second key insight", "Third takeaway"],
        "test_image.png",
        120, config
    )
    for frame in topic_frames:
        frame_np = np.array(frame)
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
    
    # Conclusion (2 seconds)
    print("   Writing conclusion...")
    conclusion = create_text_image("Thanks for Watching!", config, 44)
    for _ in range(60):
        frame_np = np.array(conclusion)
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
    
    out.release()
    print(f"   ✓ test_video.mp4 saved")


def test_image_processing():
    """Test background removal on an image"""
    print("\n🖼️ Testing image processing...")
    
    test_path = "test_image.png"  # Change to your test image
    
    if not os.path.exists(test_path):
        print(f"   ⚠ Test image not found: {test_path}")
        print("   Create a test image or change the path")
        return
    
    img = Image.open(test_path)
    print(f"   Original: {img.mode}, {img.size}")
    
    # Remove background
    no_bg = remove_white_background(img)
    no_bg.save("test_outputs/no_background.png")
    print("   ✓ no_background.png")
    
    # Add shadow
    with_shadow = add_drop_shadow(no_bg)
    with_shadow.save("test_outputs/with_shadow.png")
    print("   ✓ with_shadow.png")
    
    # Full processing
    processed = load_and_process_image(test_path, VideoConfig)
    if processed:
        processed.save("test_outputs/fully_processed.png")
        print("   ✓ fully_processed.png")


def test_animated_topic_with_image(
    image_path: str,
    title: str = "Understanding Machine Learning",
    bullets: List[str] = None,
    subtitle_text: str = "This is a sample subtitle to test positioning",
    num_frames: int = 120,
    output_gif: str = "test_outputs/topic_full_test.gif",
    output_video: str = "test_outputs/topic_full_test.mp4",
    save_gif: bool = True,
    save_video: bool = True
):
    """
    Test animated topic frame with image, text, bullets, and subtitles.
    
    Args:
        image_path: Path to test image (cartoon with white background)
        title: Topic title text
        bullets: List of bullet points (default provided if None)
        subtitle_text: Subtitle text to display
        num_frames: Number of frames to generate (default 120 = 4 seconds)
        output_gif: Path for output GIF
        output_video: Path for output MP4
        save_gif: Whether to save GIF
        save_video: Whether to save MP4
    
    Usage:
        test_animated_topic_with_image("my_image.png")
        test_animated_topic_with_image(
            "my_image.png",
            title="Custom Title",
            bullets=["Point 1", "Point 2", "Point 3"],
            subtitle_text="Custom subtitle here"
        )
    """
    print("\n🎬 Testing animated topic with image...")
    config = VideoConfig
    
    # Default bullets
    if bullets is None:
        bullets = [
            "Neural networks mimic brain structure",
            "Training requires large datasets for accuracy",
            "Applications in healthcare and finance",
            "Deep learning enables pattern recognition"
        ]
    
    # Check image exists
    if not os.path.exists(image_path):
        print(f"   ⚠ Image not found: {image_path}")
        print("   Continuing without image...")
    
    # Generate animated frames
    print(f"   Generating {num_frames} frames...")
    frames = generate_topic_frames_animated(
        title=title,
        bullet_points=bullets,
        image_path=image_path,
        num_frames=num_frames,
        config=config
    )
    
    # Add subtitles to frames (appear after initial animations)
    subtitle_start = 40  # Start showing subtitle after 40 frames
    frames_with_subtitles = []
    
    for i, frame in enumerate(frames):
        if i >= subtitle_start and subtitle_text:
            # Fade in subtitle
            sub_frame = i - subtitle_start
            frame = add_animated_subtitle(frame, subtitle_text, sub_frame, config)
        frames_with_subtitles.append(frame)
    
    # Save GIF
    if save_gif:
        frames_with_subtitles[0].save(
            output_gif,
            save_all=True,
            append_images=frames_with_subtitles[1:],
            duration=33,  # ~30fps
            loop=0
        )
        print(f"   ✓ Saved: {output_gif}")
    
    # Save MP4
    if save_video:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_video, fourcc, config.FPS, (config.WIDTH, config.HEIGHT))
        
        if out.isOpened():
            for frame in frames_with_subtitles:
                frame_np = np.array(frame)
                if frame_np.shape[-1] == 4:  # RGBA
                    frame_np = frame_np[:, :, :3]  # Drop alpha
                bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                out.write(bgr)
            out.release()
            print(f"   ✓ Saved: {output_video}")
        else:
            print("   ✗ Could not open video writer")
    
    # Also save first and last frame as PNG for inspection
    frames_with_subtitles[0].save("test_outputs/topic_first_frame.png")
    frames_with_subtitles[-1].save("test_outputs/topic_last_frame.png")
    print("   ✓ Saved: topic_first_frame.png, topic_last_frame.png")
    
    print(f"   ✅ Generated {len(frames_with_subtitles)} frames")
    return frames_with_subtitles


def add_animated_subtitle(frame: Image.Image, text: str, anim_frame: int,
                          config: VideoConfig = VideoConfig) -> Image.Image:
    """Add subtitle with fade-in animation"""
    if not text.strip():
        return frame
    
    frame = frame.copy()
    draw = ImageDraw.Draw(frame, 'RGBA')
    sub_font = load_font(config.SUBTITLE_SIZE)
    
    # Fade in over 10 frames
    fade_progress = min(anim_frame / 10, 1.0)
    alpha = int(255 * ease_out(fade_progress))
    bg_alpha = int(180 * ease_out(fade_progress))
    
    lines = wrap_text(draw, text, sub_font, config.WIDTH - 100)
    
    y = config.HEIGHT - (len(lines) * config.SUBTITLE_LINE_HEIGHT) - 35
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=sub_font)
        line_width = bbox[2] - bbox[0]
        x = (config.WIDTH - line_width) // 2
        
        # Background
        padding = config.SUBTITLE_PADDING
        draw.rectangle(
            [(x - padding - 5, y - padding),
             (x + line_width + padding + 5, y + 28 + padding)],
            fill=(0, 0, 0, bg_alpha)
        )
        
        # Text
        draw.text((x, y), line, fill=(*config.SUBTITLE_COLOR, alpha), font=sub_font)
        y += config.SUBTITLE_LINE_HEIGHT
    
    return frame


def test_full_video_with_image(
    image_path: str,
    hook_text: str = "Welcome to Our Presentation!",
    topic_title: str = "Key Concepts Explained",
    bullets: List[str] = None,
    conclusion_text: str = "Thanks for Watching!",
    output_path: str = "test_outputs/full_test_video.mp4"
):
    """
    Generate a complete test video with hook, topic (with image), and conclusion.
    
    Args:
        image_path: Path to cartoon image for topic section
        hook_text: Text for opening hook
        topic_title: Title for topic section
        bullets: Bullet points for topic
        conclusion_text: Text for conclusion
        output_path: Output video path
    
    Usage:
        test_full_video_with_image("my_cartoon.png")
    """
    print("\n🎥 Generating full test video...")
    config = VideoConfig
    
    if bullets is None:
        bullets = [
            "First key insight to share",
            "Second important point here", 
            "Third takeaway for viewers",
            "Final thought to remember"
        ]
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, config.FPS, (config.WIDTH, config.HEIGHT))
    
    if not out.isOpened():
        print("   ✗ Could not open video writer")
        return
    
    total_frames = 0
    
    # === HOOK SECTION (3 seconds) ===
    print("   📝 Generating hook...")
    hook_frames = generate_hook_frames_animated(hook_text, 90, config)
    for frame in hook_frames:
        frame_np = np.array(frame)
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
        total_frames += 1
    
    # === TRANSITION (0.5 seconds) ===
    print("   🔄 Adding transition...")
    last_hook = hook_frames[-1]
    first_topic = generate_topic_frames_animated(topic_title, bullets, image_path, 1, config)[0]
    
    for i in range(15):
        progress = ease_in_out(i / 14)
        # Cross-fade
        blended = Image.blend(last_hook.convert('RGBA'), first_topic.convert('RGBA'), progress)
        frame_np = np.array(blended.convert('RGB'))
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
        total_frames += 1
    
    # === TOPIC SECTION (5 seconds) ===
    print("   📊 Generating topic with image...")
    topic_frames = generate_topic_frames_animated(topic_title, bullets, image_path, 150, config)
    
    # Add subtitles after animations settle
    subtitle_texts = [
        "Let me explain these key concepts",
        "Each point builds on the previous one",
        "Understanding these will help you succeed"
    ]
    
    for i, frame in enumerate(topic_frames):
        # Cycle through subtitles
        if i >= 30:
            sub_idx = ((i - 30) // 40) % len(subtitle_texts)
            sub_frame = (i - 30) % 40
            frame = add_animated_subtitle(frame, subtitle_texts[sub_idx], sub_frame, config)
        
        frame_np = np.array(frame)
        if frame_np.shape[-1] == 4:
            frame_np = frame_np[:, :, :3]
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
        total_frames += 1
    
    # === TRANSITION TO CONCLUSION ===
    print("   🔄 Adding transition...")
    last_topic = topic_frames[-1]
    conclusion_frame = create_text_image(conclusion_text, config, font_size=44)
    
    for i in range(15):
        progress = ease_in_out(i / 14)
        blended = Image.blend(last_topic.convert('RGBA'), conclusion_frame.convert('RGBA'), progress)
        frame_np = np.array(blended.convert('RGB'))
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
        total_frames += 1
    
    # === CONCLUSION (2 seconds) ===
    print("   🎬 Generating conclusion...")
    for _ in range(60):
        frame_np = np.array(conclusion_frame)
        bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        out.write(bgr)
        total_frames += 1
    
    out.release()
    
    duration = total_frames / config.FPS
    print(f"   ✅ Saved: {output_path}")
    print(f"   📊 Total: {total_frames} frames ({duration:.1f} seconds)")


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 Video Frame Experimentation")
    print("=" * 50)
    
    # === BASIC TESTS ===
    # test_static_frames()
    # test_animated_frames()
    
    # === TEST WITH YOUR IMAGE ===
    # Change this to your actual image path
    TEST_IMAGE = "./output/images/topic_1_visual_1.png"
    
    # Test 1: Animated topic with image (GIF + MP4 + PNGs)
    test_animated_topic_with_image(
        image_path=TEST_IMAGE,
        title="Workplace Safety Policies",
        bullets=[
            "Create Internal Complaints Committees (ICCs)",
            "Ensure timely handling of harassment cases",
            "Raise awareness about what constitutes harassment",
            "Provide safe reporting mechanisms"
        ],
        subtitle_text="Let's discuss workplace safety policies",
        num_frames=120,
        save_gif=True,
        save_video=True
    )
    
    # Test 2: Full video with hook, topic, and conclusion
    # test_full_video_with_image(
    #     image_path=TEST_IMAGE,
    #     hook_text="Welcome to Workplace Safety Training!",
    #     topic_title="Key Safety Policies",
    #     bullets=[
    #         "Create Internal Complaints Committees",
    #         "Ensure timely handling of cases",
    #         "Raise awareness about harassment",
    #         "Provide safe reporting channels"
    #     ],
    #     conclusion_text="Stay Safe, Stay Informed!"
    # )
    
    # === IMAGE PROCESSING TEST ===
    # test_image_processing()
    
    print("\n" + "=" * 50)
    print("✅ Done! Check 'test_outputs/' folder")
    print("=" * 50)