from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# Create your views here.

@login_required
def inicio(request):
    # return render(request,"panel.html")
    return redirect('inicio_usuario')
