from dynamicalsystem.pytests.environment import variables as environment_variables
from dataclasses import FrozenInstanceError
from os.path import join
from pathlib import Path
from pytest import raises

# pytest doesn't observe 'implied namespace src-layout' per PEP 420.
# The tests establish a 'tests.__module__' __name__.
# We create a fake name which mocks the namespace.
__fake_name__ = "dynamicalsystem." + __name__


def test_config_values(environment_variables):
    from dynamicalsystem.halogen.config import config_instance

    config = config_instance(__fake_name__)

    print(f"\nconfig._namespace_file:\t{config._namespace_file}")
    print(f"  config._package_file:\t{config._package_file}")
    print(f"        config._prefix:\t{config._prefix}")
    print(f"         __fake_name__:\t{__fake_name__}")
    print(f"              __name__:\t{__name__}")
    print(f"           __package__:\t{__package__}\n")

    root_folder = join(Path.home(), ".local", "share", "dynamicalsystem")
    assert config._namespace_file == join(
        root_folder, "config", "dynamicalsystem.pytest.env"
    )
    assert config.environment == "pytest"
    assert config._package_file.endswith(
        join(root_folder, "config", f"{__package__}.pytest.env")
    )
    assert config.log_level == "DEBUG"


def test_config_attributes(environment_variables):
    from dynamicalsystem.halogen.config import config_instance

    config = config_instance(__fake_name__)

    instance_attributes = sorted(list(config.__dict__.keys()))
    expected_attributes = sorted(
        [
            "_namespace_file",
            "data_folder",
            "environment",
            "log_level",
            "_namespace",
            "_package",
            "_package_file",
            "_prefix",
            "log_signal_identity",
            "log_signal_target",
            "log_signal_url",
        ]
    )
    assert instance_attributes == expected_attributes


def test_config_is_singleton(environment_variables):
    from dynamicalsystem.halogen.config import config_instance

    config_a = config_instance(__fake_name__)
    config_b = config_instance(__fake_name__)

    assert config_a == config_b
    assert config_a is config_b


def test_config_is_immutable(environment_variables):
    from dynamicalsystem.halogen.config import config_instance

    config = config_instance(__fake_name__)

    with raises(FrozenInstanceError):
        config.environment = "not pytest"

    assert config.environment == "pytest"
