from operator import ge
import random
from typing import Any, Callable, Generator, Generic, List
from uuid import uuid4

from fipy.ngsi.entity import Entity, FloatAttr, TextAttr


def float_attr_close_to(base: float) -> FloatAttr:
    """Generate a `FloatAttr` having a random value close to `base`.
    More accurately, the generated value `x` will be such that
    `abs(x - base) <= 1`.

    Args:
        base: a base value from which to generate the attribute value.

    Returns:
        A `FloatAttr` instance with a random value close to `base`.
    """
    seed = random.uniform(0, 1)
    return FloatAttr.new(base + seed)


def text_attr_from_one_of(choices: List[str]) -> TextAttr:
    """Pick a value from the given `choices` to instantiate a `TextAttr`.

    Args:
        choices: list of values to choose from.

    Returns:
        A `TextAttr` instance with a value randomly picked from `choices`.
    """
    pick = random.choice(choices)
    return TextAttr.new(pick)


EntityGenerator = Callable[[], Entity]
"""A function to generate an NGSI entity with possibly random attribute
values.

The function implementation must make sure
- every call returns a new `Entity` object---i.e. the Python type of
  the returned objects is the same across calls and is a subclass of
  `BaseEntity`;
- every call returns an object with the same NGSI type---i.e. the
  value of the `type` field is the same across calls.

The function should set the `id` field to an empty string since the
classes and utils in this module override the ID value.
"""

class EntityFactory(Generic[Entity]):
    """Use an `EntityGenerator` to make NGSI entities all having IDs in the
    format `urn:ngsi-ld:T:S` where `T` is the NGSI type of the entities and
    and `S` a string suffix drawn from a given list.
    """

    def __init__(self, generator: EntityGenerator, suffixes = [Any]):
        """Create a new instance.

        Args:
            generator: creates NGSI entities.
            suffixes: list of suffixes to append to entity IDs. Must not be
                empty. Values will be converted to their string representation.
        """
        assert generator is not None
        assert len(suffixes) > 0

        self._suffixes = [str(s) for s in suffixes]
        self._generator = generator

    def new_entity(self, suffix_index: int) -> Entity:
        """Create a new entity with an entity ID ending with the suffix
        associated to the given index.

        Args:
            suffix_index: a valid index for the suffix list passed in when
                creating the factory.

        Returns:
            The NGSI entity.
        """
        suffix = self._suffixes[suffix_index]
        entity = self._generator()
        entity.set_id_with_type_prefix(suffix)
        return entity

    def new_batch(self) -> List[Entity]:
        """Create an entity for each entity ID suffix passed in when creating
        the factory.

        Returns:
            A list of entities where the first one has an entity ID ending
            with the fist suffix, the second has an ID ending with the second
            suffix, and so on to the last one that's got an ID ending with the
            last suffix passed in when creating the factory.
        """
        return [self.new_entity(k) for k in range(0, len(self._suffixes))]

    def entity_id(self, suffix_index: int) -> str:
        """Generate an NGSI entity ID in the format used for the entities
        this factory creates.
        The ID is in the format `urn:ngsi-ld:T:S` where `T` is the NGSI type
        of the entities and and `S` the string suffix at `suffix_index` in
        the list passed in when creating the factory.

        Args:
            suffix_index: a valid index for the suffix list passed in when
                creating the factory.

        Returns:
            The NGSI ID.
        """
        return self.new_entity(suffix_index).id

    @staticmethod
    def with_numeric_suffixes(how_many: int, generator: EntityGenerator) \
        -> 'EntityFactory':
        """Create an `EntityFactory` with the given generator and a list
        of entity ID suffixes of `[1, .., N]` where `N = how_many + 1`.

        Args:
            how_many: number of numeric suffixes to use.
            generator: creates NGSI entities.

        Returns:
            The factory.
        """
        assert how_many > 0

        suffixes = [k for k in range(1, how_many + 1)]
        return EntityFactory(generator, suffixes)

    @staticmethod
    def with_uuid_suffixes(how_many: int, generator: EntityGenerator) \
        -> 'EntityFactory':
        """Create an `EntityFactory` with the given generator and a list
        of entity ID suffixes of `[u1, .., uN]` where `N = how_many + 1`
        and `u[k]` is a random UUID.

        Args:
            how_many: number of numeric suffixes to use.
            generator: creates NGSI entities.

        Returns:
            The factory.
        """
        assert how_many > 0

        suffixes = [uuid4() for _ in range(1, how_many + 1)]
        return EntityFactory(generator, suffixes)


def entity_batch(pool: EntityFactory[Entity]) \
     -> Generator[List[Entity], None, None]:
    """Use the given factory to produce an infinite stream of lists of
    entities. Generate each list by calling the factory's `new_batch`
    method.
    """
    while True:
        yield pool.new_batch()
