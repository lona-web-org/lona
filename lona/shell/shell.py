from rlpython import embed


def load_commands(server):
    import_strings = server.settings.CORE_COMMANDS + server.settings.COMMANDS
    commands = []

    for import_string in import_strings:
        commands.append(server.acquire(import_string))

    return commands


def embed_shell(server, **embed_kwargs):
    embed_kwargs['commands'] = load_commands(server)

    embed(**embed_kwargs)


def generate_shell_server(server, **embed_kwargs):
    embed_kwargs['commands'] = load_commands(server)
    embed_kwargs['multi_session'] = True

    return embed(**embed_kwargs)
