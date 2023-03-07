# SPDX-License-Identifier: AGPL-3.0-or-later
# lint: pylint
"""Twitter (microblogging platform)"""

from json import loads
from urllib.parse import urlencode
from datetime import datetime
from datetime import timedelta

about = {
    "website": 'https://twitter.com',
    "wikidata_id": None,
    "official_api_documentation": 'https://developer.twitter.com/en/docs/twitter-api',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

categories = ['general', 'web', 'social media']
time_range_support = True
time_range_dict = {'day': 'd', 'week': 'w', 'month': 'm', 'year': 'y'}



url = "https://api.twitter.com"
search_url = (
    "{url}/2/search/adaptive.json?{query}&tweet_mode=extended&query_source=typed_query&pc=1&spelling_corrections=1"
)


def request(query, params):

    if params['time_range'] in time_range_dict:
        # 计算截止时间
        today = datetime.today()
        if params['time_range'] == 'day':
            until_date = today - timedelta(days=1)
        elif params['time_range'] == 'week':
            until_date = today - timedelta(weeks=1)
        elif params['time_range'] == 'month':
            until_date = today - timedelta(days=30)
        elif params['time_range'] == 'year':
            until_date = today - timedelta(days=365)
    
        # 将截止时间格式化为字符串
        until_str = until_date.strftime('%Y-%m-%d')
        query += ' since:' + until_str
    else:
        today = datetime.today()
        until_date = today - timedelta(weeks=1)
        until_str = until_date.strftime('%Y-%m-%d')
        query += ' since:' + until_str


    params['url'] = search_url.format(url=url, query=urlencode({'q': query}))

    params['headers'] = {
        # This token is used in the Twitter web interface (twitter.com). Without this header, the API doesn't work.
        # The value of the token has never changed (or maybe once a long time ago).
        # https://github.com/zedeus/nitter/blob/5f31e86e0e8578377fa7d5aeb9631bbb2d35ef1e/src/consts.nim#L5
        'Authorization': (
            "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKb"
            "T3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
        )
    }

    return params


def response(resp):
    results = []

    json_res = loads(resp.text)['globalObjects']

    for tweet in json_res['tweets'].values():
        text = tweet['full_text']
        display = tweet['display_text_range']

        # img_src = tweet.get('extended_entities', {}).get('media', [{}])[0].get('media_url_https')
        # if img_src:
        #     img_src += "?name=thumb"

        results.append(
            {
                'url': 'https://twitter.com/i/web/status/' + tweet['id_str'],
                'title': (text[:40] + '...') if len(text) > 40 else text,
                'content': text[display[0] : display[1]],
                # 'img_src': img_src,
                'publishedDate': datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y'),
            }
        )
        if len(results)>=3: break

    # for user in json_res['users'].values():
    #     results.append(
    #         {
    #             'title': user['name'],
    #             'content': user['description'],
    #             'url': 'https://twitter.com/' + user['screen_name'],
    #             # 'img_src': user['profile_image_url_https'],
    #         }
    #     )

    return results
