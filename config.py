import json


class Configuration:
    """
    Simple implementation of configuration loading/saving with JSON file.
    """
    def __init__(self, path="config.json", filters=None):
        self._path = path
        self.config = None
        # for Geeks
        if filters is None:
            filters = {} # so it will be Empty
        self.__filters = filters

    def load(self, path=None, *args, **kwargs):
        """
        Load JSON file
        :param path:
        :param kwargs:
        :return:
        """
        if path is None:
            path = self._path
        with open(path, *args) as fp:
            self.config = json.load(fp)

        # Some Geek stuff
        for fn in  self.__filters.get('load', []):
            self.config = fn(self.config, **kwargs)

    def save(self, path=None, *args, **kwargs):
        """
        Save JSON file
        :param path:
        :param kwargs:
        :return:
        """
        if path is None:
            path = self._path
        with open(path, *args) as fp:
            json.dump(self.config, fp)

        # Some Geek stuff
        for fn in  self.__filters.get('save', []):
            self.config = fn(self.config, **kwargs)
