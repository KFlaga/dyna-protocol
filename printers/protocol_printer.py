from . import protocol_types as types
import os.path


class ProtocolPrinter(object):
    def __init__(self, protocol):
        self.protocol = protocol

    def _get_module_content(self, module, imports):
        raise NotImplementedError()

    def _get_module_file_format(self):
        raise NotImplementedError()

    def _print_module_to_stdout(self, module):
        content = self._get_module_content(module)
        print(content)

    def _print_module_to_file(self, module, output_dir):
        file_path = os.path.join(output_dir, self._get_module_file_format().format(module.name))

        content = self._get_module_content(module)
        file = open(file_path, "w")
        file.write(content)

    def print_to_stdout(self):
        for module in self.protocol.modules:
            self._print_module_to_stdout(module)

    def print_to_file(self, output_dir):
        for module in self.protocol.modules:
            self._print_module_to_file(module, output_dir)
