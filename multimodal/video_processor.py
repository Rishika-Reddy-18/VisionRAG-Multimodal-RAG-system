import os
from moviepy.editor import VideoFileClip


def extract_audio(video_path, audio_path=None):

    os.makedirs("uploads", exist_ok=True)

    if audio_path is None:
        audio_path = video_path.replace(".mp4", ".wav")

    video = VideoFileClip(video_path)

    if video.audio is None:
        return None

    video.audio.write_audiofile(audio_path, logger=None)

    return audio_path