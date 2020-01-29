import time
import os
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.http import JsonResponse
from django.views import View
from django.http import HttpResponse
from .forms import PhotoForm
from .models import Photo
from PIL import Image 
import pytesseract 
import sys 
from pdf2image import convert_from_path 
import re

def submit(request):
    data = os.listdir("media/photos")
    for dat in data:
        if dat.startswith("."):
            data.remove(dat)
    for dat in data:
        PDF_file = "media/photos/"+dat
        pages = convert_from_path(PDF_file, 500) 
        image_counter = 1
        for page in pages: 
            filename = "page_"+str(image_counter)+".jpg"
            page.save(filename, 'JPEG')
            image_counter = image_counter + 1

        filelimit = image_counter-1

        # Creating a text file to write the output 
        outfile = "out_text.txt"
        f = open(outfile, "w")
        for i in range(1,filelimit+1):
            filename = "page_"+str(i)+".jpg"
            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = text.replace('-\n','')
            f.write(text)
            os.remove(filename)
        f.close()
        input1 = open("out_text.txt","r")
        output = open("output.txt","w")
        for line in input1:
            output.write(re.sub('(^| )e( |$)','-> ', line))
        output.close()
        input1.close()
    return render(request,'photos/drag_and_drop_upload/index.html',{'alert_flag' : True })

def viewfiles(request):
    with open('output.txt') as f:
        filecontent = f.read().replace("\n","<br />\n")
        context = {'filecontent':filecontent}
        return render(request,'photos/drag_and_drop_upload/index.html',context)



class BasicUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/basic_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


class ProgressBarUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/progress_bar_upload/index.html', {'photos': photos_list})

    def post(self, request):
        time.sleep(1)  # You don't need this line. This is just to delay the process so you can see the progress bar testing locally.
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


class DragAndDropUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/drag_and_drop_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def clear_database(request):
    for photo in Photo.objects.all():
        photo.file.delete()
        photo.delete()
    return redirect(request.POST.get('next'))
