import time
import re

_PERIODS = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 24 * 60 * 60,
        }
rate_re = re.compile(r'([\d]+)/([\d]*)([smhd])?')

def _split_rate(rate):
        if isinstance(rate, tuple):
            return rate
        count, multi, period = rate_re.match(rate).groups()
        count = int(count)
        if not period:
            period = 's'
        seconds = _PERIODS[period.lower()]
        if multi:
            seconds = seconds * int(multi)
        return count, seconds
        
class TokenBucket:
    
    def __init__(self, rate):
        self.capacity, self.fill_rate = _split_rate(rate)
        self.tokens = self.capacity
        self.last_update = time.time()
    
    def consume(self, tokens):
        if tokens <= self.tokens:
            self.tokens -= tokens
            return True
        else:
            return False

    def update(self):
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * self.fill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now

    

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.token_bucket = TokenBucket(capacity=10, fill_rate=1)

    def __call__(self, request):
        if not self.token_bucket.consume(1):
            return HttpResponse('Rate limit exceeded', status=429)
        self.token_bucket.update()
        response = self.get_response(request)
        return response
