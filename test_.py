from update_regions import fetch_slice
from aiohttp.client import ClientSession
from s4_final_preparation import sanity_check
import pytest
from lxutils import timer

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
    

def test_run_stages():
    '''
    with timer('===== Этап 1 - парсинг ====='):
        import s1_parse_offers

    with timer('===== Этап 2 - оценка ====='):
        import s2_evaluate_offers

    with timer('===== Этап 3 - обработка комментариев ====='):
        import s3_process_comments
    '''
    with timer('===== Этап 4 - финальная подготовка ====='):
        import s4_final_preparation
        s4_final_preparation.main()

    with timer('===== Этап 5 - загрузка ====='):
        import s5_upload_everything
