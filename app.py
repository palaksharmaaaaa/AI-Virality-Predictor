import os
import json
import traceback
import tempfile
import subprocess
import wave

import numpy as np
import imageio_ffmpeg

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
)
from werkzeug.utils import secure_filename
from ml.feature_builder import FeatureBuilder


from config.config import Config

from database.database import (
    init_db,
    save_analysis,
    get_all_analyses,
    get_analysis_by_id
)

from video.extractor import VideoFeatureExtractor
from video.transcript import transcribe_video
from video.thumbnail import generate_thumbnail

from content.content_analyzer import ContentAnalyzer
from creator.creator_analyzer import CreatorAnalyzer
from platform_analysis.platform_analyzer import PlatformAnalyzer,analyze_all_platforms
from hashtag.hashtag_analyzer import HashtagAnalyzer

from ml.predict import ViralityPredictor


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = getattr(
    Config,
    "SECRET_KEY",
    "ai-virality-predictor-secret-key"
)

UPLOAD_FOLDER = getattr(
    Config,
    "UPLOAD_FOLDER",
    os.path.join("data", "uploads")
)

ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm",
    "m4v"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

try:
    init_db()
except Exception:
    pass


# ============================================================
# FFmpeg
# ============================================================

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

FFMPEG_DIR = os.path.dirname(FFMPEG_PATH)

os.environ["PATH"] = (
    FFMPEG_DIR
    + os.pathsep
    + os.environ.get("PATH", "")
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def allowed_file(filename):
    """
    Check whether uploaded file has an allowed video extension.
    """
    if not filename:
        return False

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def safe_dict(value):
    """
    Always return a dictionary.
    """
    if isinstance(value, dict):
        return value

    return {}


def safe_float(value, default=0.0):
    """
    Convert value safely to float.
    """
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    """
    Convert value safely to integer.
    """
    try:
        return int(float(value))
    except Exception:
        return default


# ============================================================
# VIDEO ANALYSIS
# ============================================================

def analyze_video(video_path):
    try:
        extractor = VideoFeatureExtractor(video_path)

        # Your extractor.py uses extract()
        result = extractor.extract()

        if not isinstance(result, dict):
            return {}

        return result

    except Exception as error:
        print("Video extraction error:", error)
        return {}


# ============================================================
# AUDIO ANALYSIS
# ============================================================

def analyze_audio(video_path):
    """
    Extract basic audio characteristics.

    This includes:
    - audio availability
    - RMS energy
    - silence ratio
    - active audio ratio

    speech_ratio here is an activity-based estimate.
    It is NOT a dedicated speech classifier.
    """

    result = {
        "has_audio": 0,
        "audio_available": False,
        "audio_duration": 0.0,
        "rms_energy": 0.0,
        "silence_ratio": 1.0,
        "speech_ratio": 0.0,
        "music_ratio": 0.0
    }

    wav_path = None

    try:

        if not os.path.exists(video_path):
            return result

        wav_path = os.path.join(
            tempfile.gettempdir(),
            "virality_audio_analysis.wav"
        )

        command = [
            FFMPEG_PATH,
            "-y",
            "-i",
            video_path,
            "-map",
            "0:a:0",
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-acodec",
            "pcm_s16le",
            wav_path
        ]

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore"
        )

        if process.returncode != 0:
            return result

        if not os.path.exists(wav_path):
            return result

        with wave.open(wav_path, "rb") as wf:

            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_count = wf.getnframes()

            audio_bytes = wf.readframes(frame_count)

        if sample_width != 2:
            return result

        audio = np.frombuffer(
            audio_bytes,
            dtype=np.int16
        ).astype(np.float32)

        if channels > 1:

            audio = audio.reshape(
                -1,
                channels
            )

            audio = audio.mean(axis=1)

        if len(audio) == 0:
            return result

        audio = audio / 32768.0

        duration = len(audio) / float(sample_rate)

        rms = float(
            np.sqrt(
                np.mean(
                    np.square(audio)
                )
            )
        )

        # --------------------------------------------
        # Frame-based audio analysis
        # --------------------------------------------

        frame_size = int(sample_rate * 0.05)

        if frame_size <= 0:
            frame_size = 800

        frame_count = len(audio) // frame_size

        frame_rms = []

        for i in range(frame_count):

            frame = audio[
                i * frame_size:
                (i + 1) * frame_size
            ]

            if len(frame) == 0:
                continue

            frame_energy = float(
                np.sqrt(
                    np.mean(
                        np.square(frame)
                    )
                )
            )

            frame_rms.append(frame_energy)

        if frame_rms:

            frame_rms = np.array(
                frame_rms,
                dtype=np.float32
            )

            silence_threshold = max(
                0.005,
                rms * 0.20
            )

            silent_frames = np.sum(
                frame_rms < silence_threshold
            )

            total_frames = len(frame_rms)

            silence_ratio = (
                silent_frames / total_frames
                if total_frames > 0
                else 1.0
            )

            active_ratio = 1.0 - silence_ratio

        else:

            silence_ratio = 1.0
            active_ratio = 0.0

        result = {
            "has_audio": 1,
            "audio_available": True,
            "audio_duration": round(
                duration,
                2
            ),
            "rms_energy": round(
                rms,
                4
            ),
            "silence_ratio": round(
                silence_ratio,
                4
            ),

            # Activity-based estimate.
            "speech_ratio": round(
                active_ratio,
                4
            ),

            # No music classifier yet.
            "music_ratio": 0.0
        }

        return result

    except Exception:
        return result

    finally:

        if wav_path:

            try:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception:
                pass


# ============================================================
# TRANSCRIPT ANALYSIS
# ============================================================

def analyze_transcript(video_path):
    """
    Run Qwen3-ASR transcription silently.

    Transcript is returned to the application/UI
    but is NOT printed in the terminal.
    """

    try:

        result = transcribe_video(video_path)

        if not isinstance(result, dict):

            return {
                "success": False,
                "transcript": "",
                "language": "unknown",
                "segments": [],
                "error": "Invalid transcript result"
            }

        transcript = (
            result.get("transcript", "")
            or ""
        ).strip()

        result["transcript"] = transcript

        return result

    except Exception as error:

        return {
            "success": False,
            "transcript": "",
            "language": "unknown",
            "segments": [],
            "error": str(error)
        }


# ============================================================
# CONTENT ANALYSIS
# ============================================================

def analyze_content(transcript, duration=0):
    try:
        transcript = transcript or ""

        analyzer = ContentAnalyzer(
            transcript=transcript,
            duration=duration
        )

        content_features = analyzer.analyze()

        if not isinstance(
            content_features,
            dict
        ):
            content_features = {}

        return content_features

    except Exception:
        return {}


# ============================================================
# CREATOR ANALYSIS
# ============================================================

def analyze_creator(
    followers,
    following,
    creator_category
):
    """
    Analyze creator profile.
    """

    try:

        analyzer = CreatorAnalyzer(
            followers=followers,
            following=following,
            creator_category=creator_category
        )

        result = analyzer.analyze()

        if not isinstance(result, dict):
            return {}

        return result

    except Exception:
        return {}


# ============================================================
# PLATFORM ANALYSIS
# ============================================================

def analyze_platform(
    platform,
    width,
    height,
    duration
):
    """
    Analyze platform compatibility.
    """

    try:

        analyzer = PlatformAnalyzer(
            platform=platform,
            width=width,
            height=height,
            duration=duration
        )

        result = analyzer.analyze()

        if not isinstance(result, dict):
            return {}

        return result

    except Exception:
        return {}



# ============================================================
# PLATFORM-WISE VIRALITY PREDICTION
# ============================================================

def analyze_all_platform_predictions(
    video_features,
    prediction,
    category="general"
):
    """
    Generate platform-wise virality estimates.

    The overall ML prediction is used as the baseline.
    PlatformAnalyzer then adjusts the baseline according
    to platform/video-format compatibility.
    """

    video_features = safe_dict(video_features)
    prediction = safe_dict(prediction)

    duration = safe_float(
        video_features.get(
            "duration",
            0
        )
    )

    width = safe_int(
        video_features.get(
            "width",
            0
        )
    )

    height = safe_int(
        video_features.get(
            "height",
            0
        )
    )

    base_score = safe_float(
        prediction.get(
            "virality_score",
            0
        )
    )

    estimated_views = safe_float(
        prediction.get(
            "estimated_views",
            0
        )
    )

    try:

        return analyze_all_platforms(
            duration=duration,
            width=width,
            height=height,
            base_virality_score=base_score,
            overall_estimated_views=estimated_views,
            category=category
        )

    except Exception as error:

        print(
            "Platform-wise prediction error:",
            error
        )

        return {}




# ============================================================
# HASHTAG ANALYSIS
# ============================================================

def analyze_hashtags(
    hashtags,
    category
):
    """
    Analyze hashtags.
    """

    try:

        analyzer = HashtagAnalyzer(
            hashtags=hashtags,
            category=category
        )

        result = analyzer.analyze()

        if not isinstance(result, dict):
            return {}

        return result

    except Exception:
        return {}


# ============================================================
# RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    video_features,
    audio_features,
    content_features,
    creator_features,
    platform_features,
    hashtag_features
):
    """
    Generate human-readable recommendations
    based on extracted features.
    """

    recommendations = []

    video_features = safe_dict(video_features)
    audio_features = safe_dict(audio_features)
    content_features = safe_dict(content_features)
    creator_features = safe_dict(creator_features)
    platform_features = safe_dict(platform_features)
    hashtag_features = safe_dict(hashtag_features)

    # --------------------------------------------
    # Duration
    # --------------------------------------------

    duration = safe_float(
        video_features.get("duration", 0)
    )

    if duration > 60:

        recommendations.append(
            "Consider keeping the video shorter for better short-form engagement."
        )

    elif duration > 0 and duration < 5:

        recommendations.append(
            "The video is very short; consider adding enough context to make the hook meaningful."
        )

    # --------------------------------------------
    # Hook
    # --------------------------------------------

    hook_intensity = safe_float(
        video_features.get(
            "hook_intensity",
            0
        )
    )

    content_hook_score = safe_float(
        content_features.get(
            "hook_score",
            0
        )
    )

    if hook_intensity < 30 and content_hook_score < 30:

        recommendations.append(
            "Improve the first few seconds with a stronger visual or verbal hook."
        )

    # --------------------------------------------
    # Motion
    # --------------------------------------------

    motion_score = safe_float(
        video_features.get(
            "motion_score",
            0
        )
    )

    if motion_score < 5:

        recommendations.append(
            "The video has relatively low visual motion. Consider adding movement or faster visual changes where appropriate."
        )

    # --------------------------------------------
    # Scene changes
    # --------------------------------------------

    scene_changes = safe_int(
        video_features.get(
            "scene_changes",
            0
        )
    )

    if duration > 10 and scene_changes <= 1:

        recommendations.append(
            "Consider adding meaningful scene or visual changes to maintain attention."
        )

    # --------------------------------------------
    # Audio
    # --------------------------------------------

    if not audio_features.get(
        "audio_available",
        False
    ):

        recommendations.append(
            "No audio track was detected. Consider adding relevant audio, narration, or captions."
        )

    silence_ratio = safe_float(
        audio_features.get(
            "silence_ratio",
            0
        )
    )

    if silence_ratio > 0.50:

        recommendations.append(
            "A large portion of the audio is silent. Consider reducing unnecessary silence."
        )

    # --------------------------------------------
    # Transcript
    # --------------------------------------------

    word_count = safe_int(
        content_features.get(
            "word_count",
            0
        )
    )

    cta_score = safe_float(
        content_features.get(
            "cta_score",
            0
        )
    )

    transcript_quality = safe_float(
        content_features.get(
            "transcript_quality",
            0
        )
    )

    if word_count == 0:

        recommendations.append(
            "No usable speech transcript was detected. Consider adding clear narration or captions if the content depends on speech."
        )

    elif transcript_quality < 40:

        recommendations.append(
            "Speech transcription quality is low. Clearer audio and speech can improve content analysis."
        )

    if word_count > 0 and cta_score < 30:

        recommendations.append(
            "Consider adding a clear call-to-action such as follow, comment, save, or share."
        )

    # --------------------------------------------
    # Creator
    # --------------------------------------------

    followers = safe_int(
        creator_features.get(
            "followers",
            0
        )
    )

    if followers < 1000:

        recommendations.append(
            "For a smaller creator account, focus on niche relevance and consistent audience engagement."
        )

    # --------------------------------------------
    # Hashtags
    # --------------------------------------------

    hashtag_count = safe_int(
        hashtag_features.get(
            "hashtag_count",
            0
        )
    )

    if hashtag_count == 0:

        recommendations.append(
            "Consider using a small set of relevant and specific hashtags."
        )

    elif hashtag_count > 30:

        recommendations.append(
            "The number of hashtags is high. Focus on highly relevant hashtags instead of excessive tagging."
        )

    # --------------------------------------------
    # Platform
    # --------------------------------------------

    compatibility = safe_float(
        platform_features.get(
            "format_compatibility",
            0
        )
    )

    if compatibility < 50:

        recommendations.append(
            "Consider adjusting the video format, orientation, or duration for the selected platform."
        )

    # --------------------------------------------
    # Default
    # --------------------------------------------

    if not recommendations:

        recommendations.append(
            "The video has a reasonable combination of technical, content, and platform features. Continue testing different hooks and formats."
        )

    return recommendations


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def perform_complete_analysis(
    video_path,
    platform,
    followers,
    following,
    creator_category,
    hashtags
):
    """
    Run the complete video analysis pipeline.
    """

    # --------------------------------------------------------
    # 1. VIDEO
    # --------------------------------------------------------

    video_features = analyze_video(
        video_path
    )

    video_features = safe_dict(
        video_features
    )

    # --------------------------------------------------------
    # 2. AUDIO
    # --------------------------------------------------------

    audio_features = analyze_audio(
        video_path
    )

    audio_features = safe_dict(
        audio_features
    )

    # --------------------------------------------------------
    # 3. TRANSCRIPT
    # --------------------------------------------------------

    transcript_result = analyze_transcript(
        video_path
    )

    transcript_result = safe_dict(
        transcript_result
    )

    transcript = (
        transcript_result.get(
            "transcript",
            ""
        )
        or ""
    ).strip()

# --------------------------------------------------------
    # 4. CONTENT
    # --------------------------------------------------------

    duration = safe_float(
        video_features.get(
            "duration",
            0
        )
    )

    content_features = analyze_content(
        transcript,
        duration=duration
    )

    content_features = safe_dict(
        content_features
    )

    # --------------------------------------------------------
    # 5. CREATOR
    # --------------------------------------------------------

    creator_features = analyze_creator(
        followers,
        following,
        creator_category
    )

    creator_features = safe_dict(
        creator_features
    )

    # --------------------------------------------------------
    # 6. PLATFORM
    # --------------------------------------------------------

    width = safe_int(
        video_features.get(
            "width",
            0
        )
    )

    height = safe_int(
        video_features.get(
            "height",
            0
        )
    )

   

    platform_features = analyze_platform(
        platform,
        width,
        height,
        duration
    )

    platform_features = safe_dict(
        platform_features
    )

    # --------------------------------------------------------
    # 7. HASHTAGS
    # --------------------------------------------------------

    category = content_features.get(
        "category",
        "general"
    )

    hashtag_features = analyze_hashtags(
        hashtags,
        category
    )

    hashtag_features = safe_dict(
        hashtag_features
    )

    # --------------------------------------------------------
    # 8. ML PREDICTION
    # --------------------------------------------------------

    prediction = {}

    try:

        # Create feature builder
        feature_builder = FeatureBuilder()

        # Combine all analysis modules using the
        # same feature structure expected by the model
        combined_features = feature_builder.build(
            video_features=video_features,
            audio_features=audio_features,
            content_features=content_features,
            creator_features=creator_features,
            platform_features=platform_features,
            hashtag_features=hashtag_features
        )

        # Create predictor
        predictor = ViralityPredictor()

        # Run ML prediction
        prediction = predictor.predict(
            combined_features
        )

        if not isinstance(
            prediction,
            dict
        ):
            prediction = {}

    except Exception as error:

        print(
            "ML prediction error:",
            error
        )

        traceback.print_exc()

        prediction = {}



    # --------------------------------------------------------
    # 9. PLATFORM-WISE VIRALITY PREDICTION
    # --------------------------------------------------------

    platform_predictions = analyze_all_platform_predictions(
        video_features=video_features,
        prediction=prediction,
        category=category
    )

    platform_predictions = safe_dict(
        platform_predictions
    )



    # --------------------------------------------------------
    # 10. RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = generate_recommendations(
        video_features,
        audio_features,
        content_features,
        creator_features,
        platform_features,
        hashtag_features
    )

    # --------------------------------------------------------
    # 11. FINAL RESULT
    # --------------------------------------------------------

    analysis = {

        "video_features": video_features,

        "audio_features": audio_features,

        "transcript_result":transcript_result,

        "transcript":transcript,

        "content_features": content_features,

        "creator_features": creator_features,

        "platform_features": platform_features,

        "platform_predictions": platform_predictions,

        "hashtag_features": hashtag_features,

        "prediction": prediction,

        "recommendations":  recommendations
    }

    return analysis


# ============================================================
# index
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# ANALYZE VIDEO
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    if "video" not in request.files:

        flash(
            "Please select a video file."
        )

        return redirect(
            url_for("index")
        )

    video_file = request.files[
        "video"
    ]

    if not video_file or not video_file.filename:

        flash(
            "No video file was selected."
        )

        return redirect(
            url_for("index")
        )

    if not allowed_file(
        video_file.filename
    ):

        flash(
            "Unsupported video format."
        )

        return redirect(
            url_for("index")
        )

    # --------------------------------------------------------
    # Social media information
    # --------------------------------------------------------

    platform = (
        request.form.get(
            "platform",
            "instagram"
        )
        or "instagram"
    ).strip().lower()

    followers = safe_int(
        request.form.get(
            "followers",
            0
        )
    )

    following = safe_int(
        request.form.get(
            "following",
            0
        )
    )

    creator_category = (
        request.form.get(
            "creator_category",
            "general"
        )
        or "general"
    ).strip().lower()

    hashtags_text = (
        request.form.get(
            "hashtags",
            ""
        )
        or ""
    )

    hashtags = [
        tag.strip()
        for tag in hashtags_text.split()
        if tag.strip()
    ]

    # --------------------------------------------------------
    # Save uploaded video
    # --------------------------------------------------------

    original_filename = secure_filename(
        video_file.filename
    )

    video_path = os.path.join(
        UPLOAD_FOLDER,
        original_filename
    )

    try:

        video_file.save(
            video_path
        )

    except Exception as error:

        flash(
            f"Could not save video: {error}"
        )

        return redirect(
            url_for("index")
        )

    # --------------------------------------------------------
    # Complete analysis
    # --------------------------------------------------------

    try:

        analysis = perform_complete_analysis(
            video_path=video_path,
            platform=platform,
            followers=followers,
            following=following,
            creator_category=creator_category,
            hashtags=hashtags
        )
        print("VIDEO FEATURES:", analysis.get("video_features", {}))

    except Exception as error:

        traceback.print_exc()

        flash(
            f"Video analysis failed: {error}"
        )

        return redirect(
            url_for("index")
        )

    # --------------------------------------------------------
    # Thumbnail
    # --------------------------------------------------------

    thumbnail = None

    try:

        thumbnail = generate_thumbnail(
            video_path
        )

    except Exception:

        thumbnail = None

    # --------------------------------------------------------
    # Save database record
    # --------------------------------------------------------

    try:

        analysis_id = save_analysis(
            filename=original_filename,
            analysis_data=analysis
        )

    except TypeError:

        # Compatibility with alternate save_analysis
        # implementations.

        try:

            analysis_id = save_analysis(
                original_filename,
                json.dumps(
                    analysis,
                    default=str
                )
            )

        except Exception:

            analysis_id = None

    except Exception:

        analysis_id = None

    # --------------------------------------------------------
    # Render result
    # --------------------------------------------------------

    return render_template(
        "result.html",

        filename=original_filename,

        thumbnail=thumbnail,

        prediction=analysis.get(
            "prediction",
            {}
        ),
        platform_predictions=analysis.get(
            "platform_predictions",
            {}
        ),

        features=analysis.get(
            "video_features",
            {}
        ),

        audio_features=analysis.get(
            "audio_features",
            {}
        ),

        content_features=analysis.get(
            "content_features",
            {}
        ),

        transcript=analysis.get(
            "transcript",
            ""
        ),
        transcript_result=analysis.get(
            "transcript_result",
            {}
        ),


        creator_features=analysis.get(
            "creator_features",
            {}
        ),

        platform_features=analysis.get(
            "platform_features",
            {}
        ),

        hashtag_features=analysis.get(
            "hashtag_features",
            {}
        ),

        recommendations=analysis.get(
            "recommendations",
            []
        ),

        analysis_id=analysis_id
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    try:

        analyses = get_all_analyses()

    except Exception:

        analyses = []

    return render_template(
        "history.html",
        analyses=analyses
    )


# ============================================================
# SINGLE ANALYSIS
# ============================================================

@app.route(
    "/analysis/<int:analysis_id>"
)
def analysis_detail(
    analysis_id
):

    try:

        record = get_analysis_by_id(
            analysis_id
        )

    except Exception:

        record = None

    if not record:

        flash(
            "Analysis not found."
        )

        return redirect(
            url_for("history")
        )

    # --------------------------------------------------------
    # Handle dictionary record
    # --------------------------------------------------------

    if isinstance(
        record,
        dict
    ):

        analysis_data = record.get(
            "analysis_data",
            record.get(
                "data",
                {}
            )
        )

        if isinstance(
            analysis_data,
            str
        ):

            try:
                analysis_data = json.loads(
                    analysis_data
                )
            except Exception:
                analysis_data = {}

        if not isinstance(
            analysis_data,
            dict
        ):
            analysis_data = {}

        filename = record.get(
            "filename",
            "Video"
        )

    else:

        analysis_data = {}
        filename = "Video"

    return render_template(
        "result.html",

        filename=filename,

        thumbnail=None,

        prediction=analysis_data.get(
            "prediction",
            {}
        ),

        platform_predictions=analysis_data.get(
            "platform_predictions",
            {}
        ),
        features=analysis_data.get(
            "video_features",
            {}
        ),

        audio_features=analysis_data.get(
            "audio_features",
            {}
        ),

        content_features=analysis_data.get(
            "content_features",
            {}
        ),

        transcript=analysis_data.get(
            "transcript",
            ""
        ),


        creator_features=analysis_data.get(
            "creator_features",
            {}
        ),

        platform_features=analysis_data.get(
            "platform_features",
            {}
        ),

        hashtag_features=analysis_data.get(
            "hashtag_features",
            {}
        ),

        recommendations=analysis_data.get(
            "recommendations",
            []
        ),

        analysis_id=analysis_id
    )


# ============================================================
# API - SINGLE ANALYSIS
# ============================================================

@app.route(
    "/api/analysis/<int:analysis_id>"
)
def api_analysis(
    analysis_id
):

    try:

        record = get_analysis_by_id(
            analysis_id
        )

        if not record:

            return jsonify({
                "success": False,
                "error": "Analysis not found"
            }), 404

        if isinstance(
            record,
            dict
        ):

            analysis_data = record.get(
                "analysis_data",
                record.get(
                    "data",
                    {}
                )
            )

            if isinstance(
                analysis_data,
                str
            ):

                try:

                    analysis_data = json.loads(
                        analysis_data
                    )

                except Exception:

                    analysis_data = {}

        else:

            analysis_data = {}

        return jsonify({
            "success": True,
            "analysis_id": analysis_id,
            "data": analysis_data
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API - ALL HISTORY
# ============================================================

@app.route(
    "/api/history"
)
def api_history():

    try:

        analyses = get_all_analyses()

        return jsonify({
            "success": True,
            "data": analyses
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/report/<int:analysis_id>")
def report(analysis_id):

    try:
        # =========================================================
        # GET ANALYSIS
        # =========================================================

        analysis = get_analysis_by_id(analysis_id)
       
        if not analysis:
            flash("Analysis record not found.")
            return redirect(url_for("history"))

        # =========================================================
        # IMPORTS
        # =========================================================

        import os
        import json
        from datetime import datetime

        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )

        # =========================================================
        # FIND PROJECT ROOT
        # =========================================================

        project_root = os.path.dirname(
            os.path.abspath(__file__)
        )

        reports_dir = os.path.join(
            project_root,
            "reports"
        )

        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        # =========================================================
        # PDF PATH
        # =========================================================

        pdf_filename = (
            f"virality_report_{analysis_id}.pdf"
        )

        pdf_path = os.path.join(
            reports_dir,
            pdf_filename
        )

        # =========================================================
        # DEBUG
        # =========================================================

        print("=" * 60)
        print("GENERATING PDF REPORT")
        print("Analysis ID:", analysis_id)
        print("Analysis type:", type(analysis))
        print("PDF path:", pdf_path)
        print("=" * 60)

        

        # =========================================================
        # READ ANALYSIS DATA
        # =========================================================

        if isinstance(analysis, dict):

            # get_analysis_by_id() returns:
            # {
            #     "id": ...,
            #     "filename": ...,
            #     "timestamp": ...,
            #     "analysis_data": {...}
            # }

            analysis_data = analysis.get(
                "analysis_data",
                {}
            )

        else:

            # -----------------------------------------------------
            # Object based result
            # -----------------------------------------------------

            if hasattr(
                analysis,
                "analysis_data"
            ):

                raw_data = analysis.analysis_data

                if isinstance(
                    raw_data,
                    str
                ):

                    try:

                        analysis_data = json.loads(
                            raw_data
                        )

                    except Exception:

                        analysis_data = {}

                elif isinstance(
                    raw_data,
                    dict
                ):

                    analysis_data = raw_data

                else:

                    analysis_data = {}

            else:

                analysis_data = {}


        if not isinstance(
            analysis_data,
            dict
        ):

            analysis_data = {}


        print("=" * 60)
        print("PDF DATA EXTRACTED")
        print("Video Features:", analysis_data.get("video_features", {}))
        print("Prediction:", analysis_data.get("prediction", {}))
        print("Audio Features:", analysis_data.get("audio_features", {}))
        print("=" * 60)

        # =========================================================
        # EXTRACT DATA
        # =========================================================

        prediction = analysis_data.get(
            "prediction",
            {}
        )

        video_features = analysis_data.get(
            "video_features",
            {}
        )

        audio_features = analysis_data.get(
            "audio_features",
            {}
        )

        content_features = analysis_data.get(
            "content_features",
            {}
        )

        platform_predictions = analysis_data.get(
            "platform_predictions",
            {}
        )

        transcript = analysis_data.get(
            "transcript",
            ""
        )

        recommendations = analysis_data.get(
            "recommendations",
            []
        )

        # Safety

        if not isinstance(
            prediction,
            dict
        ):
            prediction = {}

        if not isinstance(
            video_features,
            dict
        ):
            video_features = {}

        if not isinstance(
            audio_features,
            dict
        ):
            audio_features = {}

        if not isinstance(
            content_features,
            dict
        ):
            content_features = {}

        if not isinstance(
            platform_predictions,
            dict
        ):
            platform_predictions = {}

        # =========================================================
        # DOCUMENT
        # =========================================================

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,

            rightMargin=40,
            leftMargin=40,

            topMargin=40,
            bottomMargin=40,

            title=(
                f"AI Virality Predictor "
                f"Report {analysis_id}"
            )
        )

        styles = getSampleStyleSheet()

        story = []

        # =========================================================
        # TITLE
        # =========================================================

        story.append(
            Paragraph(
                "AI Virality Predictor",
                styles["Title"]
            )
        )

        story.append(
            Paragraph(
                "Video Analysis Report",
                styles["Heading2"]
            )
        )

        story.append(
            Spacer(1, 15)
        )

        story.append(
            Paragraph(
                f"<b>Analysis ID:</b> "
                f"{analysis_id}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Generated:</b> "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1, 20)
        )

        # =========================================================
        # OVERALL VIRALITY PREDICTION
        # =========================================================

        story.append(
            Paragraph(
                "Virality Prediction",
                styles["Heading2"]
            )
        )

        virality_score = prediction.get(
            "virality_score",
            0
        )

        estimated_views = prediction.get(
            "estimated_views",
            0
        )

        prediction_label = prediction.get(
            "prediction_label",
            prediction.get(
                "virality_label",
                "Unknown"
            )
        )

        model_name = prediction.get(
            "model_type",
            prediction.get(
                "model_name",
                prediction.get(
                    "model",
                    "Unknown"
                )
            )
        )

        prediction_data = [
            ["Metric", "Value"],

            [
                "Virality Score",
                f"{virality_score} / 100"
            ],

            [
                "Prediction Label",
                str(prediction_label)
            ],

            [
                "Estimated Views",
                f"{int(float(estimated_views or 0)):,}"
            ],

            [
                "Model",
                str(model_name)
            ]
        ]

        table = Table(
            prediction_data,
            colWidths=[
                220,
                250
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(table)

        story.append(
            Spacer(1, 20)
        )

        # =========================================================
        # VIDEO ANALYSIS
        # =========================================================

        story.append(
            Paragraph(
                "Video Analysis",
                styles["Heading2"]
            )
        )

        video_data = [
            ["Feature", "Value"],

            [
                "Duration",
                f"{video_features.get('duration', 0)} sec"
            ],

            [
                "FPS",
                str(
                    video_features.get(
                        "fps",
                        0
                    )
                )
            ],

            [
                "Resolution",
                f"{video_features.get('width', 0)} x "
                f"{video_features.get('height', 0)}"
            ],

            [
                "Motion Score",
                str(
                    video_features.get(
                        "motion_score",
                        0
                    )
                )
            ],

            [
                "Scene Changes",
                str(
                    video_features.get(
                        "scene_changes",
                        0
                    )
                )
            ],

            [
                "Scene Change Rate",
                str(
                    video_features.get(
                        "scene_change_rate",
                        0
                    )
                )
            ],

            [
                "Hook Intensity",
                str(
                    video_features.get(
                        "hook_intensity",
                        0
                    )
                )
            ],

            [
                "Person Count",
                str(
                    video_features.get(
                        "person_count",
                        0
                    )
                )
            ],

            [
                "Face Count",
                str(
                    video_features.get(
                        "face_count",
                        0
                    )
                )
            ],

            [
                "Face Presence",
                str(
                    video_features.get(
                        "face_presence_ratio",
                        0
                    )
                )
            ],

            [
                "Brightness",
                str(
                    video_features.get(
                        "brightness",
                        0
                    )
                )
            ],

            [
                "Contrast",
                str(
                    video_features.get(
                        "contrast",
                        0
                    )
                )
            ],

            [
                "Pacing Score",
                str(
                    video_features.get(
                        "pacing_score",
                        0
                    )
                )
            ]
        ]

        table = Table(
            video_data,
            colWidths=[
                220,
                250
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(table)

        story.append(
            Spacer(1, 20)
        )

        # =========================================================
        # AUDIO ANALYSIS
        # =========================================================

        story.append(
            Paragraph(
                "Audio Analysis",
                styles["Heading2"]
            )
        )

        audio_data = [
            ["Feature", "Value"],

            [
                "Audio Available",
                str(
                    audio_features.get(
                        "audio_available",
                        "N/A"
                    )
                )
            ],

            [
                "Speech Ratio",
                str(
                    audio_features.get(
                        "speech_ratio",
                        0
                    )
                )
            ],

            [
                "Silence Ratio",
                str(
                    audio_features.get(
                        "silence_ratio",
                        0
                    )
                )
            ],

            [
                "Music Ratio",
                str(
                    audio_features.get(
                        "music_ratio",
                        0
                    )
                )
            ]
        ]

        table = Table(
            audio_data,
            colWidths=[
                220,
                250
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(table)

        story.append(
            Spacer(1, 20)
        )

        # =========================================================
        # CONTENT ANALYSIS
        # =========================================================

        story.append(
            Paragraph(
                "Content & Transcript Analysis",
                styles["Heading2"]
            )
        )

        content_data = [
            ["Feature", "Value"],

            [
                "Word Count",
                str(
                    content_features.get(
                        "word_count",
                        0
                    )
                )
            ],

            [
                "Sentence Count",
                str(
                    content_features.get(
                        "sentence_count",
                        0
                    )
                )
            ],

            [
                "Vocabulary Diversity",
                str(
                    content_features.get(
                        "vocabulary_diversity",
                        0
                    )
                )
            ],

            [
                "Hook Score",
                str(
                    content_features.get(
                        "hook_score",
                        0
                    )
                )
            ],

            [
                "CTA Score",
                str(
                    content_features.get(
                        "cta_score",
                        0
                    )
                )
            ],

            [
                "Sentiment Score",
                str(
                    content_features.get(
                        "sentiment_score",
                        0
                    )
                )
            ],

            [
                "Transcript Quality",
                str(
                    content_features.get(
                        "transcript_quality",
                        0
                    )
                )
            ]
        ]

        table = Table(
            content_data,
            colWidths=[
                220,
                250
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(table)

        # =========================================================
        # TRANSCRIPT
        # =========================================================

        if transcript:

            story.append(
                Spacer(1, 15)
            )

            story.append(
                Paragraph(
                    "Transcript",
                    styles["Heading2"]
                )
            )

            # ReportLab's default Helvetica does not support
            # Hindi/Devanagari reliably.
            # Therefore keep transcript in a safe basic form
            # if Unicode rendering is unavailable.

            safe_transcript = (
                str(transcript)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            story.append(
                Paragraph(
                    safe_transcript,
                    styles["Normal"]
                )
            )

        # =========================================================
        # PLATFORM-WISE VIRALITY
        # =========================================================

        if platform_predictions:

            story.append(
                Spacer(1, 25)
            )

            story.append(
                Paragraph(
                    "Platform-wise Virality Prediction",
                    styles["Heading2"]
                )
            )

            platform_rows = [
                [
                    "Platform",
                    "Score",
                    "Estimated Reach",
                    "Compatibility"
                ]
            ]

            platform_names = {
                "instagram": "Instagram",
                "youtube": "YouTube",
                "tiktok": "TikTok",
                "facebook": "Facebook"
            }

            for (
                platform_key,
                platform_data
            ) in platform_predictions.items():

                if not isinstance(
                    platform_data,
                    dict
                ):
                    continue

                score = platform_data.get(
                    "virality_score",
                    0
                )

                reach = platform_data.get(
                    "estimated_reach",
                    0
                )

                compatibility = platform_data.get(
                    "format_compatibility",
                    0
                )

                platform_rows.append(
                    [
                        platform_names.get(
                            platform_key,
                            platform_key.title()
                        ),

                        f"{score} / 100",

                        f"{int(float(reach or 0)):,}",

                        f"{compatibility} / 100"
                    ]
                )

            if len(platform_rows) > 1:

                table = Table(
                    platform_rows,
                    colWidths=[
                        120,
                        100,
                        150,
                        100
                    ]
                )

                table.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey
                        ),

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey
                        ),

                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            8
                        )
                    ])
                )

                story.append(table)

        # =========================================================
        # RECOMMENDATIONS
        # =========================================================

        if recommendations:

            story.append(
                Spacer(1, 20)
            )

            story.append(
                Paragraph(
                    "Recommendations",
                    styles["Heading2"]
                )
            )

            if isinstance(
                recommendations,
                list
            ):

                for recommendation in recommendations:

                    if isinstance(
                        recommendation,
                        dict
                    ):

                        recommendation_text = (
                            recommendation.get(
                                "text",
                                recommendation.get(
                                    "recommendation",
                                    str(recommendation)
                                )
                            )
                        )

                    else:

                        recommendation_text = str(
                            recommendation
                        )

                    story.append(
                        Paragraph(
                            "• " +
                            str(
                                recommendation_text
                            ),
                            styles["Normal"]
                        )
                    )

                    story.append(
                        Spacer(1, 5)
                    )

        # =========================================================
        # FINAL NOTE
        # =========================================================

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                "This report contains automatically "
                "extracted video characteristics, "
                "audio/content analysis, platform-adjusted "
                "estimates and machine-learning prediction "
                "results.",
                styles["Normal"]
            )
        )

        # =========================================================
        # BUILD PDF
        # =========================================================

        doc.build(story)

        # =========================================================
        # CHECK PDF
        # =========================================================

        if not os.path.exists(pdf_path):

            raise RuntimeError(
                "PDF file was not created."
            )

        file_size = os.path.getsize(
            pdf_path
        )

        print(
            "PDF generated successfully:"
        )

        print(
            "Path:",
            pdf_path
        )

        print(
            "Size:",
            file_size,
            "bytes"
        )

        if file_size == 0:

            raise RuntimeError(
                "Generated PDF file is empty."
            )

        # =========================================================
        # SEND PDF TO BROWSER
        # =========================================================

        return send_file(
            pdf_path,

            as_attachment=True,

            download_name=pdf_filename,

            mimetype="application/pdf"
        )

    except Exception as error:

        import traceback

        print("=" * 60)
        print("PDF REPORT ERROR")
        print("=" * 60)

        traceback.print_exc()

        flash(
            f"PDF report generation failed: {error}"
        )

        return redirect(
            url_for(
                "analysis_detail",
                analysis_id=analysis_id
            )
        )

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health"
)
def health():

    return jsonify({
        "status": "ok",
        "application":
            "AI Virality Predictor"
    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )