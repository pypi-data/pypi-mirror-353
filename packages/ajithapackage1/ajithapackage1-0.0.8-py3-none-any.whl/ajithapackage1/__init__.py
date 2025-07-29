r'''
# replace this
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *


class HelloWorld(metaclass=jsii.JSIIMeta, jsii_type="ajithapackage1.HelloWorld"):
    def __init__(self, options: "IHelloOptions") -> None:
        '''
        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__212fa063b66ca519b8e31185e36384e4fa2fa5ede3e4cca962a73b0e9cefbeac)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="generateInfo")
    def generate_info(self) -> "IHelloInfo":
        return typing.cast("IHelloInfo", jsii.invoke(self, "generateInfo", []))

    @jsii.member(jsii_name="sayHello")
    def say_hello(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "sayHello", []))


@jsii.interface(jsii_type="ajithapackage1.IHelloInfo")
class IHelloInfo(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        ...


class _IHelloInfoProxy:
    __jsii_type__: typing.ClassVar[str] = "ajithapackage1.IHelloInfo"

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHelloInfo).__jsii_proxy_class__ = lambda : _IHelloInfoProxy


@jsii.interface(jsii_type="ajithapackage1.IHelloOptions")
class IHelloOptions(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="greeting")
    def greeting(self) -> typing.Optional[builtins.str]:
        ...


class _IHelloOptionsProxy:
    __jsii_type__: typing.ClassVar[str] = "ajithapackage1.IHelloOptions"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="greeting")
    def greeting(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "greeting"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHelloOptions).__jsii_proxy_class__ = lambda : _IHelloOptionsProxy


__all__ = [
    "HelloWorld",
    "IHelloInfo",
    "IHelloOptions",
]

publication.publish()

def _typecheckingstub__212fa063b66ca519b8e31185e36384e4fa2fa5ede3e4cca962a73b0e9cefbeac(
    options: IHelloOptions,
) -> None:
    """Type checking stubs"""
    pass
