
import json
import os.path
import os.path as ospath
import atexit
import inspect

LOCALE = "fixme"
SEARCH_DIRS = [ospath.dirname(ospath.abspath(__file__))]

def set_locale(locale):
    global LOCALE
    LOCALE = locale


MISSING_LOCALES = []

locale_dict = dict()


def check_localization():
    if not locale_dict:
        for cwd in SEARCH_DIRS:
            print("Loading localization from ", cwd)
            locale_path = ospath.join(cwd, LOCALE + ".json")
            print("LOCALE:", locale_path)
            with open(locale_path, "r") as fp:
                locale_dict.update(json.load(fp))

def format_locale(key,*args,**kwargs):
    check_localization()
    if key in locale_dict.keys():
        return locale_dict[key].format(*args,**kwargs)
    else:
        if key not in MISSING_LOCALES:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            MISSING_LOCALES.append([key, calframe[1][3]])
        return key

def get_locale(key):
    check_localization()
    if key in locale_dict.keys():
        return locale_dict[key]
    else:
        if key not in MISSING_LOCALES:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            MISSING_LOCALES.append([key, calframe[1][3]])
        return key



def find_help_file(key):
    for cwd in SEARCH_DIRS:
        help_path = ospath.join(cwd, "help", LOCALE)
        tgtfile = ospath.join(help_path, key)
        if ospath.isfile(tgtfile):
            return tgtfile
    return None

def get_help(key):
    with open(find_help_file(key), "r") as fp:
        return fp.read()


def report_missing_locales():
    if MISSING_LOCALES:
        print(f"Found missing locales for locale '{LOCALE}'")
        for item in MISSING_LOCALES:
            print("{} (caller {})".format(*item))


atexit.register(report_missing_locales)