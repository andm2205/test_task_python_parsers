import json
import requests
import re
from requests.exceptions import ProxyError, ChunkedEncodingError, ConnectionError

USERNAME = 'elonmusk'

TWEETS_LIMIT = 10

DEFAULT_HEADERS ={
    'Authority': 'twitter.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-language': 'ru,en-US;q=0.9,en;q=0.8',
    'Cache-control': 'max-age=0',
    'Sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    'Sec-ch-ua-mobile': '?0',
    'Sec-ch-ua-platform': '"Windows"',
    'Sec-fetch-dest': 'document',
    'Sec-fetch-mode': 'navigate',
    'Sec-fetch-site': 'same-origin',
    'Sec-fetch-user': '?1',
    'Upgrade-insecure-requests': '1',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
}

FEATURES_USER = '{"hidden_profile_likes_enabled":false,"hidden_profile_subscriptions_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_is_identity_verified_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}'
FEATURES_TWEETS = '{"rweb_lists_timeline_redesign_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}'

HEADERS = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
}

GET_USER_URL = 'https://twitter.com/i/api/graphql/SAMkL5y_N9pmahSw8yy6gw/UserByScreenName'
GET_TWEETS_URL = 'https://twitter.com/i/api/graphql/XicnWRbyQ3WgVY__VataBQ/UserTweets'

class TwitterParser:

    def __init__(self, username, proxies):
        self.HEADERS = HEADERS
        self.username = username
        self.proxies = proxies
        response = requests.get("https://twitter.com/", headers=DEFAULT_HEADERS, proxies=self.proxies)
        self.guess_token = "".join(re.findall(r'(?<=\"gt\=)[^;]+', response.text))
        if not self.guess_token:
            raise ValueError
        HEADERS['x-guest-token'] = self.guess_token

    def get_user(self):
        params = {
            'variables': json.dumps({"screen_name": self.username, "withSafetyModeUserFields": True}),
            'features': FEATURES_USER,
        }
        response = requests.get(
            GET_USER_URL,
            params=params, 
            headers=self.HEADERS,
            proxies=self.proxies
        )
        json_response = response.json()
        result = json_response.get("data", {}).get("user", {}).get("result", {})
        legacy = result.get("legacy", {})
        return {
            "id": result.get("rest_id"), 
            "username": self.username, 
            "full_name": legacy.get("name")
        }

    def iter_tweets(self, limit):
        print('Start getting tweets')
        user_id = self.get_user().get("id")
        if not user_id:
            raise ValueError('No user found')
        tweets = []

        while True:
            var = {
                "userId": user_id, 
                "count": TWEETS_LIMIT,
                "includePromotedContent": True,
                "withQuickPromoteEligibilityTweetFields": True, 
                "withVoice": True
            }

            params = {
                'variables': json.dumps(var),
                'features': FEATURES_TWEETS,
            }

            response = requests.get(
                GET_TWEETS_URL,
                params=params,
                headers=self.HEADERS,
                proxies=self.proxies
            )

            json_response = response.json()

            result = json_response.get("data", {}).get("user", {}).get("result", {})
            timeline = result.get("timeline", {}).get("timeline", {}).get("instructions", {})
            entries = [x.get("entries") for x in timeline if x.get("type") == "TimelineAddEntries"]
            entries = entries[0] if entries else []

            for entry in entries:
                legacy = entry.get("content").get("itemContent", {}).get("tweet_results", {}).get("result", {}).get("legacy")
                tweets.append({"created_at": legacy.get("created_at"), "content": legacy.get("full_text")})
                if len(tweets) >= limit:
                    break
                
            print('Tweets getted')

            if len(tweets) >= limit or len(entries) == 2:
                break

        return tweets


def main():
    with open('proxy_ips.txt') as file:
        while True:
            try:
                print('Start')
                ip = file.readline().strip()
                if not ip:
                    print('Defeat, all proxies were searched')
                    break
                proxies = {'http': ip, 'https': ip}
                parser = TwitterParser(USERNAME, proxies)
                tweets = parser.iter_tweets(TWEETS_LIMIT)
                for tweet in tweets: 
                    print(f'{tweet['created_at']}: {tweet['content']}')
                print('Success')
                break
            except (ProxyError, ChunkedEncodingError, ConnectionError) as e:
                print(f'{e.__class__.__name__}, getting next proxy')


if __name__ == '__main__':
    main()