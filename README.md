# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> This project was built during the [Tips Hindawi](https://www.tipshindawi.com/) **Internship (August–October 2026)**.

## 👤 Participant

| Field | Value |
| --- | --- |
| Full Name | Hoda Ashraf Mohamed Abdelghany|
| Project Name | AI Personal Tutor |
| GitHub Username | [Hodhod-16](https://github.com/Hodhod-16) |
| Internship Batch | August–October 2026 |
| Training Program | Large Language Models (LLMs) Program |
| Organization | [Edrak for AI](https://edrak4ai.com/en) |

---

# 📖 Project Overview

AI Personal Tutor helps students study from their lecture PDFs. After uploading a text-based PDF, a student can ask questions about the lecture, receive an explanation with source page numbers, or generate a multiple-choice quiz from the full document. The app also checks the student's answers and shows a score with explanations.

The Streamlit interface sends the PDF and questions to a FastAPI service. The service runs in a Kaggle notebook, retrieves relevant lecture text, and uses a quantized Mistral-Nemo model to generate responses grounded in that text.

---

# ✨ Features

* Upload a text-based lecture PDF and index its readable pages.
* Ask questions about the lecture and receive answers with source page numbers.
* Continue a conversation with short chat history for follow-up questions.
* Generate a full-PDF multiple-choice quiz with a user-selected number of questions and an optional focus topic.
* Answer quiz questions in the app and see the score and explanations.
* Protect API requests with Bearer token authentication.

---

# 🛠️ Technologies Used

* Python
* PyTorch and Hugging Face Transformers
* Mistral-Nemo-Instruct-2407 with 4-bit bitsandbytes quantization
* LangChain: PyPDFLoader, CharacterTextSplitter, HuggingFaceEmbeddings, FAISS, PromptTemplate, and StructuredOutputParser
* FastAPI and Uvicorn
* pyngrok
* Streamlit
* Kaggle GPU for model inference

---

# ⚙️ Installation

## Start the model API on Kaggle

1. Open the project notebook in Kaggle and select a GPU accelerator if one is available.
2. Attach the lecture PDF as a Kaggle dataset input.
3. Add these two secrets in Kaggle **Add-ons → Secrets**. Use your own secret values; never put them in notebook code.

```text
CV_API_TOKEN=your_private_api_token
NGROK_AUTHTOKEN=your_ngrok_authtoken
```

4. Run the notebook cells from top to bottom. The final cells start FastAPI and the ngrok tunnel.
5. Copy the printed **Public API URL**. Keep the Kaggle session running while using the app.

## Install and run the Streamlit app locally

Open a terminal in the folder containing `app.py`, then install the app's Python packages:

```bash
pip install streamlit requests
```

Start Streamlit:

```bash
streamlit run app.py
```

---

# 🚀 Usage

1. Start the Kaggle API and copy its public base URL. Use the URL without `/chat`, `/upload`, or another endpoint suffix.
2. Open the Streamlit app and enter the API base URL and the matching `CV_API_TOKEN` in the sidebar.
3. Upload a text-based PDF in the **Lecture PDF** section.
4. In **Explain a topic**, ask a question about the lecture. The tutor returns an answer and the source page numbers it used.
5. In **Create a quiz**, choose the number of questions and optionally enter a focus topic. Leave the topic blank for a broad quiz about the PDF.
6. Select one answer for each question and submit to see your score and explanations.

The ngrok URL can change when a new tunnel is started. Update the URL in the app when that happens.

---

# 📸 Demo

Add screenshots of the PDF upload, lecture explanation, and quiz results here. A short screen recording can also be linked here:

```text
Demo video: add link here
```

---

# 📈 Results

The app was manually tested with lecture PDFs. The tested workflow includes PDF upload and indexing, asking lecture questions with page citations, generating a quiz, submitting answers, and viewing the score and explanations.

No formal accuracy benchmark has been completed. Generated explanations and quiz questions can still contain mistakes, so students should check them against the lecture material.

---

# 🔮 Future Improvements

* Add OCR support for scanned PDFs.
* Evaluate answer and quiz quality on a labeled test set and improve the prompts based on measured errors.
* Improve support for long PDFs and pages with little or repeated text.
* Host the model API on a more persistent service so it does not depend on an active Kaggle session and ngrok tunnel.

---

# 📚 About the Internship

This project was developed as part of the [Tips Hindawi](https://www.tipshindawi.com/) **Internship (August–October 2026)**, and it will be showcased on the official [Tips Hindawi](https://www.tipshindawi.com/) website.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [Edrak for AI](https://edrak4ai.com/en), and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
