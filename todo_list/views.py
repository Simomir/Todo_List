from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from .forms import TodoForm
from .models import Todo
from django.contrib.auth.decorators import login_required


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo_list/signup_user.html', {'form': UserCreationForm()})
    else:
        # Create new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')

            # Username already exist
            except IntegrityError:
                return render(request, 'todo_list/signup_user.html',
                              {'form': UserCreationForm(), 'error': 'Username already exist. Choose a different one'})
        else:
            # Tell the user the passwords didn't match.
            return render(request, 'todo_list/signup_user.html', {'form': UserCreationForm(),
                                                                  'error': 'Passwords did not match.'})


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo_list/current_todos.html', {'todos': todos})


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def home(request):
    return render(request, 'todo_list/home.html')


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo_list/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo_list/login_user.html', {'form': AuthenticationForm(),
                                                                 'error': 'Username or password did not match.'})
        else:
            login(request, user)
            return redirect('current_todos')


@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo_list/create_todo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo_list/create_todo.html',
                          {'form': TodoForm(), 'error': 'Bad data passed in. Try again.'})


@login_required
def todo_detail(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo_list/todo_detail.html', {'todo': todo, 'form': form})
    else:
        form = TodoForm(request.POST, instance=todo)
        try:
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo_list/todo_detail.html',
                          {'todo': todo, 'form': form, 'error': 'Bad info. Try again.'})


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('current_todos')


def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo_list/completed_todos.html', {'todos': todos})
