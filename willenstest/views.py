# App: Willenstest

from django.db import models
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import path, include
from django.core.files.storage import FileSystemStorage
import csv
import re

# --- MODELS ---
class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:50]

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.IntegerField()
    session_id = models.CharField(max_length=100)

# --- ADMIN ---
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ('text',)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'score', 'session_id')
    list_filter = ('session_id',)

# --- FORMS ---
class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizForm, self).__init__(*args, **kwargs)
        for q in questions:
            self.fields[f"question_{q.id}"] = forms.IntegerField(
                label=q.text,
                min_value=1,
                max_value=5,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )

class UploadCSVForm(forms.Form):
    file = forms.FileField(label=_("Fragen-CSV hochladen"))

# --- VIEWS ---
def quiz_view(request):
    questions = Question.objects.all()
    session_id = request.session.session_key or request.session.save()

    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            for q in questions:
                score = form.cleaned_data[f"question_{q.id}"]
                Response.objects.create(question=q, score=score, session_id=session_id)
            return redirect('results')
    else:
        form = QuizForm(questions=questions)

    return render(request, 'willenstest/quiz.html', {'form': form})

def results_view(request):
    session_id = request.session.session_key
    responses = Response.objects.filter(session_id=session_id)
    scores = {r.question.text: r.score for r in responses}

    def score_color(score):
        if score < 2.5:
            return _('🔴 Zu gering')
        elif score > 4.2:
            return _('🟡 Zu hoch')
        else:
            return _('🟢 Optimal')

    scored_feedback = [(q, s, score_color(s)) for q, s in scores.items()]
    return render(request, 'willenstest/results.html', {'scored_feedback': scored_feedback})

@login_required
def upload_csv_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            filepath = fs.path(filename)
            import_questions_from_csv(filepath)
            return redirect('admin:index')
    else:
        form = UploadCSVForm()
    return render(request, 'willenstest/upload.html', {'form': form})

# --- URL CONFIG ---
urlpatterns = [
    path('', quiz_view, name='quiz'),
    path('results/', results_view, name='results'),
    path('upload/', upload_csv_view, name='upload_csv'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# --- IMPORT SCRIPT FOR QUESTIONS ---
def import_questions_from_csv(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                qid, text = row[0], row[1]
                Question.objects.get_or_create(id=int(qid), defaults={'text': text})

def extract_questions_from_sql(sql_path, output_csv_path):
    with open(sql_path, 'r', encoding='utf-8') as file:
        sql = file.read()

    entries = re.findall(r"\((\d+),\s*'(.*?)',\s*\d+\)", sql, re.DOTALL)
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for qid, frage in entries:
            frage_clean = frage.replace("\\'", "'").replace('\\"', '"').replace('\\n', ' ').strip()
            writer.writerow([qid, frage_clean])