import hmtai


def get_hentai(request_type='hentai'):
    return hmtai.get("nekobot", request_type)
