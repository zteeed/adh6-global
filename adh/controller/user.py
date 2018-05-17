from connexion import NoContent
from adh.model.database import Database as db
from adh.model.models import Adherent, Chambre, Adhesion
from adh.util.date import string_to_date
from adh.exceptions import InvalidEmail, RoomNotFound, UserNotFound
import datetime
import sqlalchemy
from adh.auth import auth_simple_user
import hashlib


def adherentExists(session, username):
    """ Returns true if the user exists """
    try:
        Adherent.find(session, username)
    except UserNotFound:
        return False
    return True


@auth_simple_user
def filterUser(limit=100, offset=0, terms=None, roomNumber=None):
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
    return list(map(dict, r)), 200, headers


@auth_simple_user
def getUser(username):
    """ [API] Get the specified user from the database """
    s = db.get_db().get_session()
    try:
        return dict(Adherent.find(s, username))
    except UserNotFound:
        return NoContent, 404


@auth_simple_user
def deleteUser(username):
    """ [API] Delete the specified User from the database """
    s = db.get_db().get_session()
    try:
        s.delete(Adherent.find(s, username))
        s.commit()
        return NoContent, 204
    except UserNotFound:
        return NoContent, 404


@auth_simple_user
def putUser(username, body):
    """ [API] Create/Update user from the database """
    s = db.get_db().get_session()

    try:
        new_user = Adherent.from_dict(s, body)
    except InvalidEmail:
        return "Invalid email", 400
    except RoomNotFound:
        return "No room found", 400
    except ValueError:
        return "String must not be empty", 400

    update = adherentExists(s, username)
    if update:
        new_user.id = Adherent.find(s, username).id

    s.merge(new_user)
    s.commit()
    if update:
        return NoContent, 204
    else:
        return NoContent, 201


@auth_simple_user
def addMembership(username, body):
    """ [API] Add a membership record in the database """

    s = db.get_db().get_session()

    start = string_to_date(body["start"])
    end = None
    if start and "duration" in body:
        duration = body["duration"]
        end = start + datetime.timedelta(days=duration)

    try:
        s.add(Adhesion(
            adherent=Adherent.find(s, username),
            depart=start,
            fin=end
        ))
    except UserNotFound:
        return NoContent, 404

    s.commit()
    return NoContent, 200, {'Location': 'test'}  # TODO: finish that!


def ntlm_hash(txt):
    """
    NTLM hashing function
    wow much security such hashing function
    Needed by MSCHAPv2.
    """

    return hashlib.new('md4', txt.encode('utf-16le')).hexdigest()


@auth_simple_user
def updatePassword(username, body):
    password = body["password"]
    s = db.get_db().get_session()

    try:
        a = Adherent.find(s, username)
    except UserNotFound:
        return NoContent, 404

    a.password = ntlm_hash(password)
    s.commit()
    return NoContent, 204
