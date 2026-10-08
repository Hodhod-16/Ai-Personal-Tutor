# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October 2026)

> 🎓 This project was built during the [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October 2026).

## 👤 Participant

| Field | Value |
| --- | --- |
| Full Name | Hoda Ashraf Mohamed Abdelghany |
| Project Name | AI Personal Tutor |
| GitHub Username | [Hodhod-16](https://github.com/Hodhod-16) |
| Internship Batch | August–October 2026 |
| Training Program | Large Language Models (LLMs) Program |
| Organization | [Edrak for AI](https://edrak4ai.com/en) |

---

# 📖 Project Overview

AI Personal Tutor helps students study from lecture PDFs. After uploading a text-based PDF, a student can ask questions about the lecture, request a short study guide, create flashcards, or generate an interactive multiple-choice quiz.

The Streamlit app sends requests to a FastAPI service running in a Kaggle notebook. The service reads the PDF, retrieves lecture text, and uses a 4-bit quantized Mistral-Nemo model to generate answers grounded in that text.

---

# ✨ Features

- Upload and index a text-based lecture PDF.
- Ask questions and follow up in a chat; answers include source page numbers.
- Generate a short study guide with key points and source pages.
- Create question-and-answer flashcards, reveal answers, and move between cards.
- Generate a multiple-choice quiz from the full PDF, with an optional focus topic and a chosen question count.
- Check quiz answers and view a score, explanations, and source pages.
- Download the quiz and its answer key as Markdown files.
- Protect API requests with Bearer token authentication.

---

# 🛠️ Technologies Used

- Python and PyTorch
- Hugging Face Transformers
- Mistral-Nemo-Instruct-2407
- bitsandbytes 4-bit quantization
- LangChain: PyPDFLoader, CharacterTextSplitter, HuggingFaceEmbeddings, FAISS, PromptTemplate, and StructuredOutputParser
- FastAPI and Uvicorn
- pyngrok
- Streamlit
- Kaggle GPU

The project uses retrieval and prompting; the model is not fine-tuned.

---

# ⚙️ Installation

## Start the model API on Kaggle

1. Open the project notebook and enable a GPU accelerator.
2. Attach a text-based lecture PDF dataset as notebook input. The notebook uses a PDF for its initial index; a PDF can also be uploaded through the app.
3. Add these secret names in Kaggle Add-ons → Secrets, using your own values:
   - CV_API_TOKEN
   - NGROK_AUTHTOKEN
4. Run the notebook cells in order. The final cells start FastAPI and ngrok and print the public base URL.
5. Keep the Kaggle session and ngrok tunnel running while using the app. The public URL can change when a new tunnel starts.

Do not put real tokens in the notebook, README, or GitHub.

## Install and run the Streamlit app locally

Open a terminal in the folder containing app.py, then install the frontend requirements:

~~~bash
pip install -r requirements.txt
~~~

Start Streamlit:

~~~bash
streamlit run app.py
~~~

The theme file belongs in the .streamlit folder beside app.py:

~~~text
.streamlit/config.toml
~~~

---

# 🚀 Usage

1. Start the Kaggle API and copy its public base URL. Enter the base URL in the app without an endpoint suffix such as /chat or /upload.
2. Enter the matching CV_API_TOKEN in the sidebar.
3. Upload a text-based PDF in the Lecture PDF area.
4. Use Ask to ask questions and follow up. Answers include source pages.
5. Use Study guide to create a summary and key points. A focus topic is optional.
6. Use Flashcards to create question-and-answer cards, reveal answers, and navigate through them.
7. Use Quiz to choose the question count and an optional topic, answer each question, and check the result.
8. Download the quiz or the separate answer key from the Quiz tab.

---

# 📸 Demo

<img width="1298" height="915" alt="image" src="https://github.com/user-attachments/assets/3eaea32c-78e5-4c08-854b-c6de1db5e6e0" />


---

# 📈 Results

Manual checks confirmed the main workflow with a text-based lecture PDF: upload and indexing, question answering with page citations, quiz generation, answer checking, and scoring.

The study guide and flashcard endpoints have been added to the current implementation and need end-to-end validation in the active Kaggle session. No formal accuracy benchmark has been completed. Generated material can contain mistakes and should be checked against the lecture.

---

# 🔮 Future Improvements

- Add OCR support for scanned PDFs.
- Evaluate explanation and quiz quality on a labeled test set.
- Improve handling of long PDFs and pages with little or repeated text.
- Host the API on a persistent service so it does not depend on an active Kaggle session and ngrok tunnel.

---

# 📚 About the Internship

This project was developed as part of the [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October 2026).

Tips Hindawi is the internships department of [Edrak for AI](https://edrak4ai.com/en). The program encourages participants to build practical projects and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the [Tips Hindawi website](https://www.tipshindawi.com/).

---

# 📄 License

This project is shared for educational and portfolio purposes.
