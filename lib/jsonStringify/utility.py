from dateutil import parser
from django.utils import timezone

#decoding
def decodeReceivedText(string):
    return unicode(string).encode('latin-1',errors='ignore')

def decodeDate(string): # javascript date should be date.toISOString()
    now = parser.parse(string)
    return timezone.localtime(now)

def decodeBulletinBoardDate(string):
    return parser.parse(string)

#encoding
def encodeDate(date):
    date.isoformat()

def encodeDateTime(date):
    date.isoformat()

def encodeDecimal(decimal):
    return "%.2f" % decimal
