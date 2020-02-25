from django.shortcuts import render

# Create your views here.
def register(request):
    '''显示用户主页面'''
    return render(request,'users/register.html')