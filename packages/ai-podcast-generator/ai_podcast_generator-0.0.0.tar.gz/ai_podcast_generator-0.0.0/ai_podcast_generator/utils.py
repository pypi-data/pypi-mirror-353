import ast
from pydub import AudioSegment

_global_audio_buffer = None

def reset_audio_buffer():
    """Reset the global audio buffer."""
    global _global_audio_buffer
    _global_audio_buffer = None

def get_current_audio_duration():
    """Return current audio duration in seconds."""
    global _global_audio_buffer
    return len(_global_audio_buffer) / 1000 if _global_audio_buffer else 0

def parse_script(script_text, num_rounds):
    """Parse script from text to list of tuples."""
    try:
        start = script_text.find("[")
        end = script_text.rfind("]") + 1
        parsed = ast.literal_eval(script_text[start:end])
        return parsed[:num_rounds]
    except Exception:
        print("Script parsing failed, using default.")
        return []