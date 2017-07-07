import csv

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def main():

    hosts = dict()

    with open('./host_table.csv', 'r') as f:

        for row in csv.reader(f):

            if row[0] in hosts:

                hosts[row[0]].append({
                    'name': row[1],
                    'address': row[2]
                })

            else:

                hosts[row[0]] = [{
                    'name': row[1],
                    'address': row[2]
                }]

    top = Element('FileZilla3')

    servers = SubElement(top, 'Servers')

    for folder, host_list in hosts.iteritems():
        folder_element = SubElement(servers, 'Folder', expanded="0")
        folder_element.text = folder
        for host in host_list:
            server = SubElement(folder_element, 'Server')
            server.text = host['name']

            element = SubElement(server, 'Host')
            element.text = host['address']

            element = SubElement(server, 'Port')
            element.text = '22'

            element = SubElement(server, 'Protocol')
            element.text = '1'

            element = SubElement(server, 'Type')
            element.text = '0'

            element = SubElement(server, 'User')
            element.text = 'hosting'

            SubElement(server, 'Pass', encoding='base64')

            element = SubElement(server, 'Logontype')
            element.text = '1'

            element = SubElement(server, 'TimezoneOffset')
            element.text = '0'

            element = SubElement(server, 'PasvMode')
            element.text = 'MODE_DEFAULT'

            element = SubElement(server, 'MaximumMultipleConnections')
            element.text = '0'

            element = SubElement(server, 'EncodingType')
            element.text = 'Auto'

            element = SubElement(server, 'BypassProxy')
            element.text = '0'

            element = SubElement(server, 'Name')
            element.text = host['name']

            SubElement(server, 'Comments')

            SubElement(server, 'LocalDir')

            SubElement(server, 'RemoteDir')

            host_element = SubElement(server, 'SyncBrowsing')
            host_element.text = '0'

    with open('./sitemanager.xml', 'wb') as f:
        f.write(prettify(top))

    print prettify(top)

if __name__ == "__main__":
    main()
