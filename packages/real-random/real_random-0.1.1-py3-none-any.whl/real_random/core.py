import sounddevice as sd
import numpy as np
import hashlib
import struct
import time
import random
import string
import math


def record_audio(duration: float = None, samplerate: int = 44100) -> np.ndarray:
    """Records audio from the microphone for the given duration."""
    if duration is None:
        duration = random.uniform(1, 2)
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    return recording.flatten()


def audio_to_entropy(audio_data: np.ndarray) -> bytes:
    """Converts audio data into an entropy byte sequence."""
    max_val = np.max(np.abs(audio_data))
    if max_val == 0 or np.isnan(max_val):
        audio_data = np.random.rand(len(audio_data)).astype('float32')
        max_val = np.max(np.abs(audio_data))

    normalized = np.int16(audio_data / max_val * 32767)
    byte_data = normalized.tobytes()
    return hashlib.sha256(byte_data).digest()


def entropy_to_random_float(entropy: bytes) -> float:
    """Converts the first 8 bytes of the hash to a float in [0, 1)."""
    int_val = struct.unpack("Q", entropy[:8])[0]  # 8 bytes = 64 bits
    return int_val / 2**64


def real_random() -> float:
    """Generates a random float between 0 and 1 based on microphone audio entropy."""
    audio = record_audio()
    entropy = audio_to_entropy(audio)
    return entropy_to_random_float(entropy)


def real_random_int(min_value: int, max_value: int) -> int:
    """Generates a random integer in the inclusive range [min_value, max_value]."""
    base = real_random()
    if base >= 1.0:
        base = 0.9999999999999999
    return min_value + math.floor(base * (max_value - min_value + 1))


def real_random_float(min_value: float, max_value: float) -> float:
    """Generates a random float between min_value and max_value."""
    base = real_random()
    return min_value + base * (max_value - min_value)


def real_random_choice(seq):
    """Selects a random element from a non-empty sequence."""
    if not seq:
        raise ValueError("The sequence cannot be empty")
    index = real_random_int(0, len(seq) - 1)
    return seq[index]


def real_random_string(length: int, charset: str = None) -> str:
    """Generates a random string of the given length using the provided character set."""
    if charset is None:
        charset = string.ascii_letters + string.digits
    return ''.join(real_random_choice(charset) for _ in range(length))
