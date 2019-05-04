from .models import Artist, Track

SEARCH_TYPES = ('album', 'artist', 'playlist', 'track')

RESULT_TYPES = {
    'album': 'albums',
    'artist': 'artists',
    'playlist': 'playlists',
    'track': 'tracks',
}

PITCH_CLASS = {
    0: 'C',
    1: 'C#',
    2: 'D',
    3: 'D#',
    4: 'E',
    5: 'F',
    6: 'F#',
    7: 'G',
    8: 'G#',
    9: 'A',
    10: 'A#',
    11: 'B',
}

ENTITY_TYPES = ('artists', 'tracks')

ENTITY_CLASS = {
    'artists': Artist,
    'tracks': Track,
}

TIME_RANGES = ('short_term', 'medium_term', 'long_term')