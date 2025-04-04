from django.db import models
from django.contrib.auth.models import AbstractUser


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    # Change the 3D model field from URLField to FileField:
    model_3d = models.FileField(null=True ,upload_to='models_3d/', help_text="Upload a GLB/GLTF file for AR")

    def __str__(self):
        return self.name



