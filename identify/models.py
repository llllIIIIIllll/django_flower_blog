from django.db import models

class identify_flower(models.Model):

    # 花名
    flower_name = models.CharField(max_length=100)
    # 花的简介
    flower_info = models.TextField()


    def __str__(self):

        return self.flower_name