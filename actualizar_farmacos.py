import re
# Estandarización de abreviaturas de soluciones a SSN 0,9% / DAD 5% / DAD 10%
_RULES = [
 (re.compile(r'\bSG\s*10\s*%', re.I), 'DAD 10%'),
 (re.compile(r'\bsuero\s+glucosado\s+(?:al\s+)?10\s*%', re.I), 'DAD 10%'),
 (re.compile(r'\bdextrosa\s+(?:en\s+agua\s+(?:destilada|estéril)\s+)?(?:al\s+)?10\s*%', re.I), 'DAD 10%'),
 (re.compile(r'\bDAD\s*10\s*%', re.I), 'DAD 10%'),
 (re.compile(r'\bSG\s*5\s*%', re.I), 'DAD 5%'),
 (re.compile(r'\bsuero\s+glucosado\s+(?:al\s+)?5\s*%', re.I), 'DAD 5%'),
 (re.compile(r'\bdextrosa\s+(?:en\s+agua\s+(?:destilada|estéril)\s+)?(?:al\s+)?5\s*%', re.I), 'DAD 5%'),
 (re.compile(r'\bD5W\b', re.I), 'DAD 5%'),
 (re.compile(r'\bDAD\s*5\s*%', re.I), 'DAD 5%'),
 (re.compile(r'\bSSF\b', re.I), 'SSN 0,9%'),
 (re.compile(r'\bSSN?\s*0[.,]9\s*%', re.I), 'SSN 0,9%'),
 (re.compile(r'\bsoluci[oó]n\s+salina\s+(?:normal\s+)?(?:al\s+)?0[.,]9\s*%', re.I), 'SSN 0,9%'),
 (re.compile(r'\bsuero\s+(?:salino\s+)?fisiol[oó]gico\b', re.I), 'SSN 0,9%'),
]
def standardize(s):
    if not s: return s
    for rx, rep in _RULES:
        s = rx.sub(rep, s)
    return s
