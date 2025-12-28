
# 🛡️ CrisisSafe

**Team Name:** Kernel Panic

**Submission Type:** Solo

CrisisSafe is a hybrid misinformation detection and critical thinking toolkit designed to combat the spread of digital wildfires during emergencies. Unlike traditional fact-checkers, CrisisSafe focuses on **transparency** and **user empowerment** rather than outright censorship.

## 🚀 The Core Innovation

CrisisSafe uses a **Dual-Core Verification Engine**:

1. **Rule-Based Logic:** Instantly detects "Panic Patterns" (excessive punctuation) and "Intensity Patterns" (all-caps shouting) that are characteristic of viral misinformation.
2. **Semantic AI Layer:** Leverages **GitHub Models (GPT-4o-mini)** to perform deep-dive factual verification and subjectivity analysis.

## ✨ Key Features

* **Semantic Nuance:** Distinguishes between technical truths (e.g., a "Sovereign State") and common-usage errors to prevent AI hallucinations.
* **Article Verification:** Integrated with **Newspaper3k** to extract and verify the actual text content of news URLs.
* **Subjectivity Detection:** Uses **TextBlob** to identify opinion-based statements. Instead of a "False" label, it provides a **Critical Thinking Framework** to help users evaluate nuances themselves.
* **Privacy-Ready:** Designed to support local LLM deployment (via RTX GPUs) for sensitive crisis data.

## 🛠️ Tech Stack

* **UI/UX:** Streamlit
* **Language:** Python 3.12+
* **AI Models:** GitHub Models API (GPT-4o-mini)
* **NLP Libraries:** TextBlob, Newspaper3k, LXML
* **Environment:** PyCharm / VS Code

## ⚙️ Installation & Setup

1. **Clone the Repo:**
```bash
git clone https://github.com/your-username/CrisisSafe.git
cd CrisisSafe

```


2. **Install Dependencies:**
```bash
pip install streamlit openai textblob newspaper3k lxml_html_clean python-dotenv

```


3. **Configure Environment:**
Create a `.env` file and add your GitHub Personal Access Token:
```text
GITHUB_TOKEN=your_ghp_token_here

```


4. **Run the App:**
```bash
streamlit run main.py

```



## 🧠 Ethical Handling of Misinformation

CrisisSafe addresses the challenge of misinformation without resorting to censorship:

* **Advisory Scores:** Provides a credibility percentage rather than a binary "Delete" command.
* **Explainable Indicators:** Every flag is accompanied by a reasoning component so the user understands *why* a score was lowered.
* **Opinion Respect:** Subjective political claims are flagged for perspective, encouraging users to engage in lateral reading.

---

**Developed with ❤️ by Team Kernel Panic for the 2025 AI Hackathon.**
