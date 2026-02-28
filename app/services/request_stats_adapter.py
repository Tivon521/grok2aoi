"""Request Stats Adapter"""
class RequestStats:
    async def record(self, model, success=True):
        pass
request_stats = RequestStats()
