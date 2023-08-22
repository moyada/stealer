import ffmpeg


def concat(video_path: str, audio_path: str, output_path: str):
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)
    ffmpeg.output(input_video.video, input_audio.audio, output_path).run(overwrite_output=True, capture_stdout=True)

