import os
from lxutils.log import timer, log, exception
from lxutils import config


def clear_scrapy_result_files():
    files_to_remove = [
        'autoru - trucks.csv',
        'autoru - trailers.csv',
        'comments - auto.ru - results.csv'
    ]
    for f in files_to_remove:
        try:
            os.remove(config['dirs']['data'] + '\\' + f)
            log(f"File '{f}' deleted'")
        except:
            log(f"File '{f}' not found'")


def main():
    with timer("===== Очищаем файлы с результатами скрейпинга ====="):
        clear_scrapy_result_files()
        
    with timer('===== Этап 1 - парсинг ====='):
        import s1_parse_offers

    with timer('===== Этап 2 - оценка ====='):
        import s2_evaluate_offers

    with timer('===== Этап 3 - обработка комментариев ====='):
        import s3_process_comments

    with timer('===== Этап 4 - финальная подготовка ====='):
        import s4_final_preparation

    with timer('===== Этап 5 - загрузка ====='):
        import s5_upload_everything

    log('ALL DONE!!!')

try:
    exit(main())
except Exception:
    exception("Exception in main()")
    exit(1)