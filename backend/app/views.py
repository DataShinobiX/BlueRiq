from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.highlight_pdf import highlight_important_parts   ## path to util for highlighting tool
from .utils.highlight_pdf import identify_important_parts


def upload_document(request):
    if request.method == 'POST' and request.FILES['document']:
        document = request.FILES['document']
        fs = FileSystemStorage()
        filename = fs.save(document.name, document)
        input_pdf = fs.path(filename)
        output_pdf = fs.path("highlighted_" + document.name)
        
        # Highlight important parts
        important_parts = identify_important_parts(input_pdf)  #Need to link code to nlp for highlighting important parts
        highlight_important_parts(input_pdf, output_pdf, important_parts)
    
        uploaded_file_url = fs.url(output_pdf)
        return render(request, 'upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'upload.html')

