# evemap

Map plugin for [AllianceAuth](https://gitlab.com/allianceauth/allianceauth).

> This is a proof-of-concept that is a work-in-progress.

## Features

- View a map of New Eden
- Pan + Zoom
- - Scroll to zoom
- - Shift + Drag to zoom to box

## Installation

### Step 1 - Pre_Requisites

Evemap is an App for Alliance Auth, Please make sure you have this installed. Evemap is not a standalone Django Application

Evemap needs the App [django-eveuniverse](https://gitlab.com/ErikKalkoken/django-eveuniverse) in order to give the map context

Evemap needs the `shapely` python package in `requirements.txt` for doing gis stuff.

### Step 2 - Install app

pip install evemap

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

```python
INSTALLED_APPS += [
	'eveuniverse',
	'evemap',
...
```

### Step 4 - Maintain Alliance Auth

- Run migrations `python manage.py migrate`
- Gather your staticfiles `python manage.py collectstatic`
- Restart Alliance Auth


### Step 5 - Populate universe data

```bash
python manage.py eveuniverse_load_data map
```

# Screenshot

![Map](https://i.imgur.com/0j3NGFj.png)
