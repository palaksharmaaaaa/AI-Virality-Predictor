document.addEventListener(
    "DOMContentLoaded",
    function () {

        const videoInput =
            document.getElementById("video");

        const fileName =
            document.getElementById("fileName");

        const form =
            document.getElementById("uploadForm");

        const analyzeButton =
            document.getElementById("analyzeButton");


        // -------------------------------------------------
        // Show selected filename
        // -------------------------------------------------

        if (videoInput) {

            videoInput.addEventListener(
                "change",
                function () {

                    if (
                        videoInput.files &&
                        videoInput.files.length > 0
                    ) {

                        fileName.textContent =
                            videoInput.files[0].name;

                    } else {

                        fileName.textContent =
                            "No video selected";

                    }

                }
            );

        }


        // -------------------------------------------------
        // Loading state
        // -------------------------------------------------

        if (form) {

            form.addEventListener(
                "submit",
                function () {

                    if (
                        !videoInput.files ||
                        videoInput.files.length === 0
                    ) {

                        return;

                    }

                    analyzeButton.disabled = true;

                    analyzeButton.textContent =
                        "Analyzing Video...";

                }
            );

        }

    }
);