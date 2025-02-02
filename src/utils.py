from src.evento import ARGUMENT_TYPES
import unidecode
import asyncio

async def simple_cmp(a, b):
    a_sub = unidecode.unidecode(a).lower()
    b_sub = unidecode.unidecode(b).lower()
    return a_sub == b_sub


async def parse(*args, optional_fields, required_fields):
    opt_fields = [('-' + ARGUMENT_TYPES[k].alias, '--' + ARGUMENT_TYPES[k].name) for k in optional_fields]
    req_fields = [('-' + ARGUMENT_TYPES[k].alias, '--' + ARGUMENT_TYPES[k].name) for k in required_fields]

    all_fields = opt_fields + req_fields

    alias_prefix, name_prefix = '-', '--'
    arg_names = [item for item in args if alias_prefix == item[0]]

    for field in all_fields:
        alias, name = field
        if alias not in arg_names and name not in arg_names:
            if field in req_fields:
                return False, '**Error**: El argumento **{}** es requerido, pero falta en el comando.'.format(name)

    for item in arg_names:
        if item not in [item for field in all_fields for item in field]:
            return False, '**Error**: El argumento **{}** no esta permitido para este comando.'.format(item)

    parsed_dict = dict()

    for key, item in ARGUMENT_TYPES.items():
        arg_alias = alias_prefix + item.alias
        arg_name = name_prefix + item.name
        value = None

        if arg_alias in args and arg_name in args:
            return False, '**Error**: Argumentos **{}** y **{}** están repetidos.'.format(arg_alias, arg_name)
        elif arg_alias in args:
            if args.count(arg_alias) > 1:
                return False, '**Error**: Argumento **{}** aparece por duplicado.'.format(arg_alias)
            idx = args.index(arg_alias)
        elif arg_name in args:
            if args.count(arg_name) > 1:
                return False, '**Error**: Argumento **{}** aparece por duplicado.'.format(arg_name)
            idx = args.index(arg_name)

        if arg_alias in args or arg_name in args:
            if idx >= len(args) - 1:
                return False, '**Error**: Falta un valor para el argumento {}'.format(args[idx])
            elif args[idx + 1][0] == alias_prefix:
                return False, '**Error**: Falta un valor para el argumento {}'.format(args[idx])

            value_list = []
            idx += 1

            while idx < len(args) and args[idx][0] != alias_prefix:
                value_list.append(args[idx])
                idx += 1

            value = ' '.join(value_list)

        parsed_dict[key] = value

    return True, parsed_dict
