import responses
import pytest

from instabot.api.config import API_URL, SIG_KEY_VERSION

from .test_bot import TestBot
from .test_variables import (TEST_CAPTION_ITEM, TEST_COMMENT_ITEM,
                             TEST_PHOTO_ITEM, TEST_USER_ITEM)


class TestBotGet(TestBot):
    @responses.activate
    def test_get_media_owner(self):
        media_id = 1234

        responses.add(
            responses.POST, "{API_URL}media/{media_id}/info/".format(
                API_URL=API_URL, media_id=media_id),
            json={
                "auto_load_more_enabled": True,
                "num_results": 1,
                "status": "ok",
                "more_available": False,
                "items": [TEST_PHOTO_ITEM]
            }, status=200)
        responses.add(
            responses.POST, "{API_URL}media/{media_id}/info/".format(
                API_URL=API_URL, media_id=media_id),
            json={"status": "ok"}, status=200)

        owner = self.BOT.get_media_owner(media_id)

        assert owner == str(TEST_PHOTO_ITEM["user"]["pk"])

        owner = self.BOT.get_media_owner(media_id)

        assert owner is False

    @responses.activate
    def test_get_popular_medias(self):
        results = 5
        responses.add(
            responses.GET, "{API_URL}feed/popular/?people_teaser_supported=1&rank_token={rank_token}&ranked_content=true&".format(
                API_URL=API_URL, rank_token=self.BOT.rank_token),
            json={
                "auto_load_more_enabled": True,
                "num_results": results,
                "status": "ok",
                "more_available": False,
                "items": [TEST_PHOTO_ITEM for _ in range(results)]
            }, status=200)

        medias = self.BOT.get_popular_medias()

        assert medias == [str(TEST_PHOTO_ITEM["pk"]) for _ in range(results)]
        assert len(medias) == results

    @responses.activate
    def test_get_timeline_medias(self):
        self.BOT.max_likes_to_like = TEST_PHOTO_ITEM['like_count'] + 1
        results = 8
        responses.add(
            responses.GET, "{API_URL}feed/timeline/".format(API_URL=API_URL),
            json={
                "auto_load_more_enabled": True,
                "num_results": results,
                "is_direct_v2_enabled": True,
                "status": "ok",
                "next_max_id": None,
                "more_available": False,
                "items": [TEST_PHOTO_ITEM for _ in range(results)]
            }, status=200)
        responses.add(
            responses.GET, "{API_URL}feed/timeline/".format(API_URL=API_URL),
            json={
                "status": "fail"
            }, status=400)

        medias = self.BOT.get_timeline_medias()

        assert medias == [TEST_PHOTO_ITEM["pk"] for _ in range(results)]
        assert len(medias) == results

        medias = self.BOT.get_timeline_medias()

        assert medias == []
        assert len(medias) == 0

    @responses.activate
    def test_get_timeline_users(self):
        results = 8
        responses.add(
            responses.GET, "{API_URL}feed/timeline/".format(API_URL=API_URL),
            json={
                "auto_load_more_enabled": True,
                "num_results": results,
                "is_direct_v2_enabled": True,
                "status": "ok",
                "next_max_id": None,
                "more_available": False,
                "items": [TEST_PHOTO_ITEM for _ in range(results)]
            }, status=200)
        responses.add(
            responses.GET, "{API_URL}feed/timeline/".format(API_URL=API_URL),
            json={
                "status": "fail"
            }, status=400)

        users = self.BOT.get_timeline_users()

        assert users == [str(TEST_PHOTO_ITEM["user"]["pk"]) for _ in range(results)]
        assert len(users) == results

        users = self.BOT.get_timeline_users()

        assert users == []
        assert len(users) == 0

    @responses.activate
    def test_get_your_medias(self):
        results = 5
        my_test_photo_item = TEST_PHOTO_ITEM.copy()
        my_test_photo_item['user']['pk'] = self.USER_ID
        response_data = {
            "auto_load_more_enabled": True,
            "num_results": results,
            "status": "ok",
            "more_available": False,
            "items": [my_test_photo_item for _ in range(results)]
        }
        responses.add(
            responses.GET, '{API_URL}feed/user/{user_id}/?max_id=&min_timestamp=&rank_token={rank_token}&ranked_content=true'.format(
                API_URL=API_URL, user_id=self.BOT.user_id, rank_token=self.BOT.rank_token),
            json=response_data, status=200)

        medias = self.BOT.get_your_medias()

        assert medias == [my_test_photo_item["pk"] for _ in range(results)]
        assert len(medias) == results

        medias = self.BOT.get_your_medias(as_dict=True)

        assert medias == response_data['items']
        assert len(medias) == results

    @responses.activate
    def test_get_archived_medias(self):
        results = 5
        my_test_photo_item = TEST_PHOTO_ITEM.copy()
        my_test_photo_item['user']['pk'] = self.USER_ID
        response_data = {
            "auto_load_more_enabled": True,
            "num_results": results,
            "status": "ok",
            "more_available": False,
            "items": [my_test_photo_item for _ in range(results)]
        }
        responses.add(
            responses.GET, '{API_URL}feed/only_me_feed/?rank_token={rank_token}&ranked_content=true&'.format(
                API_URL=API_URL, rank_token=self.BOT.rank_token),
            json=response_data, status=200)

        medias = self.BOT.get_archived_medias()

        assert medias == [my_test_photo_item["pk"] for _ in range(results)]
        assert len(medias) == results

        medias = self.BOT.get_archived_medias(as_dict=True)

        assert medias == response_data['items']
        assert len(medias) == results

    @responses.activate
    def test_search_users(self):
        results = 5
        query = "test"
        my_test_user_item = TEST_USER_ITEM
        response_data = {
            "has_more": True,
            "num_results": results,
            "rank_token": self.BOT.rank_token,
            "status": "ok",
            "users": [my_test_user_item for _ in range(results)]
        }
        responses.add(
            responses.GET, '{API_URL}users/search/?ig_sig_key_version={SIG_KEY}&is_typeahead=true&query={query}&rank_token={rank_token}'.format(
                API_URL=API_URL, rank_token=self.BOT.rank_token, query=query, SIG_KEY=SIG_KEY_VERSION), json=response_data, status=200)

        medias = self.BOT.search_users(query)

        assert medias == [str(my_test_user_item["pk"]) for _ in range(results)]
        assert len(medias) == results

    @responses.activate
    def test_search_users_failed(self):
        query = "test"
        response_data = {'status': 'fail'}
        responses.add(
            responses.GET, '{API_URL}users/search/?ig_sig_key_version={SIG_KEY}&is_typeahead=true&query={query}&rank_token={rank_token}'.format(
                API_URL=API_URL, rank_token=self.BOT.rank_token, query=query, SIG_KEY=SIG_KEY_VERSION), json=response_data, status=200)

        medias = self.BOT.search_users(query)

        assert medias == []

    @responses.activate
    def test_get_comments(self):
        results = 5
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": 4,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok"
        }
        media_id = 1234567890
        responses.add(
            responses.GET, '{API_URL}media/{media_id}/comments/?'.format(
                API_URL=API_URL, media_id=media_id), json=response_data, status=200)

        comments = self.BOT.get_media_comments(media_id)
        assert comments == response_data['comments']
        assert len(comments) == results

    @responses.activate
    def test_get_comments_text(self):
        results = 5
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": 4,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok"
        }
        media_id = 1234567890
        responses.add(
            responses.GET, '{API_URL}media/{media_id}/comments/?'.format(
                API_URL=API_URL, media_id=media_id), json=response_data, status=200)

        comments = self.BOT.get_media_comments(media_id, only_text=True)
        expected_result = [comment['text'] for comment in response_data['comments']]

        assert comments == expected_result
        assert len(comments) == results

    @responses.activate
    def test_get_comments_failed(self):
        response_data = {"status": "fail"}
        media_id = 1234567890
        responses.add(
            responses.GET, '{API_URL}media/{media_id}/comments/?'.format(
                API_URL=API_URL, media_id=media_id), json=response_data, status=200)

        comments = self.BOT.get_media_comments(media_id)
        assert comments == []

    @responses.activate
    def test_get_commenters(self):
        results = 5
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": 4,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok"
        }
        media_id = 1234567890
        responses.add(
            responses.GET, '{API_URL}media/{media_id}/comments/?'.format(
                API_URL=API_URL, media_id=media_id), json=response_data, status=200)

        expected_commenters = [str(TEST_COMMENT_ITEM['user']['pk']) for _ in range(results)]

        commenters = self.BOT.get_media_commenters(media_id)
        assert commenters == expected_commenters
        assert len(commenters) == results

    @responses.activate
    def test_get_commenters_failed(self):
        response_data = {"status": "fail"}
        media_id = 1234567890
        responses.add(
            responses.GET, '{API_URL}media/{media_id}/comments/?'.format(
                API_URL=API_URL, media_id=media_id), json=response_data, status=200)

        expected_commenters = []

        commenters = self.BOT.get_media_commenters(media_id)
        assert commenters == expected_commenters

    @pytest.mark.parametrize('url_result', [
        ['https://www.instagram.com/p/BfHrDvCDuzC/', 1713527555896569026],
        ['test', False]
    ])
    def test_get_media_id_from_link_with_wrong_data(self, url_result):
        media_id = self.BOT.get_media_id_from_link(url_result[0])

        assert url_result[1] == media_id

    @pytest.mark.parametrize('comments', [
        ['comment1', 'comment2', 'comment3'],
        [],
        None
    ])
    def test_get_comment(self, comments):
        self.BOT.comments = comments

        if self.BOT.comments:
            assert self.BOT.get_comment() in self.BOT.comments
        else:
            assert self.BOT.get_comment() == 'wow'
