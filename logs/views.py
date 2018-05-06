import os
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@require_POST
@csrf_exempt
def read_log(request):
    try:
        offset = int(json.loads(request.body)['offset'])
    except KeyError:
        return JsonResponse({'ok': False, 'reason': 'offset parameter is missing'})
    except ValueError:
        return JsonResponse({'ok': False, 'reason': 'incorrect offset value or json format'})

    correct_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR']
    step = 3
    logs = []
    try:
        with open(settings.LOG_JSON, 'r') as f:
            for log_line in f:
                log_line = json.loads(log_line)
                if len(log_line.keys()) != 2 or 'message' not in log_line.keys() \
                   or 'level' not in log_line.keys() or log_line['level'] not in correct_levels:
                    return JsonResponse({'ok': False, 'reason': 'incorrect log format'})
                logs.append(log_line)
    except IOError:
        return JsonResponse({'ok': False, 'reason': 'file not found'})
    except ValueError:
        return JsonResponse({'ok': False, 'reason': 'incorrect json format'})
    except Exception:
        return JsonResponse({'ok': False, 'reason': 'incorrect file'})

    total_size = len(logs)
    if offset < 0:
        return JsonResponse({'ok': False, 'reason': 'offset value is less than zero'})
    elif offset > total_size:
        return JsonResponse({'ok': False, 'reason': 'offset value exceeds the log size'})
    next_offset = min(offset + step, total_size)
    messages = logs[offset:next_offset]

    return JsonResponse({'ok': True, 'total_size': total_size, 'next_offset': next_offset, 'messages': messages})
