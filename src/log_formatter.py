import multiprocessing
import threading
import json_log_formatter


class JSONFormatter(json_log_formatter.JSONFormatter):

    def format(self, record):
        message = record.getMessage()
        extra = self.extra_from_record(record)
        json_record = self.json_record(message, extra, record)
        mutated_record = self.mutate_json_record(json_record)
        if 'request' in mutated_record:
            del mutated_record['request']
        # Backwards compatibility: Functions that overwrite this but don't
        # return a new value will return None because they modified the
        # argument passed in.
        if mutated_record is None:
            mutated_record = json_record
        return self.to_json(mutated_record)

    def json_record(self, message, extra, record):
        process = multiprocessing.current_process()
        extra_params = {"severity": record.levelname,
                        "pathname": record.pathname, "lineno": record.lineno}
        extra_params['pid'] = process.pid
        extra_params['thread_id'] = threading.get_ident()

        extra.update(
            extra_params
        )
        res = super().json_record(message, extra, record)

        res['textPayload'] = res['message']
        del res['message']
        if 'exc_info' in res:
            res['error'] = res['exc_info']
            del res['exc_info']
        return res
