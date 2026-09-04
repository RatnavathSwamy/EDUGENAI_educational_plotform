let currentTopic = "";
let currentGeneratedContent = "";
let currentContentId = null;


/* ============================================================
   NORMAL AI CONTENT GENERATION
============================================================ */

const generateBtn = document.getElementById("generateBtn");

if (generateBtn) {

    generateBtn.addEventListener("click", async function () {

        const topicInput =
            document.getElementById("topicInput");

        const resultBox =
            document.getElementById("resultBox");

        const topic =
            topicInput.value.trim();

        if (topic === "") {

            resultBox.innerHTML =
                "<p>Please enter a topic.</p>";

            return;
        }

        resultBox.innerHTML = `
            <div class="loading-box">
                <h3>Generating AI Content...</h3>
                <p>Please wait...</p>
            </div>
        `;

        try {

            const response = await fetch(
                "/generate/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },

                    body: JSON.stringify({
                        topic: topic
                    })
                }
            );

            const data = await response.json();

            console.log("Generate response:", data);

            if (data.success) {

                currentTopic = topic;

                currentGeneratedContent =
                    data.content;

                currentContentId =
                    data.content_id;

                showGeneratedContent(
                    topic,
                    data.content
                );

            } else {

                resultBox.innerHTML = `
                    <h3>Error</h3>
                    <p>${escapeHtml(data.error)}</p>
                `;
            }

        } catch (error) {

            console.error(error);

            resultBox.innerHTML = `
                <h3>Error generating content</h3>
                <p>${escapeHtml(error.message)}</p>
            `;
        }

    });

}


/* ============================================================
   SHOW GENERATED CONTENT
============================================================ */

function showGeneratedContent(topic, content) {

    const resultBox =
        document.getElementById("resultBox");

    if (!resultBox) {
        return;
    }

    resultBox.innerHTML = `

        <div class="generated-content">

            <h2>${escapeHtml(topic)}</h2>

            <div class="language-buttons">

                <button onclick="translateContent('Telugu')">
                    Telugu
                </button>

                <button onclick="translateContent('Hindi')">
                    Hindi
                </button>

                <button onclick="translateContent('Tamil')">
                    Tamil
                </button>

                <button onclick="translateContent('Kannada')">
                    Kannada
                </button>

                <button onclick="translateContent('Malayalam')">
                    Malayalam
                </button>

                <button onclick="translateContent('English')">
                    English
                </button>

            </div>

            <div
                class="content-body"
                id="translatedContent"
            >
                ${formatText(content)}
            </div>

            <div class="followup-section">

                <h3>
                    💬 Ask Follow-up Questions
                </h3>

                <div
                    id="chatArea"
                    class="chat-area"
                ></div>

                <div class="followup-input">

                    <input
                        type="text"
                        id="followupInput"
                        placeholder="Ask anything about this topic..."
                    >

                    <button
                        id="askFollowupBtn"
                        onclick="askFollowupQuestion()"
                    >
                        Ask AI
                    </button>

                </div>

            </div>

        </div>
    `;


    const followupInput =
        document.getElementById("followupInput");

    if (followupInput) {

        followupInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    askFollowupQuestion();
                }
            }
        );
    }

}


/* ============================================================
   TRANSLATE
============================================================ */

async function translateContent(language) {

    const contentBox =
        document.getElementById("translatedContent");

    if (!contentBox) {
        return;
    }

    contentBox.innerHTML =
        "<p>Translating...</p>";

    try {

        const response = await fetch(
            "/translate/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                body: JSON.stringify({

                    content: currentGeneratedContent,

                    language: language

                })
            }
        );

        const data =
            await response.json();

        if (data.success) {

            contentBox.innerHTML =
                formatText(
                    data.translated_content
                );

        } else {

            contentBox.innerHTML =
                `<p>Translation error: ${escapeHtml(data.error)}</p>`;
        }

    } catch (error) {

        console.error(error);

        contentBox.innerHTML =
            "<p>Translation failed.</p>";
    }
}


/* ============================================================
   DOWNLOAD PDF
============================================================ */

function downloadPDF() {

    if (currentContentId === null) {

        alert("Generate content first.");

        return;
    }

    window.location.href =
        "/download/pdf/" +
        currentContentId +
        "/";
}


/* ============================================================
   DOWNLOAD PPT
============================================================ */

function downloadPPT() {

    if (currentContentId === null) {

        alert("Generate content first.");

        return;
    }

    window.location.href =
        "/download/ppt/" +
        currentContentId +
        "/";
}


/* ============================================================
   FOLLOW-UP QUESTION
============================================================ */

async function askFollowupQuestion() {

    const input =
        document.getElementById("followupInput");

    const chatArea =
        document.getElementById("chatArea");

    if (!input || !chatArea) {
        return;
    }

    const question =
        input.value.trim();

    if (question === "") {
        return;
    }

    if (currentContentId === null) {

        alert("Generate content first.");

        return;
    }

    chatArea.innerHTML += `

        <div class="user-chat">

            <b>You:</b>

            <br>

            ${escapeHtml(question)}

        </div>
    `;

    input.value = "";

    try {

        const response = await fetch(
            "/followup/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                body: JSON.stringify({

                    question: question,

                    content_id: currentContentId

                })
            }
        );

        const data =
            await response.json();

        if (data.success) {

            chatArea.innerHTML += `

                <div class="ai-chat">

                    <b>EduGen AI:</b>

                    <br><br>

                    ${formatText(data.answer)}

                </div>
            `;

        } else {

            chatArea.innerHTML += `

                <div class="ai-chat">

                    <b>Error:</b>

                    <br>

                    ${escapeHtml(data.error)}

                </div>
            `;
        }

        chatArea.scrollTop =
            chatArea.scrollHeight;

    } catch (error) {

        console.error(error);

        chatArea.innerHTML += `

            <div class="ai-chat">

                <b>Error:</b>

                <br>

                ${escapeHtml(error.message)}

            </div>
        `;
    }
}


/* ============================================================
   POPULAR TOPICS
============================================================ */

function fillTopic(topic) {

    const input =
        document.getElementById("topicInput");

    if (input) {

        input.value = topic;

        input.focus();
    }
}


/* ============================================================
   CSRF COOKIE
============================================================ */

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie) {

        const cookies =
            document.cookie.split(";");

        for (let cookie of cookies) {

            cookie =
                cookie.trim();

            if (
                cookie.startsWith(
                    name + "="
                )
            ) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;
            }
        }
    }

    return cookieValue;
}


/* ============================================================
   DOWNLOAD BUTTON EVENTS
============================================================ */

document.addEventListener(
    "click",
    function (event) {

        if (
            event.target &&
            event.target.id ===
            "downloadPdfBtn"
        ) {

            downloadPDF();
        }


        if (
            event.target &&
            event.target.id ===
            "downloadPptBtn"
        ) {

            downloadPPT();
        }

    }
);


/* ============================================================
   VISUAL AI TUTOR VARIABLES
============================================================ */

let visualStream = null;

let visualAudioStream = null;

let visualMediaRecorder = null;

let visualAudioChunks = [];

let visualAudioBlob = null;


/* ============================================================
   OPEN CAMERA + MICROPHONE
============================================================ */

async function openVisualTutor() {

    const modal =
        document.getElementById(
            "visualTutorModal"
        );

    const video =
        document.getElementById(
            "cameraVideo"
        );

    const status =
        document.getElementById(
            "cameraStatus"
        );

    if (!modal || !video) {

        alert(
            "Visual Tutor HTML elements are missing."
        );

        return;
    }

    modal.style.display = "flex";

    status.innerHTML =
        "Opening camera and microphone...";

    try {

        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {

            throw new Error(
                "Camera and microphone are not supported by this browser."
            );
        }


        visualStream =
            await navigator.mediaDevices.getUserMedia({

                video: {

                    facingMode: {
                        ideal: "environment"
                    },

                    width: {
                        ideal: 1280
                    },

                    height: {
                        ideal: 720
                    }
                },

                audio: true
            });


        video.srcObject =
            visualStream;

        video.muted = true;

        await video.play();


        status.innerHTML = `
            <span class="recording-dot"></span>
            Camera and microphone are ready.
            Speak your question.
        `;


        startVisualRecording();

    } catch (error) {

        console.error(
            "Camera error:",
            error
        );

        status.innerHTML = `
            ❌ Unable to access camera or microphone.
            <br><br>
            Please allow camera and microphone permissions.
            <br>
            Error: ${escapeHtml(error.message)}
        `;
    }
}


/* ============================================================
   CLOSE VISUAL TUTOR
============================================================ */

function closeVisualTutor() {

    stopVisualRecording();


    if (visualStream) {

        visualStream
            .getTracks()
            .forEach(
                function (track) {
                    track.stop();
                }
            );

        visualStream = null;
    }


    if (visualAudioStream) {

        visualAudioStream
            .getTracks()
            .forEach(
                function (track) {
                    track.stop();
                }
            );

        visualAudioStream = null;
    }


    const video =
        document.getElementById(
            "cameraVideo"
        );

    if (video) {

        video.pause();

        video.srcObject = null;
    }


    const modal =
        document.getElementById(
            "visualTutorModal"
        );

    if (modal) {

        modal.style.display = "none";
    }
}


/* ============================================================
   START AUDIO RECORDING
============================================================ */

function startVisualRecording() {

    if (!visualStream) {

        return;
    }


    if (
        visualMediaRecorder &&
        visualMediaRecorder.state ===
        "recording"
    ) {

        return;
    }


    visualAudioChunks = [];

    visualAudioBlob = null;


    try {

        const audioTracks =
            visualStream.getAudioTracks();


        if (
            !audioTracks ||
            audioTracks.length === 0
        ) {

            throw new Error(
                "Microphone audio track not available."
            );
        }


        visualAudioStream =
            new MediaStream(
                audioTracks
            );


        let options = {};


        if (
            MediaRecorder.isTypeSupported(
                "audio/webm;codecs=opus"
            )
        ) {

            options.mimeType =
                "audio/webm;codecs=opus";

        } else if (
            MediaRecorder.isTypeSupported(
                "audio/webm"
            )
        ) {

            options.mimeType =
                "audio/webm";
        }


        visualMediaRecorder =
            new MediaRecorder(
                visualAudioStream,
                options
            );


        visualMediaRecorder.ondataavailable =
            function (event) {

                if (
                    event.data &&
                    event.data.size > 0
                ) {

                    visualAudioChunks.push(
                        event.data
                    );
                }
            };


        visualMediaRecorder.onstop =
            function () {

                visualAudioBlob =
                    new Blob(
                        visualAudioChunks,
                        {
                            type:
                                visualMediaRecorder.mimeType ||
                                "audio/webm"
                        }
                    );


                const status =
                    document.getElementById(
                        "cameraStatus"
                    );

                if (status) {

                    status.innerHTML = `
                        🎤 Voice captured.
                        Click
                        <strong>
                        Capture & Ask AI
                        </strong>
                        to analyze the image.
                    `;
                }
            };


        visualMediaRecorder.start();


        const status =
            document.getElementById(
                "cameraStatus"
            );

        if (status) {

            status.innerHTML = `
                <span class="recording-dot"></span>
                🎤 Listening...
                Speak your question.
            `;
        }

    } catch (error) {

        console.error(
            "Recording error:",
            error
        );

        const status =
            document.getElementById(
                "cameraStatus"
            );

        if (status) {

            status.innerHTML =
                "❌ Microphone recording could not start.";
        }
    }
}


/* ============================================================
   STOP AUDIO RECORDING
============================================================ */

function stopVisualRecording() {

    if (
        visualMediaRecorder &&
        visualMediaRecorder.state ===
        "recording"
    ) {

        visualMediaRecorder.stop();
    }
}


/* ============================================================
   CAPTURE CAMERA IMAGE
============================================================ */

function captureCameraImage() {

    const video =
        document.getElementById(
            "cameraVideo"
        );

    if (
        !video ||
        !video.videoWidth ||
        !video.videoHeight
    ) {

        return null;
    }


    const canvas =
        document.createElement(
            "canvas"
        );


    let width =
        video.videoWidth;

    let height =
        video.videoHeight;


    const maxWidth = 1280;


    if (width > maxWidth) {

        const ratio =
            maxWidth / width;

        width =
            maxWidth;

        height =
            Math.round(
                height * ratio
            );
    }


    canvas.width =
        width;

    canvas.height =
        height;


    const context =
        canvas.getContext(
            "2d"
        );


    context.drawImage(
        video,
        0,
        0,
        width,
        height
    );


    return canvas.toDataURL(
        "image/jpeg",
        0.80
    );
}


/* ============================================================
   CAPTURE IMAGE + AUDIO + ASK AI
============================================================ */

async function captureAndAskVisualAI() {

    const loading =
        document.getElementById(
            "visualLoading"
        );

    const questionInput =
        document.getElementById(
            "visualQuestionInput"
        );

    const transcriptBox =
        document.getElementById(
            "visualTranscript"
        );

    const transcriptText =
        document.getElementById(
            "visualTranscriptText"
        );


    const imageData =
        captureCameraImage();


    if (!imageData) {

        alert(
            "Camera image could not be captured."
        );

        return;
    }


    const typedQuestion =
        questionInput
            ? questionInput.value.trim()
            : "";


    /*
     * Stop audio recording.
     */

    if (
        visualMediaRecorder &&
        visualMediaRecorder.state ===
        "recording"
    ) {

        visualMediaRecorder.stop();


        await new Promise(
            function (resolve) {

                setTimeout(
                    resolve,
                    600
                );
            }
        );
    }


    if (
        !visualAudioBlob &&
        typedQuestion === ""
    ) {

        alert(
            "Please speak your question or type a question."
        );

        return;
    }


    if (loading) {

        loading.style.display =
            "block";
    }


    if (transcriptBox) {

        transcriptBox.style.display =
            "none";
    }


    try {

        const formData =
            new FormData();


        formData.append(
            "image",
            dataURLToBlob(imageData),
            "camera_image.jpg"
        );


        if (visualAudioBlob) {

            formData.append(
                "audio",
                visualAudioBlob,
                "student_question.webm"
            );
        }


        formData.append(
            "question",
            typedQuestion
        );


        const response =
            await fetch(
                "/visual-tutor/",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        console.log(
            "Visual Tutor response:",
            data
        );


        if (data.success) {

            if (
                data.transcript &&
                transcriptText &&
                transcriptBox
            ) {

                transcriptText.innerText =
                    data.transcript;

                transcriptBox.style.display =
                    "block";
            }


            displayVisualTutorResult(
                data
            );

        } else {

            alert(
                "Visual AI Error: " +
                data.error
            );
        }


    } catch (error) {

        console.error(
            "Visual AI error:",
            error
        );

        alert(
            "Error communicating with Visual AI: " +
            error.message
        );

    } finally {

        if (loading) {

            loading.style.display =
                "none";
        }


        /*
         * Prepare for another question.
         */

        visualAudioBlob = null;

        visualAudioChunks = [];

        startVisualRecording();
    }
}


/* ============================================================
   DATA URL TO BLOB
============================================================ */

function dataURLToBlob(dataURL) {

    const parts =
        dataURL.split(",");

    const mimeMatch =
        parts[0].match(
            /:(.*?);/
        );

    const mime =
        mimeMatch
            ? mimeMatch[1]
            : "image/jpeg";

    const binary =
        atob(parts[1]);

    const array =
        new Uint8Array(
            binary.length
        );


    for (
        let i = 0;
        i < binary.length;
        i++
    ) {

        array[i] =
            binary.charCodeAt(i);
    }


    return new Blob(
        [array],
        {
            type: mime
        }
    );
}


/* ============================================================
   DISPLAY VISUAL AI RESULT
============================================================ */

function displayVisualTutorResult(data) {

    const resultBox =
        document.getElementById(
            "resultBox"
        );

    if (!resultBox) {
        return;
    }


    const transcript =
        data.transcript ||
        data.question ||
        "Not available";


    const answer =
        data.answer ||
        "No answer received.";


    resultBox.innerHTML = `

        <div class="generated-content">

            <h2>
                📷 Visual AI Tutor
            </h2>

            <div class="content-body">

                <h3>
                    📚 What You Showed
                </h3>

                <p>
                    EduGen AI analyzed the
                    educational material shown
                    through your camera.
                </p>


                <h3>
                    🎤 Your Question
                </h3>

                <p>
                    ${formatText(transcript)}
                </p>


                <hr>


                <h3>
                    🧠 EduGen AI Answer
                </h3>

                <div>
                    ${formatText(answer)}
                </div>

            </div>

        </div>
    `;
}


/* ============================================================
   ESCAPE HTML
============================================================ */

function escapeHtml(text) {

    if (text === null || text === undefined) {

        return "";
    }

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================================
   FORMAT TEXT
============================================================ */

function formatText(text) {

    return escapeHtml(text)
        .replace(/\n/g, "<br>");
}


/* ============================================================
   CLOSE CAMERA WHEN PAGE CLOSES
============================================================ */

window.addEventListener(
    "beforeunload",
    function () {

        if (visualStream) {

            visualStream
                .getTracks()
                .forEach(
                    function (track) {
                        track.stop();
                    }
                );
        }

    }
);


/* ============================================================
   CLOSE MODAL WHEN CLICKING OUTSIDE
============================================================ */

window.addEventListener(
    "click",
    function (event) {

        const modal =
            document.getElementById(
                "visualTutorModal"
            );

        if (
            modal &&
            event.target === modal
        ) {

            closeVisualTutor();
        }
    }
);