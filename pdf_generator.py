import os
import re

from xml.sax.saxutils import escape

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether
)

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import TA_CENTER

from reportlab.lib.units import mm

from reportlab.lib import colors


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(data, followups, filename):

    # ========================================================
    # CREATE MEDIA DIRECTORY
    # ========================================================

    media_directory = "media"

    os.makedirs(
        media_directory,
        exist_ok=True
    )


    # ========================================================
    # PDF PATH
    # ========================================================

    path = os.path.join(
        media_directory,
        f"{filename}.pdf"
    )


    # ========================================================
    # PDF DOCUMENT
    # ========================================================

    pdf = SimpleDocTemplate(

        path,

        pagesize=A4,

        rightMargin=18 * mm,

        leftMargin=18 * mm,

        topMargin=18 * mm,

        bottomMargin=18 * mm,

        title="EduGen AI Educational Notes",

        author="EduGen AI"

    )


    # ========================================================
    # DEFAULT STYLES
    # ========================================================

    styles = getSampleStyleSheet()


    # ========================================================
    # TITLE STYLE
    # ========================================================

    title_style = ParagraphStyle(

        "EduGenTitle",

        parent=styles["Title"],

        fontSize=20,

        leading=25,

        alignment=TA_CENTER,

        spaceAfter=15,

        textColor=colors.black

    )


    # ========================================================
    # TOPIC STYLE
    # ========================================================

    topic_style = ParagraphStyle(

        "TopicStyle",

        parent=styles["Heading2"],

        fontSize=14,

        leading=19,

        spaceBefore=8,

        spaceAfter=12,

        textColor=colors.black

    )


    # ========================================================
    # MAIN HEADING
    # ========================================================

    heading1_style = ParagraphStyle(

        "MainHeading",

        parent=styles["Heading1"],

        fontSize=16,

        leading=21,

        spaceBefore=14,

        spaceAfter=8,

        textColor=colors.black

    )


    # ========================================================
    # SUB HEADING
    # ========================================================

    heading2_style = ParagraphStyle(

        "SubHeading",

        parent=styles["Heading2"],

        fontSize=13,

        leading=18,

        spaceBefore=10,

        spaceAfter=6,

        textColor=colors.black

    )


    # ========================================================
    # NORMAL TEXT
    # ========================================================

    body_style = ParagraphStyle(

        "EduGenBody",

        parent=styles["BodyText"],

        fontSize=10.5,

        leading=16,

        spaceAfter=7,

        textColor=colors.black

    )


    # ========================================================
    # BULLET STYLE
    # ========================================================

    bullet_style = ParagraphStyle(

        "BulletStyle",

        parent=styles["BodyText"],

        fontSize=10.5,

        leading=16,

        leftIndent=15,

        firstLineIndent=-8,

        spaceAfter=5,

        textColor=colors.black

    )


    # ========================================================
    # NUMBER STYLE
    # ========================================================

    number_style = ParagraphStyle(

        "NumberStyle",

        parent=styles["BodyText"],

        fontSize=10.5,

        leading=16,

        leftIndent=18,

        firstLineIndent=-12,

        spaceAfter=5,

        textColor=colors.black

    )


    # ========================================================
    # QUESTION STYLE
    # ========================================================

    question_style = ParagraphStyle(

        "QuestionStyle",

        parent=styles["Heading3"],

        fontSize=12,

        leading=18,

        spaceBefore=8,

        spaceAfter=8,

        textColor=colors.black

    )


    # ========================================================
    # ANSWER LABEL STYLE
    # ========================================================

    answer_label_style = ParagraphStyle(

        "AnswerLabel",

        parent=styles["Heading3"],

        fontSize=12,

        leading=18,

        spaceBefore=6,

        spaceAfter=8,

        textColor=colors.black

    )


    # ========================================================
    # CONTENT CONTAINER
    # ========================================================

    content = []


    # ========================================================
    # TITLE
    # ========================================================

    content.append(

        Paragraph(

            "EduGen AI Educational Notes",

            title_style

        )

    )


    content.append(

        Spacer(
            1,
            10
        )

    )


    # ========================================================
    # TOPIC
    # ========================================================

    content.append(

        Paragraph(

            f"<b>Topic:</b> {escape(str(data.topic))}",

            topic_style

        )

    )


    content.append(

        Spacer(
            1,
            10
        )

    )


    # ========================================================
    # EDUCATIONAL CONTENT HEADING
    # ========================================================

    content.append(

        Paragraph(

            "Educational Content",

            heading1_style

        )

    )


    content.append(

        Spacer(
            1,
            5
        )

    )


    # ========================================================
    # ADD MAIN EDUCATIONAL CONTENT
    # ========================================================

    content.extend(

        convert_text_to_pdf_elements(

            data.content,

            body_style,

            heading1_style,

            heading2_style,

            bullet_style,

            number_style

        )

    )


    # ========================================================
    # FOLLOW-UP SECTION
    # ========================================================

    if followups:

        content.append(

            PageBreak()

        )


        content.append(

            Paragraph(

                "Student Follow-up Questions and Answers",

                heading1_style

            )

        )


        content.append(

            Paragraph(

                "The following section contains the questions "
                "asked by the student and the corresponding "
                "answers provided by EduGen AI.",

                body_style

            )

        )


        content.append(

            Spacer(
                1,
                10
            )

        )


        # ====================================================
        # LOOP THROUGH FOLLOW-UPS
        # ====================================================

        for index, item in enumerate(

            followups,

            start=1

        ):

            question = str(
                item.question
            ).strip()


            answer = str(
                item.answer
            ).strip()


            # =================================================
            # QUESTION NUMBER
            # =================================================

            question_header = Paragraph(

                f"Question {index}",

                heading2_style

            )


            # =================================================
            # QUESTION TEXT
            # =================================================

            question_text = Paragraph(

                f"<b>Student Question:</b> "
                f"{escape(question)}",

                question_style

            )


            # =================================================
            # ANSWER LABEL
            # =================================================

            answer_label = Paragraph(

                "<b>EduGen AI Answer:</b>",

                answer_label_style

            )


            # =================================================
            # ADD QUESTION
            # =================================================

            content.append(

                KeepTogether(

                    [

                        question_header,

                        question_text,

                        answer_label

                    ]

                )

            )


            # =================================================
            # ADD ANSWER
            # =================================================

            content.extend(

                convert_text_to_pdf_elements(

                    answer,

                    body_style,

                    heading1_style,

                    heading2_style,

                    bullet_style,

                    number_style

                )

            )


            # =================================================
            # SEPARATOR
            # =================================================

            if index < len(followups):

                content.append(

                    Spacer(
                        1,
                        10
                    )

                )

                content.append(

                    Paragraph(

                        "--------------------------------------------------",

                        body_style

                    )

                )

                content.append(

                    Spacer(
                        1,
                        10
                    )

                )


    # ========================================================
    # BUILD PDF
    # ========================================================

    pdf.build(

        content,

        onFirstPage=add_page_number,

        onLaterPages=add_page_number

    )


    return path


# ============================================================
# CONVERT AI TEXT TO PDF ELEMENTS
# ============================================================

def convert_text_to_pdf_elements(

    text,

    body_style,

    heading1_style,

    heading2_style,

    bullet_style,

    number_style

):

    elements = []


    if not text:

        return elements


    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )


    lines = text.split("\n")


    paragraph_lines = []


    # ========================================================
    # FUNCTION TO ADD NORMAL PARAGRAPH
    # ========================================================

    def add_paragraph():

        nonlocal paragraph_lines

        if not paragraph_lines:

            return


        paragraph_text = " ".join(

            line.strip()

            for line in paragraph_lines

            if line.strip()

        )


        if paragraph_text:

            paragraph_text = format_inline_markdown(

                paragraph_text

            )


            elements.append(

                Paragraph(

                    paragraph_text,

                    body_style

                )

            )


            elements.append(

                Spacer(
                    1,
                    3
                )

            )


        paragraph_lines = []


    # ========================================================
    # PROCESS EACH LINE
    # ========================================================

    for line in lines:

        line = line.strip()


        # ====================================================
        # EMPTY LINE
        # ====================================================

        if not line:

            add_paragraph()

            continue


        # ====================================================
        # REMOVE TABLE FORMAT
        # ====================================================

        if "|" in line:

            # Convert table rows into readable text.
            # This prevents broken tables inside PDFs.

            parts = [

                part.strip()

                for part in line.strip("|").split("|")

                if part.strip()

            ]


            # Ignore Markdown separator rows

            if parts and all(

                re.fullmatch(
                    r"[-: ]+",
                    part
                )

                for part in parts

            ):

                continue


            add_paragraph()


            if parts:

                converted = " - ".join(parts)


                elements.append(

                    Paragraph(

                        format_inline_markdown(
                            converted
                        ),

                        bullet_style

                    )

                )


            continue


        # ====================================================
        # MARKDOWN HEADING 1
        # ====================================================

        if re.match(
            r"^#\s+",
            line
        ):

            add_paragraph()


            heading = re.sub(

                r"^#\s+",

                "",

                line

            )


            elements.append(

                Paragraph(

                    format_inline_markdown(
                        heading
                    ),

                    heading1_style

                )

            )


            continue


        # ====================================================
        # MARKDOWN HEADING 2
        # ====================================================

        if re.match(
            r"^##\s+",
            line
        ):

            add_paragraph()


            heading = re.sub(

                r"^##\s+",

                "",

                line

            )


            elements.append(

                Paragraph(

                    format_inline_markdown(
                        heading
                    ),

                    heading1_style

                )

            )


            continue


        # ====================================================
        # MARKDOWN HEADING 3
        # ====================================================

        if re.match(
            r"^###\s+",
            line
        ):

            add_paragraph()


            heading = re.sub(

                r"^###\s+",

                "",

                line

            )


            elements.append(

                Paragraph(

                    format_inline_markdown(
                        heading
                    ),

                    heading2_style

                )

            )


            continue


        # ====================================================
        # BULLET POINT
        # ====================================================

        bullet_match = re.match(

            r"^[-*•]\s+(.*)",

            line

        )


        if bullet_match:

            add_paragraph()


            bullet_text = bullet_match.group(1)


            elements.append(

                Paragraph(

                    "• " +

                    format_inline_markdown(
                        bullet_text
                    ),

                    bullet_style

                )

            )


            continue


        # ====================================================
        # NUMBERED LIST
        # ====================================================

        number_match = re.match(

            r"^(\d+)[.)]\s+(.*)",

            line

        )


        if number_match:

            add_paragraph()


            number = number_match.group(1)

            number_text = number_match.group(2)


            elements.append(

                Paragraph(

                    f"{number}. " +

                    format_inline_markdown(
                        number_text
                    ),

                    number_style

                )

            )


            continue


        # ====================================================
        # NORMAL TEXT
        # ====================================================

        paragraph_lines.append(

            line

        )


    # ========================================================
    # ADD REMAINING PARAGRAPH
    # ========================================================

    add_paragraph()


    return elements


# ============================================================
# FORMAT INLINE MARKDOWN
# ============================================================

def format_inline_markdown(text):

    if not text:

        return ""


    # ========================================================
    # ESCAPE HTML
    # ========================================================

    text = escape(
        str(text)
    )


    # ========================================================
    # BOLD
    # ========================================================

    text = re.sub(

        r"\*\*(.*?)\*\*",

        r"<b>\1</b>",

        text

    )


    # ========================================================
    # ITALIC
    # ========================================================

    text = re.sub(

        r"(?<!\*)\*([^*]+?)\*(?!\*)",

        r"<i>\1</i>",

        text

    )


    # ========================================================
    # INLINE CODE
    # ========================================================

    text = re.sub(

        r"`([^`]+)`",

        r"<font name='Courier'>\1</font>",

        text

    )


    return text


# ============================================================
# PAGE NUMBER
# ============================================================

def add_page_number(canvas, document):

    canvas.saveState()


    canvas.setFont(

        "Helvetica",

        8

    )


    canvas.setFillColor(

        colors.grey

    )


    page_number = canvas.getPageNumber()


    canvas.drawCentredString(

        A4[0] / 2,

        10 * mm,

        f"Page {page_number}"

    )


    canvas.restoreState()