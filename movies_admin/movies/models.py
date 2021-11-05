import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator



class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Title'), max_length=25)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        db_table = 'content\".\"genre'

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(_('Full name'), max_length=128)
    birth_date = models.DateField(_('Birth date'), blank=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        db_table = 'content\".\"person'

    def __str__(self):
        return self.full_name


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('movie')
    TV_SHOW = 'tv_show', _('TV Show')


class FilmWork(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=128)
    description = models.TextField(_('Description'), blank=True)
    creation_date = models.DateField(_('Creation date'), blank=True)
    certificate = models.TextField(_('Certificate'), blank=True)
    file_path = models.FileField(_('File'), upload_to='film_works/', blank=True)
    rating = models.FloatField(
        _('Rating'),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0.0,
        blank=True
    )
    type = models.CharField(_('Type'), max_length=20, choices=FilmWorkType.choices)
    genres = models.ManyToManyField(Genre, through='FilmWorkGenre')
    persons = models.ManyToManyField(Person, through='FilmWorkPerson')

    class Meta:
        verbose_name = _('Film')
        verbose_name_plural = _('Films')
        db_table = 'content\".\"film_work'

    def __str__(self):
        return self.title


class FilmWorkGenre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey('FilmWork', to_field='id', db_column='film_work_id', on_delete=models.CASCADE)
    genre_id = models.ForeignKey('Genre', to_field='id', db_column='genre_id', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content\".\"genre_film_work'
        indexes = [
            models.Index(fields=['film_work_id', 'genre_id'], name='genre_film_work'),
        ]
        verbose_name = "Genres of film"
        verbose_name_plural = _('Genres of film')

    def __str__(self):
        return f'{self.film_work_id}'

class FilmWorkPerson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey('FilmWork', to_field='id', db_column='film_work_id', on_delete=models.CASCADE)
    person_id = models.ForeignKey('Person', to_field='id', db_column='person_id', on_delete=models.CASCADE)
    role = models.CharField(_('Role'), max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content\".\"person_film_work'
        indexes = [
            models.Index(fields=['film_work_id', 'person_id'], name='person_film_work'),
        ]
        verbose_name = "Persons of film"
        verbose_name_plural = _('Persons of film')

    def __str__(self):
        return f'{self.film_work_id}'
