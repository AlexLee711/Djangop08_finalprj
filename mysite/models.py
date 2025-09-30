from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Post(models.Model):
    UNITS = (('super','管理室'),('public','公設'),('equip','設備'),('parking','停車場'),('clean','清掃'),('others','其他'))
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    body = models.TextField()
    person = models.CharField(max_length=15)
    unit = models.CharField(max_length=10, choices=UNITS)
    pub_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ('-pub_date',)
    
    def __str__(self):
        return self.title

class Profile(models.Model):
    BUILDING = (('A','A棟'),('B','B棟'))
    DOOR = (('A','A'),('B','B'),('C','C'),('D','D'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    build = models.CharField(max_length=10, choices=BUILDING)
    floor = models.IntegerField(verbose_name='樓層', default=2, validators=[MinValueValidator(2),MaxValueValidator(15)])
    household = models.CharField(max_length=5, choices=DOOR)
    phone = models.CharField(max_length=10)
    
    def __str__(self):
        return self.user.username
    
class Mail(models.Model):
    TYPE = (('NP','常溫包裹'),('CLP','冷藏包裹'),('CDP','冷凍包裹'),('M','郵件類'))
    STATUS = (('N','未領取'),('Y','已領取'),('O','其他'),)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mail_type = models.CharField(max_length=5, choices=TYPE)
    sender = models.CharField(max_length=10)
    receiver = models.CharField(max_length=10)
    time = models.DateTimeField(default=timezone.now)
    note = models.TextField()
    status = models.CharField(max_length=5, choices=STATUS)
        
    def __str__(self):
        return self.user.username

class Forum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    posttime = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return "{}({})".format(self.posttime, self.user)

class Comment(models.Model):
    forum = models.ForeignKey(Forum, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=500)
    posttime = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return "{}({})".format(self.posttime, self.user)

class Poll(models.Model):
    subject = models.CharField(max_length=200)
    date_created = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
        
    def __str__(self):
        return str(self.id)+ ")" + self.subject

class Option(models.Model):
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    title = models.CharField(max_length=200)
    count = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.id) + ")" + self.title
    
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'poll')

class ManagementFee(models.Model):
    PAYMENT = (('CS','超商繳費'),('ATM','ATM轉帳'),('LP','Line Pay繳費'),)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='fees')
    title = models.CharField(max_length=20, verbose_name='繳費明細')
    amount = models.PositiveIntegerField(verbose_name='管理費用', default=9000)
    due_date = models.DateField(verbose_name='應繳日期')
    payment_date = models.DateField(null=True, blank=True, verbose_name='繳費日期')
    payway = models.CharField(max_length=5, choices=PAYMENT, null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name='是否已繳費')
    
    #def __str__(self):
        #return f"{self.profile.build}棟 {self.profile.floor}樓 {self.profile.household}戶 - {self.title} - {self.amount} 元"
    
    def is_overdue(self):
        return self.due_date < timezone.now().date() and not self.status
    
class Activity(models.Model):
    name = models.CharField(max_length=100, verbose_name='活動名稱')
    date = models.DateField(verbose_name='活動日期')
    location = models.CharField(max_length=50, verbose_name='活動地點')
    description = models.TextField(verbose_name='活動描述')
    max_particioants = models.PositiveIntegerField(verbose_name='人數上限')
    current_participants = models.PositiveIntegerField(default=0, verbose_name='目前報名人數')

    def __str__(self):
        return self.name

class ActivityApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='個人資料')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活動')
    application_date = models.DateTimeField(auto_now_add=True, verbose_name='報名日期')
    is_registered = models.BooleanField(default=False, verbose_name='是否已報名')
    participant_count = models.PositiveIntegerField(default=1, verbose_name='報名人數', validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.user.username} - {self.activity.name}"