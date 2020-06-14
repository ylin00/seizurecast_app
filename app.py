import configparser
import time
import streamlit as st
import numpy as np
import pickle
import matplotlib.pyplot as plt

from BeatMaker import BeatMaker
from MsgConsumer import MsgConsumer


class App(BeatMaker):
    def __init__(self, configfile='app_config.ini', verbose=False):
        """

        Args:
            config: path to app_config.ini
            verbose: verbose mode. (default: False)
        """
        self.__status_text = None
        self.__configfile = configfile

        config = configparser.ConfigParser()
        config.read(configfile)
        super().__init__(duration=int(config['DEFAULT']['DURATION']),
                         beat=int(config['DEFAULT']['BEAT']),
                         delay_refresh_intv=0.05,
                         verbose=verbose)

        self.csdata = None
        self.csalert = None

        # plot setting
        self.__plot_width = 4096

        self.__data_width = int(config['DEFAULT']['DATA_WIDTH'])
        """Sampling rate in Hz"""
        self.__data_height = int(config['DEFAULT']['DATA_HEIGHT'])
        """Number of channel"""
        self.__plot_data = []
        """Plot data. (nchannel x fsamp)"""
        self.__plot_t = []
        """Time for plot"""
        self.__lines = []
        self.__st_plot = None

        self.__alert = None

    def setup(self):
        if self.csdata is None or self.csalert is None:
            config = configparser.ConfigParser()
            config.read(self.__configfile)
            self.csdata = MsgConsumer(topic=config['DEFAULT']['DATA_TOPIC'],
                                      broker_address=config['DEFAULT']['KALFK_BROKER_ADDRESS'],
                                      group_id=config['DEFAULT']['GROUP_ID'],
                                      client_id='data_consumer',
                                      num_messages=self.__data_width,
                                      auto_offset_reset='latest',
                                      verbose=True)
            self.csalert= MsgConsumer(topic=config['DEFAULT']['ALERT_TOPIC'],
                                      broker_address=config['DEFAULT']['KALFK_BROKER_ADDRESS'],
                                      group_id=config['DEFAULT']['GROUP_ID'],
                                      client_id='alert_consumer',
                                      num_messages=1,
                                      auto_offset_reset='latest',
                                      verbose=True)

    def _main_(self):
        self.listen()
        self.update()

    def listen(self):
        self.csdata.listen()
        self.csalert.listen()

        tmp = list(zip(*self.__plot_data))
        for i in range(0, len(self.csdata.data)):
            tmp += list(zip(*self.csdata.data.popleft()))
        tmp = tmp[-min(len(tmp), self.__plot_width):]
        self.__plot_data = list(zip(*tmp))

        la = len(self.csalert.data)
        if la > 0:
            alert = [self.csalert.data.popleft() for i in range(len(self.csalert.data))][-1]
            self.__alert = alert[0]

    def update(self):
        self.update_plot()
        self.show_alert()
        pass

    def update_plot(self):

        #Update plot data and time
        for ch in range(0, min(self.__data_height, len(self.__plot_data))):
            ydata = self.__plot_data[ch]
            # scale to 0 and 1
            ydata = (ydata - np.mean(ydata))/(np.max(ydata) - np.min(ydata)) + ch + 1

            # add nan to the head
            n = self.__plot_width - len(ydata)
            ydata = np.concatenate([[np.nan]*n, ydata])

            self.__lines[ch].set_ydata(ydata)

        self.__st_plot.pyplot(plt)

    def show_alert(self):
        """show alarm"""
        if self.__alert is not None and len(self.__alert) > 0 and \
                (self.__alert[0] == 0 or self.__alert[0] == 'pres'):
            self.__status_text.text(
                '!!!!!!SEIZURE IS COMMING in 10~15 minutes!!!!')
        else:
            self.__status_text.text(
            'All good. No seizure in the next 10~15 minutes.')

    def title(self):
        st.title('SeizureCast')
        st.markdown("""
        Real-time forecasting epileptic seizure from electroencephalogram.
        """)

    def box_sampling_rate(self):
        # Sampling rate
        fsamp = st.text_input('Sampling rate (Hz)', value='256')
        try:
            fsamp = int(fsamp)
            if fsamp <= 0:
                raise Exception
        except:
            st.write('Samping rate must be positive integer')
        self.__data_width = fsamp

    def init_plot(self):
        """Initialize plot"""
        x = (np.arange(0, self.__plot_width) - self.__plot_width)/self.__data_width

        fig, ax = plt.subplots()
        ax.set_ylim(0, self.__data_height * 1.2)
        ax.set_xlim(min(x), max(x))
        for ch in range(0, self.__data_height):
            y = [np.nan] * len(x)
            line, = ax.plot(x, y)
            self.__lines.append(line)
        plt.xlabel('time (s)')
        plt.ylabel('channel')
        self.__st_plot = st.pyplot(plt)
        self.__status_text = st.empty()


#
# def plot_eeg(data, fsamp=1):
#     """Make a plot of eeg data
#
#     Args:
#         data: nchannel x nsample
#         fsamp: samping rate. must be integer
#
#     Returns:
#         plot
#
#     """


app = App()
app.setup()
app.title()
app.init_plot()
app.start()

