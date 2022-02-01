from typing import TypeVar, Generic, Union

K = TypeVar('K')
V = TypeVar('V')
MaybeV = Union[V, None]


class KeyValue(Generic[K, V]):
    """Represent a key-value pair.

    This class is meant to be subclassed so that the subclass fixes the
    key as in:

        class MyKey(KeyValue[str, int]):
            def __init__(self, value: int):
                super().__init__('my-key', value)

    This way you can escape key duplication hell.
    """

    def __init__(self, key: K, value: MaybeV = None):
        self._key = key
        self._value = value

    def key(self) -> K:
        """
        Returns:
            the key.
        """
        return self._key

    def value(self) -> MaybeV:
        """
        Returns:
            the current value.
        """
        return self._value

    def read(self, data: dict) -> MaybeV:
        """Read this key value from the input dictionary.
        It also sets the value to be the current value.

        Args:
            data: where to get the value from.

        Returns:
            the value read if any.
        """
        self._value = data.get(self._key)
        return self._value

    def add(self, data: dict) -> dict:
        """Add this key-value pair to the input dictionary.

        Args:
            data: the dictionary to add to.

        Returns:
            the input dictionary with this key-value pair added.
        """
        data[self._key] = self._value
        return data


def add_to_dict(*args: KeyValue, data: dict = None) -> dict:
    """Add the specified key-value pairs to a dictionary.

    Args:
        data: the dictionary to add to. If not specified we'll build
            a fresh dictionary out of the input key-value pairs.
        args: the key-value pairs to add.

    Returns:
        the dictionary with the key-value pairs in it.
    """
    data = data if data else {}
    for kv in args:
        kv.add(data)
    return data
