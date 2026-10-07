import hashlib
import re

import requests
import streamlit as st


st.set_page_config(page_title="AI Personal Tutor")

st.title("AI Personal Tutor")
st.write("Upload a lecture PDF, ask questions, and create a quiz from it.")


# API connection settings stay in the sidebar.
st.sidebar.header("API connection")

api_url = st.sidebar.text_input(
    "API base URL",
    placeholder="https://your-ngrok-url.ngrok-free.dev",
).strip().rstrip("/")

api_token = st.sidebar.text_input(
    "Bearer token",
    type="password",
)


# Keep the conversation and quiz answers during this browser session.
if "history" not in st.session_state:
    st.session_state.history = []

if "indexed_pdf_key" not in st.session_state:
    st.session_state.indexed_pdf_key = ""

if "pdf_page_count" not in st.session_state:
    st.session_state.pdf_page_count = 0

if "indexed_pdf_pages" not in st.session_state:
    st.session_state.indexed_pdf_pages = []

if "indexed_chunk_count" not in st.session_state:
    st.session_state.indexed_chunk_count = 0

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

if "quiz_score_result" not in st.session_state:
    st.session_state.quiz_score_result = None


# The PDF uploader is on the main page, not in the sidebar.
st.subheader("Lecture PDF")

uploaded_pdf = st.file_uploader(
    "Upload a text-based PDF",
    type=["pdf"],
)

pdf_ready = False

if uploaded_pdf and api_url and api_token:
    pdf_bytes = uploaded_pdf.getvalue()
    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    upload_key = hashlib.sha256(
        f"{api_url}:{file_hash}".encode()
    ).hexdigest()

    if st.session_state.indexed_pdf_key != upload_key:
        with st.spinner("Uploading and reading the PDF..."):
            try:
                response = requests.post(
                    api_url + "/upload",
                    files={
                        "file": (
                            uploaded_pdf.name,
                            pdf_bytes,
                            "application/pdf",
                        )
                    },
                    headers={
                        "Authorization": f"Bearer {api_token}",
                    },
                    timeout=300,
                )

                if response.ok:
                    st.session_state.indexed_pdf_key = upload_key
                    upload_result = response.json()
                    st.session_state.pdf_page_count = upload_result.get(
                        "pages_loaded",
                        0,
                    )
                    st.session_state.indexed_chunk_count = upload_result.get(
                        "chunks_created",
                        0,
                    )

                    indexed_pages = upload_result.get("indexed_pages")

                    # Older upload endpoints may not return indexed pages.
                    # Ask the API's document-info endpoint if it is available.
                    if indexed_pages is None:
                        try:
                            info_response = requests.get(
                                api_url + "/document_info",
                                headers={
                                    "Authorization": f"Bearer {api_token}",
                                },
                                timeout=30,
                            )
                            if info_response.ok:
                                document_info = info_response.json()
                                indexed_pages = document_info.get(
                                    "indexed_pages",
                                    [],
                                )
                                st.session_state.indexed_chunk_count = (
                                    document_info.get(
                                        "chunks_created",
                                        st.session_state.indexed_chunk_count,
                                    )
                                )
                        except requests.exceptions.RequestException:
                            indexed_pages = []

                    st.session_state.indexed_pdf_pages = sorted(
                        {
                            int(page)
                            for page in (indexed_pages or [])
                            if str(page).isdigit()
                        }
                    )
                    st.session_state.pop("selected_pdf_pages", None)

                    st.success(
                        "PDF ready. "
                        f"Pages: {st.session_state.pdf_page_count}, "
                        f"readable pages: "
                        f"{', '.join(map(str, st.session_state.indexed_pdf_pages)) or 'not reported'}, "
                        f"chunks: {st.session_state.indexed_chunk_count}"
                    )
                else:
                    try:
                        error_message = response.json().get(
                            "detail",
                            response.text[:500],
                        )
                    except ValueError:
                        error_message = response.text[:500]

                    st.error(f"PDF upload failed: {error_message}")

            except requests.exceptions.RequestException as error:
                st.error(f"Could not reach the API: {error}")

    pdf_ready = st.session_state.indexed_pdf_key == upload_key

elif uploaded_pdf:
    st.info("Enter the API URL and Bearer token in the sidebar to use this PDF.")

if not uploaded_pdf:
    st.info("Upload a PDF here to get started.")


# The two sections appear as tabs in the main page.
explain_tab, quiz_tab = st.tabs(["Explain a topic", "Create a quiz"])


with explain_tab:
    st.header("Ask about your lecture")

    for turn in st.session_state.history:
        if turn["role"] == "user":
            st.markdown(f"**You:** {turn['content']}")
        else:
            st.markdown(f"**Tutor:** {turn['content']}")

    question = st.text_input(
        "What would you like explained?",
        key="topic_question",
    )

    ask_button = st.button("Ask the tutor", key="ask_tutor")

    if st.button("Clear conversation", key="clear_conversation"):
        st.session_state.history = []
        st.rerun()

    if ask_button:
        if not pdf_ready:
            st.error("Upload a readable PDF and enter the API details first.")
        elif not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("The tutor is reading the lecture..."):
                try:
                    response = requests.post(
                        api_url + "/chat",
                        json={
                            "topic": question,
                            "history": st.session_state.history[-6:],
                        },
                        headers={
                            "Authorization": f"Bearer {api_token}",
                        },
                        timeout=180,
                    )

                    response.raise_for_status()
                    answer = response.json()["explanation"]

                    st.session_state.history.append(
                        {"role": "user", "content": question}
                    )
                    st.session_state.history.append(
                        {"role": "assistant", "content": answer}
                    )

                    st.markdown(f"**Tutor:** {answer}")

                except requests.exceptions.RequestException as error:
                    st.error(f"Could not reach the API: {error}")
                except (ValueError, KeyError) as error:
                    st.error(f"The API returned an unexpected response: {error}")


with quiz_tab:
    st.header("Create a quiz")

    quiz_topic = st.text_input(
        "Optional focus topic",
        placeholder="Leave blank to cover the selected content broadly",
        key="quiz_topic",
    )

    question_count = st.number_input(
        "Number of questions",
        min_value=1,
        value=3,
        step=1,
        key="question_count",
    )

    if st.button("Generate quiz", key="generate_quiz"):
        if not pdf_ready:
            st.error("Upload a readable PDF and enter the API details first.")
        else:
            quiz_endpoint = api_url + "/quiz_by_scope"
            quiz_payload = {
                "scope": "all",
                "num_questions": int(question_count),
                "topic": quiz_topic,
            }

            with st.spinner("Creating the quiz..."):
                try:
                    response = requests.post(
                        quiz_endpoint,
                        json=quiz_payload,
                        headers={
                            "Authorization": f"Bearer {api_token}",
                        },
                        timeout=300,
                    )

                    response.raise_for_status()
                    new_quiz = response.json()

                    old_quiz = st.session_state.quiz_result
                    if isinstance(old_quiz, dict):
                        old_questions = old_quiz.get("questions", [])
                        for index in range(len(old_questions)):
                            st.session_state.pop(
                                f"quiz_answer_{index}",
                                None,
                            )

                    st.session_state.quiz_result = new_quiz
                    st.session_state.quiz_score_result = None

                except requests.exceptions.RequestException as error:
                    st.error(f"Could not reach the API: {error}")
                except ValueError as error:
                    st.error(f"The API returned invalid JSON: {error}")

    quiz_result = st.session_state.quiz_result

    if quiz_result:
        if "error" in quiz_result:
            st.error(quiz_result["error"])
        else:
            questions = quiz_result.get("questions", [])

            if questions:
                st.write("Choose one answer under each question.")

                with st.form("quiz_answers"):
                    for index, question in enumerate(questions):
                        st.markdown(
                            f"**Question {index + 1}: "
                            f"{question['question']}**"
                        )

                        question_pages = question.get("source_pages", [])
                        if not question_pages:
                            explanation = str(question.get("explanation", ""))
                            question_pages = re.findall(
                                r"\bpage\s+(\d+)\b",
                                explanation,
                                flags=re.IGNORECASE,
                            )

                        if question_pages:
                            unique_pages = sorted(
                                {int(page) for page in question_pages}
                            )
                            page_text = ", ".join(map(str, unique_pages))
                            st.caption(
                                "Lecture source: "
                                + ("page " if len(unique_pages) == 1 else "pages ")
                                + page_text
                            )
                        else:
                            st.caption(
                                "Lecture source: the API did not include a page number."
                            )

                        display_options = []
                        for option_index, option in enumerate(
                            question["options"][:4]
                        ):
                            option_text = re.sub(
                                r"^\s*[A-D]\s*[:.)-]\s*",
                                "",
                                str(option),
                                flags=re.IGNORECASE,
                            )
                            letter = chr(ord("A") + option_index)
                            display_options.append(
                                f"{letter}. {option_text}"
                            )

                        st.radio(
                            "Choose one answer",
                            options=display_options,
                            index=None,
                            key=f"quiz_answer_{index}",
                            label_visibility="collapsed",
                        )

                    submitted = st.form_submit_button("Check my answers")

                if submitted:
                    selected_options = [
                        st.session_state.get(
                            f"quiz_answer_{index}",
                        )
                        for index in range(len(questions))
                    ]

                    if any(answer is None for answer in selected_options):
                        st.warning("Please answer every question.")
                    else:
                        score = 0
                        details = []

                        for index, question in enumerate(questions):
                            selected = selected_options[index]
                            selected_label = selected.split(
                                ".",
                                1,
                            )[0].strip().upper()

                            correct_label = question[
                                "correct_answer"
                            ].strip().upper()

                            is_correct = selected_label == correct_label

                            if is_correct:
                                score += 1

                            details.append(
                                {
                                    "is_correct": is_correct,
                                    "correct_answer": correct_label,
                                    "explanation": question["explanation"],
                                }
                            )

                        st.session_state.quiz_score_result = {
                            "score": score,
                            "total": len(questions),
                            "details": details,
                        }

                score_result = st.session_state.quiz_score_result

                if score_result:
                    st.subheader(
                        f"Your score: {score_result['score']}/"
                        f"{score_result['total']}"
                    )

                    for index, detail in enumerate(
                        score_result["details"],
                        start=1,
                    ):
                        if detail["is_correct"]:
                            st.success(f"Question {index}: Correct")
                        else:
                            st.error(
                                f"Question {index}: The correct answer is "
                                f"{detail['correct_answer']}"
                            )

                        st.write(detail["explanation"])
