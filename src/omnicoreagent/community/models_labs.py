import json
import time
from os import getenv
from typing import Any, Dict, Optional
from uuid import uuid4

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_debug, log_info, logger

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:
    requests = None
    RequestException = None



MODELS_LAB_URLS = {
    "MP4": "https://modelslab.com/api/v6/video/text2video",
    "MP3": "https://modelslab.com/api/v6/voice/music_gen",
    "GIF": "https://modelslab.com/api/v6/video/text2video",
    "WAV": "https://modelslab.com/api/v6/voice/sfx",
}

MODELS_LAB_FETCH_URLS = {
    "MP4": "https://modelslab.com/api/v6/video/fetch",
    "MP3": "https://modelslab.com/api/v6/voice/fetch",
    "GIF": "https://modelslab.com/api/v6/video/fetch",
    "WAV": "https://modelslab.com/api/v6/voice/fetch",
}


class ModelsLabMediaGen:
    def __init__(
        self,
        api_key: Optional[str] = None,
        wait_for_completion: bool = False,
        add_to_eta: int = 15,
        max_wait_time: int = 60,
        file_type: str = "MP4",
    ):
        if requests is None:
             raise ImportError("`requests` not installed. Please install using `pip install requests`")
        self.file_type = file_type.upper()
        self.url = MODELS_LAB_URLS.get(self.file_type, MODELS_LAB_URLS["MP4"])
        self.fetch_url = MODELS_LAB_FETCH_URLS.get(self.file_type, MODELS_LAB_FETCH_URLS["MP4"])
        self.wait_for_completion = wait_for_completion
        self.add_to_eta = add_to_eta
        self.max_wait_time = max_wait_time
        self.api_key = api_key or getenv("MODELS_LAB_API_KEY")

        if not self.api_key:
            logger.error("MODELS_LAB_API_KEY not set.")

    def get_tool(self) -> Tool:
        return Tool(
            name="models_lab_generate_media",
            description=f"Generate {self.file_type} media given a prompt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text description of the desired media"},
                },
                "required": ["prompt"],
            },
            function=self._generate_media,
        )

    def _create_payload(self, prompt: str) -> Dict[str, Any]:
        base_payload: Dict[str, Any] = {
            "key": self.api_key,
            "prompt": prompt,
            "webhook": None,
            "track_id": None,
        }

        if self.file_type in ["MP4", "GIF"]:
            base_payload.update({
                "height": 512, "width": 512, "num_frames": 25,
                "negative_prompt": "low quality", "model_id": "cogvideox",
                "instant_response": False, "output_type": self.file_type.lower(),
            })
        elif self.file_type == "WAV":
            base_payload.update({"duration": 10, "output_format": "wav", "temp": False})
        else:
            base_payload.update({"base64": False, "temp": False})

        return base_payload

    def _wait_for_media(self, media_id: str, eta: int) -> bool:
        time_to_wait = min(eta + self.add_to_eta, self.max_wait_time)
        log_info(f"Waiting {time_to_wait}s for {self.file_type} to be ready")

        for _ in range(time_to_wait):
            try:
                resp = requests.post(
                    f"{self.fetch_url}/{media_id}",
                    json={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                )
                if resp.json().get("status") == "success":
                    return True
                time.sleep(1)
            except RequestException as e:
                logger.warning(f"Fetch error: {e}")
        return False

    async def _generate_media(self, prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "data": None, "message": "MODELS_LAB_API_KEY not set"}

        try:
            payload = json.dumps(self._create_payload(prompt))
            headers = {"Content-Type": "application/json"}

            log_debug(f"Generating {self.file_type} for prompt: {prompt}")
            response = requests.post(self.url, data=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if result.get("status") == "error":
                return {"status": "error", "data": None, "message": result.get("message", "Unknown error")}
            if "error" in result:
                return {"status": "error", "data": None, "message": result["error"]}

            eta = result.get("eta")
            media_id = str(uuid4())

            url_links = result.get("output", []) if self.file_type == "WAV" else result.get("future_links", [])

            media_urls = []
            for media_url in url_links:
                media_urls.append(media_url)
                if self.wait_for_completion and isinstance(eta, int):
                    if self._wait_for_media(media_id, eta):
                        log_info("Media generation completed")
                    else:
                        logger.warning("Media generation timed out")

            return {
                "status": "success",
                "data": {"media_urls": media_urls, "eta": eta, "file_type": self.file_type},
                "message": f"{self.file_type} generated, ready in ~{eta}s",
            }
        except RequestException as e:
            return {"status": "error", "data": None, "message": f"Network error: {e}"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}
