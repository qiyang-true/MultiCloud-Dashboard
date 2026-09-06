from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from k8sdashboard.models import Manager
import hashlib
import json
# from captcha.models import CaptchaStore
# from captcha.helpers import captcha_image_url

# 模拟Django中的session和cookie功能
from django.conf import settings


def login(request):
    username = request.session.get('username', None)
    return render(request, 'login/login.html')


def logout(request):
    request.session.flush()
    response = redirect('login')
    response.delete_cookie('username')
    response.delete_cookie('password')
    return redirect(login)


def check(request):
    if request.method == 'POST':
        # checkcode = request.POST.get('checkcode', None)
        # 假设verify是一个验证码校验函数
        # if not verify(checkcode):  # 需要实现verify函数进行验证码校验
        #     messages.error(request, '验证码错误')
        #     return redirect('login')
        
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if not username:
            return JsonResponse({'status': 0, 'info': '用户名不可为空'})
        
        if not password:
            return JsonResponse({'status': 0, 'info': '密码不可为空'})
        
        # 假设check_pwd是一个验证用户名密码的函数
        data = check_pwd(username, password)
        
        if data:
            request.session['userid'] = data.id
            request.session['username'] = data.username
            request.session['role_id'] = data.role_id
            print(request.session['username']+'-----------------')
            if request.POST.get('remember') == 'true':
                response = redirect('index')
                response.set_cookie('username', data.username)
                return JsonResponse({'status': 1, 'info': '登录成功'})
            return JsonResponse({'status': 1, 'info': '登录成功'})
        else:
            # messages.error(request, '用户名或密码错误')
            return JsonResponse({'status': 0, 'info': '用户名或密码错误'})
    else:
        return HttpResponse('请求错误')


def check_code(request):
    pass
    # 实现验证码生成的功能
    # 假设这里是生成验证码的函数
    # return HttpResponse('这里应该是返回验证码的图片或内容')
    # if request.method == 'GET':
    #     captcha = CaptchaStore.generate_key()
    #     image_url = captcha_image_url(captcha)
    #     # return HttpResponse(f'<img src="{image_url}" alt="captcha">')
    #     return HttpResponse(image_url)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def check_pwd(username, password):
    try:
        data = Manager.objects.get(username=username)
        if data.password == hash_password(password):
            return data
        return None
    except Manager.DoesNotExist:
        return None

def verify(checkcode):
    return True
