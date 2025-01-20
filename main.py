#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import requests
import math
import random
import urllib3
import urllib
import argparse
import os

from ratelimit import limits, sleep_and_retry


@sleep_and_retry
@limits(calls=2, period=4)
def do_get_data(url, useCors=False, sleepBefore=0.5):
    if sleepBefore > 0:
        time.sleep(0.5)
    if useCors:
        origin = 'https://oss.uredjenazemlja.hr'
        secFetchSite = 'cross-site'
    else:
        origin = None
        secFetchSite = 'same-origin'
    r = requests.get(url, headers=
    {
        "connection": "keep-alive",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "accept": 'application/json, text/plain, */*',
        "sec-ch-ua-mobile": '?0',
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        "origin": origin,
        "sec-fetch-site": secFetchSite,
        "sec-fetch-mode": 'cors',
        "sec-fetch-dest": 'empty',
        "referer": 'https://www.katastar.hr/',
        "accept-language": 'hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7,ru-RU;q=0.6,ru;q=0.5,bs;q=0.4,it;q=0.3,fr;q=0.2',
        # "cookie": '_ga=GA1.2.868565600.1623147427; _gid=GA1.2.873534028.1623147427; cookieconsent_status=dismiss; cookieHistData=6592906%23cestica%235267%2C%20335045%2C%20SOLINE%23335045%2C5267%3B6592907%23cestica%235268%2C%20335045%2C%20SOLINE%23335045%2C5268%3B',
    }, verify=False)
    return r.json()


def get_data(url, f, useCors):
    data = do_get_data(url, useCors)
    retry = 10
    while type(data) is not list and retry > 0:
        retry = retry - 1
        time.sleep(2.)
        data = do_get_data(url, useCors)
    if type(data) is not list:
        raise RuntimeError(str(data))
    return list(filter(f, data))


def search_puk(naziv):
    return get_data("https://oss.uredjenazemlja.hr/oss/public/search-cad-parcels/offices",
                    lambda obj: naziv in obj.get('name'), False)


def search_odjel(puk, naziv):
    return get_data(
        f"https://oss.uredjenazemlja.hr/oss/public/search-cad-parcels/municipalities?search={urllib.parse.quote(naziv)}&officeId={puk}",
        lambda obj: naziv in obj.get('value1'), False)


def search_ko(puk, odjel, naziv):
    return get_data(
        f"https://oss.uredjenazemlja.hr/oss/public/search-cad-parcels/municipalities?search={urllib.parse.quote(naziv)}&officeId={puk}&departmentId={odjel}",
        lambda obj: naziv in obj.get('value1'), False)


def search_cestica(ko, cestica):
    return get_data(
        f"https://oss.uredjenazemlja.hr/oss/public/search-cad-parcels/parcel-numbers?search={cestica}&municipalityRegNum={ko}",
        lambda obj: f"{cestica}" == obj.get('value1') or obj.get('value1').startswith(f"{cestica}/"), False)


def fetch_parcel_details_url(number):
    id = runbase()
    status = create(str(id), number)
    return "https://oss.uredjenazemlja.hr/rest/katHr/parcelDetails?id=" + str(id) + "&status=" + str(status)


def fetch_parcel_details(id):
    return get_data(
        f"https://oss.uredjenazemlja.hr/oss/public/cad/search-parcels?parcelId={id}",
        lambda obj: True, False)


def runbase():
    return int(math.floor(1e7 * random.random()))


def create(t, e):
    n = 0
    for i in range(len(t)):
        n = (n << 5) - n + ord(t[i])
        n &= n
        if n > 4294967295:
            n = (n % 4294967295) - 4294967295
    if not e:
        e = t
    return str(abs(n))[0:6] + str(int(e) << 1)


def log(line, append):
    mode = "w"
    if append:
        mode = "a"
    with open("cestice.csv", mode, encoding='utf-8') as f:
        f.write(line + "\n")
    print(line)


def last_non_empty_line(filename):
    with open(filename, 'rb') as file:
        # Move to the end of the file
        file.seek(0, 2)
        position = file.tell()
        line = ''

        while position >= 0:
            file.seek(position)
            bytes = file.read(4)

            lines = line.rstrip().splitlines()
            if len(lines) > 1:
                line = lines[-1]
                break

            line = bytes.decode("utf-8") + line
            position -= 4

        # In case the file ends without a newline
        return line.strip() if line.strip() else None


def fix(s, d=" "):
    if s:
        return s.upper().replace(",", ";")
    else:
        return d


def safe_int(s):
    try:
        return int(s)
    except ValueError:
        return 0


def dump_katastar(ko, cesticaNum, cesticaMax):
    if os.path.exists('cestice.csv'):
        lastLine = last_non_empty_line('cestice.csv')
        if lastLine:
            c = lastLine.split(",")[0]
            if c:
                c = c.split("/")[0]
                if c:
                    i = safe_int(c)
                    if i > cesticaNum:
                        cesticaNum = i
    else:
        log("čestica,adresa,površina,udio,ime vlasnika,adresa vlasnika,OIB vlasnika", False)
    while cesticaMax > cesticaNum:
        cesticaNum = cesticaNum + 1
        cesticas = search_cestica(ko, cesticaNum)
        if not cesticas or len(cesticas) == 0:
            print(f"Skipping {cesticaNum}")
            continue
        for cestica in cesticas:
            parcel_details = fetch_parcel_details(int(cestica["key1"]))
            for parcel_detail in parcel_details:
                for parcel_share in parcel_detail["lrUnit"]["ownershipSheetB"]["lrUnitShares"]:
                    for share_owner in parcel_share["lrOwners"]:
                        line = ','.join(
                            (parcel_detail["parcelNumber"],
                             fix(parcel_detail["address"]),
                             parcel_detail["area"],
                             parcel_share["share"],
                             fix(share_owner["name"]),
                             fix(share_owner.get("address")),
                             fix(share_owner.get("taxNumber"))
                             )
                        )
                        log(line, True)


urllib3.disable_warnings()
# reload(sys)
# sys.setdefaultencoding('utf-8')


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--puk', required=True, type=str, help='PUK - područni ured za katastar (npr. --puk=ZADAR)')
parser.add_argument('--odjel', required=True, type=str, help='Odjel (npr. --odjel=ZADAR)')
parser.add_argument('--ko', required=True, type=str, help='Katastarska općina (npr. --ko="VELI RAT")')
parser.add_argument('--max', default=10000, type=int, help='Max čestica (default 10000)')
parser.add_argument('--min', default=1, type=int, help='Min čestica (default 1)')

args = parser.parse_args()

pukName = args.puk
odjelName = args.odjel
koName = args.ko
cesticaMax = args.max
cesticaNum = args.min - 1

puks = search_puk(pukName)
if not puks or len(puks) == 0:
    raise RuntimeError("PUK nije pronađen za naziv: " + pukName)
puk = puks[0]["id"]

odjels = search_odjel(puk, odjelName)
if not odjels or len(odjels) == 0:
    raise RuntimeError("ODJEL nije pronađen za naziv: " + odjelName)
odjel = odjels[0]["value3"]

kos = search_ko(puk, odjel, koName)
if not kos or len(kos) == 0:
    raise RuntimeError("KO nije pronađena za naziv: " + koName)
ko = kos[0]["key2"]

dump_katastar(ko, cesticaNum, cesticaMax)
