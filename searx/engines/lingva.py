# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lingva (alternative Google Translate frontend)"""

about = {
    "website": 'https://lingva.ml',
    "wikidata_id": None,
    "official_api_documentation": 'https://github.com/thedaviddelta/lingva-translate#public-apis',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

engine_type = 'online_dictionary'
categories = ['general', 'translate']

url = "https://lingva.thedaviddelta.com"
search_url = "{url}/api/v1/{from_lang}/{to_lang}/{query}"


def request(_query, params):
    params['url'] = search_url.format(
        url=url, from_lang=params['from_lang'][1], to_lang=params['to_lang'][1], query=params['query']
    )
    return params


def response(resp):
    results = []

    result = resp.json()
    info = result["info"]
    from_to_prefix = "%s-%s " % (resp.search_params['from_lang'][1], resp.search_params['to_lang'][1])

    if "typo" in info:
        results.append({"suggestion": from_to_prefix + info["typo"]})

    if 'definitions' in info:  # pylint: disable=too-many-nested-blocks
        for definition in info['definitions']:
            for item in definition.get('list', []):
                for synonym in item.get('synonyms', []):
                    results.append({"suggestion": from_to_prefix + synonym})

    data = []

    for definition in info['definitions']:
        for translation in definition['list']:
            data.append(
                {
                    'text': result['translation'],
                    'definitions': [translation['definition']] if translation['definition'] else [],
                    'examples': [translation['example']] if translation['example'] else [],
                    'synonyms': translation['synonyms'],
                }
            )

    for translation in info["extraTranslations"]:
        for word in translation["list"]:
            data.append(
                {
                    'text': word['word'],
                    'definitions': word['meanings'],
                }
            )

    if not data and result['translation']:
        data.append({'text': result['translation']})

    results.append(
        {
            'answer': data[0]['text'],
            'answer_type': 'translations',
            'translations': data,
        }
    )

    return results
