#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import binascii
import re
import sys
import time
import argparse
import xlsxwriter
from xml.etree import ElementTree


def parse_xml(_xml):
    _dict = {}
    with open(_xml,'r',encoding='utf8') as f_xml:
        _xml_str = f_xml.read()
    if not _xml_str.strip():
        return _dict
    try:
        dom = ElementTree.fromstring(_xml_str)
    except Exception as e:
        print(e)
        return _dict
    for dhost in dom.findall('host'):
        host = dhost.find('address').get('addr')
        _dict.setdefault(host,{})
        for dport in dhost.findall('ports/port'):
            proto = dport.get('protocol')
            port = int(dport.get('portid'))
            _dict[host].setdefault(proto,{})
            _dict[host][proto].setdefault(port,{})
            _dict[host][proto][port].update(
                {
                    'state':dport.find('state').get('state'),
                    'reason':dport.find('state').get('reason'),
                    'reason_ttl':dport.find('state').get('reason_ttl'),
                    'reason_ip':dport.find('state').get('reason_ip'),
                })
            for dname in dport.findall('service'):
                _dict[host][proto][port].update(
                    {'service':dname.get('name',''),
                    'servicefp':dname.get('servicefp',''),
                    'product':dname.get('product',''),
                    'version':dname.get('version',''),
                    'extrainfo':dname.get('extrainfo',''),
                    'method':dname.get('method',''),
                    'conf':dname.get('conf',''),
                    'cpe':'\t'.join([dcpe.text for dcpe in dname.findall('cpe')]),
                    'ostype':dname.get('ostype',''),
                    })
            for dscript in dport.findall('script'):
                script_id = dscript.get('id')
                script_out = dscript.get('output')
                _dict[host][proto][port][script_id] = script_out
    return _dict

def parse_result(nmap_dict):
    _list = []
    for ip in nmap_dict:
        for proto in nmap_dict[ip]:
            for port in nmap_dict[ip][proto]:
                _dict ={"ip":ip,"proto":proto,'port':port}
                _dict.update(nmap_dict[ip][proto][port])
                _list.append(_dict)
    return _list

def _decode(_str):
    if isinstance(_str,str):
        try:
            _str = re.sub(r'(\\x[0-9a-fA-F][0-9a-fA-F])+',lambda x:binascii.a2b_hex(x.group().replace('\\x','')).decode('utf8',errors='ignore'),_str)
        except:
            pass
    return _str

def write_xlsx(xlsx_file,scan_result):
    title = []
    for item in scan_result:
        for t in item.keys():
            if t not in title:
                title.append(t)
    workbook = xlsxwriter.Workbook(xlsx_file)
    sheet = workbook.add_worksheet() 
    sheet.activate() 
    sheet.write_row('A1',[t.title() for t in title])
    ROW = 2
    for item in scan_result:
        row = []
        for t in title:
            row.append(_decode(item.get(t,"")))
        sheet.write_row('A{}'.format(ROW),row)
        ROW += 1
    workbook.close()

def main():
    parser = argparse.ArgumentParser(description=u'masscan+nmap')
    parser.add_argument('-i',"--input",dest='xml',help=u'指定xml文件')
    parser.add_argument('-o',"--output",dest='xlsx',help=u'指定xlsx文件')
    args = parser.parse_args()
    if not args.xml or not args.xlsx:
        parser.print_help()
        sys.exit(f"{time.asctime()} need -i")
    else:
        _list = parse_result(parse_xml(args.xml))
        write_xlsx(args.xlsx,_list)
if __name__ == "__main__":
    main()