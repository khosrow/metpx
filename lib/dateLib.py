"""
#############################################################################################
# Name: dateLib.py
#
# Author: Daniel Lemay
#
# Date: 2005-09-15
#
# Description:
#
#############################################################################################
"""
import time

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

now = time.mktime

def getISODateParts(date):
    # year, month, day
    return (date[0:4], date[4:6], date[6:])

def getMonthAbbrev(month):
    return MONTHS[int(month) -1]

def getSecondsSinceEpoch(date='08/30/05 20:06:59'):
    try:
        timeStruct = time.strptime(date, '%m/%d/%y %H:%M:%S')
    except:
        print date
    return time.mktime(timeStruct)
    
def getYesterdayInSeconds():
    return now(time.gmtime())  - DAY

def getYesterdayFormatted(format='%m/%d/%y'):
    return time.strftime(format, time.gmtime(getYesterdayInSeconds()))

def getISODate(string, dash=True):
        # Format of string is : MM/DD/YY
        month, day, year = string.split('/')
        year = 2000 + int(year)
        if dash: return (str(year) + '-' + month + '-' + day)
        else: return (str(year) + month + day)
        # In python 2.3 and later
        #return datetime.date(year, month, day).isoformat()

def ISOToBad(ISODate, dash=False):
    if dash:
        raise 'Not implemented'
    else:
        year = ISODate[2:4]
        month = ISODate[4:6]
        day = ISODate[6:8]
        return  '%s/%s/%s' % (month, day, year)

def getSeconds(string):
    # Should be used with string of following format: hh:mm:ss
    hours, minutes, seconds = string.split(':')
    return int(hours) * HOUR + int(minutes) * MINUTE + int(seconds)

def getSeparators(width=DAY, interval=20*MINUTE):
    separators = []
    for value in range(interval, width+interval, interval):
        separators.append(value)
    
    return separators

def getEmptyBuckets(separators=getSeparators()):
    buckets = {}
    buckets[0] = [0, separators[0], 0, 0.0] # min, max, count, total_lat

    for i in range(1, len(separators)):
        buckets[i] = [separators[i-1], separators[i], 0, 0.0]    
    return buckets

if __name__ == '__main__':

    """
    getSecondsSinceEpoch('09/01/05 21:53:15')
    print now(time.gmtime())
    print getYesterdayInSeconds()
    print getYesterdayFormatted()
    print getSeconds('08:07:04')
    print getSeparators()
    print len(getSeparators())
    print len(getEmptyBuckets())
    print ISOToBad('20050830') 
    print ISOToBad('20050830', True) 
    print getISODateParts('20050908')
    print getMonthAbbrev('12')
    """
    from bisect import bisect
    sep = getSeparators(DAY, 60)
    insert_point = bisect(sep, 179)
    print insert_point
