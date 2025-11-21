"""
models.py - Pydantic models for structured outputs
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class VisualDescription(BaseModel):
    """Visual description for a specific timing"""
    timing: str = Field(description="Time range like '0-10s'")
    description: str = Field(description="Detailed image generation prompt")
    type: str = Field(description="Type: photo")
    text_overlay: str = Field(description="Text to overlay on the image")


class SubtitleSegment(BaseModel):
    """Subtitle timing and text"""
    start_time: str = Field(description="Start time like '0s'")
    end_time: str = Field(description="End time like '5s'")
    text: str = Field(description="Subtitle text for this segment")


class KeyTopic(BaseModel):
    """A key topic extracted from the document"""
    topic_number: int = Field(description="Topic sequence number")
    title: str = Field(description="Topic title")
    importance: str = Field(description="Why this topic is important")
    estimated_duration: str = Field(description="Estimated duration like '30-40 seconds'")


class TopicDetails(BaseModel):
    """Detailed breakdown of a topic"""
    topic_number: int
    title: str
    duration: str
    narration: str = Field(description="Full narration script for this topic")
    key_points: List[str] = Field(description="2-3 key bullet points")
    visuals: List[VisualDescription] = Field(description="Visual descriptions with timing")
    subtitle_segments: List[SubtitleSegment] = Field(description="Subtitle timing breakdown")


class HookSection(BaseModel):
    """Video hook/opening"""
    duration: str = Field(default="10 seconds")
    narration: str = Field(description="Engaging opening statement")
    visuals: VisualDescription = Field(description="Hook visual description")
    subtitle_text: str = Field(description="Subtitle for hook section")


class ConclusionSection(BaseModel):
    """Video conclusion"""
    duration: str = Field(default="10-15 seconds")
    narration: str = Field(description="Closing statement with CTA")
    visuals: VisualDescription = Field(description="Final visual description")
    subtitle_text: str = Field(description="Closing subtitle")
    call_to_action: str = Field(description="What viewers should do next")


class VideoMetadata(BaseModel):
    """Video metadata"""
    title: str = Field(description="Catchy video title")
    duration_estimate: str = Field(description="Total duration estimate")
    target_audience: str = Field(description="Target audience description")
    tone: str = Field(description="Video tone: educational/professional/casual")


class CompleteVideoScript(BaseModel):
    """Complete video script with all components"""
    video_metadata: VideoMetadata
    hook: HookSection
    main_topics: List[TopicDetails]
    conclusion: ConclusionSection
    image_generation_prompts: List[str] = Field(description="All image prompts in sequence")
    full_audio_script: str = Field(description="Complete narration ready for TTS")
    subtitle_file_srt: str = Field(description="Complete SRT format subtitles")


class KeyTopicsExtraction(BaseModel):
    """Initial extraction of key topics from document"""
    topics: List[KeyTopic] = Field(description="List of 2-4 key topics")
    document_summary: str = Field(description="Brief summary of the document")
    suggested_video_title: str = Field(description="Suggested video title")
    target_audience: str = Field(description="Identified target audience")