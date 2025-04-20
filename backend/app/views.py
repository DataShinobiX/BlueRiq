from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.nlp_processor_copy import extract_policy_insights


def upload_document(request):
    if request.method == 'POST' and request.FILES.get('document'):
        document = request.FILES['document']
        fs = FileSystemStorage()
        filename = fs.save("uploads/" + document.name, document)
        input_pdf_path = fs.path(filename)

        insights = extract_policy_insights(input_pdf_path)

        return render(request, 'upload.html', {
            'filename': filename,
            'rules': insights.get('rules', []),
            'definitions': insights.get('definitions', []),
            'exceptions': insights.get('exceptions', []),
            'external_sources': insights.get('external_sources', []),
            'entities': insights.get('entities', {})
        })

    return render(request, 'upload.html')
