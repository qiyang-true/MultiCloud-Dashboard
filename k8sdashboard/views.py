from django.shortcuts import render, redirect, HttpResponse
# from k8sdashboard.models import Manager, Role, Authority
from .utils.decorators import login_required


@login_required
def index(request):
    # print(locals())
    # print(globals())
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def logout(request):
    return redirect(index)