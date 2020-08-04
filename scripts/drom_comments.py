import requests, xml, pandas, datetime, re
from selenium import webdriver

from lxutils import *

proxies = {
  'http': 'http://OmLm5lT9tO:leshchenko@83.217.8.134:44538',
  'https': 'http://OmLm5lT9tO:leshchenko@95.214.8.62:44538',
}

project_dir = "C:\\users\\a.leshchenko\\documents\\ctrl\\stocks\\"
data_dir = project_dir + "data\\"
task_file = data_dir + "drom.ru - comments task.csv"
comment_file = data_dir + 'drom.ru - comments.xlsx'

log ('Reading task file')
task_urls = pandas.read_csv(task_file, sep=';', usecols=['link', 'Benefit'])
log ('{} tasks received'.format(task_urls.shape[0]))
task_urls.sort_values (by=['Benefit'], ascending=False, inplace=True)

log('Reading existing comment file')
existing_comments = pandas.read_excel (comment_file, usecols=['URL', 'Name', "Comment"])
log('{} comments already in file'.format(existing_comments.shape[0]))

log ('Adjusting the list of tasks')
merge = pandas.merge(task_urls, existing_comments, how="outer", left_on="link", right_on="URL", indicator=True)
task_urls = merge.loc[merge._merge == "left_only"]

log ('Reading pages from drom.ru')

log ('Preparing webdriver')

import os
import zipfile

PROXY_HOST = '83.217.8.134'  # rotating proxy or host
PROXY_PORT = 44538 # port
PROXY_USER = 'OmLm5lT9tO' # username
PROXY_PASS = 'leshchenko' # password

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        options=chrome_options)
    return driver

driver = get_chromedriver(use_proxy=True)
result = []

i = 0
for u in task_urls['link']:
    r = {}
    successive_failures = 0
    while successive_failures < 2:
        log ('Reading page {} ({})'.format(i+1, u))
        r['URL']=u
        driver.get(u)
        try:
            r['Name']=driver.find_element_by_xpath("//span[@class='inplace auto-shy']").text
            try:
                c=driver.find_element_by_xpath("//p[@class='inplace mod__label_up_down auto-shy']").get_attribute('innerHTML')
                c=re.sub(r'(\n|\t|\<br\>)', ' ', c)
                r['Comment']=c
            except:
                r['Comment']=''               
            result.append(r)
            i += 1
            break
        except:
            log("Seems like we've been spotted, resetting driver")
            successive_failures += 1
            driver.close()
            driver = get_chromedriver(use_proxy=True)
    if successive_failures == 2:
        log('Double failure, wrapping up')
        break


driver.close()

log ('{} pages read'.format (i))

df = existing_comments.append(result)
df.to_excel(comment_file, index=False)

log ('Written to file')