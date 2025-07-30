# real-random
![Pepy Total Downlods](https://img.shields.io/pepy/dt/real-random)

**real-random** is a Python package that generates random values using real-world entropy from ambient microphone audio. It converts raw audio noise into cryptographic hashes, which are then transformed into useful random outputs such as:

- Floating-point numbers in [0, 1)
- Integers within a range
- Random selections from sequences
- Random alphanumeric strings

This provides a non-deterministic alternative to traditional pseudorandom generators.

---

## Installation

```bash
pip install real-random
```

If you plan to build from source:

```bash
git clone https://github.com/yourusername/real-random
cd real-random
pip install .
```

## Usage
```python
from real_random import (
    real_random,
    real_random_int,
    real_random_float,
    real_random_choice,
    real_random_string,
)

print(real_random())                          # → 0.72623...
print(real_random_int(1, 10))                 # → 7
print(real_random_float(0.5, 2.5))            # → 1.934...
print(real_random_choice(["red", "blue"]))    # → "blue"
print(real_random_string(8))                  # → "aG9xB2dZ"
```

## How It Works

    Captures 1–2 seconds of microphone input (ambient noise).

    Normalizes and hashes the audio using SHA-256.

    Converts part of the hash into usable randomness.

    Uses that base randomness to build higher-level utilities.

If no audio signal is detected (silence), it falls back to generated synthetic noise to ensure entropy.


## Requirements

    A working microphone or audio input device

    Python 3.7+

    sounddevice, numpy

On Linux, make sure your user has access to audio input devices (PulseAudio or PipeWire is recommended).

## License

This project is licensed under the MIT License.

