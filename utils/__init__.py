from datetime import datetime as dt
import time, uuid
    

def timestamp():
    return int(time.time())


def dateback(seconds, ts=timestamp()):
    return dt.fromtimestamp(ts - seconds)


def ascii_printable(s, repl=' '):
    return ''.join([(c if c.isprintable() else repl) for c in [chr(i) for i in s]])


def dict_union(A, B):
    C = {}
    for a in A:
        C[a] = A[a]
    for b in B:
        C[b] = B[b]
    return C
    

def dict_reverse(A):
    B = {}
    for a in A:
        B[A[a]] = a
    return B


def dict_exclude(doc, *exclude):
    return {prop: doc[prop] for prop in doc if prop not in exclude}


def random_token():
    return str(uuid.uuid4())