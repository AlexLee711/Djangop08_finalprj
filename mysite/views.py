from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from mysite import models
from mysite import forms
from django.template.loader import get_template
from .models import Post
from django.http import HttpResponse

from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm
import random
from django.views.generic import DetailView

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    quotes = ['平凡的腳步也可以走完偉大的行程。',
    '每天醒來，敲醒自己的不是鐘聲，而是夢想。',
    '沒有口水與汗水，就沒有成功的淚水。',
    '別想一下造出大海，必須先由小河川開始。']
    quote = random.choice(quotes)
    return render(request, 'index.html', locals())

def post(request):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    post = models.Post.objects.all()
    return render(request, 'post.html', locals())

def showpost(request, slug):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    template = get_template('postdetails.html')
    try:
        post = Post.objects.get(slug = slug)
        if post != None:
            html = template.render(locals())
            return HttpResponse(html)
    except:
        return redirect('/post')

@login_required(login_url='/login/')
def post_forum(request, fid=None):
    if request.user.is_authenticated:
        username = request.user.username
        
        try:
            user = models.User.objects.get(username=username)
            forums = models.Forum.objects.order_by('-posttime')
        except:
            pass
        
        if fid:
            try:
                f = models.Forum.objects.get(id=fid)
            except:
                f = None
            if f:
                f.delete()
                messages.add_message(request, messages.INFO, "議題貼文刪除成功！")
    messages.get_messages(request)
    
    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = forms.CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.forum = get_object_or_404(models.Forum, id=request.POST.get('forum_id'))
                comment.save()
                messages.info(request, "留言已張貼")
                return redirect('/forum')
        else:
            user = User.objects.get(username=username)
            forum = models.Forum(user = user)
            forum_form = forms.ForumForm(request.POST, instance=forum)
            if forum_form.is_valid():
                messages.add_message(request, messages.INFO, "討論議題已儲存")
                forum_form.save()
                return redirect('/forum')
            else:
                messages.add_message(request, messages.INFO, "張貼討論議題每項都要填寫")
    else:
        forum_form = forms.ForumForm()
        comment_form = forms.CommentForm()
        
    return render(request, 'forum.html', locals())

@login_required(login_url='/login/')
def delete_comment(request, comment_id):
    comment = get_object_or_404(models.Comment, id=comment_id)
    forum_id = comment.forum.id
    
    if request.user == comment.user or request.user == comment.forum.user:
        comment.delete()
        messages.info(request, "留言已刪除")
    
    return redirect('/forum')

def public(request):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    
    current_time = timezone.now()
    activity = models.Activity.objects.filter(date__gte=current_time)
    #activity = models.Activity.objects.all()
    return render(request, 'public.html', locals())

def apply_for_activity(request, activity_id):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)    
    activity = get_object_or_404(models.Activity, id=activity_id)
    existing_application = models.ActivityApplication.objects.filter(user=request.user, activity=activity).first()
    
    if request.method == 'POST':
        form = forms.ActivityApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.profile = request.user.profile
            application.activity = activity
            participant_count = form.cleaned_data.get('participant_count')
            
            if activity.current_participants + participant_count <= activity.max_particioants:
                application.save()                
                activity.current_participants+=participant_count
                activity.save()
                messages.info(request, "報名成功！")
                return redirect('/public')
            else:
                messages.error(request, "活動已額滿！")
                return redirect('/public')
    else:
        form = forms.ActivityApplicationForm()
        
    is_full = activity.current_participants >= activity.max_particioants
            
    return render(request, 'apply_for_activity.html', locals())

def cancel_application(request, activity_id):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    activity = get_object_or_404(models.Activity, id=activity_id)
    existing_application = models.ActivityApplication.objects.filter(user=request.user, activity=activity).first()
        
    if existing_application:
        activity.current_participants -= existing_application.participant_count
        activity.save()
        existing_application.delete()
        messages.info(request, "報名已取消")
    else:
        messages.error(request, "您尚未報名此活動")
    return redirect('/public')

def user_registered_activities(request):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    current_time = timezone.now()
    registered_activities = models.ActivityApplication.objects.filter(user=request.user, activity__date__gte=current_time).select_related('activity')
    history_activities = models.ActivityApplication.objects.filter(user=request.user, activity__date__lt=current_time)
    return render(request, 'registered_activities.html', locals())
    
def PollList(request):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    poll = models.Poll.objects.all().order_by('date_created','end_date')
    for p in poll:
        if p.end_date and p.end_date < timezone.now().date():
            if p.enabled:
                p.enabled = False
                p.save()
    return render(request, 'poll.html', locals())

def PollDetail(request, pk):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    
    poll = get_object_or_404(models.Poll, pk=pk)
    options = poll.options.all()
    
    if not poll.enabled:
        top_option = options.order_by('-count').first()
    else:
        top_option = None
    
    return render(request, 'polldetails.html', locals())

def vote(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            poll = get_object_or_404(models.Poll, pk=pk)
            selected_option_id = request.POST.get('option')
            
            if selected_option_id:
                option = get_object_or_404(models.Option, id=selected_option_id)
                '''if models.Vote.objects.filter(user=request.user, poll=poll):
                    messages.warning(request, "您已經投過票了。")'''
                    # 查找使用者的現有投票記錄
                existing_vote = models.Vote.objects.filter(user=request.user, poll=poll).first()
                if existing_vote: 
                    # 如果存在，先減少舊選項的數量
                    old_option = existing_vote.option
                    old_option.count-=1
                    old_option.save()
                    
                    # 更新投票記錄
                    existing_vote.option = option
                    existing_vote.save()
                    
                    # 增加新選項的數量
                    option.count+=1
                    option.save()
                    messages.info(request, "投票更新成功！")
                else: # 如果不存在，直接創建新投票記錄
                    option.count+=1
                    option.save()
                    models.Vote.objects.create(user=request.user, poll=poll, option=option)
                    messages.success(request, "投票成功！")
            return redirect('/poll', pk=poll.id)

def mail(request):
    if request.user.is_authenticated:
        username = request.user.username
    messages.get_messages(request)
    mail = models.Mail.objects.all().filter(user=request.user)
    return render(request, 'mail.html', locals())
 
def sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, '註冊成功，以自動登入')
            return redirect('/')
        else:
            messages.warning(request, '註冊失敗，請檢查表單內容')
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign_up.html', {'form': form})
    
def login(request):
    if request.method == 'POST': 
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            login_name = request.POST['username'].strip()
            login_password=request.POST['password']
            user = authenticate(username=login_name, password=login_password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    print("success")
                    messages.add_message(request, messages.SUCCESS, '成功登入了')
                    return redirect('/')
                else:
                    messages.add_message(request, messages.WARNING, '帳號尚未啟用')
            else:
                messages.add_message(request, messages.WARNING, '登入失敗')
        else:
            messages.add_message(request, messages.INFO,'請檢查輸入的欄位內容')
    else:
        login_form = forms.LoginForm()
    return render(request, 'login.html', locals())

def logout(request):
    auth.logout(request)
    messages.add_message(request, messages.INFO, "成功登出")
    return redirect('/')

@login_required(login_url='/login/')
def userinfo(request):
    if request.user.is_authenticated:
        username = request.user.username
    user = User.objects.get(username=username)
    try:
        userinfo = models.Profile.objects.get(user=user)
    except:
        userinfo = models.Profile(user=user)
    if request.method == 'POST':
        profile_form = forms.ProfileForm(request.POST, instance=userinfo)
        if profile_form.is_valid():
            messages.add_message(request, messages.INFO, "個人資料已儲存")
            profile_form.save()
            return redirect('/userinfo')
        else:
            messages.add_message(request, messages.INFO, "要修改個人資料，每一個欄位都要填...")
    else:
        profile_form = forms.ProfileForm()
    
    return render(request, 'userinfo.html', locals())

def payment(request, fee_id=None):
    if request.user.is_authenticated:
        username = request.user.username
    if fee_id:
        fee = get_object_or_404(models.ManagementFee, id=fee_id, profile__user=request.user)
        if request.method == 'POST':
            form = forms.PaymentForm(request.POST, instance=fee)
            if form.is_valid():
                form.save()
                return redirect('/payment')
                
        else:
            form = forms.PaymentForm(instance=fee)
            
        return render(request, 'payment.html', locals())
    else:
        fees = models.ManagementFee.objects.filter(profile__user=request.user)
        return render(request, 'payment_list.html', locals())