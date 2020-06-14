import configparser
from collections import deque

from confluent_kafka.cimpl import Consumer

from message import msg_decode


class MsgConsumer:
    def __init__(self, topic, broker_address, group_id='group', client_id='client',
                 auto_offset_reset='earliest',
                 num_messages=1,
                 verbose=False):
        """Consumer for handling EEG Streamer messages.

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
        self.timestamps = deque()

        self.__num_msgs = num_messages
        """Maximum number of messages to consume each time (default: 1)"""

        self.__verbose = verbose

        self.__streamqueue = deque()

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
        chunk_size = self.__num_msgs
        msgs = []
        while chunk_size > 100:
            msgs.extend(self.__consumer.consume(num_messages=100, timeout=1))
            chunk_size -= 100
        msgs.extend(self.__consumer.consume(num_messages=chunk_size, timeout=1))

        print(f"INFO: Received {str(len(msgs))} messages") if self.__verbose else None

        if msgs is None or len(msgs) <= 0:
            return None

        self.__streamqueue.extendleft(msgs)  # Enqueue

        if len(self.__streamqueue) < self.__num_msgs:
            return None

        # Dequeue
        msgs__ = [self.__streamqueue.pop() for i in range(0, self.__num_msgs)]

        timestamps, data = [], []
        for msg in msgs__:
            time, values = msg_decode(msg.value())
            timestamps.append(time) if time is not None else None
            data.append(values) if time is not None else None
        #TODO:// assert there is not big time gap in the data

        if len(data) < self.__num_msgs:
            return None

        print(timestamps[0], data[0]) if self.__verbose else None

        data = tuple(zip(*data))
        self.data.append(data)
        self.timestamps.append(timestamps[0])

        print(f"INFO: Sucessfully Read a chunk") if self.__verbose else None

    def stop(self):
        self.__consumer.close()
        pass

    def drain(self):
        self.__num_msgs = 100000
        for i in range(0, 10):
            self.listen()


if __name__ == '__main__':
    # parse config
    config = configparser.ConfigParser()
    config.read('config.ini')

    mc = MsgConsumer(topic=config['DEFAULT']['INBOUND_TOPIC'],
                     broker_address=config['DEFAULT']['KALFK_BROKER_ADDRESS'],
                     group_id=config['DEFAULT']['GROUP_ID'],
                     client_id=config['DEFAULT']['CLIENT_ID'],
                     verbose=True)
    mc.__num_of_sg = 200
    mc.listen()
    print(mc.data)
    mc.listen()
    print(mc.data)
    mc.stop()

