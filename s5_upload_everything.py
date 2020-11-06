from utils import *
from lxutils import *

with timer('Uploading ads to Google Sheets'):
    import upload_stock
with timer('Uploading verification data to Google Firestore'):
    import upload_verification
    upload_verification.main()