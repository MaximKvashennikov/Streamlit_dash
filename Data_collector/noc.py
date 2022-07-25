import pandas as pd
import requests


def get_duty(mr_from_st):
    proxy_url = 'fg-proxy.corp.tele2.ru:8080'
    proxies = {
        'http': proxy_url,
        'https': proxy_url,

    }
    url = 'http://noc.corp.tele2.ru/noc_duty_regions/'
    df = pd.read_html(requests.get(url, proxies=proxies, verify=False).text)[0]

    mr_dict = {'South': 'KRA, ROS, VLG',
               'F-EAST': 'AND, BIR, BRT, IRK, KAM, MGD, SAH, VLD, YAK, KHB',
               'Siberia': 'GRN, BRN, KEM, KHA, KRS, NSK, OMS, TOM, TYV',
               'CBS': 'KUR, BEL, BRY, LIP, MRD, ORL, PNZ, SRV, TAM, VRN',
               'Volga': 'IZH, KAZ, KIR, NIN, SAM, ULN, YOL, CHV',
               'Centre': ['IVN', 'KLG', 'KOS', 'RYZ', 'SMO', 'TUL', 'TVE', 'VLA', 'YRL'],
               'N-W': 'ARH, KLN, MUR, NOV, PSK, PZV, SPB, SPE, SPN, SPS, SPW, VOL, NEN',
               'Moscow': 'MOS, SEA, NEA, CNT, NWS, SWS',
               'Ural': 'CHE, EKT, HAN, KOM, KRG, ORB, PRM, TUM, YNR',
               }
    duty_selected_mr = []
    for mr in mr_from_st:
        duty = [f'{row["Name"]}: {reg}' for i, row in df.iterrows() for reg in row["Region"].split(',') if
                reg in mr_dict[mr]]

        duty_selected_mr.append(duty)
    return duty_selected_mr
