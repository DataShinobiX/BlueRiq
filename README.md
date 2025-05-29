# Blueriq - PolicyIQ

PolicyIQ is an intelligent document analysis tool designed to assist business engineers in rapidly understanding and processing complex Dutch policy documents. It uses Natural Language Processing (NLP), interactive highlighting, and per-user learning to reduce time spent reading and manually analyzing regulatory content.

## 🔍 Features

- **PDF Upload and Parsing**: Upload Dutch policy PDFs and extract structured text.
- **Rule-Based NLP Pipeline**: Detects rules, definitions, exceptions, and external references using regex, fuzzy matching, and SpaCy dependency parsing.
- **Interactive UI**: Users can review and select/deselect extracted sentences for customized PDF highlighting.
- **Personalized Suggestions**: Learns from user behavior using logistic regression to recommend likely relevant sentences.
- **Smart PDF Highlighting**: Generates color-coded PDFs using PyMuPDF.
- **User Authentication**: Supports login, registration, and personalized sessions.

## 🛠️ Tech Stack

- **Backend**: Django, PyMuPDF, SpaCy (nl_core_news_lg)
- **Frontend**: HTML, CSS, JavaScript
- **ML/Modeling**: Logistic Regression (scikit-learn), Custom NLP heuristics
- **PDF Parsing**: PyMuPDF

## 🧠 NLP Strategy

- Rule extraction via:
  - Regex patterns
  - Fuzzy keyword matching
  - Dependency tree parsing
- Sentence classification into:
  - Rules
  - Definitions
  - Exceptions
  - External references
- Optional user-guided annotation for training data generation

## 🚀 Getting Started

1. Clone the repo
   ```
   git clone https://github.com/your-repo/blueriqiq.git
   cd blueriqiq
   ```

2. Create a virtual environment
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Run migrations and start the server
   ```
   python manage.py migrate
   python manage.py runserver
   ```

5. Access the application at `http://127.0.0.1:8000/`

## 👥 User Flow

1. Register or log in
2. Upload a document
3. View extracted insights
4. Select sentences for highlighting
5. Generate a highlighted PDF
6. Apply smart suggestions