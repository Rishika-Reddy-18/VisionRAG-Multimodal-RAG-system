from multimodal.audio_transcriber import transcribe_audio


text = transcribe_audio("sample.mp3")

print("\nTRANSCRIBED TEXT:\n")

print(text)