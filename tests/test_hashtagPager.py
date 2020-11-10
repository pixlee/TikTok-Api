from TikTokApi import TikTokApi


class TestHashtagPager:
    """Test the pager returned by getHashtagPager"""
    def test_page_size(self):
        """Pages should be pretty close to the specified size"""
        api = TikTokApi.get_instance()

        hashtag_info = api.getHashtagObject('regal')
        pager = api.getHashtagPager(hashtag_info['challengeInfo']['challenge']['id'], page_size=5)

        page = pager.__next__()
        assert abs(len(page)-5) <= 2  # allow up to 2 fewer than max page size

        page = pager.__next__()
        assert abs(len(page)-5) <= 2

        # clean up
        TikTokApi._instance = None
        del api

    def test_max_pages(self):
        """Pages should be pretty close to the specified size."""
        api = TikTokApi.get_instance()

        hashtag_info = api.getHashtagObject('regal')
        pager = api.getHashtagPager(hashtag_info['challengeInfo']['challenge']['id'])

        pages = 0
        total_tiktoks = 0
        for page in pager:
            pages += 1
            total_tiktoks += len(page)
            if pages > 3:
                break

        assert pages == 4

        assert abs(total_tiktoks - pages * 30) <= 5  # allow for up to 5 fewer than expected

        # clean up
        TikTokApi._instance = None
        del api
