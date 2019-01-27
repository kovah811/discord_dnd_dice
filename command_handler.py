class CommandHandler:

    def __init__(self, client):
        self.client = client
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def command_handler(self, message):
        for command in self.commands:

            if not message.content.startswith(command['trigger']):
                continue

            args = message.content.split(' ')
            if args[0] != command['trigger']:
                continue

            args.pop(0)

            if command['req_args_num'] == 0:
                return (
                    self.client.send_message(message.channel,
                                             str(command['function']
                                                 (message, self.client,
                                                  args))
                                             )
                )
            elif len(args) >= command['req_args_num']:
                return (
                    self.client.send_message(message.channel,
                                             str(command['function']
                                                 (message, self.client,
                                                  args))
                                             )
                )
            else:
                return (
                    self.client.send_message(message.channel,
                                             'command "{}" requires {} '
                                             'argument(s) "{}"'
                                             .format(command['trigger'],
                                                     command['args_num'],
                                                     ', '.join(
                                                         command['args_name']))
                                             )
                )
