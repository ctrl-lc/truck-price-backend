from lxutils.log import timer, log, exception

def main():
    with timer('===== Этап 1 - парсинг ====='):
        import parse_offers
    with timer('===== Этап 2 - оценка ====='):
        import evaluate_offers
    with timer('===== Этап 3 - обработка комментариев ====='):
        import process_comments
    with timer('===== Этап 4 - финальная подготовка ====='):
        import final_preparation

try:
    exit(main())
except Exception:
    exception("Exception in main()")
    exit(1)