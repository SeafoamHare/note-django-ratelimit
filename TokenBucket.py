import time

class TokenBucket:
    
    def __init__(self, capacity, fill_rate):
        self.capacity = float(capacity)
        self.tokens = self.capacity
        self.fill_rate = fill_rate
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
