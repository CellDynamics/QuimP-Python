"""JSON investigator."""
import json
import logging
import argparse
from my_logger import get_logger

logger = get_logger('digson')
logger.setLevel('DEBUG')


class Parser:
    """
    Parse input JSON reading all keys and obtaining their types.

    This class parse JSON file recursivly visiting all keys and building PlantUml scheme.

    Use `Parser.create(qjson, handle)` to get first instance.

    """

    _level = 0  # level of nesting
    _handle = None  # handle of file to write output

    def __init__(self, qjson, instance, rootname):
        """
        Create instance.

        Use `Parser.create(qjson, handle)` to get first instance.

        Args:
            qjson:  a branch of json object (`qjson = json.load(file)`)
            instance: unique number of instance. First must have 0
            rootname: name of the key of qjson branch
        """
        self._root = qjson
        self._keys = self._root.keys()
        self._types = [type(self._root.get(x)) for x in self._keys]
        # descriptive name of the type for UML (can be modified in decode())
        self._desctype = [type(self._root.get(x)).__name__ for x in self._keys]
        self._instance = instance  # count instances, we need to know which is 0 to close uml section
        self._rootname = rootname  # root of json we process now (key)
        Parser._level += 1
        self.decode()
        self._write_block()  # write current block at the end, decode() can modify _desctype

    @classmethod
    def create(cls, qjson, handle):
        """
        Create instance of Parser.

        Args:
            qjson: json object read as: (`qjson = json.load(file)`)
            handle: handle to file where PlantUml script is written. File should be opened with 'w'
        """
        Parser._handle = handle
        Parser._handle.write("@startuml\n")
        cls(qjson, 0, 'root')

    def __del__(self):
        """Add PlantUml tag at the end."""
        if self._instance == 0:
            Parser._handle.write("@enduml\n")

    def decode(self):
        """Process keys from current level recursively."""
        for i, (k, t) in enumerate(zip(self._keys, self._types)):  # along keys for current level
            logger.debug('Key {} type {} level {}'.format(k, t.__name__, Parser._level))
            if t == dict:  # go deeper
                self.parser = Parser(self._root.get(k), self._instance+1, k)  # parse key for current level
                self._write_connection(self._rootname, k, '--')  # connect this instance with that processed one
            elif t == list:  # check what is first list element and then decide
                el, listType, lev = self._unravel(self._root.get(k))  # get type of list elements (all the same assumed)
                self._desctype[i] = 'list{}[{}]'.format(
                    '[]'*(lev-1), listType.__name__)  # modify descriptive type for UML (for class block)
                if listType == dict:  # if it is list of objects
                    self.parser = Parser(el, self._instance+1, k)  # go deeper
                    self._write_connection(self._rootname, k, '..', 'el{}[0]'.format('[]'*(lev-1)))
                else:  # nothing to do here, primitive arrays are marked in class block (_desctype)
                    logger.debug("\t List type {}, lev {}".format(listType.__name__, lev))

    def _unravel(self, data):
        """Find datatype for nested lists (like arrays)."""
        _l = data
        lev = 0
        while type(_l) is list and len(_l) > 0:
            _l = _l[0]
            lev += 1
        if type(_l) is list:  # must be empty then
            return None
        else:
            return _l, type(_l), lev

    def _write_connection(self, source, dest, connection, note=''):
        if not note:
            Parser._handle.write('{} {} {}\n'.format(source, connection, dest))
        else:
            Parser._handle.write('{} {} {}: {}\n'.format(source, connection, dest, note))

    def _write_block(self):
        """Write class block."""
        Parser._handle.write('class {} {{\n'.format(self._rootname))
        for k, t in zip(self._keys, self._desctype):
            Parser._handle.write('\t+{} : {}\n'.format(k, t))
        Parser._handle.write('}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--qconf', required=True, help='QCONF file to analyse')
    parser.add_argument('--out', required=True, help='Output file with UML definition')
    args = parser.parse_args()
    with open(args.qconf) as js:
        qjson = json.load(js)
        with open(args.out, 'w') as out:
            p = Parser.create(qjson, out)
    print('Call ''java -jar plantuml.jar {}'' to get UML plot'.format(args.out))
