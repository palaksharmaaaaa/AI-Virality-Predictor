def generate_recommendations(
    features,
    prediction
):

    recommendations = []

    motion = features.get(
        "motion_score",
        0
    )

    hook = features.get(
        "hook_intensity",
        0
    )

    scene_changes = features.get(
        "scene_changes",
        0
    )

    pacing = features.get(
        "pacing_score",
        0
    )

    face_presence = features.get(
        "face_presence_ratio",
        0
    )

    brightness = features.get(
        "brightness",
        0
    )

    contrast = features.get(
        "contrast",
        0
    )

    duration = features.get(
        "duration",
        0
    )

    # -----------------------------------------------------
    # Hook
    # -----------------------------------------------------

    if hook < 35:

        recommendations.append(
            "Strengthen the first 3 seconds with a "
            "clear visual hook or immediately useful "
            "information."
        )

    elif hook < 60:

        recommendations.append(
            "The opening has moderate visual activity. "
            "Consider making the first few seconds "
            "more immediate and attention-grabbing."
        )

    else:

        recommendations.append(
            "The opening section has strong visual activity."
        )

    # -----------------------------------------------------
    # Motion
    # -----------------------------------------------------

    if motion < 20:

        recommendations.append(
            "Motion is relatively low. Consider adding "
            "camera movement, transitions, demonstrations, "
            "or other visual changes where appropriate."
        )

    elif motion > 80:

        recommendations.append(
            "Motion is very high. Make sure the video "
            "remains easy to follow and does not become "
            "visually overwhelming."
        )

    else:

        recommendations.append(
            "Motion level is within a moderate range."
        )

    # -----------------------------------------------------
    # Pacing
    # -----------------------------------------------------

    if pacing < 35:

        recommendations.append(
            "Pacing may benefit from tighter editing "
            "and more purposeful transitions."
        )

    elif pacing > 85:

        recommendations.append(
            "Pacing is very fast. Consider allowing "
            "important moments enough time to be understood."
        )

    # -----------------------------------------------------
    # Faces
    # -----------------------------------------------------

    if face_presence < 20:

        recommendations.append(
            "Faces are detected in relatively few sampled "
            "frames. If the content is people-focused, "
            "consider using clearer presenter or subject shots."
        )

    elif face_presence > 70:

        recommendations.append(
            "Faces are consistently present in the video, "
            "which can support presenter-focused content."
        )

    # -----------------------------------------------------
    # Brightness
    # -----------------------------------------------------

    if brightness < 45:

        recommendations.append(
            "Average brightness is relatively low. "
            "Consider improving lighting or exposure."
        )

    elif brightness > 220:

        recommendations.append(
            "Average brightness is high. Check for "
            "overexposed areas and preserve visual detail."
        )

    # -----------------------------------------------------
    # Contrast
    # -----------------------------------------------------

    if contrast < 20:

        recommendations.append(
            "Contrast is relatively low. Improving lighting "
            "separation may make visual elements clearer."
        )

    # -----------------------------------------------------
    # Duration
    # -----------------------------------------------------

    if duration < 5:

        recommendations.append(
            "The video is very short. Make sure the core "
            "message is delivered immediately."
        )

    elif duration > 180:

        recommendations.append(
            "The video is relatively long. Consider removing "
            "repetitive sections and maintaining viewer interest."
        )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    score = prediction.get(
        "virality_score",
        0
    )

    if score < 40:

        recommendations.append(
            "The current feature profile indicates lower "
            "viral potential. Focus first on the opening, "
            "pacing, and visual engagement."
        )

    elif score >= 75:

        recommendations.append(
            "The current feature profile shows strong "
            "engagement-oriented characteristics. "
            "Validate these characteristics against actual "
            "historical performance data."
        )

    return recommendations