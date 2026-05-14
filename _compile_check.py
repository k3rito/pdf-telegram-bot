import py_compile

for path in [
    'bot.py',
    'core/prefix_parser.py',
    'services/extract_service.py',
    'tests/test_command_router.py',
]:
    try:
        py_compile.compile(path, doraise=True)
        print(f'OK {path}')
    except Exception as exc:
        print(f'ERR {path}: {exc}')
        raise
