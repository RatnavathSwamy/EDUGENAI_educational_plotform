import json
import os
import base64

from dotenv import load_dotenv
from groq import Groq

from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User

from .models import GeneratedContent, FollowUpConversation

from .pdf_generator import create_pdf
from .ppt_generator import create_ppt


# ============================================================
# GROQ CLIENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:

    raise RuntimeError(
        "GROQ_API_KEY was not found. Check your .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# GROQ MODELS
# ============================================================

TEXT_MODEL = "openai/gpt-oss-120b"

AUDIO_MODEL = "whisper-large-v3-turbo"


# ============================================================
# CHECK TEXT MODEL
# ============================================================

def check_text_model():

    try:

        model = client.models.retrieve(
            TEXT_MODEL
        )

        print(
            "Groq text model available:",
            model.id
        )

        return True

    except Exception as e:

        print(
            "Groq text model is not available:",
            e
        )

        return False


# ============================================================
# FORMAT GROQ ERROR
# ============================================================

def get_groq_error_message(error):

    error_message = str(error)

    error_lower = error_message.lower()


    # --------------------------------------------------------
    # MODEL NOT FOUND
    # --------------------------------------------------------

    if (
        "model_not_found" in error_lower
        or "does not exist" in error_lower
        or "404" in error_lower
    ):

        return (
            f"The Groq model '{TEXT_MODEL}' is not available "
            "or you do not have access to it. "
            "Please check your Groq model access."
        )


    # --------------------------------------------------------
    # API KEY ERROR
    # --------------------------------------------------------

    if (
        "authentication" in error_lower
        or "invalid api key" in error_lower
        or "401" in error_lower
    ):

        return (
            "Groq API authentication failed. "
            "Please check your GROQ_API_KEY in the .env file."
        )


    # --------------------------------------------------------
    # RATE LIMIT
    # --------------------------------------------------------

    if (
        "rate limit" in error_lower
        or "429" in error_lower
    ):

        return (
            "Groq API rate limit reached. "
            "Please wait for some time and try again."
        )


    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return error_message


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "index.html"
    )


# ============================================================
# NORMAL AI CONTENT GENERATION
# ============================================================

@csrf_exempt
def generate_content(request):

    if request.method != "POST":

        return JsonResponse({

            "success": False,

            "error": "Invalid request method"

        })


    try:

        # ====================================================
        # GET REQUEST DATA
        # ====================================================

        data = json.loads(
            request.body
        )


        topic = data.get(
            "topic",
            ""
        ).strip()


        if not topic:

            return JsonResponse({

                "success": False,

                "error": "Topic is required"

            })


        # ====================================================
        # STRUCTURED EDUCATIONAL PROMPT
        # ====================================================

        prompt = f"""
You are EduGen AI, an intelligent educational tutor.

The student wants to learn about:

{topic}


YOUR MAIN TASK:

Create a clear, structured and student-friendly explanation
of the requested topic.


IMPORTANT CONTENT RULE:

Do NOT generate the answer in table format.

Never use:

| Column | Column |
|--------|--------|

Do not create markdown tables.

Instead use:

- Headings
- Subheadings
- Short paragraphs
- Bullet points
- Numbered steps
- Formulas
- Code blocks when programming is involved
- Examples
- Simple explanations


============================================================
STRUCTURE
============================================================

Choose the sections according to the topic.

Do NOT force every section into every answer.

For a simple concept, keep the answer shorter.

For an algorithm, explain the algorithm properly.

For mathematics, show formulas and calculations.

For programming, provide code and explain it.

For comparison questions, explain the differences using
headings or bullet points instead of tables.


Possible structure:

1. Definition
2. Introduction
3. Important Concepts
4. How It Works
5. Step-by-Step Process
6. Formula
7. Example
8. Real-World Example
9. Applications
10. Advantages
11. Limitations
12. Complexity
13. Key Points
14. Summary


However:

ONLY include sections that are actually useful.


============================================================
IF THE TOPIC IS AN ALGORITHM
============================================================

Use a structure such as:

Definition

Introduction

How the Algorithm Works

Step-by-Step Process

Mathematical Explanation if required

Example

Real-World Example

Advantages

Limitations

Time Complexity

Space Complexity

Key Points


============================================================
IF THE TOPIC IS A MATHEMATICAL CONCEPT
============================================================

Use:

Definition

Formula

Meaning of Variables

Step-by-Step Calculation

Example

Practical Application

Key Points


============================================================
IF THE TOPIC IS PROGRAMMING
============================================================

Use:

Definition

How It Works

Syntax if useful

Simple Code Example

Line-by-Line Explanation

Example Output

Real-World Usage

Common Mistakes

Key Points


============================================================
IF THE TOPIC IS MACHINE LEARNING
============================================================

Explain:

Definition

Purpose

Important Concepts

How It Works

Training Process

Prediction Process

Example

Real-World Example

Advantages

Limitations

Key Points


============================================================
IF THE TOPIC IS A COMPARISON
============================================================

Do NOT create a table.

Instead use:

Topic A

- Meaning
- Working
- Advantages
- Use cases

Topic B

- Meaning
- Working
- Advantages
- Use cases

Then provide:

Key Differences

1. ...
2. ...
3. ...


============================================================
WRITING RULES
============================================================

- Use simple student-friendly English.
- Explain from the basic level.
- Do not assume the student already knows the topic.
- Explain difficult terminology in simple words.
- Use clear headings.
- Use short paragraphs.
- Use bullet points when useful.
- Use numbered steps for processes.
- Give practical examples.
- Give real-world examples when useful.
- Explain formulas clearly.
- Explain variables used in formulas.
- Show calculations step by step when mathematics is involved.
- Explain code clearly when programming is involved.
- Avoid unnecessary repetition.
- Avoid unrelated information.
- Do not unnecessarily explain advanced concepts.
- Do not make the answer unnecessarily long.
- Focus on understanding.
- Do not use tables.
- Do not use markdown tables.


============================================================
TOPIC
============================================================

{topic}
"""


        # ====================================================
        # CALL GROQ
        # ====================================================

        completion = client.chat.completions.create(

            model=TEXT_MODEL,

            messages=[

                {
                    "role": "system",

                    "content": (
                        "You are EduGen AI, "
                        "a clear, patient and student-friendly "
                        "educational tutor."
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }

            ],

            temperature=0.5,

            max_tokens=6000
        )


        # ====================================================
        # GET GENERATED CONTENT
        # ====================================================

        generated_text = (

            completion
            .choices[0]
            .message
            .content

        )


        # ====================================================
        # GUEST USER
        # ====================================================

        guest_user, created = User.objects.get_or_create(

            username="guest"

        )


        # ====================================================
        # SAVE CONTENT
        # ====================================================

        saved_content = GeneratedContent.objects.create(

            user=guest_user,

            topic=topic,

            content=generated_text

        )


        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        return JsonResponse({

            "success": True,

            "content": generated_text,

            "content_id": saved_content.id

        })


    except Exception as e:

        print(
            "GENERATE CONTENT ERROR:",
            e
        )


        error_message = get_groq_error_message(
            e
        )


        return JsonResponse({

            "success": False,

            "error": error_message

        })


# ============================================================
# TRANSLATE CONTENT
# ============================================================

@csrf_exempt
def translate_content(request):

    if request.method != "POST":

        return JsonResponse({

            "success": False,

            "error": "Invalid request"

        })


    try:

        # ====================================================
        # REQUEST DATA
        # ====================================================

        data = json.loads(
            request.body
        )


        content = data.get(
            "content",
            ""
        )


        language = data.get(
            "language",
            "English"
        )


        if not content:

            return JsonResponse({

                "success": False,

                "error": "Content is required"

            })


        # ====================================================
        # TRANSLATION PROMPT
        # ====================================================

        prompt = f"""
Translate the following educational content into:

{language}


IMPORTANT:

Preserve the original educational structure.

Do NOT convert the content into a table.

Do NOT create markdown tables.

Preserve:

- Headings
- Subheadings
- Bullet points
- Numbered steps
- Examples
- Formulas
- Code
- Explanations


Rules:

- Preserve the original meaning.
- Do not remove important information.
- Do not add unrelated information.
- Use natural language.
- Use simple language that students can understand.
- Keep the same logical order.
- Keep formulas unchanged where appropriate.
- Keep programming code unchanged where appropriate.


CONTENT:

{content}
"""


        # ====================================================
        # CALL GROQ
        # ====================================================

        completion = client.chat.completions.create(

            model=TEXT_MODEL,

            messages=[

                {
                    "role": "system",

                    "content": (
                        "You are an expert educational "
                        "translator."
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }

            ],

            temperature=0.3,

            max_tokens=6000
        )


        # ====================================================
        # GET TRANSLATION
        # ====================================================

        translated = (

            completion
            .choices[0]
            .message
            .content

        )


        return JsonResponse({

            "success": True,

            "translated_content": translated

        })


    except Exception as e:

        print(
            "TRANSLATION ERROR:",
            e
        )


        error_message = get_groq_error_message(
            e
        )


        return JsonResponse({

            "success": False,

            "error": error_message

        })


# ============================================================
# FOLLOW-UP QUESTION
# ============================================================

@csrf_exempt
def followup_question(request):

    if request.method != "POST":

        return JsonResponse({

            "success": False,

            "error": "Invalid request"

        })


    try:

        # ====================================================
        # REQUEST DATA
        # ====================================================

        data = json.loads(
            request.body
        )


        question = data.get(
            "question",
            ""
        ).strip()


        content_id = data.get(
            "content_id"
        )


        if not question:

            return JsonResponse({

                "success": False,

                "error": "Question is required"

            })


        if not content_id:

            return JsonResponse({

                "success": False,

                "error": "Content ID is required"

            })


        # ====================================================
        # GET ORIGINAL CONTENT
        # ====================================================

        generated_content = (
            GeneratedContent.objects.get(
                id=content_id
            )
        )


        # ====================================================
        # FOLLOW-UP PROMPT
        # ====================================================

        prompt = f"""
You are EduGen AI, a personal educational tutor.

The student originally learned about:

{generated_content.topic}


Original educational explanation:

{generated_content.content}


The student now asks:

{question}


============================================================
MOST IMPORTANT RULE
============================================================

Answer ONLY the student's current question.

Do NOT answer questions that the student did not ask.

Do NOT automatically generate a complete lesson.

Do NOT repeat the original explanation unnecessarily.

Do NOT add unrelated sections.

Do NOT provide unrelated information.

Do NOT create a table.

Do NOT use markdown tables.


============================================================
UNDERSTAND THE STUDENT'S INTENTION
============================================================

First understand exactly what the student is asking.

Then answer only that requirement.


If the student asks:

"what is X?"

Explain only the definition of X.


If the student asks:

"why is X used?"

Explain why X is used.


If the student asks:

"how does X work?"

Explain the working process.


If the student asks:

"give an example"

Give an example and explain it.


If the student asks:

"give a real-world example"

Give a real-world example.


If the student asks:

"calculate"

Show the required calculation step by step.


If the student asks:

"give the formula"

Give the formula and explain the variables.


If the student asks:

"explain this code"

Explain the code that is relevant to the question.


If the student asks:

"compare X and Y"

Compare only X and Y using headings or bullet points.

Do NOT use a table.


If the student says:

"I don't understand"

Explain the same concept again using simpler language
and a small example.


If the student asks:

"explain in detail"

Give a detailed explanation of ONLY the requested concept.


If the student asks:

"give brief explanation"

Give only a brief explanation.


============================================================
ANSWER STYLE
============================================================

- Use simple student-friendly English.
- Answer directly.
- Stay focused on the student's question.
- Explain step by step when required.
- Use a small example when useful.
- Use bullet points when useful.
- Use numbered steps when explaining a process.
- Use formulas when required.
- Never use tables.
- Never create markdown tables.
- Do not repeat the entire original content.
- Do not unnecessarily introduce unrelated concepts.
- Do not add sections just to make the answer longer.
- Keep the answer reasonably short unless the student specifically asks for detail.


============================================================
STUDENT QUESTION
============================================================

{question}
"""


        # ====================================================
        # CALL GROQ
        # ====================================================

        completion = client.chat.completions.create(

            model=TEXT_MODEL,

            messages=[

                {
                    "role": "system",

                    "content": (
                        "You are a patient educational tutor "
                        "who answers exactly what the student "
                        "asks."
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }

            ],

            temperature=0.4,

            max_tokens=3000
        )


        # ====================================================
        # GET ANSWER
        # ====================================================

        answer = (

            completion
            .choices[0]
            .message
            .content

        )


        # ====================================================
        # SAVE FOLLOW-UP
        # ====================================================

        FollowUpConversation.objects.create(

            generated_content=generated_content,

            question=question,

            answer=answer

        )


        # ====================================================
        # RETURN ANSWER
        # ====================================================

        return JsonResponse({

            "success": True,

            "answer": answer

        })


    except GeneratedContent.DoesNotExist:

        return JsonResponse({

            "success": False,

            "error": "Generated content not found"

        })


    except Exception as e:

        print(
            "FOLLOW-UP ERROR:",
            e
        )


        error_message = get_groq_error_message(
            e
        )


        return JsonResponse({

            "success": False,

            "error": error_message

        })


# ============================================================
# VISUAL AI TUTOR
# ============================================================

@csrf_exempt
def visual_tutor(request):

    if request.method != "POST":

        return JsonResponse({

            "success": False,

            "error": "Invalid request method"

        })


    try:

        # ====================================================
        # GET IMAGE
        # ====================================================

        image_file = request.FILES.get(
            "image"
        )


        if not image_file:

            return JsonResponse({

                "success": False,

                "error": "No camera image received"

            })


        # ====================================================
        # GET QUESTION
        # ====================================================

        typed_question = request.POST.get(

            "question",

            ""

        ).strip()


        # ====================================================
        # AUDIO TRANSCRIPTION
        # ====================================================

        transcript = ""


        audio_file = request.FILES.get(
            "audio"
        )


        if audio_file:

            try:

                transcription = (
                    client.audio.transcriptions.create(

                        file=(

                            audio_file.name,

                            audio_file.read(),

                            audio_file.content_type

                        ),

                        model=AUDIO_MODEL,

                        response_format="text"

                    )
                )


                transcript = str(
                    transcription
                ).strip()


            except Exception as audio_error:

                print(
                    "Audio transcription error:",
                    audio_error
                )


        # ====================================================
        # COMBINE QUESTION
        # ====================================================

        if transcript:

            final_question = transcript

        elif typed_question:

            final_question = typed_question

        else:

            final_question = (
                "Explain the educational content "
                "shown in this image."
            )


        # ====================================================
        # READ IMAGE
        # ====================================================

        image_bytes = image_file.read()


        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")


        mime_type = (

            image_file.content_type

            or "image/jpeg"

        )


        image_url = (

            f"data:{mime_type};base64,"

            f"{image_base64}"

        )


        # ====================================================
        # VISUAL AI
        # ====================================================
        #
        # The text model above is used for normal content.
        #
        # Visual analysis requires a vision-capable model.
        #
        # If your Groq account does not currently provide a
        # vision model, return a clear message instead of
        # generating an incorrect answer.
        #
        # ====================================================

        return JsonResponse({

            "success": False,

            "transcript": transcript,

            "question": final_question,

            "error": (
                "Visual image analysis is not available "
                "with the currently configured Groq model."
            )

        })


    except Exception as e:

        print(
            "VISUAL TUTOR ERROR:",
            e
        )


        return JsonResponse({

            "success": False,

            "error": get_groq_error_message(e)

        })


# ============================================================
# ABOUT
# ============================================================

def about(request):

    return render(

        request,

        "about.html"

    )


# ============================================================
# CONTACT
# ============================================================

def contact(request):

    return render(

        request,

        "contact.html"

    )


# ============================================================
# DOWNLOAD PDF
# ============================================================

def download_pdf(request, id):

    data = GeneratedContent.objects.get(

        id=id

    )


    followups = data.followups.all()


    file = create_pdf(

        data,

        followups,

        f"EduGen_{id}"

    )


    return FileResponse(

        open(file, "rb"),

        as_attachment=True,

        filename="EduGen.pdf"

    )


# ============================================================
# DOWNLOAD PPT
# ============================================================

def download_ppt(request, id):

    data = GeneratedContent.objects.get(

        id=id

    )


    followups = data.followups.all()


    file = create_ppt(

        data,

        followups,

        f"EduGen_{id}"

    )


    return FileResponse(

        open(file, "rb"),

        as_attachment=True,

        filename="EduGen.pptx"

    )







# ============================================================
# VOICE AI TUTOR PAGE
# ============================================================

def voice_tutor_page(request):

    return render(
        request,
        "voice_tutor.html"
    )


# ============================================================
# VOICE AI TUTOR CHAT
# ============================================================

@csrf_exempt
def voice_tutor_chat(request):

    if request.method != "POST":

        return JsonResponse({
            "success": False,
            "error": "Invalid request method"
        })

    try:

        data = json.loads(request.body)

        question = data.get(
            "question",
            ""
        ).strip()

        conversation = data.get(
            "conversation",
            []
        )

        if not question:

            return JsonResponse({
                "success": False,
                "error": "Question is required"
            })


        # ====================================================
        # SYSTEM INSTRUCTION
        # ====================================================

        messages = [

            {
                "role": "system",
                "content": """
You are EduGen AI Voice Tutor.

You are an intelligent educational tutor.

Your job is to have a natural conversation with students.

Rules:

1. Understand the student's question carefully.
2. Answer in simple student-friendly language.
3. Explain concepts step by step when necessary.
4. Give examples when useful.
5. If the student asks a follow-up question, remember the
   previous conversation.
6. Do not unnecessarily repeat previous answers.
7. If the student asks for a simple explanation, keep it simple.
8. If the student asks for a detailed explanation, provide more detail.
9. If the student asks for a real-world example, provide one.
10. If the student asks a mathematical question, show the steps.
11. If the student asks programming questions, explain the logic.
12. Be conversational because the answer will be spoken aloud.
13. Avoid unnecessary markdown tables.
14. Keep answers reasonably concise for voice interaction.

You are speaking directly with the student.
"""
            }

        ]


        # ====================================================
        # ADD PREVIOUS CONVERSATION
        # ====================================================

        if isinstance(conversation, list):

            for message in conversation[-10:]:

                if not isinstance(message, dict):
                    continue

                role = message.get("role")
                content = message.get("content")

                if role in ["user", "assistant"] and content:

                    messages.append({

                        "role": role,

                        "content": str(content)

                    })


        # ====================================================
        # CURRENT QUESTION
        # ====================================================

        messages.append({

            "role": "user",

            "content": question

        })


        # ====================================================
        # CALL GPT-OSS-120B
        # ====================================================

        completion = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=messages,

            temperature=0.5,

            max_tokens=1000

        )


        # ====================================================
        # GET AI ANSWER
        # ====================================================

        answer = (

            completion
            .choices[0]
            .message
            .content
        )


        if not answer:

            answer = (
                "I could not generate an answer. "
                "Please try asking the question again."
            )


        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        return JsonResponse({

            "success": True,

            "question": question,

            "answer": answer

        })


    except Exception as e:

        print(
            "VOICE AI TUTOR ERROR:",
            e
        )

        return JsonResponse({

            "success": False,

            "error": str(e)

        })