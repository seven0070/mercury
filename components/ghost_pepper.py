import os
import json
import glob
import re
from collections import Counter

class GhostPepper:
    def __init__(self, transcript_dir: str = None):
        self.transcript_dir = transcript_dir or os.getenv(
            "GHOST_PEPPER_TRANSCRIPT_DIR",
            os.path.expanduser("~/Documents/GhostPepper")
        )

    def process(self, data_json: str = None) -> str:
        """
        Process transcript text or read the latest transcript file.
        Returns JSON string with structured analysis.
        """
        if data_json and data_json.strip():
            transcript = data_json
        else:
            transcript = self._read_latest_transcript()

        headlines = self._extract_headlines(transcript)
        processed = {
            "headlines": headlines,
            "word_counts": len(transcript.split()),
            "top_terms": self._extract_top_terms(transcript),
            "transcript": transcript,
            "processed_by": "ghost_pepper"
        }
        return json.dumps(processed)

    def _read_latest_transcript(self) -> str:
        """Read the most recently modified .md file in transcript_dir."""
        if not os.path.isdir(self.transcript_dir):
            return "Sample meeting transcript: We discussed AI trends and new product features. The team agreed to focus on real-time data visualization."

        files = glob.glob(os.path.join(self.transcript_dir, "*.md"))
        if not files:
            return "No transcript found. Please provide audio input."

        latest = max(files, key=os.path.getmtime)
        with open(latest, 'r') as f:
            return f.read()

    def _extract_headlines(self, text: str) -> list:
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        return [s.strip() for s in sentences[:3] if s.strip()]

    def _extract_top_terms(self, text: str, n: int = 5) -> list:
        stopwords = {'the','a','an','is','of','to','in','and','for','on','with','we','our','this','that','it','as','at','by','be','are','was','were'}
        words = re.findall(r'\b\w+\b', text.lower())
        filtered = [w for w in words if w not in stopwords and len(w) > 2]
        return Counter(filtered).most_common(n)
