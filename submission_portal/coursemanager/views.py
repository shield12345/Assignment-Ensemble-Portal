from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SiteUser, Assignment, SubmittedAssignment
from django.http import HttpResponseForbidden, FileResponse
from .forms import AssignmentForm, SubmissionForm, EvaluationForm
from django import template
from django.db.models import Q
import datetime
from django.utils import timezone

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
    user, created = SiteUser.objects.get_or_create(user_id=request.user.id)
    if request.user.is_staff:
        assignments = Assignment.objects.all()
        context = {"assignments": assignments}
        return render(request, 'instructor_index.html', context)
    else:
        assignments_all = Assignment.objects.all()
        submissions = SubmittedAssignment.objects.filter(Q(student_name = user.user.first_name))
        print(user.user.first_name)
        submitted_array = []
        graded_array = []
        marks_array = []
        total_marks_array = []
        feedbacks_array = []
        deadlines_array = []
        submitted_assign_array= []

        for assignment in assignments_all:
            flag = False
            flag_graded = False
            marks = 0
            feedback = ""
            for submission in submissions:
                if submission.submitted_assignment_name == assignment.assignment_name:
                    flag = True
                    flag_graded = submission.is_graded
                    marks = submission.marks
                    feedback = submission.feedback
                    submitted_assign_array.append(submission.pk)
                    break


            if assignment.deadline < timezone.now():
                deadlines_array.append(False)
            else:
                deadlines_array.append(True)
                
            submitted_array.append(flag)
            graded_array.append(flag_graded)
            marks_array.append(marks)
            total_marks_array.append(assignment.max_marks)
            feedbacks_array.append(feedback)

        print(assignments_all)
        my_list = zip(assignments_all, submitted_array, graded_array, marks_array, total_marks_array, feedbacks_array, deadlines_array)
        print(submitted_array)

        context = { "my_list": my_list }
        print(context)
        return render(request, 'student_index.html', context)


@login_required(login_url='/accounts/login/') 
def AddAssignment(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = AssignmentForm(request.POST, request.FILES)
            if form.is_valid():
                assignment = form.save(commit=False)
                if request.FILES.get('assignment_file', None):
                    assignment.assignment_file = request.FILES.get(
                        'assignment_file', None)

                assignment.save()

                return redirect('coursemanager:home')
            else:
                print(form.errors)
        else:
           form = AssignmentForm() 

        return render(request, 'assignment.html', {'form': form, 'url': 'add'})
    else:
        return HttpResponseForbidden()
    

@login_required(login_url='/accounts/login/')
def EditAssignment(request,pk):
    if request.user.is_staff:
        form_instance = Assignment.objects.get(pk=pk)
        if request.method == 'POST':
            form = AssignmentForm(request.POST, request.FILES, instance = form_instance)

            if form.is_valid():
                assignment = form.save(commit=False)

                if request.FILES.get('assignment_file', None):
                    assignment.assignment_file = request.FILES.get(
                        'assignment_file', None)

                assignment.save()

                return redirect('coursemanager:home')
            
            else:
                print(form.errors)

        else:
           form = AssignmentForm(instance = form_instance) 

        return render(request, 'assignment.html', {'form': form, 'url': str(pk)})
    else:
        return HttpResponseForbidden()  
    

@login_required(login_url='/accounts/login/') 
def SubmitAssignment(request,pk):
    user, created = SiteUser.objects.get_or_create(user_id=request.user.id)
    if request.user.is_staff:
        return HttpResponseForbidden()
    else:
        assignment = Assignment.objects.get(pk=pk)
        if request.method == 'POST':
            form = SubmissionForm(request.POST, request.FILES)

            if form.is_valid():
                submission = form.save(commit=False)
                submission.student = SiteUser.objects.get(user_id=request.user.id)
                submission.student_name = user.user.first_name
                submission.roll_number = user.user.last_name
                submission.submitted_assignment_name = assignment.assignment_name

                if request.FILES.get('submission_file', None):
                    submission.submission_file = request.FILES.get(
                        'submission_file', None)

                submission.save()

                return redirect('coursemanager:home')
            
            else:
                print(form.errors)

        else:
           form = SubmissionForm() 

        return render(request, 'submission.html', {'form': form, 'name_assignment': assignment.assignment_name, 'url': str(pk)})


@login_required(login_url='/accounts/login/')
def EditSubmittedAssignment(request,pk1,pk2):
    user, created = SiteUser.objects.get_or_create(user_id=request.user.id)
    if request.user.is_staff:
        return HttpResponseForbidden()
    else:
        assignment = Assignment.objects.get(pk=pk1)
        form_instance = SubmittedAssignment.objects.get(pk=pk2)
        if request.method == 'POST':
            form = SubmissionForm(request.POST, request.FILES, form_instance)

            if form.is_valid():
                submission = form.save(commit=False)
                submission.student = SiteUser.objects.get(user_id=request.user.id)
                submission.student_name = user.user.first_name
                submission.roll_number = user.user.last_name
                submission.submitted_assignment_name = assignment.assignment_name

                if request.FILES.get('submission_file', None):
                    submission.submission_file = request.FILES.get(
                        'submission_file', None)

                submission.save()

                return redirect('coursemanager:home')
            
            else:
                print(form.errors)

        else:
           form = SubmissionForm(form_instance) 

        return render(request, 'submission.html', {'form': form, 'name_assignment': assignment.assignment_name, 'url': str(pk1)+"/"+str(pk2)+"/"}) 


@login_required(login_url='/accounts/login/') 
def SubmissionsView(request, pk):
    user, created = SiteUser.objects.get_or_create(user_id=request.user.id)
    if request.user.is_staff:
        assignment_object = Assignment.objects.get(pk=pk)
        submissions_objects = SubmittedAssignment.objects.filter(Q(submitted_assignment_name = assignment_object.assignment_name))
        return render(request, 'submissions_view.html', { 'submission_objects': submissions_objects, 'assignment_object': assignment_object })
    else:
        return HttpResponseForbidden()
    

@login_required(login_url='/accounts/login/') 
def EvaluateAssignment(request, pk1, pk2):
    user, created = SiteUser.objects.get_or_create(user_id=request.user.id)
    if request.user.is_staff:
        assignment_obj = Assignment.objects.get(pk=pk1)
        form_instance = SubmittedAssignment.objects.get(pk=pk2)
        if request.method == 'POST':
            form = EvaluationForm(request.POST, request.FILES, instance=form_instance)
            if form.is_valid():
                submission_obj = form.save(commit=False)
                submission_obj.student = SubmittedAssignment.objects.get(pk=pk2).student
                submission_obj.is_graded = True
                submission_obj.save()
                return redirect('coursemanager:home')
            else:
                print(form.errors)
        else:
            form = EvaluationForm(instance=form_instance)

        return render(request, 'evaluation.html', {'assignment_obj': assignment_obj, 'form_instance': form_instance, 'form': form, 'url': str(pk1)+"/"+str(pk2)})
    else:
       return HttpResponseForbidden() 


@login_required(login_url='/accounts/login/')
def MediaView(request, file):
    try:
        return FileResponse(open('media/' + file, 'rb'))
    except:
        return HttpResponseForbidden()