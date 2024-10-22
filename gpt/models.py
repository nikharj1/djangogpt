from django.db import models
from django.utils import timezone
from django.db import models
import datetime





class chat_history(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    date = models.DateField(default=datetime.date.today)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp =  models.DateTimeField(default=timezone.now)
    image_path = models.FileField(upload_to='Bot_Response', null=True, blank=True)
    input_image = models.FileField(upload_to='User_Uploaded', null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'chat_history'

    def __str__(self) :
        return f"{self.username}" if self.username else "User Not defined"

    


