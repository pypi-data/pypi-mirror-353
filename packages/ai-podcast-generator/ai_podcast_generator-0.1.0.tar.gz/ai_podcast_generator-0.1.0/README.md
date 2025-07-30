AI Podcast Generator
A Python package to generate AI-powered podcasts in Hindi, Marathi, or English using the Gemini API. Create engaging podcasts on any topic with customizable rounds and output options (save to MP3 or play immediately).
Installation
pip install ai-podcast-generator

Usage
from ai_podcast_generator import PodcastGenerator

# Initialize with your Gemini API key
pg = PodcastGenerator(api_key="YOUR_GEMINI_API_KEY", language="english")

# Generate a podcast
pg.run_podcast(
    topic="AngularJS vs ReactJS",
    num_rounds=2,
    output=True,  # Save to MP3
    output_path="angular_vs_react.mp3"
)

Features

Supports Hindi, Marathi, and English languages.
Customizable number of Q&A rounds.
Option to save podcast as MP3 or play immediately.
Uses Gemini AI for script generation and text-to-speech.

Requirements

Python 3.10+
Gemini API key
Dependencies: pyaudio, pydub, google-generativeai

License
MIT License
Contributing
Contributions welcome! Please open an issue or PR on GitHub.
