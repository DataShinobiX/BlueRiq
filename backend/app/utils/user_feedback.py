from app.models import SentenceFeedback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def get_user_feedback_data(user):
    """
    Retrieve all sentence feedback data for a given user,
    and return it as a list of training samples: (sentence, category, label)
    where label is 1 for 'kept' and 0 for 'removed'
    """
    feedback_entries = SentenceFeedback.objects.filter(user=user)
    data = []
    for entry in feedback_entries:
        label = 1 if entry.action == 'kept' else 0
        data.append((entry.sentence.strip(), entry.category, label))
    return data


def train_user_model(user):
    """
    Train a simple logistic regression classifier based on the user's feedback data.
    """
    # Get labeled training data
    samples = get_user_feedback_data(user)
    if not samples:
        return None

    X = [s[0] for s in samples]  # Sentences
    y = [s[2] for s in samples]  # Labels (0 or 1)

    # Define a basic pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000)),
        ('clf', LogisticRegression())
    ])

    model.fit(X, y)

    return model


def get_model_recommendations(model, sentences):
    """
    Use a trained model to recommend sentences predicted as relevant.
    Returns only the sentences with prediction = 1.
    """
    if not model or not sentences:
        return []
    preds = model.predict(sentences)
    return [sent for sent, pred in zip(sentences, preds) if pred == 1]

