import utils

home_url="https://www.douyin.com/user/MS4wLjABAAAAfP1ScdvTLKhf50A7R3_YNQdGO3G_KDm9_rfPtZrkx0JD4a0rhOa1a1NjNYuRD75b?from_tab_name=main&vid=7267136925083962683"
keyword="死神来了"
page_count=9
utils.download_douyin_video_by_search_keywords(home_url,keyword,page_count)
