from __future__ import unicode_literals

from shutil import which

from django.utils.functional import cached_property

from require.conf import settings as require_settings
from require.helpers import import_module_attr


def load_environment():
    environment = require_settings.REQUIRE_ENVIRONMENT
    aliases = require_settings.REQUIRE_ENVIRONMENT_ALIASES
    environment = aliases.get(environment, environment)
    environment = import_module_attr(environment)
    return environment


class Environment(object):
    def __init__(self, environment):
        self.env = environment

    def args(self):
        raise NotImplementedError()


class NodeEnvironment(Environment):
    def args(self):
        # Start of the command to run the compiler in Node.
        return ["node"]


class RhinoEnvironment(Environment):
    def args(self):
        # Start of the command to run the compiler in Java.
        return [
            "java",
            # The `--add-exports` flag lets Rhino access Java’s internal
            # `sun.nio.ch` package, which is restricted by default in
            # Java 9+. Without it, file operations in Rhino fail.
            "--add-exports", "java.base/sun.nio.ch=ALL-UNNAMED",
            "-Xss100M",
            "-classpath",
            ":".join((
                self.env.resource_path("js.jar"),
                self.env.resource_path("compiler.jar"),
            )),
            "org.mozilla.javascript.tools.shell.Main",
            "-opt", "-1",
        ]


class AutoEnvironment(Environment):
    environments = [NodeEnvironment, RhinoEnvironment]

    @cached_property
    def environment(self):
        for environment in self.environments:
            environment = environment(self.env)
            executable = environment.args()[0]
            if which(executable):
                return environment

        raise EnvironmentError("no environments detected: {envs}".format(
            envs=', '.join([ str(env) for env in self.environments ])))

    def args(self):
        return self.environment.args()
