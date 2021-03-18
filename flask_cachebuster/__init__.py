import hashlib
import os
from pathlib import Path

HASH_SIZE = 5


class CacheBuster:
    def __init__(self, app=None, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")

        self.app = app
        self.config = config
        self.extensions = self.config.get("extensions") if self.config else []
        self.hash_size = self.config.get("hash_size") if self.config else HASH_SIZE
        if self.app is not None:
            self.register_cache_buster(app, config)

    def __is_file_to_be_busted(self, filepath):
        """
        :param filepath:
        :return: True or False
        """
        if not self.extensions:
            return True
        return Path(filepath).suffix in self.extensions if filepath else False

    def init_app(self, app, config=None):
        """
        Register `app` in cache buster so that `url_for` adds a unique prefix
        to URLs generated for the `'static'` endpoint. Also make the app able
        to serve cache-busted static files.

        This allows setting long cache expiration values on static resources
        because whenever the resource changes, so does its URL.
        """
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")

        bust_map = {}  # map from an unbusted filename to a busted one
        # http://flask.pocoo.org/docs/0.12/api/#flask.Flask.static_folder

        app.logger.debug("Computing hashes for static assets...")
        # compute (un)bust tables.
        for dirpath, dirnames, filenames in os.walk(app.static_folder):
            for filename in filenames:
                # compute version component
                rooted_filename = os.path.join(dirpath, filename)
                if not self.__is_file_to_be_busted(rooted_filename):
                    continue
                app.logger.debug("Computing hashes for {}".format(rooted_filename))
                with open(rooted_filename, "rb") as f:
                    version = hashlib.md5(f.read()).hexdigest()[: self.hash_size]

                # add version
                unbusted = os.path.relpath(rooted_filename, app.static_folder)

                # save computation to map
                bust_map[unbusted] = version
        app.logger.debug("Hashes generated for all static assets.")

        def bust_filename(file):
            return bust_map.get(file, "")

        @app.url_defaults
        def reverse_to_cache_busted_url(endpoint, values):
            """
            Make `url_for` produce busted filenames when using the 'static'
            endpoint.
            """
            if endpoint == "static":
                values["q"] = bust_filename(values["filename"])
