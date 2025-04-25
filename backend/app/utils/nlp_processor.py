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

#test

def categorize_sentences(text):
    rules = []
    definitions = []
    exceptions = []
    external_sources = []
    entities = defaultdict(set)

    doc = nlp(text)
    sentences = list(doc.sents)
    
    # Process sentences in pairs to catch if-then constructions across sentences
    for i in range(len(sentences)):
        current_sent = sentences[i].text.strip()
        next_sent = sentences[i + 1].text.strip() if i + 1 < len(sentences) else ""
        
        # Check for if-then pattern within single sentence
        if re.search(r"\b(is|als|indien|wanneer|mits|in het geval dat)\b.*\b(dan|wordt|is|geldt|moet|dient|kan|mag)\b", current_sent, re.IGNORECASE):
            rules.append(current_sent)
        
        # Check for if-then pattern across two sentences
        elif re.search(r"\b(is|als|indien|wanneer|mits|in het geval dat)\b", current_sent, re.IGNORECASE) and \
             re.search(r"\b(dan|wordt|is|geldt|moet|dient|kan|mag)\b", next_sent, re.IGNORECASE):
            rules.append(f"{current_sent} {next_sent}")
        
        # Rule detection
        elif re.search(r"\b(kan|mag|moet|in het geval dat|dient|geldend van|hebben recht op)\b", current_sent, re.IGNORECASE):
            rules.append(current_sent)

        if re.search(r"\b(is|het geval|=)\b", current_sent, re.IGNORECASE):
            definitions.append(current_sent)

        if re.search(r"\b(indien|alsnog|niet|geval|maar)\b", current_sent, re.IGNORECASE):
            exceptions.append(current_sent)

        if re.search(r"\b(artikel|wetvoorstel|wet)\b", current_sent, re.IGNORECASE):
            external_sources.append(current_sent)

        # Named Entity Recognition
        for ent in sentences[i].ents:
            entities[ent.label_].add(ent.text)

    return rules, {label: list(vals) for label, vals in entities.items()}


def extract_policy_insights(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    rules, entities = categorize_sentences(text)
    return {
        "rules": rules,
        "entities": entities
    }