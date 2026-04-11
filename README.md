# MIDI to Car Horn Converter

Transforms any MIDI file into a symphony of car horns with **complete accuracy**. Every note becomes a gloriously authentic automotive honk.

## Features

- **Pitch-perfect honking**: Each MIDI note converts to a car horn at the exact corresponding frequency
- **Authentic horn synthesis**: Sawtooth wave + harmonics + LFO modulation = genuine car alarm vibes
- **Full MIDI support**: Handles tempo changes, velocity dynamics, multiple tracks
- **Envelope processing**: Attack + decay envelope for natural horn decay
- **Batch-friendly**: CLI interface for scripting

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic usage:
```bash
python midi_to_carhorn.py song.mid
```
Output: `song_carhorn.wav`

### Custom output filename:
```bash
python midi_to_carhorn.py song.mid my_honking_masterpiece.wav
```

## How it works

1. **Parses MIDI**: Extracts all note events, pitch, duration, velocity, and tempo
2. **Frequency mapping**: Converts MIDI note numbers to Hz using the standard A4=440Hz reference
3. **Horn synthesis**: Generates sawtooth waves with:
   - Primary frequency (MIDI note converted to Hz)
   - +127 Hz harmonic (adds grit)
   - +200 Hz harmonic (adds bite)
   - 6 Hz LFO tremolo (wobble effect)
4. **Envelope**: Quick attack (10ms) + exponential decay for realistic horn tail-off
5. **Velocity mapping**: Softer MIDI notes → quieter honks, louder notes → louder honks
6. **Audio mixing**: Overlapping notes sum together for polyphonic honking chaos
7. **Normalization**: Prevents clipping while preserving dynamic range

## Examples

### Convert a simple melody:
```bash
python midi_to_carhorn.py melody.mid
```

### Process multiple files:
```bash
for file in *.mid; do
    python midi_to_carhorn.py "$file"
done
```

### Custom synthesis parameters

Edit the `CarHornSynthesizer` class to tweak:
- `horn_decay`: How fast the honk fades (0.3 = quick, higher = slower)
- `lfo` frequency: Change the 6 Hz wobble to a different value
- Harmonic amplitudes: 0.4 and 0.2 multipliers on the +127/-200 Hz components

## Technical specs

- **Sample rate**: 44.1 kHz (CD quality)
- **Bit depth**: 32-bit float (normalized to 16-bit during write)
- **Format**: WAV (uncompressed)
- **MIDI standard**: General MIDI compatible

## Requirements

- Python 3.7+
- mido (MIDI parsing)
- scipy (signal processing + WAV writing)
- numpy (audio math)

## Accuracy notes

- **Pitch accuracy**: ±1 semitone (exact MIDI->Hz conversion using A4=440 Hz standard)
- **Timing accuracy**: Sample-accurate (44100 samples per second)
- **Velocity mapping**: Linear 0-127 MIDI velocity → 0-90% amplitude
- **Duration accuracy**: Tick-to-time conversion respects tempo changes

## Known limitations

- Expression/CC events: Ignored (only note_on/note_off events processed)
- Sustain pedal: Not implemented (each note has fixed decay)
- Program changes: Ignored (all outputs are car horn)
- Relative timing: Based on MIDI clock divisions, not wall-clock time

## The Name

"Complete accuracy" means:
- Every note plays at the precise frequency
- Every note plays at the exact duration
- Every velocity maps linearly to amplitude
- Polyphonic overlap is handled correctly
- Tempo changes are respected
- Sample-accurate rendering

It does NOT mean the honks sound like actual car horns, only that the mathematical conversion is perfect.
