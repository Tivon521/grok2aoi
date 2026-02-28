"""API Keys Adapter"""
class APIKeyManager:
    def __init__(self):
        self.keys = {}
    def validate_key(self, key):
        return {"key": key}
    async def record_usage(self, key):
        pass
api_key_manager = APIKeyManager()
