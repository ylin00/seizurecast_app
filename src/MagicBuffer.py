from collections import deque


class MagicBuffer:
    """Multi-key data buffer"""
    def __init__(self, buffer_size=1, max_count=1024):
        """
        Args:
            buffer_size: Size of buffer.
            max_count: Maximum number of update before dropping idle keys.
        """
        self.__buffer_size = buffer_size
        self.__max_count = max_count
        self.__data = {}
        """key-data pair"""
        self.__count = {}
        """counter"""
        self.__n = 0
        """always increasing counter"""

    def append(self, key:str, value):
        """Insert key and data to buffer. Return None if number of data points
        is less than BUFFER_SIZE, otherwise return a tuple of data points

        Args:
            key: key
            value: any object
        Returns:
            list(str, tuple(object)): key and a tuple of BUFFER_SIZE of data
        """
        self.__n += 1
        self.__cleanup()

        # new key
        if key not in self.__data.keys():
            self.__data[key] = deque()
            self.__count[key] = 0

        # append data
        self.__data[key].appendleft(value)
        self.__count[key] = self.__n

        # return None or return chunk of data
        if len(self.__data[key]) >= self.__buffer_size:
            value = tuple(self.__data[key].pop() for i in range(0, self.__buffer_size))
            del self.__data[key]
            del self.__count[key]
            return key, value
        else:
            return None, None

    def __cleanup(self):
        """Drop keys that are idle for too long"""
        drop_keys = tuple(
            key for key in self.__data.keys()
            if self.__n - self.__count[key] > self.__max_count
            or self.__n - self.__count[key] < 0
        )

        for key in drop_keys:
            del self.__data[key]
            del self.__count[key]

        # reset counter if it gets too large
        if self.__n > 99999999:
            self.__n = 0
