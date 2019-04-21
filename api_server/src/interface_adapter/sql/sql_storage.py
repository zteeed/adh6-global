# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from typing import List

from src.constants import CTX_SQL_SESSION
from src.entity.member import Member
from src.interface_adapter.sql.model.models import Adherent, Chambre, Adhesion
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.member_repository import MemberRepository, NotFoundError
from src.use_case.interface.membership_repository import MembershipRepository


class SQLStorage(MemberRepository, MembershipRepository):
    """
    Represent the interface to the SQL database.
    """

    def add_membership(self, ctx, username, start, end) -> None:
        """
        Add a membership record.

        :raises NotFoundError
        """
        s = ctx.get(CTX_SQL_SESSION)

        member = _get_member_by_login(s, username)
        if member is None:
            raise NotFoundError('cannot find any member with that username')

        s.add(Adhesion(
            adherent=member,
            depart=start,
            fin=end
        ))

    def create_member(self, ctx,
                      last_name=None, first_name=None, email=None, username=None, comment=None,
                      room_number=None, departure_date=None, association_mode=None
                      ) -> None:
        """
        Create a member.

        :raises NotFoundError
        """
        s = ctx.get(CTX_SQL_SESSION)
        now = datetime.now()

        room = None
        if room_number is not None:
            room = s.query(Chambre).filter(Chambre.numero == room_number).one_or_none()
            if not room:
                raise NotFoundError('room not found')

        member = Adherent(
            nom=last_name,
            prenom=first_name,
            mail=email,
            login=username,
            chambre=room,
            created_at=now,
            updated_at=now,
            commentaires=comment,
            date_de_depart=departure_date,
            mode_association=association_mode,
        )

        with track_modifications(ctx, s, member):
            s.add(member)

    def update_member(self, ctx, member_to_update,
                      last_name=None, first_name=None, email=None, username=None, comment=None,
                      room_number=None, departure_date=None, association_mode=None, password=None
                      ) -> None:
        """
        Update a member.

        :raises NotFoundError
        """
        s = ctx.get(CTX_SQL_SESSION)

        member = _get_member_by_login(s, member_to_update)
        if member is None:
            raise NotFoundError()

        with track_modifications(ctx, s, member):
            member.nom = last_name or member.nom
            member.prenom = first_name or member.prenom
            member.mail = email or member.mail
            member.commentaires = comment or member.commentaires
            member.login = username or member.login

            if departure_date is not None:
                member.date_de_depart = departure_date

            if association_mode is not None:
                member.mode_association = association_mode

            if room_number is not None:
                member.chambre = Chambre.find(s, room_number)

            member.updated_at = datetime.now()

        member.password = password or member.password  # Will not be tracked.

    def delete_member(self, ctx, username=None) -> None:
        """
        Delete a member.

        :raises NotFoundError
        """
        s = ctx.get(CTX_SQL_SESSION)

        # Find the soon-to-be deleted user
        member = _get_member_by_login(s, username)
        if not member:
            raise NotFoundError(f"could not find user '{username}'")

        with track_modifications(ctx, s, member):
            # Actually delete it
            s.delete(member)

    def search_member_by(self, ctx, limit=None, offset=None, room_number=None, terms=None, username=None) -> (
            List[Member], int):
        """
        Search a member.
        """
        s = ctx.get(CTX_SQL_SESSION)
        q = s.query(Adherent)

        if username:
            q = q.filter(Adherent.login == username)

        if room_number:
            try:
                q2 = s.query(Chambre)
                q2 = q2.filter(Chambre.numero == room_number)
                result = q2.one()
            except NoResultFound:
                return [], 0

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

        return list(map(_map_member_sql_to_entity, r)), count


def _map_member_sql_to_entity(adh: Adherent) -> Member:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    departure_date = _date_to_string(adh.date_de_depart)
    association_mode = _date_to_string(adh.mode_association)

    room_number = None
    if adh.chambre is not None:
        room_number = str(adh.chambre.numero)

    return Member(
        username=adh.login,
        email=adh.mail,
        first_name=adh.prenom,
        last_name=adh.nom,
        departure_date=departure_date,
        comment=adh.commentaires,
        association_mode=association_mode,
        room_number=room_number,
    )


def _get_member_by_login(s, login) -> Adherent:
    return s.query(Adherent).filter(Adherent.login == login).one_or_none()


def _date_to_string(d) -> str:
    if d is None:
        return d

    return d.isoformat()
