import hashlib
import os
from pathlib import Path
from typing import Optional, Union, List, Any, Dict
from flask import Flask

HASH_SIZE = 5


class CacheBuster:
    def __init__(self, app: Optional[Flask] = None, config: Dict[str, Any] = None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")

        self.app = app
        self.config = config
        self.extensions: Union[List[str], str, None] = (
            self.config.get("extensions") if self.config else []
        )
        self.hash_size: int = (
            self.config.get("hash_size", HASH_SIZE) if self.config else HASH_SIZE
        )
        if self.app is not None:
            self.init_app(self.app, config)

    def __is_file_to_be_busted(self, filepath: str):
        """
        :param filepath:
        :return: True or False
        """
        if not self.extensions:
            return True
        return Path(filepath).suffix in self.extensions if filepath else False

    def init_app(self, app: Flask, config: Dict[str, Any] = None):
        """
        Register `app` in cache buster so that `url_for` adds a unique prefix
        to URLs generated for the `'static'` endpoint. Also make the app able
        to serve cache-busted static files.

        This allows setting long cache expiration values on static resources
        because whenever the resource changes, so does its URL.
        """
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")

        bust_map: Dict[str, str] = {}  # map from an unbusted filename to a busted one
        # http://flask.pocoo.org/docs/0.12/api/#flask.Flask.static_folder

        app.logger.debug("Computing hashes for static assets...")

        assert (
            app.static_folder is not None
        ), "`app` must have an specifed `static_folder`"

        # compute (un)bust tables.
        for dirpath, dirnames, filenames in os.walk(app.static_folder):
            for filename in filenames:
                # compute version component
                rooted_filename = os.path.join(dirpath, filename)
                if not self.__is_file_to_be_busted(rooted_filename):
                    continue

                with open(rooted_filename, "rb") as f:
                    version = hashlib.md5(f.read()).hexdigest()[: self.hash_size]

                # add version
                unbusted = os.path.relpath(rooted_filename, app.static_folder)

                # save computation to map
                bust_map[unbusted] = version

        app.logger.debug("Hashes generated for all static assets.")

        def bust_filename(file: str):
            return bust_map.get(file, "")

        @app.url_defaults
        def reverse_to_cache_busted_url(endpoint: str, values: Dict[str, Any]):
            """
            Make `url_for` produce busted filenames when using the 'static'
            endpoint.
            """
            if endpoint == "static":
                values["q"] = bust_filename(values["filename"])
