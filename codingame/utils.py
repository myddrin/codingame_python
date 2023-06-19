import pkg_resources


def read_package_resource(package_name: str, resource_filename: str, encoding='utf-8') -> str:
    with pkg_resources.resource_stream(package_name, resource_filename) as f:
        contents = f.read()
    if encoding is not None:
        contents = contents.decode(encoding)
    return contents
