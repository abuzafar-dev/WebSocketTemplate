from django.db import models


class Message(models.Model):
    room = models.CharField(max_length=50, db_index=True)
    sender = models.CharField(max_length=150)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"[{self.room}] {self.sender}: {self.text[:30]}"
