/* ============================================================
   EDU GEN AI VOICE TUTOR
============================================================ */


/* ============================================================
   VARIABLES
============================================================ */

let recognition = null;

let isListening = false;

let conversation = [];


/* ============================================================
   HTML ELEMENTS
============================================================ */

const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );

const micCircle =
    document.getElementById(
        "micCircle"
    );

const conversationArea =
    document.getElementById(
        "conversationArea"
    );


/* ============================================================
   BROWSER SPEECH RECOGNITION
============================================================ */

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (!SpeechRecognition) {

    if (voiceStatus) {

        voiceStatus.innerText =
            "Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.";

    }

} else {

    recognition =
        new SpeechRecognition();


    recognition.continuous =
        false;


    recognition.interimResults =
        false;


    recognition.lang =
        "en-US";


    recognition.onstart =
        function () {

            isListening = true;

            updateListeningUI();

        };


    recognition.onresult =
        async function (event) {

            const transcript =
                event
                .results[0][0]
                .transcript
                .trim();


            if (!transcript) {

                return;

            }


            if (voiceStatus) {

                voiceStatus.innerText =
                    "You said: " +
                    transcript;

            }


            addUserMessage(
                transcript
            );


            await sendQuestionToAI(
                transcript
            );

        };


    recognition.onerror =
        function (event) {

            console.error(
                "Speech recognition error:",
                event.error
            );


            isListening = false;

            updateListeningUI();


            if (voiceStatus) {

                voiceStatus.innerText =
                    "Microphone error: " +
                    event.error;

            }

        };


    recognition.onend =
        function () {

            isListening = false;

            updateListeningUI();

        };

}


/* ============================================================
   START SPEECH RECOGNITION
============================================================ */

function startVoiceRecognition() {

    if (!recognition) {

        alert(
            "Speech recognition is not supported. Please use Google Chrome or Microsoft Edge."
        );

        return;

    }


    if (isListening) {

        return;

    }


    try {

        recognition.start();

    } catch (error) {

        console.error(error);

    }

}


/* ============================================================
   STOP SPEECH RECOGNITION
============================================================ */

function stopVoiceRecognition() {

    if (
        recognition &&
        isListening
    ) {

        recognition.stop();

    }

}


/* ============================================================
   TOGGLE MICROPHONE
============================================================ */

function toggleVoiceRecognition() {

    if (isListening) {

        stopVoiceRecognition();

    } else {

        startVoiceRecognition();

    }

}


/* ============================================================
   UPDATE MICROPHONE UI
============================================================ */

function updateListeningUI() {

    if (!micCircle) {

        return;

    }


    if (isListening) {

        micCircle.classList.add(
            "listening"
        );


        micCircle.innerText =
            "🔴";


        if (voiceStatus) {

            voiceStatus.innerText =
                "🎙️ Listening... Speak now.";

        }

    } else {

        micCircle.classList.remove(
            "listening"
        );


        micCircle.innerText =
            "🎙️";

    }

}


/* ============================================================
   ADD USER MESSAGE
============================================================ */

function addUserMessage(
    message
) {

    if (!conversationArea) {

        return;

    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "user-message message";


    div.innerHTML = `

        <div class="message-label">
            👨‍🎓 You
        </div>

        <div>
            ${escapeHtml(message)}
        </div>

    `;


    conversationArea.appendChild(
        div
    );


    scrollConversation();

}


/* ============================================================
   ADD AI MESSAGE
============================================================ */

function addAIMessage(
    message
) {

    if (!conversationArea) {

        return;

    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "ai-message message";


    div.innerHTML = `

        <div class="message-label">
            🤖 EduGen AI
        </div>

        <div>
            ${formatAnswer(message)}
        </div>

    `;


    conversationArea.appendChild(
        div
    );


    scrollConversation();

}


/* ============================================================
   THINKING MESSAGE
============================================================ */

function showThinking() {

    if (!conversationArea) {

        return;

    }


    const div =
        document.createElement(
            "div"
        );


    div.id =
        "thinkingMessage";


    div.className =
        "ai-message message thinking";


    div.innerHTML = `

        <div class="message-label">
            🤖 EduGen AI
        </div>

        Thinking...

    `;


    conversationArea.appendChild(
        div
    );


    scrollConversation();

}


/* ============================================================
   REMOVE THINKING
============================================================ */

function removeThinking() {

    const thinking =
        document.getElementById(
            "thinkingMessage"
        );


    if (thinking) {

        thinking.remove();

    }

}


/* ============================================================
   SEND QUESTION TO DJANGO
============================================================ */

async function sendQuestionToAI(
    question
) {

    showThinking();


    try {

        const response =
            await fetch(
                "/voice-tutor/chat/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        conversation:
                            conversation

                    })

                }
            );


        const data =
            await response.json();


        removeThinking();


        if (!data.success) {

            addAIMessage(
                "Sorry, I could not process your question. " +
                data.error
            );

            return;

        }


        const answer =
            data.answer;


        /* ================================================
           SAVE CONVERSATION
        ================================================ */

        conversation.push({

            role: "user",

            content: question

        });


        conversation.push({

            role: "assistant",

            content: answer

        });


        /* ================================================
           DISPLAY
        ================================================ */

        addAIMessage(
            answer
        );


        /* ================================================
           SPEAK ANSWER
        ================================================ */

        speakAnswer(
            answer
        );


        if (voiceStatus) {

            voiceStatus.innerText =
                "Answer completed. Ask another question.";

        }


    } catch (error) {

        console.error(
            "Voice AI error:",
            error
        );


        removeThinking();


        addAIMessage(
            "Connection error: " +
            error.message
        );

    }

}


/* ============================================================
   SEND TYPED QUESTION
============================================================ */

async function sendTypedVoiceQuestion() {

    const input =
        document.getElementById(
            "voiceTextInput"
        );


    if (!input) {

        return;

    }


    const question =
        input.value.trim();


    if (!question) {

        return;

    }


    input.value = "";


    addUserMessage(
        question
    );


    await sendQuestionToAI(
        question
    );

}


/* ============================================================
   ENTER KEY
============================================================ */

function handleVoiceInputKey(
    event
) {

    if (
        event.key ===
        "Enter"
    ) {

        event.preventDefault();

        sendTypedVoiceQuestion();

    }

}


/* ============================================================
   TEXT TO SPEECH
============================================================ */

function speakAnswer(
    text
) {

    if (
        !window.speechSynthesis
    ) {

        return;

    }


    window.speechSynthesis.cancel();


    const cleanText =
        text
            .replace(
                /[*#_`]/g,
                ""
            )
            .replace(
                /\n+/g,
                ". "
            );


    const utterance =
        new SpeechSynthesisUtterance(
            cleanText
        );


    utterance.lang =
        "en-US";


    utterance.rate =
        0.95;


    utterance.pitch =
        1;


    utterance.volume =
        1;


    window.speechSynthesis.speak(
        utterance
    );

}


/* ============================================================
   CLEAR CONVERSATION
============================================================ */

function clearConversation() {

    conversation = [];


    if (conversationArea) {

        conversationArea.innerHTML = `

            <div class="ai-message message">

                <div class="message-label">
                    🤖 EduGen AI
                </div>

                Hello! I am your AI Tutor.
                Ask me anything and I will help you learn.

            </div>

        `;

    }


    if (
        window.speechSynthesis
    ) {

        window.speechSynthesis.cancel();

    }


    if (voiceStatus) {

        voiceStatus.innerText =
            "Conversation cleared. Ask a new question.";

    }

}


/* ============================================================
   SCROLL
============================================================ */

function scrollConversation() {

    if (!conversationArea) {

        return;

    }


    conversationArea.scrollTop =
        conversationArea.scrollHeight;

}


/* ============================================================
   ESCAPE HTML
============================================================ */

function escapeHtml(
    text
) {

    return String(text)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


/* ============================================================
   FORMAT ANSWER
============================================================ */

function formatAnswer(
    text
) {

    return escapeHtml(
        text
    ).replace(
        /\n/g,
        "<br>"
    );

}