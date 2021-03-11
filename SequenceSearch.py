from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

class search(HighLevelAnalyzer):

    search_for = StringSetting()
    search_in_type = ChoicesSetting(['Ascii', 'Hex', 'Dec'])
    for_spi_test = ChoicesSetting(['MOSI', 'MISO'])

    result_types = {
        'match': {
            'format': 'Match: {{data.char}}'
        },
    }

    def __init__(self):

        self.print_cnt = 0

        self.search_index = 0
        self.match_start_time = None
        self.match_end_time = None

        self.search_len = 0
        self.search_raw = []
        if (self.search_in_type == "Ascii"):
            self.search_len = len(self.search_for)
            for c in self.search_for:
                self.search_raw.append(ord(c))
        else:
            nums = self.search_for.split()
            base = 10
            if (self.search_in_type == "Hex"):
                base = 16
            for n in nums:
                try:
                    self.search_raw.append(int(n,base))
                except:
                    continue
                self.search_len += 1

    def decode(self, frame: AnalyzerFrame):

        if (frame.type != 'data' and frame.type != 'result'):
            return

        try:
            if (frame.type == 'data'):
                ch = frame.data['data'][0]
            elif (frame.type == 'result'):
               if (self.for_spi_test == 'MOSI'):
                   ch = frame.data['mosi'][0]
               else:
                   ch = frame.data['miso'][0]
            else:
                return
        except:
            return

        if self.search_len == 0:
            return

        if ch != self.search_raw[self.search_index]:
            self.search_index = 0
            

        if ch == self.search_raw[self.search_index]:

            frames = []

            if self.search_index == 0:
                self.match_start_time = frame.start_time
            self.search_index = self.search_index + 1
            if self.search_index == self.search_len:
                self.match_end_time = frame.end_time

                char = ''
                for i in range(self.search_len):
                    if (self.search_in_type == "Dec"):
                        char += "%d " % self.search_raw[i]
                    elif (self.search_in_type == "Hex"):
                        char += "0x%02x " % self.search_raw[i]
                    else:
                        char += chr(self.search_raw[i])

                frames.append(AnalyzerFrame(
                    'match', self.match_start_time, self.match_end_time, {
                    'char': char.strip()
                }))
                self.search_index = 0

            return frames
