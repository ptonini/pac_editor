import uuid
import collections
import copy
import fileinput
import csv

from yaml.representer import Representer
from ruamel import yaml

import pprint

pp = pprint.PrettyPrinter(indent=4)
yaml.add_representer(collections.defaultdict, Representer.represent_dict)


class PacConfigEditor:

    def __init__(self, yaml_file):

        with open(yaml_file, 'r') as f:
            self.doc = yaml.load(f.read(), yaml.RoundTripLoader)

    def get_node_by_id(self, node_id):

        return self.doc['environments'][node_id]

    def get_nodes_by_name(self, name):

        return [k for k, n in self.doc['environments'].iteritems() if 'name' in n and n['name'] == name]

    def get_parents(self, node_id):

        parent_list = list()

        current_node = self.doc['environments'][node_id]

        while 'parent' in current_node and current_node['parent'] != '__PAC__ROOT__':
            parent_id = current_node['parent']
            parent_list.append(parent_id)
            current_node = self.doc['environments'][parent_id]

        return parent_list

    def get_node_children_by_name(self, name):

        children_list = list()

        for parent_id in self.get_nodes_by_name(name):
            for node_id, node in self.doc['environments'].iteritems():
                if parent_id in self.get_parents(node_id) and node['_is_group'] == 0:
                    children_list.append(node_id)

        return children_list

    def update_node_children(self, parent, options):

        for node_id in self.get_node_children_by_name(parent):

            print 'editing node', self.doc['environments'][node_id]['name']

            for key, value in options.iteritems():
                self.doc['environments'][node_id][key] = value

    def clone_node(self, source_node_name, options):

        source_node = self.get_node_by_id(self.get_nodes_by_name(source_node_name)[0])

        new_node_id = str(uuid.uuid4())

        self.doc['environments'][new_node_id] = copy.deepcopy(source_node)

        self.doc['environments'][source_node['parent']]['children'][new_node_id] = 1

        for key, value in options.iteritems():
            self.doc['environments'][new_node_id][key] = value

    def bulk_clone(self, source_node_name, csv_file, options):

        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            host_list = list(reader)

        for line in host_list:

            host_options = copy.copy(options)
            host_options['name'] = line[0]
            host_options['title'] = line[0]
            host_options['ip'] = line[1]

            if len(self.get_nodes_by_name(line[0])) == 0:

                self.clone_node(source_node_name, host_options)

    def dump_yaml(self, yaml_file):

        corrections = [
            ['^.+ontinue connecting \((.+)\/(.+)\)\?\s*$', "'^.+ontinue connecting \((.+)\/(.+)\)\?\s*$'"]
        ]

        stream = file(yaml_file, 'w')

        yaml.dump(self.doc, stream, explicit_start=True, Dumper=yaml.RoundTripDumper, width=9999)

        for line in fileinput.input(yaml_file, inplace=True):
            for c in corrections:
                line = line.rstrip().replace(c[0], c[1])
            print line


def main():

    pac_config = PacConfigEditor('./pac.yml')

    default_options = {
        'auth type': 'publickey',
        'user': '',
        'pass': '',
        #'public key': '/home/ptonini/.ssh/m2m-hosting',
        'public key': '/opt/ssh_keys/m2m-hosting',
        'passphrase user': 'hosting',
        'passphrase': '',
        'auth fallback': 0,
        'KPX title regexp': '',
        'options': '',
        'description': ''
    }

    if False:

        groups = ['SSO', 'Zona 4', 'Zona 5', 'Zona D', 'Zona H']

        for group in groups:
            pac_config.update_node_children(group, default_options)

    if True:

        pac_config.bulk_clone('temp1', './sso.csv', default_options)
        pac_config.bulk_clone('temp2', './zn4.csv', default_options)
        pac_config.bulk_clone('temp3', './zn5.csv', default_options)
        pac_config.bulk_clone('temp4', './znh.csv', default_options)
        pac_config.bulk_clone('temp5', './znd.csv', default_options)

    pac_config.dump_yaml('./pac_new.yml')


if __name__ == "__main__":
    main()

