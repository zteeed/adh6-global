#!/usr/bin/env python3
import logging

import connexion
from connexion.resolver import RestyResolver

from CONFIGURATION import API_CONF
from CONFIGURATION import PROD_DATABASE as DATABASE
from adh.interface_adapter.sql.model.database import Database
from adh.use_case.member_manager import MemberManager

Database.init_db(DATABASE)

member_manager = MemberManager()

logging.basicConfig(level=logging.INFO)
app = connexion.FlaskApp(__name__)
app.app.config.update(API_CONF)
app.add_api('swagger.yaml',
            resolver=RestyResolver('adh.interface_adapter.endpoint'),
            strict_validation=True)
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app
