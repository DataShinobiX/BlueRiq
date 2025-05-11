from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.nlp_processor import extract_policy_insights, highlight_pdf


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

        output_pdf_path = fs.path("uploads/" + output_pdf_filename)
        highlight_pdf(input_pdf_path, output_pdf_path, insights)

        return render(request, 'upload.html', {
            'filename': filename,
            'rules': insights.get('rules', []),
            'definitions': insights.get('definitions', []),
            'exceptions': insights.get('exceptions', []),
            'external_sources': insights.get('external_sources', []),
            'highlighted_pdf_url': fs.url("uploads/" + output_pdf_filename)
        })

    return render(request, 'upload.html')
