#Trying to extract rules and entities from a policy document using spacy
#test comment
import fitz  # PyMuPDF
import spacy
import re
import logging
import os
from collections import defaultdict
from pdfminer.high_level import extract_text

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file_path = os.path.join(log_dir, "nlp_debug.log")
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

try:
    nlp = spacy.load("nl_core_news_lg")
except:
    nlp = spacy.load("nl_core_news_sm")


def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    logger.debug("Extracted text from %s: %s", pdf_path, text)
    return text


def categorize_sentences(text):
    rules = []
    entities = defaultdict(set)

    doc = nlp(text)
    for sent in doc.sents:
        sentence = sent.text.strip()

        # Rule Detection based on common verbs
        if re.search(r"\b(moet|dient|verplicht|mag niet|is verplicht|zijn verboden)\b", sentence, re.IGNORECASE):
            rules.append(sentence)

        # Named Entity Recognition
        for ent in sent.ents:
            entities[ent.label_].add(ent.text)

    return rules, {label: list(vals) for label, vals in entities.items()}


def extract_policy_insights(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    rules, entities = categorize_sentences(text)
    return {
        "rules": rules,
        "entities": entities
    }