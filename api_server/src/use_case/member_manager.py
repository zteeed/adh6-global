# coding=utf-8
"""
Use cases (business rule layer) of everything related to members.
"""
import datetime
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List

from src.entity.member import Member
from src.log import LOG
from src.use_case.exceptions import StringMustNotBeEmptyException, InvalidEmailError, MemberNotFound, \
    MissingRequiredFieldError, IntMustBePositiveException, InvalidRoomNumberError, PasswordTooShortError, \
    UsernameMismatchError
from src.use_case.interface.logs_repository import LogsRepository, LogFetchError
from src.use_case.interface.member_repository import MemberRepository, NotFoundError
from src.use_case.interface.membership_repository import MembershipRepository
from src.util.checks import is_email
from src.util.context import build_log_extra
from src.util.date import string_to_date
from src.util.hash import ntlm_hash


class Mutation(Enum):
    """
    Mutation state.
    """
    NOT_SET = 1


@dataclass
class MutationRequest(Member):
    """
    Mutation request for a member. This represents the 'diff', that is going to be applied on the member object.
    """
    email: str = Mutation.NOT_SET
    first_name: str = Mutation.NOT_SET
    last_name: str = Mutation.NOT_SET
    username: str = Mutation.NOT_SET
    departure_date: str = Mutation.NOT_SET
    comment: str = Mutation.NOT_SET
    association_mode: str = Mutation.NOT_SET
    room_number: str = Mutation.NOT_SET


class NoPriceAssignedToThatDurationException(ValueError):
    def __init__(self):
        super().__init__('there is no price assigned to that duration')


class MemberManager:
    """
    Implements all the use cases related to member management.
    """

    def __init__(self,
                 member_storage: MemberRepository,
                 membership_storage: MembershipRepository,
                 logs_storage: LogsRepository,
                 configuration):
        self.member_storage = member_storage
        self.membership_storage = membership_storage
        self.logs_storage = logs_storage
        self.config = configuration

    def new_membership(self, ctx, username, duration, start_str=None) -> None:
        """
        Core use case of ADH. Registers a membership.

        User story: As an admin, I can create a new membership record, so that a member can have internet access.
        :param ctx: context
        :param username: username
        :param duration: duration of the membership in days
        :param start_str: optional start date of the membership

        :raises IntMustBePositiveException
        :raises NoPriceAssignedToThatDurationException
        :raises MemberNotFound
        """
        if start_str is None:
            return self.new_membership(ctx, username, duration, start_str=datetime.datetime.now().isoformat())

        if duration < 0:
            raise IntMustBePositiveException('duration')

        if duration not in self.config.PRICES:
            raise NoPriceAssignedToThatDurationException()

        start = string_to_date(start_str)

        end = start + datetime.timedelta(days=duration)

        try:
            self.membership_storage.add_membership(ctx, username, start, end)
            self.member_storage.update_member(ctx, username, departure_date=end)
        except NotFoundError:
            raise MemberNotFound()

        LOG.info("create_membership_record", extra=build_log_extra(
            ctx,
            username=username,
            duration_in_days=duration,
            start_date=start.isoformat()
        ))

    def get_by_username(self, ctx, username) -> Member:
        """
        User story: As an admin, I can see the profile of a member, so that I can help her/him.

        :raises MemberNotFound
        """
        result, _ = self.member_storage.search_member_by(ctx, username=username)
        if not result:
            raise MemberNotFound()

        # Log action.
        LOG.info('member_get_by_username', extra=build_log_extra(
            ctx,
            username='username'
        ))
        return result[0]

    def search(self, ctx, limit, offset=0, room_number=None, terms=None) -> (List[Member], int):
        """
        search member in the database.

        user story: as an admin, i want to have a list of members with some filters, so that i can browse and find
        members.

        :raises intmustbepositiveexception
        """
        if limit < 0:
            raise IntMustBePositiveException('limit')

        if offset < 0:
            raise IntMustBePositiveException('offset')

        result, count = self.member_storage.search_member_by(ctx,
                                                             limit=limit,
                                                             offset=offset,
                                                             room_number=room_number,
                                                             terms=terms)

        # Log action.
        LOG.info('member_search', extra=build_log_extra(
            ctx,
            room_number=room_number,
            terms=terms,
        ))
        return result, count

    def update_or_create(self, ctx, username, mutation_request: MutationRequest) -> bool:
        """
        Create/Update member from the database.

        User story: As an admin, I can register a new profile, so that I can add a membership with their profile.
        :return: True if the member was created, false otherwise.

        :raises InvalidEmailError
        :raises InvalidRoomNumberError
        :raises MissingRequiredFieldError
        :raises StringMustNotBeEmptyException
        :raises UsernameMismatchError
        """
        # Make sure all the fields set are valid.
        _validate_mutation_request(mutation_request)

        # Make sure all the necessary fields are set.
        if not _is_set(mutation_request.username):
            raise MissingRequiredFieldError('username')

        member, _ = self.member_storage.search_member_by(ctx, username=username)
        if member:
            # [UPDATE] Member already exists, perform a whole update.

            # Create a dict with fields to update. If field is not provided in the mutation request, consider that it
            # should be None as it is a full update of the member.
            fields_to_update = asdict(mutation_request)
            fields_to_update = {k: v if _is_set(v) else None for k, v in fields_to_update.items()}

            # This call will never throw a NotFoundError because we checked for the object existence before.
            self.member_storage.update_member(ctx, username, **fields_to_update)

            # Log action.
            LOG.info('member_whole_update', extra=build_log_extra(
                ctx,
                username=username,
                mutation=json.dumps(fields_to_update, sort_keys=True, default=str),
            ))

            return False
        else:
            # [CREATE] Member does not exist, create it.

            # Build a dict that will be transformed into a member. If a field is not set, consider that it should be
            # None.
            if username != mutation_request.username:
                raise UsernameMismatchError()

            mutation_request.username = username  # Just in case it has not been specified in the body.
            fields = asdict(mutation_request)
            fields = {k: v if _is_set(v) else None for k, v in fields.items()}

            try:
                self.member_storage.create_member(ctx, **fields)
            except NotFoundError:
                raise InvalidRoomNumberError()

            # Log action
            LOG.info('member_create', extra=build_log_extra(
                ctx,
                username=username,
                mutation=json.dumps(fields, sort_keys=True, default=str)
            ))

            return True

    def update_partially(self, ctx, username, mutation_request: MutationRequest) -> None:
        """
        User story: As an admin, I can modify some of the fields of a profile, so that I can update the information of
        a member.

        :raises MemberNotFound
        """
        # Perform all the checks on the validity of the data in the mutation request.
        _validate_mutation_request(mutation_request)

        # Create a dict with all the changed field. If a field in 'NOT_SET' it will not be put in the dict, and the
        # field will not be updated.
        fields_to_update = asdict(mutation_request)
        fields_to_update = {k: v for k, v in fields_to_update.items() if _is_set(v)}

        try:
            self.member_storage.update_member(ctx, username, **fields_to_update)
        except NotFoundError:
            raise MemberNotFound()

        # Log action.
        LOG.info('member_partial_update', extra=build_log_extra(
            ctx,
            username=username,
            mutation=json.dumps(fields_to_update, sort_keys=True, default=str)
        ))

    def change_password(self, ctx, username, password) -> None:
        """
        User story: As an admin, I can set the password of a user, so that they can connect using their credentials.
        Change the password of a member.

        BE CAREFUL: do not log the password or store it unhashed.

        :raises PasswordTooShortError
        :raises MemberNotFound
        """

        if len(password) <= 6:  # It's a bit low but eh...
            raise PasswordTooShortError()

        # Overwrite password variable by its hash, now that the checks are done, we don't need the cleartext anymore.
        # Still, be careful not to log this field!
        password = ntlm_hash(password)

        try:
            self.member_storage.update_member(ctx, username, password=password)
        except NotFoundError:
            raise MemberNotFound()

        LOG.info('member_password_update', extra=build_log_extra(
            ctx,
            username=username,
        ))

    def delete(self, ctx, username) -> None:
        """
        User story: As an admin, I can remove a profile, so that their information is not in our system.

        :raises MemberNotFound
        """

        try:
            self.member_storage.delete_member(ctx, username)

            # Log action.
            LOG.info('member_delete', extra=build_log_extra(
                ctx,
                username=username,
            ))
        except NotFoundError:
            raise MemberNotFound()

    def get_logs(self, ctx, username) -> List[str]:
        """
        User story: As an admin, I can retrieve the logs of a member, so I can help him troubleshoot their connection
        issues.

        :raises MemberNotFound
        """
        # Fetch all the devices of the member to put them in the request
        # all_devices = get_all_devices(s)
        # q = s.query(all_devices, Adherent.login.label("login"))
        # q = q.join(Adherent, Adherent.id == all_devices.columns.adherent_id)
        # q = q.filter(Adherent.login == username)
        # mac_tbl = list(map(lambda x: x.mac, q.all()))

        # Check that the user exists in the system.
        result, _ = self.member_storage.search_member_by(ctx, username=username)
        if not result:
            raise MemberNotFound()

        # Do the actual log fetching.
        try:
            # TODO: Fetch all the devices and put them into this request.
            logs = self.logs_storage.get_logs(ctx, username, [])

            LOG.info('member_get_logs', extra=build_log_extra(
                ctx,
                username=username,
            ))

            return logs

        except LogFetchError:
            LOG.warning("Log fetching failed, returning empty response.")
            return []  # We fail open here.


def _is_set(v):
    """
    Check if a field in a MutationRequest is set.
    """
    return v != Mutation.NOT_SET


def _validate_mutation_request(req: MutationRequest):
    """
    Validate the fields that are set in a MutationRequest.
    """
    if _is_set(req.email) and not is_email(req.email):
        raise InvalidEmailError()

    if req.first_name == '':
        raise StringMustNotBeEmptyException('first_name')

    if req.last_name == '':
        raise StringMustNotBeEmptyException('last_name')

    if req.username == '':
        raise StringMustNotBeEmptyException('username')

    if req.room_number == '':
        raise StringMustNotBeEmptyException('room number')
