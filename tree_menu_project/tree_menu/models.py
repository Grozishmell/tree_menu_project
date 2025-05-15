from django.db import models
from django.urls import reverse


class Menu(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название меню"
    )

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

    def __str__(self):
        return self.name
    

class MenuItem(models.Model):
    menu = models.ForeignKey(
        Menu,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Меню"
    )
    parent = models.ForeignKey(
        'self',
        related_name='children',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Родительский пункт",
        help_text="Есил пусто - пункт первого уровня"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок"
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="URL (может быть именем URL-конфигурации)"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"

    def __str__(self):
        return self.title

    def get_url(self):
        """
        Если в поле url задано имя URL-конфигурации, пытаемся его reverse().
        Иначе считаем, что это обычный путь.
        """
        if not self.url:
            return '#'
        try:
            return reverse(self.url)
        except:
            return self.url
