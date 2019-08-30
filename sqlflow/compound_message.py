from sqlflow.rows import Rows

class CompoundMessage:
    def __init__(self):
        """Message containing return result of several SQL statements
           CompoundMessage can not display in notebook since we need to
           output log messages for long running training sqls.
        """
        self._messages = []
        self.TypeRows = 1
        self.TypeMessage = 2
        self.TypeHTML = 3
    
    def add_rows(self, rows, eoe):
        assert(isinstance(rows, Rows))
        self._messages.append((rows, eoe, self.TypeRows))
    
    def add_message(self, message, eoe):
        assert(isinstance(message, str))
        self._messages.append((message, eoe, self.TypeMessage))
    
    def add_html(self, message, eoe):
        assert(isinstance(message, str))
        self._messages.append((message, eoe, self.TypeHTML))
    
    def length(self):
        return len(self._messages)

    def get(self, idx):
        return self._messages[idx][0]

