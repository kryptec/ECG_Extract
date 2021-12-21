import re
from datetime import datetime, timedelta

def mi_finding(report,ref_date):
    """
    Determine if an ecg report has a new finding of MI 
    
    :param report: full text of the ECG report
    :param ref_date: Exclude ECG if it reports no changes compared to an ECG 
                     greater than 1 day before this date (usually admission date)
    :returns: Ture if it should be excluded and False if it should be included
    """
    if exclude_no_change(report,ref_date):
        return False

    body = extract_body(report)
    body = remove_cited_on(body)
    body = remove_age_undetermined(body)
    body = remove_compared_with(body)
    
    if flag_acutemi(body):
        return True
    
    if flag_infarction(body):
        return True
    
    if flag_ischemia(body):
        return True
    
    return False

def exclude_no_change(report,ref_date):
    """
    Exclude ECGs with no change compared to an ECG more than 1 day
    before the reference date (e.g., admission date)
    
    :param report: full text of the ECG report
    :param ref_date: Exclude ECG if it reports no changes compared to an ECG 
                     greater than 1 day before this date (usually admission date)
    :returns: Ture if it should be excluded and False if it should be included
    """
    hits = re.findall('When compared with ECG of (\d{2}-\w{3}-\d{4})((?:.|\n)*)',report)
    if len(hits)>0:
        hits = hits[0]
        if re.search('no significant change',hits[1],flags=re.I):
            extract_date = datetime.strptime(hits[0],'%d-%b-%Y')
            date_dif = ref_date - extract_date
            if date_dif > timedelta(days=1):
                return True
            
    return False
    
def extract_body(report):
    """
    Remove the header and footer material from an ECG report and return the body
    
    :param report: full text of the ECG report
    :returns: The body of the ECG report if extraction successful, False otherwise
    """
    body = re.search('QTc\s*Int\s*:\s*\d+\s*ms((?:.|\n)*)Referred\s*By:',report)
    if body:
        return body[1].strip()
    else:
        return False
    
def remove_cited_on(body):
    """
    Remove all findings from the ECG body that were cited on a previous ECG
    
    :param body: body text of the ECG report
    :returns: The body of the ECG report with cited on portions removed
    """
    body = re.sub('(.*\(cited on or before \d{2}-\w{3}-\d{4}\))','',body)
    return body
    
def remove_age_undetermined(body):
    """
    Remove all findings from the ECG body that are age undetermined
    
    :param body: body text of the ECG report
    :returns: The body of the ECG report with age undetermined portions removed
    """
    body = re.sub('(.*age\s*undetermined)','',body)
    return body
    
def remove_compared_with(body):
    """
    Remove all findings from the end of the ECG body comparing to previous ECGs
    
    :param body: body text of the ECG report
    :returns: The body of the ECG report with compared with portions removed
    """
    body = re.sub('When compared with(.|\n)*','',body)
    return body
    
def flag_acutemi(body):
    """
    Flag the ECG as referencing an Acute MI/STEMI
    
    :param body: cleaned body text (various portions of body have been removed)
    :returns: True if Acute MI/STEMI noted, False otherwise 
    
    Listed STEMI as well as Acute MI since this also covers the STEMI cases
    """
    ami = re.search('\* acute mi',body,flags=re.I)
    if ami:
        return True
    
    return False
    
def flag_infarction(body):
    """
    Remove the header and footer material from an ECG report and return the body
    
    :param body: cleaned body text (various portions of body have been removed)
    :returns: True if infarction is noted, False otherwise
    """
    infarc = re.search('infarc',body,flags=re.I)
    if infarc:
        return True
    
    return False
    
def flag_ischemia(body):
    """
    Remove the header and footer material from an ECG report and return the body
    
    :param body: cleaned body text (various portions of body have been removed)
    :returns: True if ischemia is noted, False otherwise
    """
    ischem = re.search('ischem|ischaem',body,flags=re.I)
    if ischem:
        return True
    
    return False