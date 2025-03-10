from django.shortcuts import render
from django.http import HttpResponse

def upload_document(request):
    if request.method == 'POST':
        # Handle file upload
        return HttpResponse("Document uploaded successfully!")
    return render(request, 'upload.html')

