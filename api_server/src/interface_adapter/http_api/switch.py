# coding=utf-8
from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.switch import Switch
from src.exceptions import SwitchNotFoundError, UserInputError
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.auth import auth_regular_admin, auth_super_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.switch_manager import MutationRequest, SwitchManager
from src.util.context import log_extra
from src.util.log import LOG


class SwitchHandler:
    def __init__(self, switch_manager: SwitchManager):
        self.switch_manager = switch_manager

    @with_context
    @require_sql
    @auth_regular_admin
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None):
        """ Filter the switch list """
        LOG.debug("http_switch_search_called", extra=log_extra(ctx, terms=terms))

        try:
            result, count = self.switch_manager.search(ctx, limit=limit, offset=offset, terms=terms)
            headers = {
                'access-control-expose-headers': 'X-Total-Count',
                'X-Total-Count': str(count)
            }
            result = list(map(_map_switch_to_http_response, result))
            return result, 200, headers

        except UserInputError as e:
            return bad_request(e), 400

    @with_context
    @require_sql
    @auth_super_admin
    def post(self, ctx, body):
        """ Create a switch in the database """
        LOG.debug("http_switch_post_called", extra=log_extra(ctx, request=body))

        try:
            switch_id = self.switch_manager.create(ctx, MutationRequest(
                ip_v4=body.get('ip'),
                description=body.get('description'),
                community=body.get('community'),
            ))
            return NoContent, 201, {'Location': f'/switch/{switch_id}'}

        except UserInputError as e:
            return bad_request(e), 400

    @with_context
    @require_sql
    @auth_regular_admin
    def get(self, ctx, switch_id):
        """ Get the specified switch from the database """
        LOG.debug("http_switch_get_called", extra=log_extra(ctx, switch_id=switch_id))

        try:
            switch = self.switch_manager.get_by_id(ctx, switch_id)
            return _map_switch_to_http_response(switch), 200

        except SwitchNotFoundError:
            return NoContent, 404

    @with_context
    @require_sql
    @auth_super_admin
    def put(self, ctx, switch_id, body):
        """ Update the specified switch from the database """
        LOG.debug("http_switch_put_called", extra=log_extra(ctx, switch_id=switch_id, request=body))

        try:
            self.switch_manager.update(ctx, switch_id, MutationRequest(
                ip_v4=body.get('ip'),
                description=body.get('description'),
                community=body.get('community'),
            ))
            return NoContent, 204

        except SwitchNotFoundError:
            return NoContent, 404

        except UserInputError as e:
            return bad_request(e), 400

    @with_context
    @require_sql
    @auth_super_admin
    def delete(self, ctx, switch_id):
        """ Delete the specified switch from the database """
        LOG.debug("http_switch_delete_called", extra=log_extra(ctx, switch_id=switch_id))
        try:
            self.switch_manager.delete(ctx, switch_id)
            return NoContent, 204

        except SwitchNotFoundError:
            return NoContent, 404


def _map_switch_to_http_response(switch: Switch) -> dict:
    fields = {
        'id': int(switch.id),
        'ip': switch.ip_v4,
        'description': switch.description,
        'community': switch.community,
    }
    return {k: v for k, v in fields.items() if v is not None}
