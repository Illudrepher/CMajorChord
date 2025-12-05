import librosa
from pychord import find_chords_from_notes
import numpy as np
import pandas as pd
from pydub import AudioSegment
import json
import os
from itertools import permutations
import sys


def synthAudios(fileDir, bassPlus=0):
    other_path = os.path.join(fileDir, "other.wav")
    bass_path = os.path.join(fileDir, "bass.wav")
    other = AudioSegment.from_wav(other_path)
    bass = AudioSegment.from_wav(bass_path)
    combined = bass + bassPlus
    combined = combined.overlay(other)
    combine_path = os.path.join(fileDir, "combined.wav")
    combined.export(combine_path, format="wav")
    return combine_path


def get_chords_all_permutations(notes):
    results = {}
    for perm in set(permutations(notes)):
        chord_objs = find_chords_from_notes(list(perm))
        if chord_objs:
            results[perm] = [str(c) for c in chord_objs]
    return results
def choose_best_chord(chord_candidates):
    if not chord_candidates:
        return None
    best = None

    for perm, names in chord_candidates.items():
        for name in names:
            score = 0

            if "/" in name:
                score += 2

            if any(x in name for x in ["add", "sus", "dim", "aug", "7", "9", "11", "13"]):
                score += 1

            cleaned_name = name.replace("#", "").replace("b", "")
            score += len(cleaned_name) * 0.1

            if best is None or score < best[0]:
                best = (score, name, perm)

    if best is None:
        return None
    return best[1]



def getNotesByChroma(chroma_cq, frame_interval, detected_chords, proportion=0.75, thresh=0.3,notes=np.array(['C', "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])):
    for interval in frame_interval:
        chroma_vals = chroma_cq[:,interval[0]:interval[1]]
        chroma_means = np.mean(chroma_vals, axis=1)
        chroma_with_name = dict(zip(notes, chroma_means))
        sorted_chroma = list(sorted(chroma_with_name.items(), key=lambda item: item[1], reverse=True))
        detected_chroma = [sorted_chroma[0][0], sorted_chroma[1][0]]
        standard = sorted_chroma[1][1]
        counter=2
        next_chroma = sorted_chroma[counter]
        while counter < 5:
            next_chroma = sorted_chroma[counter]
            if next_chroma[1] >= proportion * standard and next_chroma[1]>thresh:
                detected_chroma.append(next_chroma[0])
                counter += 1
            else:
                break
        permutations = get_chords_all_permutations(detected_chroma)
        chord = choose_best_chord(permutations)
        detected_chords.append(chord)
    return


def analyze(synth_path, input_base_path):
    y, sr = librosa.load(synth_path)
    chroma_cq = librosa.feature.chroma_cqt(y=y, sr=sr)
    novelty = librosa.onset.onset_strength(S=chroma_cq, sr=sr)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=novelty,
        sr=sr,
        units='frames',
        backtrack=True,
        pre_max=3,
        post_max=3,
        pre_avg=3,
        post_avg=3,
        delta=0.1,
        wait=5
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    segment_times = [0.0] + onset_times.tolist() + [len(y) / sr]
    segments = list(zip(segment_times[:-1], segment_times[1:]))
    n_frames = chroma_cq.shape[1]
    frames = [0] + onset_frames.tolist() + [n_frames]
    segments_in_frames = list(zip(frames[:-1], frames[1:]))

    detected_chords = list()
    getNotesByChroma(chroma_cq, segments_in_frames, detected_chords)


    result = []
    for i in range(len(segments)):
        entry = {
            "start": round(segments[i][0], 3),
            "chord": detected_chords[i],
            "status": "normal"
        }
        result.append(entry)
    
    with open(f"{input_base_path}/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


def main():
    input_base_path = sys.argv[1]
    synth_path = synthAudios(input_base_path)
    analyze(synth_path, input_base_path)

    
if __name__ == "__main__":
    main()
