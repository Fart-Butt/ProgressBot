import datetime
import json
import logging

log = logging.getLogger('bot.' + __name__)


class ButtStatistics:

    def __init__(self, db):
        self.database = db
        self.dispositions = []
        self.messages = []
        self.disposition_load()
        self.message_load()

    def serialize_all_stats_to_disk(self):
        pass
        self.message_serialize()
        self.disposition_serialize()

    def send_stats_to_db(self):
        self._dispositions_build_insert_query()
        # self._messages_build_insert_query()

    def _dispositions_build_insert_query(self):
        log.debug("inserting dispositions: %s" % str(self.dispositions))
        query = "INSERT into butted_phrases " \
                "(`guild_guid`," \
                "`channel_guid`," \
                "`original_message`," \
                "`contains_stop_phrase`," \
                "`meets_length_requirement`," \
                "`spacy_noun_chunks`," \
                "`spacy_processed_chunks`," \
                "`weights`," \
                "`selected_noun_pair`," \
                "`passes_weight_minimum`," \
                "`butted_sentence`)" \
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.database.do_insertmany(query, self.dispositions)
        self._dispositions_delete_all()

    def _messages_build_insert_query(self):
        data = []
        query = "INSERT into channels (`channel_guid`, `number_of_messages`) VALUES ('%s', %s)" \
                "ON DUPLICATE KEY UPDATE number_of_messages = number_of_messages+%s"
        for i, t in enumerate(self.messages):
            data.append((int(t[0]), t[1], t[1]))
        self.database.do_insertmany(query, data)
        self._messages_delete_all()

    def disposition_store(self, server_guid: int, channel_guid: int, original_message: str, contains_stop_phrase: bool,
                          meets_length_requirement: bool, spacy_noun_chunks: str, spacy_processed_chunks: str,
                          weights: str, selected_noun_pair: str, passes_weight_minimum: bool, butted_sentence: str):
        # bot facing function
        self.dispositions.append(
            (server_guid, channel_guid, original_message, contains_stop_phrase,
             meets_length_requirement, spacy_noun_chunks, spacy_processed_chunks, weights, selected_noun_pair,
             passes_weight_minimum, butted_sentence))

    def message_store(self, channel_guid):
        index = next((index for (index, d) in enumerate(self.messages) if d[0] == channel_guid), None)
        if index is not None:
            self.messages[index][1] += 1
        else:
            # channel id doesnt exist - create it
            self.messages.append([channel_guid, 1])

    def _messages_delete_all(self):
        self.messages = []
        self.message_serialize()

    def _dispositions_delete_all(self):
        self.dispositions = []
        self.disposition_serialize()

    def disposition_serialize(self):
        with open('stat_dispositions.txt', 'w') as f:
            json.dump(self.dispositions, f, ensure_ascii=False, default=str)

    def disposition_load(self):
        try:
            with open('stat_dispositions.txt') as f:
                self.dispositions = json.load(f)
        except FileNotFoundError:
            # nothing special needs to happen here
            pass

    def message_serialize(self):
        with open('stat_messages.txt', 'w') as f:
            json.dump(self.messages, f, ensure_ascii=False, default=str)

    def message_load(self):
        try:
            with open('stat_messages.txt') as f:
                self.messages = json.load(f)
        except FileNotFoundError:
            # nothing special needs to happen here
            pass
