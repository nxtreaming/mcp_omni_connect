"""MoviePy Video Tools - Process video files, extract audio, and embed captions."""

from typing import Any, Dict, List, Optional

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_debug, log_info, logger

try:
    from moviepy import ColorClip, CompositeVideoClip, TextClip, VideoFileClip  # type: ignore
except ImportError:
    ColorClip = None  # type: ignore
    CompositeVideoClip = None  # type: ignore
    TextClip = None  # type: ignore
    VideoFileClip = None  # type: ignore



class MoviePyExtractAudio:
    def __init__(self):
        if VideoFileClip is None:
            raise ImportError("`moviepy` not installed. Please install using `pip install moviepy ffmpeg`")

    def get_tool(self) -> Tool:
        return Tool(
            name="moviepy_extract_audio",
            description="Extract audio from a video file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {"type": "string", "description": "Path to the video file"},
                    "output_path": {"type": "string", "description": "Path to save the audio file"},
                },
                "required": ["video_path", "output_path"],
            },
            function=self._extract_audio,
        )

    async def _extract_audio(self, video_path: str, output_path: str) -> Dict[str, Any]:
        try:
            log_info(f"Extracting audio from {video_path}")
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(output_path)
            video.close()
            return {"status": "success", "data": output_path, "message": f"Audio extracted to {output_path}"}
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return {"status": "error", "data": None, "message": str(e)}


class MoviePyCreateSRT:
    def __init__(self):
        if VideoFileClip is None:
            raise ImportError("`moviepy` not installed. Please install using `pip install moviepy ffmpeg`")

    def get_tool(self) -> Tool:
        return Tool(
            name="moviepy_create_srt",
            description="Save transcription text as an SRT file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcription": {"type": "string", "description": "SRT formatted transcription text"},
                    "output_path": {"type": "string", "description": "Path to save the SRT file"},
                },
                "required": ["transcription", "output_path"],
            },
            function=self._create_srt,
        )

    async def _create_srt(self, transcription: str, output_path: str) -> Dict[str, Any]:
        try:
            with open(output_path, "w") as f:
                f.write(transcription)
            return {"status": "success", "data": output_path, "message": f"SRT file saved to {output_path}"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}


class MoviePyEmbedCaptions:
    def __init__(self):
        if VideoFileClip is None:
            raise ImportError("`moviepy` not installed. Please install using `pip install moviepy ffmpeg`")

    def get_tool(self) -> Tool:
        return Tool(
            name="moviepy_embed_captions",
            description="Embed captions from an SRT file into a video.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "srt_path": {"type": "string"},
                    "output_path": {"type": "string"},
                    "font_size": {"type": "integer", "default": 24},
                    "font_color": {"type": "string", "default": "white"},
                },
                "required": ["video_path", "srt_path"],
            },
            function=self._embed_captions,
        )

    def _parse_srt(self, srt_content: str) -> List[Dict]:
        """Parse SRT content into word-level timing data."""
        words = []
        blocks = srt_content.strip().split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                time_line = lines[1]
                text = " ".join(lines[2:])
                try:
                    start_str, end_str = time_line.split(" --> ")
                    start = self._time_to_seconds(start_str.strip())
                    end = self._time_to_seconds(end_str.strip())
                    for word in text.split():
                        words.append({"word": word, "start": start, "end": end})
                except Exception:
                    pass
        return words

    def _time_to_seconds(self, time_str: str) -> float:
        parts = time_str.replace(",", ".").split(":")
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])

    def _split_text_into_lines(self, words: List[Dict]) -> List[Dict]:
        """Split words into subtitle lines."""
        lines = []
        current_line: List[Dict] = []
        for word in words:
            current_line.append(word)
            if len(current_line) >= 8 or (current_line and word["end"] - current_line[0]["start"] > 3.0):
                text = " ".join(w["word"] for w in current_line)
                lines.append({"text": text, "start": current_line[0]["start"], "end": current_line[-1]["end"], "words": current_line})
                current_line = []
        if current_line:
            text = " ".join(w["word"] for w in current_line)
            lines.append({"text": text, "start": current_line[0]["start"], "end": current_line[-1]["end"], "words": current_line})
        return lines

    async def _embed_captions(
        self,
        video_path: str,
        srt_path: str,
        output_path: Optional[str] = None,
        font_size: int = 24,
        font_color: str = "white",
    ) -> Dict[str, Any]:
        try:
            if not output_path:
                output_path = video_path.rsplit(".", 1)[0] + "_captioned.mp4"

            with open(srt_path, "r") as f:
                srt_content = f.read()

            words = self._parse_srt(srt_content)
            lines = self._split_text_into_lines(words)

            video = VideoFileClip(video_path)
            frame_size = video.size

            caption_clips = []
            for line in lines:
                try:
                    txt_clip = TextClip(
                        text=line["text"],
                        font_size=font_size,
                        color=font_color,
                        stroke_color="black",
                        stroke_width=1,
                    )
                    txt_clip = txt_clip.with_position(("center", frame_size[1] * 0.85))
                    txt_clip = txt_clip.with_start(line["start"]).with_end(line["end"])
                    caption_clips.append(txt_clip)
                except Exception as e:
                    log_debug(f"Error creating caption clip: {e}")

            final = CompositeVideoClip([video] + caption_clips)
            final.write_videofile(output_path, codec="libx264", audio_codec="aac")
            video.close()

            return {"status": "success", "data": output_path, "message": f"Captioned video saved to {output_path}"}
        except Exception as e:
            logger.error(f"Error embedding captions: {e}")
            return {"status": "error", "data": None, "message": str(e)}
