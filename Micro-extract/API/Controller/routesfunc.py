from Model.basic import check, auth
from Object.ocr import ocr
import json

def getauth(cn, nextc):
    err = check.contain(cn.pr, ["pass"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = auth.gettoken(cn.pr["pass"])
    return cn.call_next(nextc, err)

def myauth(cn, nextc):
    err = check.contain(cn.hd, ["token"], "HEAD")
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.hd = err[1]
    err = auth.verify(cn.hd["token"])
    return cn.call_next(nextc, err)

def download(cn, nextc):
    err = check.contain(cn.pr, ["file"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.download(cn.pr["file"])
    return cn.call_next(nextc, err)

def analyse(cn, nextc):
    err = check.contain(cn.pr, ["file"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.analyse(cn.pr["file"])
    return cn.call_next(nextc, err)

def mutlifile(cn, nextc):
    err = check.contain(cn.pr, ["files"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.multiplefiles(cn.pr["files"])
    return cn.call_next(nextc, err)

def search(cn, nextc):
    err = check.contain(cn.pr, ["word"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.search(cn.pr["word"])
    return cn.call_next(nextc, err)
