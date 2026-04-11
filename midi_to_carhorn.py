#!/usr/bin/env python3
"""
MIDI to Car Horn Converter
Converts MIDI files into gloriously accurate car horn symphonies.
Every note becomes a honk. Every rest becomes silence. Pure chaos.
"""

import mido
import numpy as np
from scipy.io import wavfile
from scipy import signal
import os
import sys
from pathlib import Path


class CarHornSynthesizer:
    """Synthesizes car horn sounds at various frequencies."""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.horn_decay = 0.3  # Quick decay for punchy honk
        
    def midi_to_hz(self, midi_note):
        """Convert MIDI note number to frequency in Hz."""
        # A4 (MIDI 69) = 440 Hz
        return 440 * (2 ** ((midi_note - 69) / 12))
    
    def generate_horn_sound(self, frequency, duration):
        """
        Generate a car horn-like sound at specified frequency.
        Uses a sawtooth wave with AM modulation for that authentic honk.
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Sawtooth wave (more aggressive than sine)
        sawtooth = signal.sawtooth(2 * np.pi * frequency * t)
        
        # Add harmonics for richer honk (127 Hz + 200 Hz components)
        harmonic1 = 0.4 * np.sin(2 * np.pi * (frequency + 127) * t)
        harmonic2 = 0.2 * np.sin(2 * np.pi * (frequency + 200) * t)
        wave = 0.6 * sawtooth + harmonic1 + harmonic2
        
        # Amplitude modulation for tremolo effect (honk wobble)
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 6 * t)  # 6 Hz LFO
        wave = wave * lfo
        
        # Envelope: quick attack, slow decay
        attack_samples = int(0.01 * self.sample_rate)
        decay_samples = int(duration * self.sample_rate) - attack_samples
        
        envelope = np.ones_like(t)
        # Attack phase
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        # Decay phase
        if decay_samples > 0:
            envelope[attack_samples:] = np.exp(-self.horn_decay * np.linspace(0, 1, decay_samples))
        
        # Apply envelope and normalize
        horn_sound = wave * envelope
        horn_sound = horn_sound / np.max(np.abs(horn_sound)) * 0.9  # Prevent clipping
        
        return horn_sound.astype(np.float32)
    
    def generate_silence(self, duration):
        """Generate silence for rests."""
        return np.zeros(int(self.sample_rate * duration), dtype=np.float32)


class MIDIToCarHorn:
    """Converts MIDI files to car horn audio."""
    
    def __init__(self, output_format='wav', sample_rate=44100):
        self.synthesizer = CarHornSynthesizer(sample_rate)
        self.sample_rate = sample_rate
        self.output_format = output_format
        
    def parse_midi(self, midi_file):
        """Parse MIDI file and extract note events."""
        mid = mido.MidiFile(midi_file)
        
        # Get tempo (default 500000 microseconds per beat)
        tempo = 500000
        ticks_per_beat = mid.ticks_per_beat
        
        # Find tempo changes in the first track
        for msg in mid.tracks[0]:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
        
        notes = []
        current_time = 0
        
        # Flatten all tracks to get all note events
        for track in mid.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on':
                    if msg.velocity > 0:  # note_on with velocity > 0
                        # Convert tick time to seconds
                        time_seconds = (current_time / ticks_per_beat) * (tempo / 1_000_000)
                        notes.append({
                            'start': time_seconds,
                            'pitch': msg.note,
                            'velocity': msg.velocity
                        })
                
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Find matching note_on and set duration
                    time_seconds = (current_time / ticks_per_beat) * (tempo / 1_000_000)
                    for note in reversed(notes):
                        if note['pitch'] == msg.note and 'duration' not in note:
                            note['duration'] = time_seconds - note['start']
                            break
        
        # Clean up notes without duration
        notes = [n for n in notes if 'duration' in n and n['duration'] > 0]
        
        return notes
    
    def convert(self, midi_file, output_file=None):
        """Convert MIDI file to car horn audio."""
        
        if output_file is None:
            output_file = Path(midi_file).stem + '_carhorn.wav'
        
        print(f"Loading MIDI: {midi_file}")
        notes = self.parse_midi(midi_file)
        
        if not notes:
            print("No notes found in MIDI file!")
            return False
        
        print(f"Found {len(notes)} notes")
        print(f"Total duration: {max(n['start'] + n['duration'] for n in notes):.2f}s")
        
        # Calculate total duration
        total_duration = max(n['start'] + n['duration'] for n in notes)
        total_samples = int(total_duration * self.sample_rate)
        
        # Initialize audio buffer
        audio = np.zeros(total_samples, dtype=np.float32)
        
        # Render each note
        print("Synthesizing honks...")
        for i, note in enumerate(notes):
            start_sample = int(note['start'] * self.sample_rate)
            frequency = self.synthesizer.midi_to_hz(note['pitch'])
            
            # Generate horn sound
            horn_sound = self.synthesizer.generate_horn_sound(note['duration'], frequency)
            
            # Place in audio buffer
            end_sample = start_sample + len(horn_sound)
            if end_sample > total_samples:
                horn_sound = horn_sound[:total_samples - start_sample]
            
            audio[start_sample:end_sample] += horn_sound * (note['velocity'] / 127.0)
            
            if (i + 1) % max(1, len(notes) // 10) == 0:
                print(f"  {i + 1}/{len(notes)} notes rendered")
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95
        
        # Write to file
        print(f"Writing to: {output_file}")
        wavfile.write(output_file, self.sample_rate, audio)
        
        print("Conversion complete!")
        print(f"Output: {output_file} ({os.path.getsize(output_file) / 1024 / 1024:.2f} MB)")
        
        return True


def main():
    """CLI interface for MIDI to Car Horn conversion."""
    
    if len(sys.argv) < 2:
        print("Usage: python midi_to_carhorn.py <midi_file> [output_file]")
        print("\nExample:")
        print("  python midi_to_carhorn.py song.mid")
        print("  python midi_to_carhorn.py song.mid output.wav")
        sys.exit(1)
    
    midi_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(midi_file):
        print(f"MIDI file not found: {midi_file}")
        sys.exit(1)
    
    converter = MIDIToCarHorn()
    success = converter.convert(midi_file, output_file)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
