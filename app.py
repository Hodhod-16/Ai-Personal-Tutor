import hashlib
import json
import re

import requests
import streamlit as st


st.set_page_config(
    page_title="AI Personal Tutor",
    page_icon="📖",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&display=swap');

    h1, h2, h3 {
        font-family: 'Bricolage Grotesque', 'Source Sans 3', sans-serif;
        letter-spacing: -0.01em;
    }
    .page-chip {
        display: inline-block;
        padding: 0 0.45rem;
        margin-right: 0.35rem;
        border-radius: 2px;
        background: linear-gradient(
            transparent 12%, #FFE45C 12%, #FFE45C 92%, transparent 92%
        );
        color: #1B2433;
        font-weight: 600;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .source-row {
        margin-top: 0.4rem;
        font-size: 0.85rem;
    }
    .source-label {
        opacity: 0.7;
        margin-right: 0.4rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
        background: #F1F4FA;
        padding: 0.45rem;
        border-radius: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        min-width: 0;
        justify-content: center;
        height: 3.25rem;
        padding: 0 0.9rem;
        border-radius: 0.75rem;
        background: transparent;
        font-size: 1.02rem;
        font-weight: 600;
        transition: background 150ms ease, color 150ms ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #2F55B5;
        color: #FFFFFF;
        box-shadow: 0 3px 10px rgba(47, 85, 181, 0.2);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    @media (max-width: 640px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.2rem;
            padding: 0.25rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            padding: 0 0.3rem;
            font-size: 0.86rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

TOKEN_MESSAGE = (
    "The API rejected the token. Enter the same value you saved as "
    "CV_API_TOKEN in Kaggle Secrets."
)
SOURCE_PATTERN = re.compile(r"Source pages:\s*([0-9,\s]+)$", re.IGNORECASE)


def describe_request_error(error):
    response = getattr(error, "response", None)
    if response is not None and response.status_code == 401:
        return TOKEN_MESSAGE
    if response is not None and response.status_code == 404:
        return (
            "This feature is not available in the running Kaggle API yet. "
            "Update the notebook cells and restart the API."
        )
    if isinstance(error, requests.exceptions.ConnectionError):
        return (
            "Could not reach the API. Check that the Kaggle notebook is still "
            "running and that the URL is the latest one."
        )
    if isinstance(error, requests.exceptions.Timeout):
        return (
            "The API took too long to answer. Try again, or ask for fewer "
            "questions or flashcards."
        )
    return f"The API request failed: {error}"


def post_json(endpoint, payload, timeout=180):
    try:
        response = requests.post(
            api_url + endpoint,
            json=payload,
            headers=auth_headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        st.error(describe_request_error(error))
    except ValueError:
        st.error("The API sent a reply the app could not read. Please try again.")
    return None


def page_chips(pages):
    if not pages:
        return
    safe_pages = sorted({int(page) for page in pages if str(page).isdigit()})
    if not safe_pages:
        return
    chips = "".join(
        f'<span class="page-chip">p. {page}</span>' for page in safe_pages
    )
    st.markdown(
        '<div class="source-row"><span class="source-label">'
        f"From the lecture</span>{chips}</div>",
        unsafe_allow_html=True,
    )


def split_answer(text):
    text = str(text).rstrip()
    match = SOURCE_PATTERN.search(text)
    if not match:
        return text, []
    pages = sorted({int(page) for page in re.findall(r"\d+", match.group(1))})
    return text[: match.start()].rstrip(), pages


def render_turn(role, content):
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    else:
        with st.chat_message("assistant"):
            body, pages = split_answer(content)
            st.markdown(body)
            page_chips(pages)


def question_pages(question):
    pages = question.get("source_pages", [])
    if not pages:
        explanation = str(question.get("explanation", ""))
        pages = re.findall(r"\bpage\s+(\d+)\b", explanation, flags=re.IGNORECASE)
    return sorted({int(page) for page in pages if str(page).isdigit()})


def display_options(question):
    options = []
    for option_index, option in enumerate(list(question.get("options", []))[:4]):
        option_text = re.sub(
            r"^\s*[A-D]\s*[:.)-]\s*",
            "",
            str(option),
            flags=re.IGNORECASE,
        )
        letter = chr(ord("A") + option_index)
        options.append(f"{letter}. {option_text}")
    return options


def clear_quiz_answers(question_total):
    for index in range(question_total):
        st.session_state.pop(f"quiz_answer_{index}", None)


def build_quiz_markdown(questions, include_answers=False):
    lines = ["# Lecture quiz", ""]

    for index, question in enumerate(questions, start=1):
        lines.append(f"## Question {index}: {question.get('question', '')}")
        pages = question_pages(question)
        if pages:
            lines.append("Source pages: " + ", ".join(map(str, pages)))
        lines.append("")

        for option in display_options(question):
            lines.append(f"- {option}")

        if include_answers:
            correct = str(question.get("correct_answer", "")).strip().upper()
            options_by_label = {
                option.split(".", 1)[0]: option
                for option in display_options(question)
            }
            lines.extend(
                [
                    "",
                    f"**Answer:** {options_by_label.get(correct, correct)}",
                    f"**Explanation:** {question.get('explanation', '')}",
                ]
            )
        lines.append("")

    return "\n".join(lines)


defaults = {
    "history": [],
    "indexed_pdf_key": "",
    "pdf_page_count": 0,
    "indexed_pdf_pages": [],
    "indexed_chunk_count": 0,
    "study_guide": None,
    "flashcard_result": None,
    "flashcard_index": 0,
    "flashcard_revealed": False,
    "quiz_result": None,
    "quiz_score_result": None,
}
for name, value in defaults.items():
    st.session_state.setdefault(name, value)


with st.sidebar:
    st.header("Connection")
    api_url = (
        st.text_input(
            "API base URL",
            placeholder="https://your-ngrok-url.ngrok-free.dev",
        )
        .strip()
        .rstrip("/")
    )
    api_token = st.text_input("Bearer token", type="password")

    if api_url and api_token:
        st.caption("The app connects after you upload a PDF.")
    else:
        st.caption("Enter both to continue.")

auth_headers = {"Authorization": f"Bearer {api_token}"}

st.title("AI Personal Tutor")
st.write(
    "Upload a lecture PDF, ask about what you do not understand, "
    "then review and test yourself."
)


def reset_document_results():
    st.session_state.history = []
    st.session_state.study_guide = None
    st.session_state.flashcard_result = None
    st.session_state.flashcard_index = 0
    st.session_state.flashcard_revealed = False
    old_quiz = st.session_state.quiz_result
    if isinstance(old_quiz, dict):
        clear_quiz_answers(len(old_quiz.get("questions", [])))
    st.session_state.quiz_result = None
    st.session_state.quiz_score_result = None


def upload_pdf(file_name, pdf_bytes, upload_key):
    try:
        response = requests.post(
            api_url + "/upload",
            files={"file": (file_name, pdf_bytes, "application/pdf")},
            headers=auth_headers,
            timeout=300,
        )
    except requests.exceptions.RequestException as error:
        st.error(describe_request_error(error))
        return False

    if not response.ok:
        if response.status_code == 401:
            st.error(TOKEN_MESSAGE)
            return False
        try:
            detail = response.json().get("detail", response.text[:500])
        except ValueError:
            detail = response.text[:500]
        st.error(f"The PDF could not be uploaded: {detail}")
        return False

    try:
        result = response.json()
    except ValueError:
        st.error("The API sent a reply the app could not read. Try uploading again.")
        return False

    reset_document_results()
    indexed_pages = result.get("indexed_pages") or []
    st.session_state.indexed_pdf_key = upload_key
    st.session_state.pdf_page_count = result.get("pages_loaded", 0)
    st.session_state.indexed_chunk_count = result.get("chunks_created", 0)
    st.session_state.indexed_pdf_pages = sorted(
        {int(page) for page in indexed_pages if str(page).isdigit()}
    )
    st.success("PDF indexed. You can ask questions or create study materials.")
    return True


uploaded_pdf = st.file_uploader("Lecture PDF", type=["pdf"])
pdf_ready = False
upload_key = ""

if uploaded_pdf and api_url and api_token:
    pdf_bytes = uploaded_pdf.getvalue()
    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    upload_key = hashlib.sha256(f"{api_url}:{file_hash}".encode()).hexdigest()

    if st.session_state.indexed_pdf_key != upload_key:
        with st.spinner("Reading the PDF..."):
            upload_pdf(uploaded_pdf.name, pdf_bytes, upload_key)

    pdf_ready = st.session_state.indexed_pdf_key == upload_key
elif uploaded_pdf:
    st.info("Enter the API URL and Bearer token in the sidebar first.")

if not pdf_ready:
    if not uploaded_pdf:
        st.info("Upload a lecture PDF to get started.")
    st.stop()


total_pages = st.session_state.pdf_page_count
readable_pages = len(st.session_state.indexed_pdf_pages)
if readable_pages and total_pages:
    st.caption(
        f"**{uploaded_pdf.name}**: {readable_pages} of {total_pages} pages "
        "have readable text."
    )



ask_tab, guide_tab, flashcard_tab, quiz_tab = st.tabs(
    ["Ask", "Study guide", "Flashcards", "Quiz"]
)


with ask_tab:
    if st.session_state.history:
        if st.button("Clear conversation", key="clear_conversation"):
            st.session_state.history = []
            st.rerun()
    else:
        st.caption(
            "Ask about a definition, a comparison, or a step in the lecture."
        )

    messages = st.container()
    prompt = st.chat_input("Ask about your lecture", key="chat_prompt")

    with messages:
        for turn in st.session_state.history:
            render_turn(turn["role"], turn["content"])

        if prompt:
            render_turn("user", prompt)
            answer = None
            with st.chat_message("assistant"):
                with st.spinner("Reading the lecture..."):
                    data = post_json(
                        "/chat",
                        {
                            "topic": prompt,
                            "history": st.session_state.history[-6:],
                        },
                        timeout=180,
                    )
                    if isinstance(data, dict):
                        answer = data.get("explanation")
                        if answer is None and data.get("error"):
                            st.error(data["error"])
                if answer is not None:
                    body, pages = split_answer(answer)
                    st.markdown(body)
                    page_chips(pages)

            if answer is not None:
                st.session_state.history.append({"role": "user", "content": prompt})
                st.session_state.history.append(
                    {"role": "assistant", "content": answer}
                )


with guide_tab:
    st.caption(
        "Create a short overview and key points from the readable lecture text."
    )
    guide_topic = st.text_input(
        "Focus topic (optional)",
        placeholder="Leave blank to cover the whole lecture",
        key="guide_topic",
    )

    if st.button("Create study guide", type="primary", key="create_study_guide"):
        with st.spinner("Summarizing the lecture..."):
            st.session_state.study_guide = post_json(
                "/study_guide",
                {"focus_topic": guide_topic},
                timeout=300,
            )

    guide = st.session_state.study_guide
    if isinstance(guide, dict):
        if guide.get("error"):
            st.error(guide["error"])
        elif guide.get("summary"):
            st.subheader("Summary")
            st.write(guide["summary"])

            points = guide.get("key_points", [])
            if points:
                st.subheader("Key points")
                for point in points:
                    st.markdown(f"- {point}")

            page_chips(guide.get("source_pages", []))


with flashcard_tab:
    st.caption("Make question-and-answer cards from the lecture, then reveal answers.")
    flashcard_topic = st.text_input(
        "Focus topic (optional)",
        placeholder="Leave blank to cover the whole lecture",
        key="flashcard_topic",
    )
    flashcard_count = st.number_input(
        "Number of cards",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        key="flashcard_count",
    )

    if st.button("Create flashcards", type="primary", key="create_flashcards"):
        with st.spinner("Creating flashcards..."):
            st.session_state.flashcard_result = post_json(
                "/flashcards",
                {
                    "num_cards": int(flashcard_count),
                    "topic": flashcard_topic,
                },
                timeout=300,
            )
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_revealed = False

    card_result = st.session_state.flashcard_result
    if isinstance(card_result, dict):
        if card_result.get("error"):
            st.error(card_result["error"])
        else:
            cards = card_result.get("cards", [])
            if cards:
                index = min(st.session_state.flashcard_index, len(cards) - 1)
                card = cards[index]

                st.progress((index + 1) / len(cards))
                st.caption(f"Card {index + 1} of {len(cards)}")

                with st.container(border=True):
                    st.markdown("**Question**")
                    st.write(card.get("question", ""))

                    if st.session_state.flashcard_revealed:
                        st.divider()
                        st.markdown("**Answer**")
                        st.write(card.get("answer", ""))
                        page_chips(card.get("source_pages", []))
                    elif st.button("Show answer", key=f"show_answer_{index}"):
                        st.session_state.flashcard_revealed = True
                        st.rerun()

                previous_col, next_col = st.columns(2)
                if previous_col.button(
                    "Previous",
                    disabled=index == 0,
                    key="previous_flashcard",
                ):
                    st.session_state.flashcard_index = index - 1
                    st.session_state.flashcard_revealed = False
                    st.rerun()
                if next_col.button(
                    "Next",
                    disabled=index >= len(cards) - 1,
                    key="next_flashcard",
                ):
                    st.session_state.flashcard_index = index + 1
                    st.session_state.flashcard_revealed = False
                    st.rerun()


with quiz_tab:
    topic_col, count_col = st.columns([3, 1])
    quiz_topic = topic_col.text_input(
        "Focus topic (optional)",
        placeholder="Leave blank to cover the whole lecture",
        key="quiz_topic",
    )
    question_count = count_col.number_input(
        "Questions",
        min_value=1,
        value=3,
        step=1,
        key="question_count",
    )

    if st.button("Create quiz", type="primary", key="generate_quiz"):
        with st.spinner("Writing questions from the lecture..."):
            new_quiz = post_json(
                "/quiz_by_scope",
                {
                    "scope": "all",
                    "num_questions": int(question_count),
                    "topic": quiz_topic,
                },
                timeout=300,
            )
            if new_quiz is not None:
                old_quiz = st.session_state.quiz_result
                if isinstance(old_quiz, dict):
                    clear_quiz_answers(len(old_quiz.get("questions", [])))
                st.session_state.quiz_result = new_quiz
                st.session_state.quiz_score_result = None

    quiz_result = st.session_state.quiz_result
    if isinstance(quiz_result, dict):
        if quiz_result.get("error"):
            st.error(quiz_result["error"])
        else:
            questions = quiz_result.get("questions", [])
            if questions:
                quiz_file = build_quiz_markdown(questions, include_answers=False)
                answer_key_file = build_quiz_markdown(
                    questions,
                    include_answers=True,
                )
                download_col, key_col = st.columns(2)
                download_col.download_button(
                    "Download quiz",
                    data=quiz_file,
                    file_name="lecture_quiz.md",
                    mime="text/markdown",
                    key="download_quiz",
                )
                key_col.download_button(
                    "Download answer key",
                    data=answer_key_file,
                    file_name="lecture_quiz_answer_key.md",
                    mime="text/markdown",
                    key="download_answer_key",
                )

                with st.form("quiz_answers"):
                    for index, question in enumerate(questions):
                        with st.container(border=True):
                            st.markdown(
                                f"**{index + 1}. {question.get('question', '')}**"
                            )
                            page_chips(question_pages(question))
                            st.radio(
                                "Choose one answer",
                                options=display_options(question),
                                index=None,
                                key=f"quiz_answer_{index}",
                                label_visibility="collapsed",
                            )
                    submitted = st.form_submit_button(
                        "Check answers",
                        type="primary",
                    )

                if submitted:
                    selected_options = [
                        st.session_state.get(f"quiz_answer_{index}")
                        for index in range(len(questions))
                    ]
                    if any(answer is None for answer in selected_options):
                        st.warning("Answer every question, then check again.")
                    else:
                        score = 0
                        details = []
                        for index, question in enumerate(questions):
                            options = display_options(question)
                            selected = selected_options[index]
                            selected_label = selected.split(".", 1)[0].strip().upper()
                            correct_label = (
                                str(question.get("correct_answer", "")).strip().upper()
                            )
                            is_correct = selected_label == correct_label
                            if is_correct:
                                score += 1

                            by_label = {
                                option.split(".", 1)[0]: option for option in options
                            }
                            details.append(
                                {
                                    "is_correct": is_correct,
                                    "selected_text": selected,
                                    "correct_text": by_label.get(
                                        correct_label,
                                        correct_label,
                                    ),
                                    "explanation": question.get("explanation", ""),
                                    "pages": question_pages(question),
                                }
                            )

                        st.session_state.quiz_score_result = {
                            "score": score,
                            "total": len(questions),
                            "details": details,
                        }

    score_result = st.session_state.quiz_score_result
    if score_result:
        st.divider()
        st.subheader(f"Score: {score_result['score']}/{score_result['total']}")
        st.progress(score_result["score"] / score_result["total"])

        for index, detail in enumerate(score_result["details"], start=1):
            with st.container(border=True):
                if detail["is_correct"]:
                    st.markdown(
                        f"✅ **{index}. Correct**  \n{detail['correct_text']}"
                    )
                else:
                    st.markdown(
                        f"❌ **{index}. Not quite**  \n"
                        f"You chose {detail['selected_text']}  \n"
                        f"Correct answer: {detail['correct_text']}"
                    )
                if detail["explanation"]:
                    st.write(detail["explanation"])
                page_chips(detail["pages"])

        if st.button("Try the quiz again", key="retake_quiz"):
            clear_quiz_answers(score_result["total"])
            st.session_state.quiz_score_result = None
            st.rerun()
