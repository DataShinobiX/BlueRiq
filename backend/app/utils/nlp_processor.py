#Extract rules and entities from a policy document using spacy
import fitz  # PyMuPDF
import spacy
import re
import logging
import os
from collections import defaultdict
from pdfminer.high_level import extract_text
from rapidfuzz import fuzz

from .pattern_config import PATTERN_CONFIG

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
    logger.debug("Extracted text from %s", pdf_path)
    return text


def categorize_sentences(text):
    rules = []
    definitions = []
    exceptions = []
    external_sources = []
    entities = defaultdict(set)

    regex_rule_count = 0
    dep_rule_count = 0

    rule_templates = PATTERN_CONFIG.get("rule_templates", [])
    definition_templates = PATTERN_CONFIG.get("definition_templates", [])
    exception_templates = PATTERN_CONFIG.get("exception_templates", [])
    source_templates = PATTERN_CONFIG.get("source_templates", [])
    exclusion_phrases = PATTERN_CONFIG.get("exclusion_phrases", [])
    exclusion_keywords = PATTERN_CONFIG.get("exclusion_keywords", [])

    # Extract additional patterns
    if_then_keywords = PATTERN_CONFIG.get("if_then_keywords", [])
    then_keywords = PATTERN_CONFIG.get("then_keywords", [])
    rule_regex_keywords = PATTERN_CONFIG.get("rule_regex_keywords", [])

    def is_fuzzy_match(sentence, templates, threshold=85):
        return any(fuzz.partial_ratio(sentence.lower(), tpl.lower()) >= threshold for tpl in templates)

    def is_descriptive_or_emotional(sentence):
        lowered = sentence.lower()
        if any(phrase in lowered for phrase in exclusion_phrases):
            return True
        if any(fuzz.partial_ratio(lowered, kw) > 80 for kw in exclusion_keywords):
            return True
        return False

    def is_dependency_rule(sent):
        for token in sent:
            if token.dep_ in ("ROOT", "aux") and token.lemma_.lower() in rule_templates:
                return True
        return False

    doc = nlp(text)
    sentences = list(doc.sents)

    for i in range(len(sentences)):
        current_sent = sentences[i].text.strip()
        next_sent = sentences[i + 1].text.strip() if i + 1 < len(sentences) else ""

        # Check for if-then pattern within single sentence
        if re.search(rf"\b({'|'.join(if_then_keywords)})\b.*\b({'|'.join(then_keywords)})\b", current_sent, re.IGNORECASE):
            rules.append(current_sent)

        # Check for if-then pattern across two sentences
        elif re.search(rf"\b({'|'.join(if_then_keywords)})\b", current_sent, re.IGNORECASE) and \
             re.search(rf"\b({'|'.join(then_keywords)})\b", next_sent, re.IGNORECASE):
            rules.append(f"{current_sent} {next_sent}")

        # Rule detection: regex + fuzzy
        elif re.search(rf"\b({'|'.join(rule_regex_keywords)})\b", current_sent, re.IGNORECASE) or \
             is_fuzzy_match(current_sent, rule_templates):
            if not is_descriptive_or_emotional(current_sent):
                rules.append(current_sent)
                regex_rule_count += 1
                # logger.info(f"Rule (regex): {current_sent}")

        # Rule detection: dependency parsing based
        elif is_dependency_rule(sentences[i]):
            if not is_descriptive_or_emotional(current_sent):
                rules.append(current_sent)
                dep_rule_count += 1
                # logger.info(f"Rule (dep): {current_sent}")

        # Definition detection
        if re.search(r"\b(is|het geval|=)\b", current_sent, re.IGNORECASE) or \
           is_fuzzy_match(current_sent, definition_templates):
            definitions.append(current_sent)

        # Exception detection
        if re.search(r"\b(indien|alsnog|niet|geval|maar)\b", current_sent, re.IGNORECASE) or \
           is_fuzzy_match(current_sent, exception_templates):
            exceptions.append(current_sent)

        # External source detection
        if re.search(r"\b(artikel|wetvoorstel|wet)\b", current_sent, re.IGNORECASE) or \
           is_fuzzy_match(current_sent, source_templates):
            external_sources.append(current_sent)

        # Named Entity Recognition
        for ent in sentences[i].ents:
            entities[ent.label_].add(ent.text)

    # Log summary counts
    logger.info(f"Total rules by regex: {regex_rule_count}")
    logger.info(f"Total rules by dependency parsing: {dep_rule_count}")

    return rules, {label: list(vals) for label, vals in entities.items()}, definitions, exceptions, external_sources

def highlight_pdf(input_pdf_path, output_pdf_path, categorized_data):
    doc = fitz.open(input_pdf_path)

    color_map = {
        "rules": (1, 1, 0),           # Yellow
        "exceptions": (1, 0.6, 0.6),  # Light Coral
        "definitions": (0.8, 1, 0.8), # Light Green
        "external_sources": (0.8, 0.6, 1), # Plum
        "entities": (0.5, 0.8, 1),    # Light Blue
    }

    # Define priority (lower = higher priority)
    priority_map = {
        "rules": 1,
        "exceptions": 2,
        "definitions": 3,
        "external_sources": 4,
        "entities": 5
    }

    # Track the highest-priority category for each sentence
    sentence_categories = {}

    for sentence in categorized_data.get("rules", []):
        sentence_categories[sentence] = "rules"

    for sentence in categorized_data.get("exceptions", []):
        if sentence not in sentence_categories or priority_map["exceptions"] < priority_map[sentence_categories[sentence]]:
            sentence_categories[sentence] = "exceptions"

    for sentence in categorized_data.get("definitions", []):
        if sentence not in sentence_categories or priority_map["definitions"] < priority_map[sentence_categories[sentence]]:
            sentence_categories[sentence] = "definitions"

    for sentence in categorized_data.get("external_sources", []):
        if sentence not in sentence_categories or priority_map["external_sources"] < priority_map[sentence_categories[sentence]]:
            sentence_categories[sentence] = "external_sources"

    for entity_list in categorized_data.get("entities", {}).values():
        for sentence in entity_list:
            if sentence not in sentence_categories:
                sentence_categories[sentence] = "entities"

    # Apply one highlight per sentence based on highest-priority category
    for page in doc:
        for sentence, category in sentence_categories.items():
            if not sentence.strip():
                continue
            rects = page.search_for(sentence, quads=False)
            for rect in rects:
                highlight = page.add_highlight_annot(rect)
                highlight.set_colors(stroke=color_map[category])
                highlight.update()

    doc.save(output_pdf_path)
    doc.close()


def extract_policy_insights(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    rules, entities, definitions, exceptions, external_sources = categorize_sentences(text)
    return {
        "rules": rules,
        "entities": entities,
        "definitions": definitions,
        "exceptions": exceptions,
        "external_sources": external_sources
    }