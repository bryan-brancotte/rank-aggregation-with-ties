# Usefull commands

Hereafter are listed some usefull commands

### make database migrations

```bash
python manage.py makemigrations
```

### migrate the database

```bash
python manage.py migrate
```

### generate language files

```bash
python manage.py makemessages -l en -l fr --no-location
```

### compile language file

```bash
python manage.py compilemessages
```

### run tests

```bash
python manage.py test
```

### generate models.png

```bash
python manage.py graph_models -a -g -o models.png
```

