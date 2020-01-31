#
# dutymanz.py makes the dutyman soap read/update/delete via zeep
#
#
#

import zeep
from zeep import Client
from zeep import xsd

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
import xml.etree.ElementTree as ET
from pprint import pprint

# contains the RosterId and dbPassword
import creds

wsdl = "https://dutyman.biz/api/dutyman.asmx?WSDL"
session = Session()

#  Basic Authentication ( username , password)
# session.auth = HTTPBasicAuth(username, password)
# client = Client(wsdl=wsdl, transport=Transport(session=session))

client = Client(wsdl=wsdl)


def parseElements(elements):
    all_elements = {}
    for name, element in elements:
        all_elements[name] = {}
        all_elements[name]['optional'] = element.is_optional
        if hasattr(element.type, 'elements'):
            all_elements[name]['type'] = parseElements(
                element.type.elements)
        else:
            all_elements[name]['type'] = str(element.type)

    return all_elements


interface = {}
for service in client.wsdl.services.values():
    interface[service.name] = {}
    for port in service.ports.values():
        interface[service.name][port.name] = {}
        operations = {}
        for operation in port.binding._operations.values():
            operations[operation.name] = {}
            operations[operation.name]['input'] = {}
            elements = operation.input.body.type.elements
            operations[operation.name]['input'] = parseElements(elements)
        interface[service.name][port.name]['operations'] = operations


# pprint(interface)


class DutyMan:

    def __init__(self, rosterid, dbpwd):

        self.rosterId = rosterid
        self.dbpswd = dbpwd

    def getMembersWithFields(self, fields, keyType="dbid", testMode=True):

        inDoc = self.inDocValue(fields, keyType, testMode)

        response = client.service.read(inDoc)

        result = self.parseResponse(response)

        # soapEnvelope = self.makeSoapEnvelope('read', self.inDoc)
        # print(response)
        return result

    def updateMember(self, fields, keyType="dbid", testMode=True):

        inDoc = self.inDocValue(fields, keyType, testMode)

        response = client.service.write(inDoc)

        result = self.parseResponse(response)

        return result

    def deleteMember(self, fields, keyType="dbid", testMode=True, swapWanted=True):

        inDoc = self.inDocValue(fields, keyType, testMode, swapWanted)

        response = client.service.delete(inDoc)

        result = self.parseResponse(response)

        return result

    def makeSoapEnvelope(self, soapFunction, inDoc):

        soapEnvelope = "<?xml version='1.0' encoding='utf-8'?>"
        soapEnvelope += "<soap:Enveloper xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xsd='http://www.w3.org/2001/XMLSchema'>"
        soapEnvelope += "<soap:Body>"
        soapEnvelope += "<"+soapFunction+" xmlns='http://www.dutyman.biz/api/'>"
        soapEnvelope += "<inDoc>"
        soapEnvelope += inDoc
        soapEnvelope += "</inDoc>"
        soapEnvelope += "</"+soapFunction+">"
        soapEnvelope += "</soap:Body>"
        soapEnvelope += "</soap:Enveloper>"

        return soapEnvelope

    def inDocValue(self, fields, keyType, test, swap=True):

        if test:
            testMode = "yes"
        else:
            testMode = "no"

        if swap:
            swapWanted = "yes"
        else:
            swapWanted = "no"

        inDoc = "<?xml version='1.0' encoding='utf-8'?>"
        inDoc += "<dutyman rosterid='" + self.rosterId + \
            "' dbpswd='" + self.dbpswd + "' testmode='" + testMode + "'>"
        inDoc += "<members keytype='" + keyType + "' swapwanted='" + swapWanted + "'>"
        inDoc += "<member>"
        inDoc += "<fields>"

        for field in fields:
            inDoc += "<field name='"+field['fieldName'] + \
                "' value='"+field['fieldValue']+"' />"

        inDoc += "</fields>"
        inDoc += "<infos />"
        inDoc += "</member>"
        inDoc += "</members>"
        inDoc += "</dutyman>"

        return inDoc

    def parseResponse(self, response):

        root = ET.fromstring(response)

        for members in root:
            for member in members:
                for content in member:
                    if content.tag == 'fields':
                        for fields in member:
                            for field in fields:
                                if field.tag == "field":
                                    print(field.attrib['name'], "  :  ",
                                          field.attrib['value'])
                    # else:
                        # for messages in member:
                        #     for message in messages:
                        #         print('Result: ', message.attrib['result'])

                        # return message.attrib['result']


def doGetMembersTest(rosterid, dbpswd):

    dutyMan = DutyMan(rosterid, dbpswd)

    fields = []

    member_firstName = {'fieldName': 'First Name',
                        'fieldValue': 'Elton'}
    member_lastName = {'fieldName': 'Last Name',
                       'fieldValue': 'John'}

    fields.append(member_firstName)
    fields.append(member_lastName)

    members = dutyMan.getMembersWithFields(fields, "name", False)

    return members


def doUpdateMemberTest(rosterid, dbpswd):
    dutyMan = DutyMan(rosterid, dbpswd)

    fields = []
    member_firstName = {'fieldName': 'First Name',
                        'fieldValue': 'Elton'}
    member_lastName = {'fieldName': 'Last Name',
                       'fieldValue': 'John'}

    fields.append(member_firstName)
    fields.append(member_lastName)

    members = dutyMan.updateMember(fields, "name", False)


doGetMembersTest(creds.RosterId, creds.dbPassword)

# doUpdateMemberTest(creds.RosterId, creds.dbPassword)
