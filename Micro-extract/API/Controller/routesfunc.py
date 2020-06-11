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
    if not check.contain(cn.private, ["name", "url"])[0]:
        err = check.contain(cn.pr, ["file"])
        if not err[0]:
            return cn.toret.add_error(err[1], err[2])
        cn.pr = err[1]
    cn.pr = check.setnoneopt(cn.pr, ["file", "title", "lang", "restriction", "save", "folder"])
    cn.private = check.setnoneopt(cn.private, ["name", "url"])
    err = ocr.analyse(cn.pr["file"], cn.pr["title"], cn.pr["lang"], cn.pr["restriction"], cn.pr["save"], cn.private["url"], cn.private["name"], cn.pr["folder"])
    return cn.call_next(nextc, err)

def fromb64(cn, nextc):
    err = check.contain(cn.pr, ["base64"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.frombase64(cn.pr["base64"])
    if err[0]:
        cn.private["name"] = err[1]["name"]
        cn.private["url"] = err[1]["url"]
    return cn.call_next(nextc, err)

def mutlifile(cn, nextc):
    err = check.contain(cn.pr, ["files"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.multiplefiles(cn.pr["files"])
    return cn.call_next(nextc, err)

def search(cn, nextc):
    err = check.contain(cn.pr, ["word", "lang"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.search(cn.pr["word"], cn.pr["lang"])
    return cn.call_next(nextc, err)

def gettext(cn, nextc):
    err = check.contain(cn.pr, ["url"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.gettext(cn.pr["url"])
    return cn.call_next(nextc, err)
