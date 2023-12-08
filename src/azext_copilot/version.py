import os
import toml


def get_version():
    return get_version_from_toml_file()


def get_version_from_toml_file(
    pyproject_path=os.path.join(
        os.path.dirname(__file__), '..', '..', 'pyproject.toml'
    )
):
    version = (0, 0, 0)

    try:
        with open(pyproject_path, 'r') as file:
            pyproject_data = toml.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The pyproject.toml file was not found at {pyproject_path}"
        )

    # Access the version information from the parsed data
    if pyproject_data:
        version_info = pyproject_data.get('tool', {}).get('poetry', {}).get(
            'version', '0.0.0')
        try:
            version = tuple(map(int, version_info.split('.')))
        except ValueError:
            raise ValueError(
                f"The pyproject.toml file has an invalid "
                f"version number: {version_info}"
            )

    return version
