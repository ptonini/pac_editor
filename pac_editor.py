from ruamel import yaml
import uuid
import collections
from yaml.representer import Representer


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

        # for source_node_id in self.get_nodes_by_name(source_node_name)[0]:

            source_node = self.get_node_by_id(self.get_nodes_by_name(source_node_name)[0])

            new_node_id = str(uuid.uuid4())

            print new_node_id

            # print source_node

            self.doc['environments'][new_node_id] = dict()

            for key, value in source_node.iteritems():

                if isinstance(value, yaml.comments.CommentedSeq):

                    print key, value

                    self.doc['environments'][new_node_id][key] = yaml.comments.CommentedSeq()

                    for v1 in value:
                        self.doc['environments'][new_node_id][key].append(v1)

                if isinstance(value, yaml.comments.CommentedMap):

                    self.doc['environments'][new_node_id][key] = yaml.comments.CommentedMap()

                    for k1, v1 in value.iteritems():
                        self.doc['environments'][new_node_id][key][k1] = v1

                else:
                    self.doc['environments'][new_node_id][key] = value

            for key, value in options.iteritems():
                self.doc['environments'][new_node_id][key] = value

    def dump_yaml(self, yaml_file):

        stream = file(yaml_file, 'w')

        yaml.dump(self.doc, stream, explicit_start=True, Dumper=yaml.RoundTripDumper, width=9999)


def main():

    pac_config = PacConfigEditor('./pac.yml')

    if False:

        options = {
            'user': 'hosting',
            'KPX title regexp': '',
            'description': '',
            'pass': '',
            'passphrase': '',
            'passphrase user': '',
            'auth type': 'userpass',
            'public key': '',
            'auth fallback': 1,
            'options': ''
        }

        groups = ['SSO', 'Zona 4', 'Zona 5']

        for group in groups:
            pac_config.update_node_children(group, options)

    if True:

        options = {
            'name': '00_test',
            'title': '00test'
        }

        pac_config.clone_node('zn4-api0', options)

    pac_config.dump_yaml('/home/ptonini/.config/pac/pac.yml')




if __name__ == "__main__":
    main()

