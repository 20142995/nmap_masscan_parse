#!/usr/bin/env python

import os
import sys
import xlsxwriter
import xml.etree.ElementTree as etree

def parse_xml(filename):
    try:
        tree = etree.parse(filename)
    except Exception as error:
        print("[-] A an error occurred. The XML may not be well formed. "
              "Please review the error and try again: {}".format(error))
        sys.exit()
    root = tree.getroot()
    host_data = []
    hosts = root.findall('host')
    for host in hosts:
        state =  host.findall('status')[0].attrib['state']
        reason =  host.findall('status')[0].attrib['reason']
        reason_ttl =  host.findall('status')[0].attrib['reason_ttl']
        address = host.findall('address')[0].attrib['addr']
        addrtype = host.findall('address')[0].attrib['addrtype']
        host_data.append([address,addrtype,state,reason,reason_ttl])
    return host_data
 
def main():
    if len(sys.argv) < 2:
        sys.exit("{} 1.xml 2.xml ...".format(sys.argv[0]))
    title = ['address','addrtype','state','reason','reason_ttl']
    workbook = xlsxwriter.Workbook("处理结果.xlsx")
    sheet = workbook.add_worksheet() 
    sheet.activate()  
    sheet.write_row('A1',title)
    ROW = 2
    for filename in sys.argv[1:]:
        for row in parse_xml(filename):
            sheet.write_row('A{}'.format(ROW),row)
            ROW += 1
    workbook.close()
    
if __name__ == "__main__":
    main()

