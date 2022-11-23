# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""
Implementation of RESTful API for AiiDA based on flask and flask_restx.

Author: Snehal P. Waychal and Fernando Gargiulo @ Theos, EPFL
"""

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import GLOBAL_CONFIG, INSTANCE


class App(Flask):
    """
    Basic Flask App customized for this REST Api purposes
    """

    def __init__(self, *args, **kwargs):
        # Decide whether or not to catch the internal server exceptions (
        # default is True)
        catch_internal_server = kwargs.pop("catch_internal_server", True)

        # Basic initialization
        super().__init__(*args, **kwargs)

        # Error handler
        from aiida.restapi.common.exceptions import (
            RestFeatureNotAvailable,
            RestInputValidationError,
            RestValidationError,
        )

        if catch_internal_server:

            @self.errorhandler(Exception)
            def error_handler(error):
                # pylint: disable=unused-variable
                """Error handler to return customized error messages from
                rest api"""

                if isinstance(error, RestValidationError):
                    response = jsonify({"message": str(error)})
                    response.status_code = 400

                elif isinstance(error, RestInputValidationError):
                    response = jsonify({"message": str(error)})
                    response.status_code = 404

                elif isinstance(error, RestFeatureNotAvailable):
                    response = jsonify({"message": str(error)})
                    response.status_code = 501

                elif isinstance(error, HTTPException) and error.code == 404:
                    from aiida.restapi.common.utils import list_routes

                    response = jsonify(
                        {
                            "message": "The requested URL is not found on the "
                                       "server.",
                            "available_endpoints": list_routes(),
                        }
                    )
                    response.status_code = 404

                # Generic server-side error (not to make the api crash if an
                # unhandled exception is raised. Caution is never enough!!)
                else:
                    response = jsonify({"message": str(error)})
                    response.status_code = 500

                return response

        else:
            pass


def get_app_instance():
    app = INSTANCE.get("service")

    if app is None:
        app = App(GLOBAL_CONFIG["APP_NAME"])
        app.url_map.strict_slashes = False
        app.app_context().push()
        INSTANCE.setdefault("service", app)

        # Apply default configuration
        app.config.update(**GLOBAL_CONFIG.get("APP_CONFIG", {}))

        # Allow cross-origin resource sharing
        cors_prefix = r"{}/*".format(
            GLOBAL_CONFIG.get("API_CONFIG", {}).get("PREFIX", "")
        )
        CORS(app, resources={cors_prefix: {"origins": "*"}})

    return app
