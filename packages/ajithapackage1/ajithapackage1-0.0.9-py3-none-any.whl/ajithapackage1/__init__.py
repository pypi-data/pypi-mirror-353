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

import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="ajithapackage1.HelloInfo",
    jsii_struct_bases=[],
    name_mapping={"message": "message", "timestamp": "timestamp"},
)
class HelloInfo:
    def __init__(self, *, message: builtins.str, timestamp: builtins.str) -> None:
        '''
        :param message: 
        :param timestamp: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a3bc9f6618303848279c1a1b4777f70a86bf17e460ef848d770099f1d9cdcc)
            check_type(argname="argument message", value=message, expected_type=type_hints["message"])
            check_type(argname="argument timestamp", value=timestamp, expected_type=type_hints["timestamp"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "message": message,
            "timestamp": timestamp,
        }

    @builtins.property
    def message(self) -> builtins.str:
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timestamp(self) -> builtins.str:
        result = self._values.get("timestamp")
        assert result is not None, "Required property 'timestamp' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HelloInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HelloWorldConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ajithapackage1.HelloWorldConstruct",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        greeting: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 
        :param greeting: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55d3178976d7f29e89b92b1bb0edbd0aef502c3a61d1997133ece746d73b38be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HelloWorldProps(name=name, greeting=greeting)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="generateInfo")
    def generate_info(self) -> HelloInfo:
        return typing.cast(HelloInfo, jsii.invoke(self, "generateInfo", []))

    @jsii.member(jsii_name="sayHello")
    def say_hello(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "sayHello", []))


@jsii.data_type(
    jsii_type="ajithapackage1.HelloWorldProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "greeting": "greeting"},
)
class HelloWorldProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        greeting: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param greeting: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4143ea399b0046a1d20fbfd2efc96ccdadad65736447c5abd9cb258aea3a84c9)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument greeting", value=greeting, expected_type=type_hints["greeting"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if greeting is not None:
            self._values["greeting"] = greeting

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def greeting(self) -> typing.Optional[builtins.str]:
        result = self._values.get("greeting")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HelloWorldProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HelloInfo",
    "HelloWorldConstruct",
    "HelloWorldProps",
]

publication.publish()

def _typecheckingstub__a0a3bc9f6618303848279c1a1b4777f70a86bf17e460ef848d770099f1d9cdcc(
    *,
    message: builtins.str,
    timestamp: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55d3178976d7f29e89b92b1bb0edbd0aef502c3a61d1997133ece746d73b38be(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    greeting: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4143ea399b0046a1d20fbfd2efc96ccdadad65736447c5abd9cb258aea3a84c9(
    *,
    name: builtins.str,
    greeting: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
