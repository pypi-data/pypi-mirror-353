from django.db import models
import json

class Todo(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField()

    def json(self):
        return json.dumps({
            "title" : self.title,
            "description" : self.description
            })

