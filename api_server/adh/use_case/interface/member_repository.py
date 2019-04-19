import abc


class NotFoundError(ValueError):
    pass


class MemberRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def search_member_by(self, ctx, limit=None, offset=None, room_number=None, terms=None, username=None) -> (
    list, int):
        pass

    @abc.abstractmethod
    def create_member(self, ctx, **fields) -> None:
        pass

    @abc.abstractmethod
    def update_member(self, ctx, member_to_update, **fields_to_update) -> None:
        pass

    @abc.abstractmethod
    def delete_member(self, ctx, username=None) -> None:
        pass
