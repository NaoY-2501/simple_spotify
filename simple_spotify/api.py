import datetime
import json
import urllib.parse

from .consts import SEARCH_TYPES, ENTITY_TYPES, TIME_RANGES
from .decorators import id_validation, ids_validation, token_refresh, auth_validation, recommendations_validation
from .errors import ValidationError
from .models import Album, SimplifiedAlbum, Artist, SimplifiedTrack, Track, \
    AudioFeature, AudioAnalysis, SearchResult, Paging, CustomPaging, CursorBasedPaging, \
    PrivateUser, PublicUser, Category, RecommendationsResponse, SimplifiedPlaylist, \
    SavedAlbum, SavedTrack
from .util import http_request, validate_limit, validate_offset


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

    # Albums

    @id_validation('album id')
    @token_refresh
    def get_album(self, album_id, market=None):
        """
        Get album information
        Endpoint: GET https://api.spotify.com/v1/albums/{id}
        :param album_id:  The Spotify ID for album
        :param market: Optional. ISO 3166-1 alpha-2 country code
        :return: Album object
        """
        endpoint = 'https://api.spotify.com/v1/albums/{id}'.format(
            id=album_id
        )
        if market:
            query ={
                'market': market
            }
            data = urllib.parse.urlencode(query)
            endpoint = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, endpoint)
        result = Album(response, self.authorization)
        return result

    @id_validation('album id')
    @token_refresh
    def get_albums_tracks(self, album_id, limit=20, offset=0, market=None):
        """
        Get tracks which is contained album
        :param album_id: The Spotify ID for album
        :param limit: Optional. Maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first result to return. Default 0. max 10,000.
        :param market: Optional. ISO 3166-1 alpha-2 country code
        :return: Paging object with Track objects
        """
        endpoint = 'https://api.spotify.com/v1/albums/{id}/tracks'.format(
            id=album_id
        )
        # validate limit
        limit = validate_limit(limit)

        # validate offset
        offset = validate_offset(offset, maximum=10000)

        queries = {
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market

        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return Paging(response, SimplifiedTrack, self.authorization)

    @ids_validation(50)
    @token_refresh
    def get_albums(self, album_ids, market=None):
        """
        Get several albums information.
        Endpoint:GET https://api.spotify.com/v1/albums
        :param album_ids: List of the Spotify IDs for album. Maximum length is 50.
        :param market: Optional. ISO 3166-1 alpha-2 country code
        :return: List of Album objects
        """
        endpoint = 'https://api.spotify.com/v1/albums'

        queries = {
            'ids': ','.join(album_ids)
        }
        if market:
            queries['market'] = market
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        converter = Album.to_object
        results = []
        for result in response['albums']:
            results.append(converter(result))
        return results

    # Artist

    @id_validation('artist id')
    @token_refresh
    def get_artist(self, artist_id):
        """
        Get artist information.
        Endpoint:GET https://api.spotify.com/v1/artists/{id}
        :param artist_id: The Spotify ID for artist
        :return: Artist object
        """
        endpoint = 'https://api.spotify.com/v1/artists/{id}'.format(
            id=artist_id
        )
        response = http_request(self.authorization, endpoint)
        result = Artist(response)
        return result

    @ids_validation(50)
    @token_refresh
    def get_artists(self, artist_ids):
        """
        Get several artists information.
        Endpoint:GET https://api.spotify.com/v1/artists
        :param artist_ids: List of the Spotify ID for artist. Maximum length is 50.
        :return: List of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists'

        query = {
            'ids': ','.join(artist_ids)
        }

        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        converter = Artist.to_object
        results = []
        for result in response['artists']:
            results.append(converter(result))
        return results

    @id_validation('artist id')
    @token_refresh
    def get_artist_albums(self, artist_id, include_groups=None, limit=20, offset=0, country=None):
        """
        Get information about artist's albums
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/albums
        :param artist_id: The Spotify ID for artist
        :param include_groups: Optional. List of filter the response.
                               Valid values are album, single, appears_on, compilation
        :param limit: Optional. Maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first result to return. Default 0. max 10,000.
        :param country: Optional. ISO 3166-1 alpha-2 country code
        :return: Paging object with SimplifiedAlbum objects.
        """
        endpoint = 'https://api.spotify.com/v1/artists/{id}/albums'.format(
            id=artist_id
        )
        # validate include_groups
        if include_groups:
            if not isinstance(include_groups, list):
                raise ValidationError('include_groups must be list')
        # validate limit
        limit = validate_limit(limit)

        # validate offset
        offset = validate_offset(offset, maximum=10000)

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
        response = http_request(self.authorization, full_url)
        return Paging(response, SimplifiedAlbum, self.authorization)

    @id_validation('artist id')
    @token_refresh
    def get_related_artists(self, artist_id):
        """
        Get information about 20 related artists to a given artist.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/related-artists
        :param artist_id: The Spotify ID for artist
        :return: List of Artist objects
        """
        endpoint = 'https://api.spotify.com/v1/artists/{artist_id}/related-artists'.format(
            artist_id=artist_id
        )
        response = http_request(self.authorization, endpoint)
        converter = Artist.to_object
        results = []
        for result in response['artists']:
            results.append(converter(result))
        return results

    @id_validation('artist id')
    @token_refresh
    def get_artist_top_tracks(self, artist_id, county_code=None):
        """
        Get information about an artist's top tracks.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}/top-tracks
        :param artist_id: The Spotify ID for artist
        :param county_code: Optional. ISO 3166-1 alpha-2 country code
        :return: List of Track objects
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
        response = http_request(self.authorization, full_url)
        converter = Track.to_object
        results = []
        for result in response['tracks']:
            results.append(converter(result))
        return results

    # Browse

    @id_validation('category id')
    @token_refresh
    def get_category(self, category_id):
        """
        Endpoint: GET https://api.spotify.com/v1/browse/categories/{category_id}
        :param category_id: The Spotify category ID
        :return: Category object
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories/{category_id}'.format(
            category_id=category_id
        )
        response = http_request(self.authorization, endpoint)
        result = Category(response)
        return result

    @token_refresh
    def get_categories(self, country=None, locale=None, limit=20, offset=0):
        """
        Endpoint: GET https://api.spotify.com/v1/browse/categories
        :param country: ISO 3166-1 alpha-2 country code
        :param locale:  Optional. Language of categories.
                        ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore.
        :param limit: Optional. The maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first item to return. Default:0.
        :return: paging object with Category object
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories'

        # validate limit
        limit = validate_limit(limit)

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
        response = http_request(self.authorization, full_url)
        return CustomPaging(response, Category, self.authorization, 'categories')

    @recommendations_validation
    def get_recommendations(self, limit=20, market=None, seed_artists=None, seed_genres=None, seed_tracks=None, **kwargs):
        """
        Recommend tracks. Recommendation are generated based on the given seed entities.
        Endpoint: GET https://api.spotify.com/v1/recommendations
        :param limit: Target size of recommendation tracks. maximium 100. Default 20.
        :param market: Provide this parameter if you want to apply Track Relinking.
        :param seed_artists: List of Spotify ID for artists.
               Up to 5 seed values may be in provided in any combinations of seed_artists, seed_genres and seed_tracks.
        :param seed_genres: List of genres in the set of available genre seeds.
               You can get list of available genre seeds with simple_spotify.consts.GENRE_SEEDS
        :param seed_tracks: List of Spotify ID for tracks.
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
        response = http_request(self.authorization, full_url)
        return RecommendationsResponse(response)

    @token_refresh
    def get_available_genre_seeds(self):
        """
        Get available genre seeds. Genre seeds use for recommendations.
        Endpoint: GET https://api.spotify.com/v1/recommendations/available-genre-seeds
        :return: List of available genre seeds
        """
        endpoint = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
        response = http_request(self.authorization, endpoint)
        return response['genres']

    @token_refresh
    def get_new_release(self, country=None, limit=20, offset=0):
        """

        :param country: ISO 3166-1 alpha-2 country code
        :param limit: Optional. The maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first item to return. Default:0.
        :return: CustomPaging object with SimplifiedAlbum object
        """
        endpoint = 'https://api.spotify.com/v1/browse/new-releases'
        # validate limit
        limit = validate_limit(limit)
        # validate offset
        offset = validate_offset(offset)

        queries = {
            'limit': limit,
            'offset': offset
        }
        if country:
            queries['country'] = country
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return CustomPaging(response, SimplifiedAlbum, self.authorization, 'albums')

    @id_validation('category id')
    @token_refresh
    def get_category_playlists(self, category_id, limit=20, offset=0, country=None):
        """
        Endpoint: GET https://api.spotify.com/v1/browse/categories/{category_id}/playlists
        :param category_id: The Spotify Category ID (e.g. pop, rock, j_tracks)
        :param limit: Optional. Maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first result to return. Default 0.
        :param country: Optional. ISO 3166-1 alpha-2 country code
        :return: pagination object with SimplifiedPlaylist objects
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories/{category_id}/playlists'.format(
            category_id=category_id
        )
        # validate limit
        limit = validate_limit(limit)
        # validate offset
        offset = validate_offset(offset)

        queries = {
            'limit': limit,
            'offset': offset
        }
        if country:
            queries['country'] = country
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return CustomPaging(response, SimplifiedPlaylist, self.authorization, 'playlists')

    @token_refresh
    def get_featured_playlists(self, locale=None, country=None, timestamp=None, limit=20, offset=0):
        """
        Get featured playlists.
        Endpoint: GET https://api.spotify.com/v1/browse/featured-playlists
        :param locale: Optional. ISO 639-1 language code and an uppercase ISO 3166-1 alpha-2 country code. (e.g. ja_JP, en_US)
        :param country: Optional. An ISO 3166-1 alpha-2 country code.
        :param timestamp: Optional. DateTime object
        :param limit: Optional. The maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first result to return. Default 0.
        :return: CustomPaging object with SimplifiedPlaylist objects
        """
        endpoint = 'https://api.spotify.com/v1/browse/featured-playlists'

        # validate limit
        limit = validate_limit(limit)
        # validate offset
        offset = validate_offset(offset)
        # validate timestamp
        if timestamp:
            if not isinstance(timestamp, datetime.datetime):
                ValidationError('timestamp must be datetime object')
            timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        queries = {
            'limit': limit,
            'offset': offset
        }
        if locale:
            queries['locale'] = locale
        if country:
            queries['country'] = country
        if timestamp:
            queries['timestamp'] = timestamp
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return CustomPaging(response, SimplifiedPlaylist, self.authorization, 'playlists')

    # Follow

    @auth_validation(['user-follow-read'])
    @ids_validation(50)
    @token_refresh
    def check_current_user_follow_artists(self, ids=None):
        """
        check current user is following artists or users.
        Endpoint: GET https://api.spotify.com/v1/me/following/contains
        :param ids: The Spotify IDs of artist
        :return: List of boolean values
        """
        endpoint = 'https://api.spotify.com/v1/me/following/contains'
        queries = {
            'type': 'artist',
            'ids': ','.join(ids)
        }
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return response

    @auth_validation(['user-follow-read'])
    @ids_validation(50)
    @token_refresh
    def check_current_user_follow_users(self, ids=None):
        """
        check current user is following artists or users.
        Endpoint: GET https://api.spotify.com/v1/me/following/contains
        :param ids: The Spotify IDs of artist or user
        :return: List of boolean values
        """
        endpoint = 'https://api.spotify.com/v1/me/following/contains'
        queries = {
            'type': 'user',
            'ids': ','.join(ids)
        }
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return response

    @auth_validation(['playlisy-read-private'])
    @id_validation('playlist_id')
    @token_refresh
    def check_users_follow_playlist(self, playlist_id, ids=None):
        """
        check one or more users following playlist
        Endpoint: GET https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains
        :param playlist_id: The Spotifty ID for Playlist
        :param ids: List of users id
        :return: List of boolean values
        """
        endpoint = 'https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains'.format(
            playlist_id=playlist_id
        )
        # validate ids
        if not ids:
            ValidationError('Spotify User IDs is required.')
        if not isinstance(ids, list):
            ValidationError('ids must be list')
        if len(ids) > 5:
            ValidationError('Length of Spotify User IDs must be less than 5 or less')
        queries = {
            'ids': ','.join(ids)
        }
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return response

    @auth_validation(['user-follow-read'])
    @token_refresh
    def get_current_user_follow_artists(self, limit=20, after=None):
        """
        Get the current user's followed artists.
        Endpoint: GET https://api.spotify.com/v1/me/following?type=artist
        :param limit: The maximum number of results to return. Default 20. min 1, max 50.
        :param after: The last ID retrieved from the previous request.
        :return: CursorBasedPaging object with Artist object
        """
        endpoint = 'https://api.spotify.com/v1/me/following'
        # validate limit
        limit = validate_limit(limit)

        queries = {
            'type': 'artist',
            'limit': limit
        }
        if after:
            queries['after'] = after
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return CursorBasedPaging(response, Artist, self.authorization, 'artists')

    @auth_validation(['user-follow-modify'])
    @ids_validation(50)
    @token_refresh
    def follow_artists(self, artist_ids):
        """
        Follow artists
        Endpoint: PUT https://api.spotify.com/v1/me/following
        :param artist_ids: List of the Spotify IDs for Album. maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/following'
        query_param = {
            'ids': ','.join(artist_ids),
            'type': 'artist'
        }
        full_url = self.make_full_url(endpoint, urllib.parse.urlencode(query_param))
        response = http_request(self.authorization, full_url, method='PUT')
        return response

    @auth_validation(['user-follow-modify'])
    @ids_validation(50)
    @token_refresh
    def follow_users(self, user_ids):
        """
        Follow users
        Endpoint: PUT https://api.spotify.com/v1/me/following
        :param user_ids: List of the Spotify IDs for Album. maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/following'
        query_param = {
            'ids': ','.join(user_ids),
            'type': 'user'
        }
        full_url = self.make_full_url(endpoint, urllib.parse.urlencode(query_param))
        response = http_request(self.authorization, full_url, method='PUT')
        return response

    @auth_validation(['play-list-modify-public', 'playlist-modify-private'])
    @id_validation('playlist ID')
    @token_refresh
    def follow_playlist(self, playlist_id, is_public=True):
        """
        Follow playlist
        Endpoint: PUT https://api.spotify.com/v1/playlists/{playlist_id}/followers
        :param playlist_id: The Spotify ID for playlist
        :param is_public: Optional. If true the playlist will be includes in user's public playlist,
               if false it will remain private. Defaults to True.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/playlists/{playlist_id}/followers'.format(
            playlist_id=playlist_id
        )
        data = json.dumps(is_public).encode('utf-8')
        response = http_request(self.authorization, endpoint, data=data, method='PUT')
        return response

    @auth_validation(['user-follow-modify'])
    @ids_validation(50)
    @token_refresh
    def unfollow_artists(self, artist_ids):
        """
        Unfollow artists
        Endpoint: PUT https://api.spotify.com/v1/me/following
        :param artist_ids: List of the Spotify IDs for Album. maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/following'
        query_param = {
            'ids': ','.join(artist_ids),
            'type': 'artist'
        }
        full_url = self.make_full_url(endpoint, urllib.parse.urlencode(query_param))
        response = http_request(self.authorization, full_url, method='DELETE')
        return response

    @auth_validation(['user-follow-modify'])
    @ids_validation(50)
    @token_refresh
    def unfollow_users(self, user_ids):
        """
        Unfollow users
        Endpoint: PUT https://api.spotify.com/v1/me/following
        :param user_ids: List of the Spotify IDs for Album. maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/following'
        query_param = {
            'ids': ','.join(user_ids),
            'type': 'user'
        }
        full_url = self.make_full_url(endpoint, urllib.parse.urlencode(query_param))
        response = http_request(self.authorization, full_url, method='DELETE')
        return response

    @auth_validation(['play-list-modify-public', 'playlist-modify-private'])
    @id_validation('playlist ID')
    @token_refresh
    def unfollow_playlist(self, playlist_id, is_public=True):
        """
        Unfollow playlist
        Endpoint: PUT https://api.spotify.com/v1/playlists/{playlist_id}/followers
        :param playlist_id: The Spotify ID for playlist
        :param is_public: Optional. If true the playlist will be includes in user's public playlist,
               if false it will remain private. Defaults to True.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/playlists/{playlist_id}/followers'.format(
            playlist_id=playlist_id
        )
        data = json.dumps(is_public).encode('utf-8')
        response = http_request(self.authorization, endpoint, data=data, method='DELETE')
        return response

    # Library

    @auth_validation(['user-library-read'])
    @ids_validation(50)
    @token_refresh
    def check_users_saved_albums(self, album_ids):
        """
        Chck albums already saved in the current 'Your Music' library
        Endpoint: GET https://api.spotify.com/v1/me/albums/contains
        :param album_ids: lLst of the Spotify IDs for albums
        :return: List of boolean object
        """
        endpoint = 'https://api.spotify.com/v1/me/albums/contains'
        query = {
            'ids': ','.join(album_ids)
        }
        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return response

    @auth_validation(['user-library-read'])
    @ids_validation(50)
    @token_refresh
    def check_users_saved_tracks(self, track_ids, market=None):
        """
        Check albums already saved in the current 'Your Music' library
        Endpoint: GET https://api.spotify.com/v1/me/tracks/contains
        :param track_ids: List of Spotify IDs for tracks
        :param market: optional. An ISO 3166-1 alpha-2 country code.
        :return: List of boolean object
        """
        endpoint = 'https://api.spotify.com/v1/me/albums/contains'
        queries = {
            'ids': ','.join(track_ids)
        }
        if market:
            queries['market'] = market
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return response

    @auth_validation(['user-library-read'])
    @token_refresh
    def get_current_users_saved_album(self, limit=20, offset=0, market=None):
        """
        Get a list of the albums saved in the current user.
        Endpoint: GET https://api.spotify.com/v1/me/albums
        :param limit: Optional. The number of entity to return. maximum is 50.
        :param offset: Optional. The index of the first object to return.
        :param market: optional. An ISO 3166-1 alpha-2 country code.
        :return: Paging object with Album objects
        """
        endpoint = 'https://api.spotify.com/v1/me/albums'
        # validate limit
        limit = validate_limit(limit)
        # validate offset
        offset = validate_offset(offset)

        queries = {
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return Paging(response, SavedAlbum, self.authorization)

    @auth_validation(['user-library-read'])
    @token_refresh
    def get_current_users_saved_track(self, limit=20, offset=0, market=None):
        """
        Get a list of the tracks saved in the current user.
        Endpoint: GET https://api.spotify.com/v1/me/tracks
        :param limit: Optional. The number of entity to return. maximum is 50.
        :param offset: Optional. The index of the first object to return.
        :param market: Optional. An ISO 3166-1 alpha-2 country code.
        :return: Paging object with Track objects
        """
        endpoint = 'https://api.spotify.com/v1/me/tracks'
        # validate limit
        limit = validate_limit(limit)
        # validate offset
        offset = validate_offset(offset)

        queries = {
            'limit': limit,
            'offset': offset
        }
        if market:
            queries['market'] = market
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        return Paging(response, SavedTrack, self.authorization)

    @ids_validation(50)
    @auth_validation(['user-library-modify'])
    @token_refresh
    def remove_current_user_saved_albums(self, album_ids):
        """
        Remove saved albums for current user.
        Endpoint: DELETE https://api.spotify.com/v1/me/albums
        :param album_ids: List of the Spotify IDs for albums. Maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/albums'
        data = json.dumps(album_ids).encode('utf-8')
        response = http_request(self.authorization, endpoint, data=data, method='DELETE')
        return response

    @ids_validation(50)
    @auth_validation(['user-library-modify'])
    @token_refresh
    def remove_current_user_saved_tracks(self, track_ids):
        """
        Remove saved tracks for current user.
        Endpoint: DELETE https://api.spotify.com/v1/me/tracks
        :param track_ids: List of the Spotify IDs for albums. Maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/tracks'
        data = json.dumps(track_ids).encode('utf-8')
        response = http_request(self.authorization, endpoint, data=data, method='DELETE')
        return response

    @ids_validation(50)
    @auth_validation(['user-library-modify'])
    @token_refresh
    def save_albums_for_current_user(self, album_ids):
        """
        Add albums for current user's library.
        Endpoint: PUT https://api.spotify.com/v1/me/albums
        :param album_ids: List of the Spotify IDs for albums. Maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/albums'
        data = json.dumps(album_ids).encode('utf-8')
        response = http_request(self.authorization, endpoint, data=data, method='PUT')
        return response

    @ids_validation(50)
    @auth_validation(['user-library-modify'])
    @token_refresh
    def save_tracks_for_current_user(self, track_ids):
        """
        Add tracks for current user's library.
        Endpoint: PUT https://api.spotify.com/v1/me/tracks
        :param track_ids: List of the Spotify IDs for albums. Maximum length is 50.
        :return:
        """
        endpoint = 'https://api.spotify.com/v1/me/tracks'
        data = json.dumps(track_ids).encode('utf-8')
        response = http_request(self.authorization, endpoint, data=data, method='PUT')
        return response

    # Personalization

    @id_validation('type')
    @auth_validation(['user-top-read'])
    @token_refresh
    def get_users_top(self, entity_type, limit=20, offset=0, time_range='medium_term'):
        """

        :param entity_type: artists or tracks
        :param limit: Optional. The number of entity to return. maximum is 50.
        :param offset: Optional. The index of the first result to return. Default 0.
        :param time_range: Optional. over what time frame the affinities are computed.
               short_term(last 4 weeks), medium_term(last 6 months), long_term(last several years)
        :return: Paging object with Artist object or Track object
        """
        endpoint = 'https://api.spotify.com/v1/me/top/{type}'.format(
            type=entity_type.lower()
        )
        # validate type
        if entity_type.lower() not in ENTITY_TYPES:
            raise ValidationError('type must be artists or tracks')

        # validate limit
        limit = validate_limit(limit)

        # validate offset
        offset = validate_offset(offset)

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
        response = http_request(self.authorization, full_url)
        if entity_type.lower() == 'artists':
            klass = Artist
        elif entity_type.lower() == 'tracks':
            klass = Track
        return Paging(response, klass, self.authorization)

    # Search

    @token_refresh
    def search(self, q='', search_types=SEARCH_TYPES, market=None, limit=20, offset=0):
        """
        Get information about artists, albums, tracks, playlist with match a keyword string.
        :param q: Search keyword
        :param search_types: Iterable object contains search type. Default is ['album', 'artist', 'playlist', 'track'].
        :param market: Optional. ISO 3166-1 alpha-2 country code
        :param limit: Optional. The maximum number of results to return. Default 20. min 1, max 50.
        :param offset: Optional. The index of the first result to return. Default 0. max 10,000.
        :return: SearchResult objects
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
        limit = validate_limit(limit)

        # validate offset
        offset = validate_offset(offset, maximum=10000)

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
        response = http_request(self.authorization, full_url)
        results = SearchResult(q, search_types, response, self.authorization)
        return results

    # Track

    @id_validation('track id')
    @token_refresh
    def get_track(self, track_id, market=None):
        """
        Get track information.
        Endpoint: GET https://api.spotify.com/v1/tracks/{id}
        :param track_id: The Spotify ID for track
        :param market: Optional. ISO 3166-1 alpha-2 country code
        :return: Track object
        """
        endpoint = 'https://api.spotify.com/v1/tracks/{track_id}'.format(
            track_id=track_id
        )
        if market:
            query = {
                'market': market
            }
            data = urllib.parse.urlencode(query)
            endpoint = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, endpoint)
        result = Track(response)
        return result

    @ids_validation(50)
    @token_refresh
    def get_tracks(self, track_ids, market=None):
        """
        Get several track informations.
        Endpoint: GET https://api.spotify.com/v1/tracks
        :param track_ids: List of the Spotify IDs for track. Maximum length is 50.
        :param market: Optional. ISO 3166-1 alpha-2 country code
        :return: List of Track object
        """
        endpoint = 'https://api.spotify.com/v1/tracks'
        queries = {
            'ids': ','.join(track_ids)
        }
        if market:
            queries['market'] = market
        data = urllib.parse.urlencode(queries)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        converter = Track.to_object
        results = []
        for result in response['tracks']:
            results.append(converter(result))
        return results

    @id_validation('track id')
    @token_refresh
    def get_audio_analysis(self, track_id):
        """
        Get audio feature for track.
        Endpoint: Get https://api.spotify.com/v1/audio-analysis/{id}
        :param track_id: The Spotify ID for track
        :return: AudioAnalysis object
        """
        endpoint = 'https://api.spotify.com/v1/audio-analysis/{id}'.format(
            id=track_id
        )
        response = http_request(self.authorization, endpoint)
        result = AudioAnalysis(response)
        return result

    @id_validation('track id')
    @token_refresh
    def get_audio_feature(self, track_id):
        """
        Get audio feature for track.
        :param track_id: The Spotify ID for track
        :return: AudioFeature object
        """
        endpoint = 'https://api.spotify.com/v1/audio-features/{id}'.format(
            id=track_id
        )
        response = http_request(self.authorization, endpoint)
        result = AudioFeature(response)
        return result

    @ids_validation(100)
    @token_refresh
    def get_audio_features(self, track_ids):
        """
        Get several audio features
        :param track_ids: List of the Spotify IDs for track. Maximum length is 100
        :return: List of AudioFeature object
        """
        endpoint = 'https://api.spotify.com/v1/audio-features/'
        query = {
            'ids': ','.join(track_ids)
        }
        data = urllib.parse.urlencode(query)
        full_url = self.make_full_url(endpoint, data)
        response = http_request(self.authorization, full_url)
        converter = AudioFeature.to_object
        results = []
        for result in response['audio_features']:
            results.append(converter(result))
        return results

    # Users Profile

    @auth_validation(['user-read-email', 'user-read-private', 'user-read-birthdate'])
    @token_refresh
    def get_current_user_profile(self):
        """
        Endpoint: GET https://api.spotify.com/v1/me
        :return: PrivateUser object
        """
        endpoint = 'https://api.spotify.com/v1/me'
        response = http_request(self.authorization, endpoint)
        return PrivateUser(response)

    @id_validation('user id')
    @token_refresh
    def get_user_profile(self, user_id):
        """
        Endpoint: GET https://api.spotify.com/v1/users/{user_id}
        :param user_id:
        :return: PublicUser object
        """
        endpoint = 'https://api.spotify.com/v1/users/{user_id}'.format(
            user_id=user_id
        )
        response = http_request(self.authorization, endpoint)
        return PublicUser(response)
