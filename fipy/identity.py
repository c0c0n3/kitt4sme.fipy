from typing import TypeVar, Generic

T = TypeVar('T')


class Identifiable(Generic[T]):
    """Interface for things that have an ID."""

    def canonical_id(self) -> T:
        """
        Returns:
            this thing's canonical ID.
        """
        pass

    def is_identifiable_as(self, the_id: T):
        """Has this thing the same ID as the given one?

        Args:
            the_id: the ID to match.

        Returns:
            `True` for yes, `False` for no.
        """
        return self.canonical_id() == the_id

    def __eq__(self, other):
        if isinstance(other, Identifiable):
            return self.canonical_id() == other.canonical_id()
        return False
    # We assume an Identifiable's ID is unique across all Identifiable objects
    # in memory.

    def __hash__(self):
        return hash(str(self.canonical_id()))
    # subclasses should override if this makes no sense!


class Named:
    """Interface for things that have a name."""

    def canonical_name(self) -> str:
        """
        Returns:
            this thing's canonical name.
        """
        pass

    def is_named_as(self, name: str):
        """Is this thing named as specified?

        Args:
            name: the name to match.

        Returns:
            `True` for yes, `False` for no.
        """
        return self.canonical_name() == name
    # TODO: case-insensitive comparison instead?
    # see: https://stackoverflow.com/questions/319426/
