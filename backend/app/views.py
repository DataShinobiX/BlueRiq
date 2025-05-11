from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.nlp_processor import extract_policy_insights, highlight_pdf
from .models import SentenceFeedback
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .utils.user_feedback import train_user_model, get_model_recommendations
from django.contrib.auth import login

@login_required
def upload_document(request):
    fs = FileSystemStorage()
    if request.method == 'POST':
        if 'document' in request.FILES:
            document = request.FILES['document']
            upload_subdir = "uploads/"
            filename = document.name
            saved_path = fs.save(upload_subdir + filename, document)
            input_pdf_path = fs.path(saved_path)

            insights = extract_policy_insights(input_pdf_path)

            output_pdf_filename = "highlighted_" + filename
        else:
            # reuse existing file
            filename = request.POST.get('filename')
            input_pdf_path = fs.path("uploads/" + filename)
            insights = extract_policy_insights(input_pdf_path)

            output_pdf_filename = "highlighted_" + filename

        # Override sentence categories only if not a file upload (i.e., checkbox resubmission)
        if 'document' not in request.FILES:
            insights['rules'] = request.POST.getlist('selected_rules')
            insights['definitions'] = request.POST.getlist('selected_definitions')
            insights['exceptions'] = request.POST.getlist('selected_exceptions')
            insights['external_sources'] = request.POST.getlist('selected_sources')

        # If user wants recommendations, apply user model filtering
        if 'apply_suggestions' in request.POST:
            model = train_user_model(request.user)
            if model:
                insights['rules'] = get_model_recommendations(model, insights.get('rules', []))
                insights['definitions'] = get_model_recommendations(model, insights.get('definitions', []))
                insights['exceptions'] = get_model_recommendations(model, insights.get('exceptions', []))
                insights['external_sources'] = get_model_recommendations(model, insights.get('external_sources', []))

        output_pdf_path = fs.path("uploads/" + output_pdf_filename)
        highlight_pdf(input_pdf_path, output_pdf_path, insights)

        # Log user feedback if resubmitting
        if 'document' not in request.FILES and request.user.is_authenticated:
            all_sentences = {
                "rules": insights.get("rules", []) + request.POST.getlist("selected_rules"),
                "definitions": insights.get("definitions", []) + request.POST.getlist("selected_definitions"),
                "exceptions": insights.get("exceptions", []) + request.POST.getlist("selected_exceptions"),
                "external_sources": insights.get("external_sources", []) + request.POST.getlist("selected_sources"),
            }
            for category in all_sentences:
                extracted = set(all_sentences[category])
                selected = set(request.POST.getlist(f"selected_{category}"))
                for sentence in extracted:
                    action = "kept" if sentence in selected else "removed"
                    SentenceFeedback.objects.create(
                        user=request.user,
                        filename=filename,
                        sentence=sentence,
                        category=category,
                        action=action,
                        timestamp=timezone.now()
                    )

        return render(request, 'upload.html', {
            'filename': filename,
            'rules': insights.get('rules', []),
            'definitions': insights.get('definitions', []),
            'exceptions': insights.get('exceptions', []),
            'external_sources': insights.get('external_sources', []),
            'highlighted_pdf_url': fs.url("uploads/" + output_pdf_filename)
        })

    return render(request, 'upload.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_document')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
