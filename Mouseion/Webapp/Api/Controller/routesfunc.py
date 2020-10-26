from Model.basic import check, auth
from Object.ocr import ocr, ged, file
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
    err =  ged.download(cn.pr["file"])
    if err[0]:
        cn.private["date"] = err[1]["date"]
    return cn.call_next(nextc, err)

def pdf_analyse(cn, nextc):
    if not check.contain(cn.private, ["name", "url"])[0]:
        err = check.contain(cn.pr, ["file"])
        if not err[0]:
            return cn.toret.add_error(err[1], err[2])
        cn.pr = err[1]

    cn.pr      = check.setnoneopt(cn.pr, ["file", "title", "lang", "restriction", "save", "folder"])
    cn.private = check.setnoneopt(cn.private, ["name", "url", "date"])

    err = ocr.pdf_analyse(
                      cn.pr["file"],
                      cn.pr["title"],
                      cn.pr["lang"],
                      cn.pr["restriction"],
                      cn.pr["save"],
                      cn.private["url"],
                      cn.private["name"],
                      cn.pr["folder"],
                      cn.private["date"]
                      )

    return cn.call_next(nextc, err)

def img_analyse(cn, nextc):
    if not check.contain(cn.private, ["name", "url"])[0]:
        err = check.contain(cn.pr, ["file"])
        if not err[0]:
            return cn.toret.add_error(err[1], err[2])
        cn.pr = err[1]

    cn.pr      = check.setnoneopt(cn.pr, ["file", "title", "lang", "restriction", "save", "folder"])
    cn.private = check.setnoneopt(cn.private, ["name", "url", "date"])

    err = ocr.img_analyse(
                      cn.pr["file"],
                      cn.pr["title"],
                      cn.pr["lang"],
                      cn.pr["restriction"],
                      cn.pr["save"],
                      cn.private["url"],
                      cn.private["name"],
                      cn.pr["folder"],
                      cn.private["date"]
                      )

    return cn.call_next(nextc, err)

def file_analyse(cn, nextc):
    if not check.contain(cn.private, ["name", "url"])[0]:
        err = check.contain(cn.pr, ["file"])
        if not err[0]:
            return cn.toret.add_error(err[1], err[2])
        cn.pr = err[1]

    cn.pr      = check.setnoneopt(cn.pr, ["file", "title", "lang", "restriction", "save", "folder"])
    cn.private = check.setnoneopt(cn.private, ["name", "url", "date"])

    err = ocr.file_analyse(
                      cn.pr["file"],
                      cn.pr["title"],
                      cn.pr["lang"],
                      cn.pr["restriction"],
                      False,
                      cn.private["url"],
                      cn.private["name"],
                      cn.pr["folder"],
                      cn.private["date"]
                      )

    return cn.call_next(nextc, err)


def pdf_fromb64(cn, nextc):
    err = check.contain(cn.pr, ["base64"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ocr.frombase64(cn.pr["base64"], "pdf")
    if err[0]:
        cn.private["name"] = err[1]["name"]
        cn.private["url"] = err[1]["url"]
    return cn.call_next(nextc, err)

def pdf_mutlifile(cn, nextc):
    err = check.contain(cn.pr, ["files"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    err = ged.multiplefiles(cn.pr["files"])
    return cn.call_next(nextc, err)

def search(cn, nextc):
    err = check.contain(cn.get, ["search"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.get = check.setnoneopt(cn.get, ["search", "type", "datef", "datet", "page", "size"])
    cn.rt =  check.setnoneopt(cn.rt, ["search"])
    err = file.search(
                     word=cn.get["search"],
                     lang=cn.rt["search"] if cn.rt["search"] is not None else cn.get['type'],
                     type=cn.get["type"],
                     date_from=cn.get["datef"],
                     date_to=cn.get["datet"],
                     page=cn.get["page"],
                     size=cn.get["size"]
                     )
    return cn.call_next(nextc, err)

def gettext(cn, nextc):
    err = check.contain(cn.pr, ["url"])
    if not err[0]:
        return cn.toret.add_error(err[1], err[2])
    cn.pr = err[1]
    cn.pr = check.setnoneopt(cn.pr, ["url", "date"])
    err = file.gettext(cn.pr["url"], cn.pr["date"])
    return cn.call_next(nextc, err)
