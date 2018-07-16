import json
import logging
from connexion import NoContent
from adh.model.database import Database as db
from adh.model.models import Adherent, Chambre, Adhesion, Modification
from adh.util.date import string_to_date
from adh.exceptions import InvalidEmail, RoomNotFound, UserNotFound
import datetime
import sqlalchemy
from adh.auth import auth_simple_user
import hashlib
from CONFIGURATION import PRICES


def adherentExists(session, username):
    """ Returns true if the user exists """
    try:
        Adherent.find(session, username)
    except UserNotFound:
        return False
    return True


@auth_simple_user
def filterUser(admin, limit=100, offset=0, terms=None, roomNumber=None):
    """ [API] Filter the list of users from the the database """
    if limit < 0:
        return "Limit must be positive", 400

    s = db.get_db().get_session()

    q = s.query(Adherent)
    if roomNumber:
        try:
            q2 = s.query(Chambre)
            q2 = q2.filter(Chambre.numero == roomNumber)
            result = q2.one()
        except sqlalchemy.orm.exc.NoResultFound:
            return [], 200, {"X-Total-Count": '0'}

        q = q.filter(Adherent.chambre == result)
    if terms:
        q = q.filter(
            (Adherent.nom.contains(terms)) |
            (Adherent.prenom.contains(terms)) |
            (Adherent.mail.contains(terms)) |
            (Adherent.login.contains(terms)) |
            (Adherent.commentaires.contains(terms))
        )
    count = q.count()
    q = q.order_by(Adherent.login.asc())
    q = q.offset(offset)
    q = q.limit(limit)
    r = q.all()
    headers = {
        "X-Total-Count": str(count),
        'access-control-expose-headers': 'X-Total-Count'
    }
    logging.info("%s fetched the user list", admin.login)
    return list(map(dict, r)), 200, headers


@auth_simple_user
def getUser(admin, username):
    """ [API] Get the specified user from the database """
    s = db.get_db().get_session()
    try:
        logging.info("%s fetched the user %s", admin.login, username)
        return dict(Adherent.find(s, username))
    except UserNotFound:
        return NoContent, 404


@auth_simple_user
def deleteUser(admin, username):
    """ [API] Delete the specified User from the database """
    s = db.get_db().get_session()

    # Find the soon-to-be deleted user
    try:
        a = Adherent.find(s, username)
    except UserNotFound:
        return NoContent, 404

    try:
        # if so, start tracking for modifications
        a.start_modif_tracking()

        # Actually delete it
        s.delete(a)
        s.flush()

        # Write it in the modification table
        Modification.add_and_commit(s, a, admin)
    except Exception:
        s.rollback()
        raise
    logging.info("%s deleted the user %s", admin.login, username)
    return NoContent, 204


@auth_simple_user
def putUser(admin, username, body):
    """ [API] Create/Update user from the database """
    s = db.get_db().get_session()

    # Create a valid object
    try:
        new_user = Adherent.from_dict(s, body)
    except InvalidEmail:
        return "Invalid email", 400
    except RoomNotFound:
        return "No room found", 400
    except ValueError:
        return "String must not be empty", 400

    try:
        # Check if it already exists
        update = adherentExists(s, username)

        if update:
            current_adh = Adherent.find(s, username)
            new_user.id = current_adh.id
            current_adh.start_modif_tracking()

        # Merge the object (will create a new if it doesn't exist)
        new_user = s.merge(new_user)
        s.flush()

        # Create the corresponding modification
        Modification.add_and_commit(s, new_user, admin)
    except Exception:
        s.rollback()
        raise

    if update:
        logging.info("%s updated the user %s\n%s",
                     admin.login, username, json.dumps(body, sort_keys=True))
        return NoContent, 204
    else:
        logging.info("%s created the user %s\n%s",
                     admin.login, username, json.dumps(body, sort_keys=True))
        return NoContent, 201


@auth_simple_user
def addMembership(admin, username, body):
    """ [API] Add a membership record in the database """

    s = db.get_db().get_session()

    start = datetime.datetime.now().date()
    if "start" in body:
        start = string_to_date(body["start"])

    duration = body["duration"]
    end = start + datetime.timedelta(days=duration)

    if duration not in PRICES:
        return "There is no price assigned to that duration", 400

    try:
        adh = Adherent.find(s, username)
        s.add(Adhesion(
            adherent=adh,
            depart=start,
            fin=end
        ))
        adh.start_modif_tracking()
        adh.date_de_depart = end

    except UserNotFound:
        return NoContent, 404

    Modification.add_and_commit(s, adh, admin)
    logging.info("%s created the membership record %s\n%s",
                 admin.login, username, json.dumps(body, sort_keys=True))
    return NoContent, 200, {'Location': 'test'}  # TODO: finish that!


def ntlm_hash(txt):
    """
    NTLM hashing function
    wow much security such hashing function
    Needed by MSCHAPv2.
    """

    return hashlib.new('md4', txt.encode('utf-16le')).hexdigest()


@auth_simple_user
def updatePassword(admin, username, body):
    password = body["password"]
    s = db.get_db().get_session()

    try:
        a = Adherent.find(s, username)
    except UserNotFound:
        return NoContent, 404

    try:
        a.start_modif_tracking()
        a.password = ntlm_hash(password)
        s.flush()

        # Build the corresponding modification
        Modification.add_and_commit(s, a, admin)

    except Exception:
        s.rollback()
        raise

    logging.info("%s updated the password of %s",
                 admin.login, username)
    return NoContent, 204