from lxutils.log import timer, log, exception


def main():
        
    with timer('===== Этап 1 - парсинг ====='):
        import s1_parse_offers

    with timer('===== Этап 2 - оценка ====='):
        import s2_evaluate_offers

    with timer('===== Этап 3 - обработка комментариев ====='):
        import s3_process_comments

    with timer('===== Этап 4 - финальная подготовка ====='):
        import s4_final_preparation
        s4_final_preparation.main()

    with timer('===== Этап 5 - загрузка ====='):
        import s5_upload_everything

    log('ALL DONE!!!')

try:
    exit(main())
except Exception:
    exception("Exception in main()")
    exit(1)