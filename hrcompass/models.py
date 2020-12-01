from django.db import models
#python manage.py inspectdb --Get Table Models


class AuthUser(models.Model):   
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField(default=0)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField(default=0)
    is_active = models.IntegerField(default=0)
    date_joined = models.DateTimeField()
    
    class Meta:
        managed = False
        db_table = 'auth_user'
    def __str__(self):
        return self.username

class Client(models.Model):
    id = models.BigAutoField(primary_key=True)
    client_name = models.CharField(max_length=255, default="")
    project_number = models.CharField(max_length=255, default="")
    consultants = models.ManyToManyField(AuthUser, through='Clientuser', related_name='clients')

    class Meta:
        ordering = ('client_name',)
        managed = True
        db_table = 'tblclient'
    def __str__(self):
        return self.client_name

class Clientuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(AuthUser, on_delete=models.RESTRICT)

    class Meta:
        managed = True
        db_table = 'tblclientuser'

class Kind(models.Model):
    id = models.BigAutoField(primary_key=True)
    kind = models.CharField(max_length=20, default="")
    active = models.BooleanField()
    
    class Meta:
        verbose_name_plural = "Kind"
        ordering = ('kind',)
        managed = True
        db_table = 'tbltaskkind'
    def __str__(self):
        return self.kind

    def is_active(self):
        return self.active
    
    __str__.admin_order_field = 'kind'

class Taskname(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=4000, default="")
    task_kind = models.ForeignKey(Kind, on_delete=models.RESTRICT, default=1)
    
    class Meta:
        verbose_name_plural = "Task Name"
        ordering = ('name',)
        managed = True
        db_table = 'tbltaskname'
    def __str__(self):
        return self.name

class Status(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=20, default="")

    class Meta:
        verbose_name_plural = "Status"
        ordering = ('status',)
        managed = True
        db_table = 'tbltaskstatus'
    def __str__(self):
        return self.status

class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    kind = models.ForeignKey('Kind', on_delete=models.RESTRICT, null=True, blank=True)
    task_name = models.ForeignKey('Taskname', on_delete=models.RESTRICT, default=1)
    task_status = models.ForeignKey('Status', on_delete=models.RESTRICT, default=1)
    client = models.ForeignKey('Client', on_delete=models.RESTRICT, default=1)
    startdate = models.DateTimeField(blank=True, null=True)
    duedate = models.DateTimeField()
    invoiced = models.DateTimeField(blank=True, null=True)

    members = models.ManyToManyField(AuthUser, through='Taskuser', related_name='tasks')

    class Meta:
        managed = True
        db_table = 'tbltask'

class Taskuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey('AuthUser', on_delete=models.RESTRICT)

    class Meta:
        managed = True
        db_table = 'tbltaskuser'