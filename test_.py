from update_regions import fetch_slice
from aiohttp.client import ClientSession
from s4_final_preparation import sanity_check
import pytest

def test_sanity_check():
    sanity_check()


@pytest.mark.asyncio    
async def test_update_regions_403_response(monkeypatch):
    
    class MockRequest():
        async def __aenter__(*args):
            return MockResponse()
        async def __await__(*args):
            pass
        async def __aexit__(*args):
            pass

        
    class MockResponse():
        status = 403
        
        
    session = ClientSession()
    monkeypatch.setattr(session, 'request', lambda *args, **kwargs: MockRequest())
    
    assert await fetch_slice('Москва', session) is None
    