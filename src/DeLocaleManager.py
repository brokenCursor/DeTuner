import locale
import os
import json


class DeLocaleManager:
    """ Class for managing locales in DeTuner """

    def __init__(self):
        self.__avaliable_locales = []
        self.__system_locale, self.__encoding = locale.getdefaultlocale()
        self.__locale_data = None
        self.load_locales()

    def load_locales(self):
        """ Get all valid locales from "locale" directory """
        # Find all files with .dl extencion
        try:
            file_list = [path for path in os.listdir(
                r'./locale/') if path.split('.')[-1] == 'dl']
        except FileNotFoundError as e:
            print(f"Unable to find locales directory!")
            raise

        # If no files found
        if not file_list:
            raise Exception("No locale files found!")

        # Process and import all files
        for file in file_list:
            with open(f"locale/{file}", 'r', encoding='utf-8-sig') as f:
                try:
                    locale = json.loads(f.read())
                    self.__avaliable_locales.append(
                        (file, locale["locale"], locale["language"]))
                except Exception as e:
                    print(e)
                    raise RuntimeWarning(
                        f"Unable to load {file}: invalid locale file!")
                f.close()
        if not self.__avaliable_locales:
            raise Exception("No valid locales found!")

    def get_avaliable_locales(self):
        """ Get list of avaliable locales and their languages """

        return [(loc[1], loc[2]) for loc in self.__avaliable_locales]

    def get_system_locale(self):
        """ Get default system locale """

        return self.__system_locale

    def set_locale(self, locale_name: str):
        """ Set locale_data to locale data from file """

        # Search for matching names
        locale_match = [
            loc for loc in self.__avaliable_locales if loc[1] == locale_name]

        if not locale_match:
            raise ValueError(f"No \"{locale_name}\" locale found")

        try:
            with open(f"locale/{locale_match[0][0]}", "r", encoding="utf-8-sig") as f:
                self.__locale_data = json.loads(f.read())
        except Exception as e:
            raise Exception(F"Unable to set locale {locale_name}: {e}")

    def get_strings(self):
        return self.__locale_data["strings"]
