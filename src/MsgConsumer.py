import configparser
from collections import deque

from confluent_kafka.cimpl import Consumer

from src.MagicBuffer import MagicBuffer
from src.message import msg_decode


class MsgConsumer:
    def __init__(self, topic, broker_address,
                 group_id='group', client_id='client',
                 auto_offset_reset='earliest',
                 num_messages=1,
                 data_width=1,
                 verbose=False):
        """Consumer for handling EEG Streamer messages.

        Consume NUM_MESSAGES at a time, and convert to a queue of data of shape
        (height, DATA_WIDTH).

        Args:
            topic: Topic to subscribe to
            broker_address: Broker address
            group_id: group ID
            client_id: client ID
            auto_offset_reset: (default: 'earliest')
            num_messages: Maximum number of messages to consume each time (default: 1)
            verbose: verbose mode. (default: False)
        """

        self.data   = deque()
        """Queue to store received and decoded data"""

        self.timestamps = deque()
        """Queue of timestamps"""

        self.key = deque()
        """Queue of data keys"""

        self.__data_width = data_width
        self.__n_msgs = num_messages
        """Maximum number of messages to consume each time (default: 1)"""

        self.__verbose = verbose

        self.__msg_buffer = MagicBuffer(
            buffer_size=self.__data_width, max_count=int(4 * self.__data_width)
        )

        self.__consumer = Consumer({
                'bootstrap.servers': broker_address,
                'auto.offset.reset': auto_offset_reset,
                'group.id': group_id,
                'client.id': client_id,
                'enable.auto.commit': True,
                'session.timeout.ms': 6000,
                'max.poll.interval.ms': 10000
        })
        """consumer that reads stream of EEG signal"""
        self.__consumer.subscribe([topic])

    def listen(self):
        """read stream from Kafka and append to streamqueue

        Returns:
            list of list: dataset (nchannel x nsample) or None
        """
        # If chunk size is too large, consume it multiple epochs
        chunk_size = self.__n_msgs
        msgs = []
        while chunk_size > 100:
            msgs.extend(self.__consumer.consume(num_messages=100, timeout=1))
            chunk_size -= 100
        msgs.extend(self.__consumer.consume(num_messages=chunk_size, timeout=1))

        print(f"INFO: Received {str(len(msgs))} messages") if self.__verbose else None

        if msgs is None or len(msgs) <= 0:
            return None

        for msg in msgs:
            # MagicBuffer will keep the key-value pair and returns values of the
            # same key as a tuple of size data_width
            key, msg_chunk = self.__msg_buffer.append(
                key=msg.key().decode('utf-8'), value=msg.value()
            )

            # Sanity check
            if msg_chunk is None:
                continue

            print(f"Received msg key = {key}") if self.__verbose else None

            # Decode the msg values.
            timestamps, data = [], []
            for value in msg_chunk:
                t, v = msg_decode(value)
                timestamps.append(t) if t is not None else None
                data.append(v) if t is not None else None

            # Sanity check
            if len(data) < self.__data_width:
                continue

            print("Decoded msg = \t", timestamps[0], data[0]) if self.__verbose else None

            data = tuple(zip(*data))
            self.data.append(data)
            self.timestamps.append(timestamps[0])
            self.key.append(key)

            print(f"INFO: Sucessfully Read a chunk") if self.__verbose else None

    def stop(self):
        self.__consumer.close()
        pass

    def drain(self):
        self.__n_msgs = 100000
        for i in range(0, 10):
            self.listen()


if __name__ == '__main__':
    import numpy
    # parse config
    config = configparser.ConfigParser()
    config.read('./app_config.ini')

    mc = MsgConsumer(topic=config['DEFAULT']['data_topic'],
                     broker_address=config['DEFAULT']['KALFK_BROKER_ADDRESS'],
                     group_id=config['DEFAULT']['GROUP_ID']+'4',
                     auto_offset_reset='latest',
                     num_messages=512,
                     data_width=256,
                     verbose=True)
    mc.listen()
    mc.listen()
    mc.listen()
    print(f"length of data = {len(mc.data)}")
    [print(f"key = {mc.key.pop()} shape of data = {numpy.shape(mc.data.pop())}") for i in range(0, len(mc.data))]
    mc.stop()
