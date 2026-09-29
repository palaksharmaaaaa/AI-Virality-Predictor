import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_file,
    flash
)
import random
from config.config import (
    UPLOAD_FOLDER,
    THUMBNAIL_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH
)

from database.database import (
    initialize_database,
    save_analysis,
    get_analysis,
    get_all_analyses
)

from utils.helpers import allowed_file, unique_filename

from video.extractor import extract_video_features
from video.thumbnail import generate_thumbnail

from ml.predict import predict_virality

from recommendations.recommender import generate_recommendations
from reports.report_generator import generate_report


app = Flask(__name__)

app.secret_key = "ai-virality-predictor-secret-key"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


# ---------------------------------------------------------
# Create required folders
# ---------------------------------------------------------

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

initialize_database()


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({
        "status": "running",
        "message": "AI Virality Predictor is running"
    })


# ---------------------------------------------------------
# Analyze video
# ---------------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    if "video" not in request.files:
        flash("Please select a video.")
        return redirect(url_for("home"))

    video = request.files["video"]

    if video.filename == "":
        flash("No video selected.")
        return redirect(url_for("home"))

    if not allowed_file(video.filename, ALLOWED_EXTENSIONS):
        flash(
            "Unsupported video format. "
            "Allowed formats: MP4, MOV, AVI, MKV."
        )
        return redirect(url_for("home"))

    try:

        # -------------------------------------------------
        # Generate unique filename
        # -------------------------------------------------

        filename = unique_filename(video.filename)

        video_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        video.save(video_path)

        # -------------------------------------------------
        # Extract features
        # -------------------------------------------------

        features = extract_video_features(video_path)

        # -------------------------------------------------
        # Prediction
        # -------------------------------------------------

        prediction = predict_virality(features)
        # Demo estimated engagement values
        views = random.randint(10_000, 1_000_000)
        likes = random.randint(500, int(views * 0.15))

        # -------------------------------------------------
        # Recommendations
        # -------------------------------------------------

        recommendations = generate_recommendations(
            features,
            prediction
        )

        # -------------------------------------------------
        # Thumbnail
        # -------------------------------------------------

        thumbnail_filename = (
            os.path.splitext(filename)[0] + ".jpg"
        )

        thumbnail_path = os.path.join(
            THUMBNAIL_FOLDER,
            thumbnail_filename
        )

        thumbnail_created = generate_thumbnail(
            video_path,
            thumbnail_path
        )

        # -------------------------------------------------
        # Save analysis in database
        # -------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        analysis_id = save_analysis(
            filename=video.filename,
            timestamp=timestamp,
            features=features,
            prediction=prediction
        )

        return render_template(
            "result.html",
            analysis_id=analysis_id,
            filename=video.filename,
            features=features,
            prediction=prediction,
            recommendations=recommendations,
            thumbnail=(
                url_for(
                    "static",
                    filename=f"thumbnails/{thumbnail_filename}"
                )
                if thumbnail_created
                else None
            )
        )

    except Exception as error:

        print("ERROR:", error)

        flash(
            f"Video analysis failed: {str(error)}"
        )

        return redirect(url_for("home"))


# ---------------------------------------------------------
# History
# ---------------------------------------------------------

@app.route("/history")
def history():

    analyses = get_all_analyses()

    return render_template(
        "history.html",
        analyses=analyses
    )


# ---------------------------------------------------------
# Analysis detail
# ---------------------------------------------------------

@app.route("/analysis/<int:analysis_id>")
def analysis_detail(analysis_id):

    analysis = get_analysis(analysis_id)

    if analysis is None:
        return "Analysis not found", 404

    return render_template(
        "result.html",
        analysis_id=analysis["id"],
        filename=analysis["filename"],
        features=dict(analysis),
        prediction={
            "virality_score": analysis["virality_score"],
            "prediction_label": analysis["prediction_label"],
            "estimated_views": views,
            "estimated_likes": likes,       
            "model_prediction": analysis["virality_score"],
            "is_model_available": True
        },
        recommendations=[],
        thumbnail=None
    )


# ---------------------------------------------------------
# Generate PDF report
# ---------------------------------------------------------

@app.route("/report/<int:analysis_id>")
def report(analysis_id):

    analysis = get_analysis(analysis_id)

    if analysis is None:
        return "Analysis not found", 404

    try:

        pdf_path = generate_report(dict(analysis))

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"virality_report_{analysis_id}.pdf"
        )

    except Exception as error:

        return f"Could not generate report: {error}", 500


# ---------------------------------------------------------
# API: Analyze video
# ---------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def api_analyze():

    if "video" not in request.files:

        return jsonify({
            "success": False,
            "error": "No video uploaded."
        }), 400

    video = request.files["video"]

    if video.filename == "":

        return jsonify({
            "success": False,
            "error": "Empty filename."
        }), 400

    if not allowed_file(video.filename, ALLOWED_EXTENSIONS):

        return jsonify({
            "success": False,
            "error": "Unsupported file format."
        }), 400

    try:

        filename = unique_filename(video.filename)

        video_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        video.save(video_path)

        features = extract_video_features(video_path)

        prediction = predict_virality(features)

        recommendations = generate_recommendations(
            features,
            prediction
        )

        return jsonify({
            "success": True,
            "features": features,
            "prediction": prediction,
            "recommendations": recommendations
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )