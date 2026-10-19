from urllib.parse import urlsplit, parse_qs

def hostname(url):
    parsed = urlsplit(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('An HTTP(S) URL without embedded credentials is required.')
    return parsed.hostname.lower()

def domain_matches(host, base):
    return host == base or host.endswith('.' + base)

def classify_url(url):
    host = hostname(url)
    if domain_matches(host, 'youtube.com') or domain_matches(host, 'youtu.be') or domain_matches(host, 'youtube-nocookie.com'):
        return 'youtube'
    if domain_matches(host, 'tiktok.com'):
        return 'tiktok'
    if domain_matches(host, 'instagram.com'):
        return 'instagram'
    return 'generic_web'

def is_image_url(url):
    hostname(url)
    return urlsplit(url).path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'))

def video_id(url):
    import re
    if classify_url(url) != 'youtube':
        return None
    parsed = urlsplit(url)
    parts = parsed.path.strip('/').split('/')
    if domain_matches(hostname(url), 'youtu.be'):
        value = parts[0]
    elif parts[0] in {'shorts', 'embed', 'live'} and len(parts) > 1:
        value = parts[1]
    else:
        value = parse_qs(parsed.query).get('v', [''])[0]
    return value if re.fullmatch(r'[a-zA-Z0-9_-]{11}', value) else None
