
def get_response_json_with_check(response):
    if response.status_code != 200:
        response.raise_for_status()
    r = response.json()
    if r.get('code') == -403:
        raise Exception("token认证失败")
    if r.get('code') != 'S00000':
        raise Exception(r.get('message'))
    return r
