import hashlib
import json
import logging
import platform
import re
import subprocess
import sys
import uuid
from collections import deque
from pathlib import Path
from typing import Any
from types import SimpleNamespace
import colorlog
from decouple import config
from openai import OpenAI
from rich.console import Console, Group
from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text

console = Console()
# Configure logging
logger = logging.getLogger("mcpomni_connect")
logger.setLevel(logging.INFO)

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create console handler with immediate flush
console_handler = colorlog.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create file handler with immediate flush
log_file = Path("mcpomni_connect.log")
file_handler = logging.FileHandler(log_file, mode="a")
file_handler.setLevel(logging.INFO)

# Create formatters
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)

file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Set formatters
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configure handlers to flush immediately
console_handler.flush = sys.stdout.flush
file_handler.flush = lambda: file_handler.stream.flush()


def clean_json_response(json_response):
    """Clean and extract JSON from the response."""
    try:
        # First try to parse as is
        json.loads(json_response)
        return json_response
    except json.JSONDecodeError:
        # If that fails, try to extract JSON
        try:
            # Remove any markdown code blocks
            if "```" in json_response:
                # Extract content between first ``` and last ```
                start = json_response.find("```") + 3
                end = json_response.rfind("```")
                # Skip the "json" if it's present after first ```
                if json_response[start : start + 4].lower() == "json":
                    start += 4
                json_response = json_response[start:end].strip()

            # Find the first { and last }
            start = json_response.find("{")
            end = json_response.rfind("}") + 1
            if start >= 0 and end > start:
                json_response = json_response[start:end]

            # Validate the extracted JSON
            json.loads(json_response)
            return json_response
        except (json.JSONDecodeError, ValueError) as e:
            raise json.JSONDecodeError(
                f"Could not extract valid JSON from response: {str(e)}",
                json_response,
                0,
            )


def hash_text(text: str) -> str:
    """Hash a string using SHA-256."""
    return hashlib.sha256(text.encode()).hexdigest()


class RobustLoopDetector:
    def __init__(
        self,
        maxlen: int = 20,
        min_calls: int = 3,
        same_output_threshold: int = 3,
        same_input_threshold: int = 3,
        full_dup_threshold: int = 3,
        pattern_detection: bool = True,
        max_pattern_length: int = 3,
    ):
        """Initialize a robust loop detector.

        Args:
            maxlen: Maximum number of recent interactions to track
            min_calls: Minimum number of interactions before loop detection is active
            same_output_threshold: Maximum unique outputs before it's considered a loop
            same_input_threshold: Maximum unique inputs before it's considered a loop
            full_dup_threshold: Maximum unique interaction signatures before it's considered a loop
            pattern_detection: Whether to detect repeating patterns
            max_pattern_length: Maximum pattern length to detect
        """
        self.recent_interactions = deque(maxlen=maxlen)
        self.min_calls = min_calls
        self.same_output_threshold = same_output_threshold
        self.same_input_threshold = same_input_threshold
        self.full_dup_threshold = full_dup_threshold
        self.pattern_detection = pattern_detection
        self.max_pattern_length = max_pattern_length

        # Cache for performance optimization
        self._cache: dict[str, Any] = {}
        self._interaction_count = 0

    def record_tool_call(
        self, tool_name: str, tool_input: str, tool_output: str
    ) -> None:
        """Record a new tool call interaction.

        Args:
            tool_name: Name of the tool that was called
            tool_input: Input provided to the tool
            tool_output: Output returned by the tool
        """
        signature = (
            "tool",
            tool_name,
            hash_text(tool_input),
            hash_text(tool_output),
        )
        self.recent_interactions.append(signature)
        self._interaction_count += 1

        # Invalidate cache
        self._cache = {}

    def record_message(self, user_message: str, assistant_message: str) -> None:
        """Record a new message exchange interaction.

        Args:
            user_message: Message from the user
            assistant_message: Response from the assistant
        """
        signature = (
            "message",
            "",
            hash_text(user_message),
            hash_text(assistant_message),
        )
        self.recent_interactions.append(signature)
        self._interaction_count += 1

        # Invalidate cache
        self._cache = {}

    def record_interaction(
        self,
        interaction_type: str,
        input_data: str,
        output_data: str,
        metadata: str = "",
    ) -> None:
        """Generic method to record any type of interaction.

        Args:
            interaction_type: Type of interaction (e.g., "tool", "message", "function")
            input_data: Input for the interaction
            output_data: Output from the interaction
            metadata: Additional information about the interaction (e.g., tool name)
        """
        signature = (
            interaction_type,
            metadata,
            hash_text(input_data),
            hash_text(output_data),
        )
        self.recent_interactions.append(signature)
        self._interaction_count += 1

        # Invalidate cache
        self._cache = {}

    def reset(self) -> None:
        """Reset the detector, clearing all recorded interactions."""
        self.recent_interactions.clear()
        self._cache = {}
        self._interaction_count = 0

    def _get_unique_inputs(self) -> set[str]:
        """Get set of unique inputs (cached)."""
        if "unique_inputs" not in self._cache:
            self._cache["unique_inputs"] = set(
                sig[2] for sig in self.recent_interactions
            )
        return self._cache["unique_inputs"]

    def _get_unique_outputs(self) -> set[str]:
        """Get set of unique outputs (cached)."""
        if "unique_outputs" not in self._cache:
            self._cache["unique_outputs"] = set(
                sig[3] for sig in self.recent_interactions
            )
        return self._cache["unique_outputs"]

    def _get_unique_signatures(self) -> set[tuple]:
        """Get set of unique full signatures (cached)."""
        if "unique_signatures" not in self._cache:
            self._cache["unique_signatures"] = set(self.recent_interactions)
        return self._cache["unique_signatures"]

    def is_ready(self) -> bool:
        """Check if we have enough data to start detecting loops."""
        return self._interaction_count >= self.min_calls

    def is_stuck_same_output(self) -> bool:
        """Detect if we're stuck getting the same outputs repeatedly."""
        if not self.is_ready():
            return False

        # Get the last few outputs
        recent_outputs = [sig[3] for sig in self.recent_interactions]

        # We need at least same_output_threshold outputs to check
        if len(recent_outputs) < self.same_output_threshold:
            return False

        # Check if the last same_output_threshold outputs are all the same
        last_outputs = recent_outputs[-self.same_output_threshold :]
        return len(set(last_outputs)) == 1

    def is_stuck_same_input(self) -> bool:
        """Detect if we're stuck using the same inputs repeatedly."""
        if not self.is_ready():
            return False

        # Get the last few inputs
        recent_inputs = [sig[2] for sig in self.recent_interactions]

        # We need at least same_input_threshold inputs to check
        if len(recent_inputs) < self.same_input_threshold:
            return False

        # Check if the last same_input_threshold inputs are all the same
        last_inputs = recent_inputs[-self.same_input_threshold :]
        return len(set(last_inputs)) == 1

    def is_fully_stuck(self) -> bool:
        """Detect if we're stuck in the same input-output combinations."""
        if not self.is_ready():
            return False

        # Get the last few interactions
        recent_interactions = list(self.recent_interactions)

        # We need at least full_dup_threshold interactions to check
        if len(recent_interactions) < self.full_dup_threshold:
            return False

        # Check if the last full_dup_threshold interactions are all the same
        last_interactions = recent_interactions[-self.full_dup_threshold :]
        return len(set(last_interactions)) == 1

    def find_repeating_pattern(self) -> list[tuple] | None:
        """Find a repeating pattern in the interaction history.

        Returns:
            The detected pattern as a list of signatures, or None if no pattern found
        """
        if not self.pattern_detection or not self.is_ready():
            return None

        interactions = list(self.recent_interactions)

        # Check patterns of different lengths
        for pattern_len in range(
            1, min(self.max_pattern_length + 1, len(interactions) // 2 + 1)
        ):
            # Check if the last N elements repeat the previous N elements
            pattern = interactions[-pattern_len:]
            prev_pattern = interactions[-2 * pattern_len : -pattern_len]

            if pattern == prev_pattern:
                # Found a repeating pattern
                return pattern

        return None

    def has_pattern_loop(self) -> bool:
        """Check if there's a repeating pattern loop."""
        return self.find_repeating_pattern() is not None

    def is_looping(self) -> bool:
        """Check if any loop detection method indicates a loop."""
        return (
            self.is_stuck_same_output()
            or self.is_stuck_same_input()
            or self.is_fully_stuck()
            or self.has_pattern_loop()
        )

    def get_loop_type(self) -> list[str]:
        """Get detailed information about the type of loop detected.

        Returns:
            List of strings describing the detected loop types
        """
        if not self.is_looping():
            return []

        loop_types = []
        if self.is_stuck_same_output():
            loop_types.append("same_output")
        if self.is_stuck_same_input():
            loop_types.append("same_input")
        if self.is_fully_stuck():
            loop_types.append("full_duplication")

        pattern = self.find_repeating_pattern()
        if pattern:
            loop_types.append(f"repeating_pattern(len={len(pattern)})")

        return loop_types

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the current state.

        Returns:
            Dictionary with statistics about inputs, outputs, etc.
        """
        if not self.recent_interactions:
            return {"interactions": 0}

        # Count different types of interactions
        interaction_types = {}
        for sig in self.recent_interactions:
            itype = sig[0]
            interaction_types[itype] = interaction_types.get(itype, 0) + 1

        return {
            "interactions": self._interaction_count,
            "queue_size": len(self.recent_interactions),
            "unique_inputs": len(self._get_unique_inputs()),
            "unique_outputs": len(self._get_unique_outputs()),
            "unique_signatures": len(self._get_unique_signatures()),
            "interaction_types": interaction_types,
            "repeating_pattern": self.find_repeating_pattern() is not None,
        }

    def get_interaction_types(self) -> dict[str, int]:
        """Get counts of each interaction type in the history.

        Returns:
            Dictionary mapping interaction types to their counts
        """
        type_counts = {}
        for sig in self.recent_interactions:
            itype = sig[0]
            type_counts[itype] = type_counts.get(itype, 0) + 1
        return type_counts


def handle_stuck_state(original_system_prompt: str, message_stuck_prompt: bool = False):
    """
    Creates a modified system prompt that includes stuck detection guidance.

    Parameters:
    - original_system_prompt: The normal system prompt you use
    - message_stuck_prompt: If True, use a shorter version of the stuck prompt

    Returns:
    - Modified system prompt with stuck guidance prepended
    """
    if message_stuck_prompt:
        stuck_prompt = (
            "⚠️ You are stuck in a loop. This must be addressed immediately.\n\n"
            "REQUIRED ACTIONS:\n"
            "1. **STOP** the current approach\n"
            "2. **ANALYZE** why the previous attempts failed\n"
            "3. **TRY** a completely different method\n"
            "4. **IF** the issue cannot be resolved:\n"
            "   - Explain clearly why not\n"
            "   - Provide alternative solutions\n"
            "   - DO NOT repeat the same failed action\n\n"
            "   - DO NOT try again. immediately stop and do not try again.\n\n"
            "   - Tell user your last known good state, error message and the current state of the conversation.\n\n"
            "❗ CONTINUING THE SAME APPROACH WILL RESULT IN FURTHER FAILURES"
        )
    else:
        stuck_prompt = (
            "⚠️ It looks like you're stuck or repeating an ineffective approach.\n"
            "Take a moment to do the following:\n"
            "1. **Reflect**: Analyze why the previous step didn't work (e.g., tool call failure, irrelevant observation).\n"
            "2. **Try Again Differently**: Use a different tool, change the inputs, or attempt a new strategy.\n"
            "3. **If Still Unsolvable**:\n"
            "   - **Clearly explain** to the user *why* the issue cannot be solved.\n"
            "   - Provide any relevant reasoning or constraints.\n"
            "   - Offer one or more alternative solutions or next steps.\n"
            "   - DO NOT try again. immediately stop and do not try again.\n\n"
            "   - Tell user your last known good state, error message and the current state of the conversation.\n\n"
            "❗ Do not repeat the same failed strategy or go silent."
        )

    # Create a temporary modified system prompt
    modified_system_prompt = (
        f"{stuck_prompt}\n\n"
        f"Your previous approaches to solve this problem have failed. You need to try something completely different.\n\n"
        # f"{original_system_prompt}"
    )

    return modified_system_prompt


def embed_text(text: str) -> list[float]:
    """Embed text using OpenAI's embedding API."""
    client = OpenAI(api_key=config("OPENAI_API_KEY"))
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding


def dict_to_namespace(d):
    return json.loads(json.dumps(d), object_hook=lambda x: SimpleNamespace(**x))


def strip_json_comments(text: str) -> str:
    """
    Removes // and /* */ style comments from JSON-like text,
    but only if they're outside of double-quoted strings.
    """

    def replacer(match):
        s = match.group(0)
        if s.startswith('"'):
            return s  # keep strings intact
        return ""  # remove comments

    pattern = r'"(?:\\.|[^"\\])*"' + r"|//.*?$|/\*.*?\*/"
    return re.sub(pattern, replacer, text, flags=re.DOTALL | re.MULTILINE)


def show_tool_response(agent_name, tool_name, tool_args, observation):
    content = Group(
        Text(agent_name.upper(), style="bold magenta"),
        Text(f"→ Calling tool: {tool_name}", style="bold blue"),
        Text("→ Tool input:", style="bold yellow"),
        Pretty(tool_args),
        Text("→ Tool response:", style="bold green"),
        Pretty(observation),
    )

    panel = Panel.fit(content, title="🔧 TOOL CALL LOG", border_style="bright_black")
    console.print(panel)


# # Initialize the model once at module level
# EMBEDDING_MODEL = SentenceTransformer('BAAI/bge-large-en-v1.5')


# def embed_text(text: str) -> List[float]:
#     """Embed text using Sentence Transformers."""
#     try:
#         # Get the embedding
#         embedding = EMBEDDING_MODEL.encode(text)
#         return embedding.tolist()
#     except Exception as e:
#         logger.error(f"Error generating embedding: {e}")
#         return []


def get_mac_address() -> str:
    """Get the MAC address of the client machine.

    Returns:
        str: The MAC address as a string, or a fallback UUID if MAC address cannot be determined.
    """
    try:
        if platform.system() == "Linux":
            # Try to get MAC address from /sys/class/net/
            for interface in ["eth0", "wlan0", "en0"]:
                try:
                    with open(f"/sys/class/net/{interface}/address") as f:
                        mac = f.read().strip()
                        if mac:
                            return mac
                except FileNotFoundError:
                    continue

            # Fallback to using ip command
            result = subprocess.run(
                ["ip", "link", "show"], capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "link/ether" in line:
                    return line.split("link/ether")[1].split()[0]

        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if "ether" in line:
                    return line.split("ether")[1].split()[0]

        elif platform.system() == "Windows":
            result = subprocess.run(["getmac"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if ":" in line and "-" in line:  # Look for MAC address format
                    return line.split()[0]

    except Exception as e:
        logger.warning(f"Could not get MAC address: {e}")

    # If all else fails, generate a UUID
    return str(uuid.uuid4())


# Create a global instance of the MAC address
CLIENT_MAC_ADDRESS = get_mac_address()
