import os
import tempfile
import subprocess
import torch

from transformers import (
    AutoProcessor,
    AutoModelForMultimodalLM
)


# ============================================================
# QWEN3-ASR CONFIGURATION
# ============================================================

MODEL_ID = "Qwen/Qwen3-ASR-0.6B-hf"

_processor = None
_model = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_qwen_model():

    global _processor
    global _model

    if _processor is not None and _model is not None:
        return _processor, _model

    print("=" * 60)
    print("Loading Qwen3-ASR")
    print("Model:", MODEL_ID)
    print("=" * 60)

    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
        print("Device: CUDA")
    else:
        device = "cpu"
        dtype = torch.float32
        print("Device: CPU")

    print("Loading processor...")

    _processor = AutoProcessor.from_pretrained(
        MODEL_ID
    )

    print("Loading model...")

    _model = AutoModelForMultimodalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype
    )

    _model.to(device)

    _model.eval()

    print("Qwen3-ASR loaded successfully.")

    return _processor, _model


# ============================================================
# EXTRACT AUDIO FROM VIDEO
# ============================================================

def extract_audio(video_path):

    temp_wav = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    temp_wav.close()

    output_path = temp_wav.name

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        output_path
    ]

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                "FFmpeg audio extraction failed:\n"
                + result.stderr
            )

        return output_path

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpeg was not found. "
            "Please install FFmpeg and add it to PATH."
        )


# ============================================================
# TRANSCRIBE AUDIO
# ============================================================

def transcribe_audio(audio_path):

    processor, model = load_qwen_model()

    device = model.device

    print("=" * 60)
    print("Transcribing audio with Qwen3-ASR")
    print("Audio:", audio_path)
    print("=" * 60)

    # Qwen processor creates the transcription request
    inputs = processor.apply_transcription_request(
        audio=audio_path
    )

    inputs = inputs.to(
        device,
        model.dtype
    )

    with torch.no_grad():

        output_ids = model.generate(
            **inputs,
            max_new_tokens=512
        )

    generated_ids = output_ids[
        :,
        inputs["input_ids"].shape[1]:
    ]

    raw_text = processor.decode(
        generated_ids
    )[0]

    # Extract clean transcript
    try:

        transcript = processor.extract_transcription(
            raw_text
        )

    except Exception:

        transcript = raw_text

    transcript = transcript or ""

    # Remove Qwen special tokens
    transcript = transcript.replace("<|im_end|>", "")
    transcript = transcript.replace("<|endoftext|>", "")

    transcript = transcript.strip()

    return transcript


# ============================================================
# MAIN VIDEO TRANSCRIPTION FUNCTION
# ============================================================

def transcribe_video(
    video_path,
    model_name=MODEL_ID
):

    if not video_path:

        return {
            "success": False,
            "transcript": "",
            "text": "",
            "language": "unknown",
            "segments": [],
            "error": "No video path provided."
        }

    if not os.path.exists(video_path):

        return {
            "success": False,
            "transcript": "",
            "text": "",
            "language": "unknown",
            "segments": [],
            "error": f"Video not found: {video_path}"
        }

    audio_path = None

    try:

        print("=" * 60)
        print("Starting Qwen3-ASR transcription")
        print("Video:", video_path)
        print("Model:", MODEL_ID)
        print("=" * 60)

        # ----------------------------------------------------
        # STEP 1: Extract audio
        # ----------------------------------------------------

        print("Extracting audio...")

        audio_path = extract_audio(
            video_path
        )

        print(
            "Audio extracted:",
            audio_path
        )

        # ----------------------------------------------------
        # STEP 2: Transcribe
        # ----------------------------------------------------

        transcript = transcribe_audio(
            audio_path
        )

        print("=" * 60)
        print("Transcription completed")
        print("Characters:", len(transcript))
        print("Words:", len(transcript.split()))
        print("Transcript:", transcript)
        print("=" * 60)

        return {

            "success": bool(transcript),

            "transcript": transcript,

            # Keep "text" for compatibility
            # with older code
            "text": transcript,

            "language": "auto",

            "segments": [],

            "error": None
        }

    except Exception as error:

        print("=" * 60)
        print("Qwen3-ASR transcription failed")
        print("Error:", error)
        print("=" * 60)

        return {

            "success": False,

            "transcript": "",

            "text": "",

            "language": "unknown",

            "segments": [],

            "error": str(error)
        }

    finally:

        # ----------------------------------------------------
        # Remove temporary WAV
        # ----------------------------------------------------

        if audio_path:

            try:

                if os.path.exists(
                    audio_path
                ):
                    os.remove(
                        audio_path
                    )

            except Exception:

                pass