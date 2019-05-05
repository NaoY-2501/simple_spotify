import urllib.parse

from .consts import SEARCH_TYPES, ENTITY_TYPES, TIME_RANGES
from .decorators import id_validation, ids_validation, token_refresh, auth_validation, recommendations_validation
from .errors import ValidationError
from .models import Album, SimplifiedAlbum, Artist, SimplifiedTrack, Track, \
    AudioFeature, AudioAnalysis, SearchResult, Paging, CustomPaging, PrivateUser, PublicUser, \
    Category, RecommendationsResponse
from .util import get_response


class SpotifyBase:
    def __init__(self, authorization):
        self.authorization = authorization

    @classmethod
    def make_full_url(cls, endpoint, data):
        full_url = '{endpoint}?{data}'.format(
            endpoint=endpoint,
            data=data
        )
        return full_url


class Spotify(SpotifyBase):

    @id_validation('album id')
    @token_refresh
    def album(self, album_id):
        """
        Get album information
        Endpoint: GET https://api.spotify.com/v1/albums/{id}
        :param album_id:
        :return:Album object
        """
        endpoint = 'https://api.spotify.com/v1/albums/{id}'.format(
            id=album_id
        )
        response = get_response(self.authorization, endpoint)
        result = Album(response, self.authorization)
        return result

    @id_validation('album id')
    @token_refresh
    def albums_tracks(self, album_id, limit=20, offset=0, market=None):
        """
        Get tracks which is contained album
        :param album_id:
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :param market: ISO 3166-1 alpha-2 country code
        :return: paging object with track objects
        """
        endpoint = 'https://api.spotify.com/v1/albums/{id}/tracks'.format(
            id=album_id
        )
        # validate limit
        if not isinstance(limit, int):
            raise ValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise ValidationError('offset must be int.')
        if offset > 10000:
            offset = 10000

        queries = {
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        return Paging(response, SimplifiedTrack, self.authorization)

    @ids_validation(50)
    @token_refresh
    def albums(self, album_ids):
        """
        Get several albums information.
        Endpoint:GET https://api.spotify.com/v1/albums
        :param album_ids: list of album id. Maximum : 50 IDs
        :return: list of album objects
        """
        endpoint = 'https://api.spotify.com/v1/albums'

        query = {
            'ids': ','.join(album_ids)
        }

        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Album.to_object
        results = []
        for result in response['albums']:
            results.append(converter(result))
        return results

    @id_validation('artist id')
    @token_refresh
    def artist(self, artist_id):
        """
        Get artist information.
        Endpoint:GET https://api.spotify.com/v1/artists/{id}
        :param artist_id:
        :return: Artist object
        """
        endpoint = 'https://api.spotify.com/v1/artists/{id}'.format(
            id=artist_id
        )
        response = get_response(self.authorization, endpoint)
        result = Artist(response)
        return result

    @ids_validation(50)
    @token_refresh
    def artists(self, artist_ids):
        """
        Get several artists information.
        Endpoint:GET https://api.spotify.com/v1/artists
        :param artist_ids: list of artist id. Maximum : 50 IDs
        :return: list of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists'

        query = {
            'ids': ','.join(artist_ids)
        }

        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Artist.to_object
        results = []
        for result in response['artists']:
            results.append(converter(result))
        return results

    @id_validation('artist id')
    @token_refresh
    def artist_albums(self, artist_id, include_groups=None, limit=20, offset=0, country=None):
        """
        Get information about artist's albums
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/albums
        :param artist_id:
        :param include_groups: list of filter the response.
                               valid values are album, single, appears_on, compilation
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :param country: ISO 3166-1 alpha-2 country code
        :return: paging object with SimplifiedAlbum objects.
        """
        endpoint = 'https://api.spotify.com/v1/artists/{id}/albums'.format(
            id=artist_id
        )
        # validate include_groups
        if include_groups:
            if not isinstance(include_groups, list):
                raise ValidationError('include_groups must be list')
        # validate limit
        if not isinstance(limit, int):
            raise ValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise ValidationError('offset must be int.')
        if offset > 10000:
            offset = 10000

        queries = {
            'limit': limit,
            'offset': offset
        }
        if country:
            queries['market'] = country
        if include_groups:
            queries['include_groups'] = ','.join(include_groups)

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        return Paging(response, SimplifiedAlbum, self.authorization)

    @id_validation('artist id')
    @token_refresh
    def related_artists(self, artist_id):
        """
        Get information about 20 related artists to a given artist.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/related-artists
        :param artist_id:
        :return: list of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/related-artists'.format(
            artist_id=artist_id
        )
        response = get_response(self.authorization, endpoint)
        converter = Artist.to_object
        results = []
        for result in response['artists']:
            results.append(converter(result))
        return results

    @id_validation('artist id')
    @token_refresh
    def artist_top_tracks(self, artist_id, county_code=None):
        """
        Get information about an artist's top tracks.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/top-tracks
        :param artist_id:
        :param county_code: ISO 3166-1 alpha-2 country code
        :return: list of Track objects
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'.format(
            artist_id=artist_id
        )
        # coutry_code validation
        if not county_code:
            raise ValidationError('country_code is required parameter.')
        if not isinstance(county_code, str):
            raise ValidationError('country_code must be str.')

        query = {
            'country': county_code
        }
        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Track.to_object
        results = []
        for result in response['tracks']:
            results.append(converter(result))
        return results

    @id_validation('track id')
    @token_refresh
    def track(self, track_id):
        """
        Get track information.
        Endpoint: GET https://api.spotify.com/v1/tracks/{id}
        :param track_id:
        :return: Track object
        """
        endpoint = 'https://api.spotify.com/v1/tracks/{track_id}'.format(
            track_id=track_id
        )
        response = get_response(self.authorization, endpoint)
        result = Track(response)
        return result

    @ids_validation(50)
    @token_refresh
    def tracks(self, track_ids):
        """
        Get several track informations.
        Endpoint: GET https://api.spotify.com/v1/tracks
        :param track_ids: list of track id. maximum length is 50.
        :return: list of Track object
        """
        endpoint = 'https://api.spotify.com/v1/tracks'
        query = {
            'ids': ','.join(track_ids)
        }
        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = Track.to_object
        results = []
        for result in response['tracks']:
            results.append(converter(result))
        return results

    @id_validation('track id')
    @token_refresh
    def audio_analysis(self, track_id):
        """
        Get audio feature for track.
        Endpoint: Get https://api.spotify.com/v1/audio-analysis/{id}
        :param track_id:
        :return: AudioAnalysis object
        """
        endpoint = 'https://api.spotify.com/v1/audio-analysis/{id}'.format(
            id=track_id
        )
        response = get_response(self.authorization, endpoint)
        result = AudioAnalysis(response)
        return result

    @id_validation('track id')
    @token_refresh
    def audio_feature(self, track_id):
        """
        Get audio feature for track.
        :param track_id:
        :return: AudioFeature object
        """
        endpoint = 'https://api.spotify.com/v1/audio-features/{id}'.format(
            id=track_id
        )
        response = get_response(self.authorization, endpoint)
        result = AudioFeature(response)
        return result

    @ids_validation(100)
    @token_refresh
    def audio_features(self, track_ids):
        """
        Get several audio features
        :param track_ids: list of track id. maximum length is 100
        :return: list of AudioFeature object
        """
        endpoint = 'https://api.spotify.com/v1/audio-features/'
        query = {
            'ids': ','.join(track_ids)
        }
        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        converter = AudioFeature.to_object
        results = []
        for result in response['audio_features']:
            results.append(converter(result))
        return results

    @token_refresh
    def search(self, q='', search_types=SEARCH_TYPES, market=None, limit=20, offset=0):
        """
        Get information about artists, albums, tracks, playlist with match a keyword string.
        :param q: search keyword
        :param search_types: iterable object contains search type. Default is ['album', 'artist', 'playlist', 'track'].
        :param market: ISO 3166-1 alpha-2 country code
        :param limit: maximum number of results to return. Default 20. min 1, max 50.
        :param offset: The index of the first result to return. Default 0. max 10,000.
        :return: SearchResult objects or json format dict when raw is True.
        """
        endpoint = 'https://api.spotify.com/v1/search'

        # validate query
        if not isinstance(q, str):
            raise ValidationError('Query must be str.')
        if not q:
            raise ValidationError('Query is empty.')

        # validate search_types
        if not hasattr(search_types, '__iter__'):
            raise ValidationError('search_types must be iterable.')

        for t in search_types:
            try:
                if t.lower() not in SEARCH_TYPES:
                    raise ValidationError('{} is invalid search type.'.format(t))
            except AttributeError:
                raise AttributeError('Invalid type object in search_types. search_types must be list of string')

        # validate limit
        if not isinstance(limit, int):
            raise ValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise ValidationError('offset must be int.')
        if offset > 10000:
            offset = 10000

        typestring = ','.join([t.lower() for t in search_types])

        queries = {
            'q': q,
            'type': typestring,
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        results = SearchResult(q, search_types, response, self.authorization)
        return results

    @id_validation('type')
    @auth_validation(['user-top-read'])
    @token_refresh
    def users_top(self, entity_type, limit=20, offset=0, time_range='medium_term'):
        """

        :param entity_type: artists or tracks
        :param limit: the number of entity to return. maximum is 50.
        :param offset:
        :param time_range: over what time frame the affinities are computed.
               short_term(last 4 weeks), medium_term(last 6 months), long_term(last several years)
        :return: paging object with Artist object or Track object
        """
        endpoint = 'https://api.spotify.com/v1/me/top/{type}'.format(
            type=entity_type.lower()
        )
        # validate type
        if entity_type.lower() not in ENTITY_TYPES:
            raise ValidationError('type must be artists or tracks')

        # validate limit
        if not isinstance(limit, int):
            raise ValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        # validate offset
        if not isinstance(offset, int):
            raise ValidationError('offset must be int.')

        # validate time_range
        if time_range.lower() not in TIME_RANGES:
            raise ValidationError('time range must be selected from short_term or medium_term or long_term')

        queries = {
            'limit': limit,
            'offset': offset,
            'time_range': time_range
        }
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        if entity_type.lower() == 'artists':
            klass = Artist
        elif entity_type.lower() == 'tracks':
            klass = Track
        return Paging(response, klass, self.authorization)

    @auth_validation(['user-read-email', 'user-read-private', 'user-read-birthdate'])
    @token_refresh
    def current_user_profile(self):
        """
        Endpoint: GET https://api.spotify.com/v1/me
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me'
        response = get_response(self.authorization, endpoint)
        return PrivateUser(response)

    @id_validation('user id')
    @token_refresh
    def user_profile(self, user_id):
        """
        Endpoint: GET https://api.spotify.com/v1/users/{user_id}
        :param user_id:
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/users/{user_id}'.format(
            user_id=user_id
        )
        response = get_response(self.authorization, endpoint)
        return PublicUser(response)

    @id_validation('category id')
    @token_refresh
    def category(self, category_id):
        """
        Endpoint: GET https://api.spotify.com/v1/browse/categories/{category_id}
        :param category_id:
        :return: Category object
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories/{category_id}'.format(
            category_id=category_id
        )
        response = get_response(self.authorization, endpoint)
        result = Category(response)
        return result

    @token_refresh
    def categories(self, country=None, locale=None, limit=20, offset=0):
        """
        Endpoint: GET https://api.spotify.com/v1/browse/categories
        :param country:
        :param locale:
        :param limit:
        :param offset:
        :return: paging object with Category object
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories'

        # validate limit
        if not isinstance(limit, int):
            raise ValidationError('limit must be int.')
        if limit > 50:
            limit = 50

        queries = {
            'limit': limit,
            'offset': offset,
        }
        if country:
            queries['country'] = country
        if locale:
            queries['locale'] = locale
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        return CustomPaging(response, Category, self.authorization, 'categories')

    @recommendations_validation
    def recommendations(self, limit=20, market=None, seed_artists=None, seed_genres=None, seed_tracks=None, **kwargs):
        """
        Recommend tracks. Recommendation are generated based on the given seed entities.
        Endpoint: GET https://api.spotify.com/v1/recommendations
        :param limit: Target size of recommendation tracks. maximium 100. Default 20.
        :param market: Provide this parameter if you want to apply Track Relinking.
        :param seed_artists: list of Spotify ID for artists.
               Up to 5 seed values may be in provided in any combinations of seed_artists, seed_genres and seed_tracks.
        :param seed_genres: list of Spotify ID for genres.
               You can get list of available genre seeds with available_genre_seeds() method.
        :param seed_tracks: list of Spotify ID for tracks.
        :param kwargs: Optional. Multiple values. Tuneable attribute for recommendation.
        :return: RecommendationsReponse object. It contains recommend tracks and information about seeds.
        """
        endpoint = 'https://api.spotify.com/v1/recommendations'
        # validate seeds length
        if not seed_artists:
            seed_artists = []
        if not seed_genres:
            seed_genres = []
        if not seed_tracks:
            seed_tracks = []
        if len(seed_artists) + len(seed_genres) + len(seed_tracks) > 5:
            raise ValidationError('Total length of seed_artists, seed_genres, seed_tracks must be less than 5 or less.')
        elif len(seed_artists) + len(seed_genres) + len(seed_tracks) == 0:
            raise ValidationError('Total length of seed_artists, seed_genres, seed_tracks must be up to 5.')

        queries = {
            'limit': limit,
        }
        if market:
            queries['market'] = market
        if seed_artists:
            queries['seed_artists'] = ','.join(seed_artists)
        if seed_genres:
            queries['seed_genres'] = ','.join(seed_genres)
        if seed_tracks:
            queries['seed_tracks'] = ','.join(seed_tracks)
        queries.update(**kwargs)
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = get_response(self.authorization, full_url)
        return RecommendationsResponse(response)

    def available_genre_seeds(self):
        """
        Get available genre seeds. Genre seeds use for recommendations.
        Endpoint: GET https://api.spotify.com/v1/recommendations/available-genre-seeds
        :return: list of available genre seeds
        """
        endpoint = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
        response = get_response(self.authorization, endpoint)
        return response['genres']
