from time import time, sleep


class BeatMaker:
    def __init__(self, duration=10, beat=1, delay_refresh_intv=1, verbose=True):
        """Running chunk of code in given frequency.

        Args:
            duration: Duration in second. (default: 10)
            beat: Beat in Hz. (default: 1)
            delay_refresh_intv: refresh interval in seconds. (default: 1)
            verbose: verbose or not. (default: False)
        """
        self.__dampening_rate = 0.8
        """from 0~1. Too large value will cause ociliation."""

        self.__verb = verbose

        self.__refresh_intv = delay_refresh_intv
        """refresh interval in seconds."""

        self.__duration = duration
        """Duration in second."""

        self.__beat = beat
        """Beat in Hz."""

    def start(self):
        start_time = time()
        heart_beat = time()
        stream_delay = 0.8 / self.__beat
        stream_count = 0

        nsamp = max(1, int(self.__duration * self.__beat))
        for isamp in range(0, nsamp):
            print(f'Cycle: {isamp}/{nsamp}') if self.__verb else None

            self._main_()

            stream_delay, stream_count, heart_beat = self.__sleep_and_sync(
                stream_delay, stream_count, heart_beat)

            # too long, shut down
            if time() - start_time > self.__duration:
                break

    def _main_(self):
        print(time())
        pass

    def __sleep_and_sync(self, sampling_delay, sampling_count, heart_beat):
        """Sleep and adjust the sampling delay

        Returns: tuple(float, int, float)
            sampling_delay, sampling_count, heart_beat
        """
        # Adhere to sampling frequency
        sleep(sampling_delay)
        sampling_count += 1

        # Adjust the sleeping interval every refresh_delay_interval seconds
        if sampling_count >= (self.__refresh_intv * self.__beat):

            new_heartbeat = time()
            duration = new_heartbeat - heart_beat
            deviation = 1./self.__beat - duration

            try:
                sampling_delay = sampling_delay + deviation * self.__dampening_rate
                if sampling_delay < 0:
                    raise ValueError
            except ValueError:
                sampling_delay = 0
                print("WARNING: NEW DELAY TIME INTERVAL WAS A NEGATIVE NUMBER. Setting to 0..")
            print(f"Deviation: {deviation:.2f} ms, "
                  f"new delay: {sampling_delay * 1000:.2f} ms.") if self.__verb else None
            sampling_count = 0
            heart_beat = new_heartbeat

        return sampling_delay, sampling_count, heart_beat


if __name__ == '__main__':
    bm = BeatMaker()
    bm.__verb = True
    bm.start()
