import logging
import json
from connexion import NoContent
from sqlalchemy import or_
from adh.model.database import Database as db
from adh.model.models import Switch
from adh.exceptions import InvalidIPv4, SwitchNotFound
from adh.auth import auth_simple_user, auth_admin


def switchExists(session, switchID):
    """ Return true if the switch exists """
    try:
        Switch.find(session, switchID)
    except SwitchNotFound:
        return False
    return True


@auth_simple_user
def filterSwitch(admin, limit=100, offset=0, terms=None):
    """ [API] Filter the switch list """
    if limit < 0:
        return "Limit must be positive", 400
    q = db.get_db().get_session().query(Switch)
    # Filter by terms
    if terms:
        q = q.filter(or_(
            Switch.description.contains(terms),
            Switch.ip.contains(terms),
            Switch.communaute.contains(terms),
        ))
    count = q.count()
    q = q.order_by(Switch.description.asc())
    q = q.offset(offset)
    q = q.limit(limit)  # Limit the number of matches
    q = q.all()

    # Convert the qs into data suited for the API
    q = map(lambda x: {'switchID': x.id, 'switch': dict(x)}, q)
    result = list(q)  # Cast generator as list

    headers = {
        'access-control-expose-headers': 'X-Total-Count',
        'X-Total-Count': str(count)
    }
    logging.info("%s fetched the switch list", admin.login)
    return result, 200, headers


@auth_admin
def createSwitch(admin, body):
    """ [API] Create a switch in the database """
    if "id" in body:
        return "You cannot set the id", 400
    session = db.get_db().get_session()
    try:
        switch = Switch.from_dict(session, body)
    except InvalidIPv4:
        return "Invalid IPv4", 400
    session.add(switch)
    session.commit()

    logging.info("%s created a switch\n%s", admin.login, json.dumps(body))
    return NoContent, 201, {'Location': '/switch/{}'.format(switch.id)}


@auth_simple_user
def getSwitch(admin, switchID):
    """ [API] Get the specified switch from the database """
    session = db.get_db().get_session()
    try:
        logging.info("%s fetched the switch %d", admin.login, switchID)
        return dict(Switch.find(session, switchID))
    except SwitchNotFound:
        return NoContent, 404


@auth_admin
def updateSwitch(admin, switchID, body):
    """ [API] Update the specified switch from the database """
    if "id" in body:
        return "You cannot update the id", 400

    session = db.get_db().get_session()
    if not switchExists(session, switchID):
        return NoContent, 404

    try:
        switch = Switch.from_dict(session, body)
        switch.id = switchID
    except InvalidIPv4:
        return "Invalid IPv4", 400

    session.merge(switch)
    session.commit()

    logging.info("%s updated the switch %d\n%s",
                 admin.login, switchID, json.dumps(body))
    return NoContent, 204


@auth_admin
def deleteSwitch(admin, switchID):
    """ [API] Delete the specified switch from the database """
    session = db.get_db().get_session()

    try:
        switch = Switch.find(session, switchID)
    except SwitchNotFound:
        return NoContent, 404

    session.delete(switch)
    session.commit()

    logging.info("%s deleted the switch %d", admin.login, switchID)
    return NoContent, 204
