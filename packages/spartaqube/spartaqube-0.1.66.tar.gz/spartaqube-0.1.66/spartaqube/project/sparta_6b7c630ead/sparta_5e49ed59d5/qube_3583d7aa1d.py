import re, os, json
import requests
from datetime import datetime
from packaging.version import parse
from project.models import AppVersioning
from project.logger_config import logger
import pytz
UTC = pytz.utc
proxies_dict = {'http': os.environ.get('http_proxy', None), 'https': os.environ.get('https_proxy', None)}


def sparta_cfc429c0d9() ->str:
    """
    #TODO to implement
    """
    return None


def sparta_86fbc59622() ->str:
    """
    Return last version using github tags
    """
    api_url = 'https://api.github.com/repos/SpartaQube/spartaqube-version/tags'
    response = requests.get(api_url, proxies=proxies_dict, verify=False)
    tags = json.loads(response.text)
    latest_tag = max(tags, key=lambda t: parse(t['name']))
    return latest_tag['name']


def sparta_d892f069be() ->str:
    """
    Return last version using cloudflare/github
    """
    url = 'https://spartaqube-version.pages.dev/latest_version.txt'
    response = requests.get(url, proxies=proxies_dict, verify=False)
    return response.text.split('\n')[0]


def sparta_a403c072d1() ->str:
    """
    Deprecated due to scrapping pip not working anymore
    """
    try:
        url = 'https://pypi.org/project/spartaqube/'
        html_content = requests.get(url, proxies=proxies_dict, verify=False
            ).text
        package_header_div_match = re.search(
            '<h1 class="package-header__name">(.*?)</h1>', html_content, re.DOTALL)
        package_header_div = package_header_div_match.group(1)
        version = package_header_div.strip().split('spartaqube ')[1]
        return version
    except:
        pass


def sparta_7d2b403019() ->str:
    """
    
    """
    current_path = os.path.dirname(__file__)
    core_path = os.path.dirname(current_path)
    project_path = os.path.dirname(core_path)
    base_path = os.path.dirname(project_path)
    try:
        with open(os.path.join(base_path, 'app_version.json'), 'r'
            ) as json_file:
            current_version_dict = json.load(json_file)
            current_version = current_version_dict['version']
    except:
        current_version = '0.1.1'
    return current_version


def sparta_b18d7fe6cc() ->dict:
    """
    
    """
    try:
        current_version = sparta_7d2b403019()
        latest_version = sparta_d892f069be()
        versioning_set = AppVersioning.objects.all()
        date_now = datetime.now().astimezone(UTC)
        if versioning_set.count() == 0:
            AppVersioning.objects.create(last_available_version_pip=
                latest_version, last_check_date=date_now)
        else:
            versioning_obj = versioning_set[0]
            versioning_obj.last_available_version_pip = latest_version
            versioning_obj.last_check_date = date_now
            versioning_obj.save()
        b_update = not current_version == latest_version
        return {'current_version': current_version, 'latest_version':
            latest_version, 'b_update': b_update, 'humanDate':
            'A moment ago', 'res': 1}
    except Exception as e:
        logger.debug('Exception versioning update')
        logger.debug(e)
        return {'res': -1, 'errorMsg': str(e)}

#END OF QUBE
