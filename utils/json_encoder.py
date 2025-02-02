import datetime
import decimal
import uuid

from django.core.serializers import json
from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware


class JSONEncoder(json.DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            # override 唯一修改的地方 保留6位小数精度
            # if o.microsecond:
            #     r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID,Promise)):
            return str(o)
        else:
            return super().default(o)


