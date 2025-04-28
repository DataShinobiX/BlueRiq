from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.nlp_processor import extract_policy_insights, highlight_pdf


def upload_document(request):
    if request.method == 'POST' and request.FILES.get('document'):
        document = request.FILES['document']
        fs = FileSystemStorage()
        filename = fs.save("uploads/" + document.name, document)
        input_pdf_path = fs.path(filename)

        insights = extract_policy_insights(input_pdf_path)

        # Create a highlighted PDF
        output_pdf_filename = "highlighted_" + document.name
        output_pdf_path = fs.path("uploads/" + output_pdf_filename)

        highlight_pdf(input_pdf_path, output_pdf_path, insights)

        return render(request, 'upload.html', {
            'filename': filename,
            'rules': insights.get('rules', []),
            'entities': insights.get('entities', {}),
            'definitions': insights.get('definitions', []),
            'exceptions': insights.get('exceptions', []),
            'external_sources': insights.get('external_sources', []),
            'highlighted_pdf_url': fs.url("uploads/" + output_pdf_filename)
        })

    return render(request, 'upload.html')
