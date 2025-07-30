"""Conversion utilities for JSDC Loader."""

import datetime
import uuid
from dataclasses import is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Type, Union, get_args, get_origin

from .compat import (
    create_pydantic_from_dict,
    is_pydantic_instance,
    is_pydantic_model,
    pydantic_to_dict,
)
from .types import T
from .validator import get_cached_type_hints, validate_type


def convert_enum(key: str, value: Any, enum_type: Type[Enum]) -> Enum:
    """Convert a string value to an Enum member."""
    try:
        return enum_type[value]
    except KeyError:
        raise ValueError(f"Invalid Enum value for key {key}: {value}")


def convert_union_type(key: str, value: Any, union_type: Any) -> Any:
    """Convert a value to one of the Union types."""
    args = get_args(union_type)

    # 杂鱼♡～处理None值喵～
    if value is None and type(None) in args:
        return None

    # 杂鱼♡～首先尝试精确类型匹配，这样可以避免不必要的类型转换喵～
    for arg_type in args:
        if arg_type is type(None):
            continue

        # 杂鱼♡～检查是否是精确的类型匹配喵～
        if _is_exact_type_match(value, arg_type):
            try:
                return convert_value(key, value, arg_type)
            except (ValueError, TypeError):
                continue

    # 杂鱼♡～如果没有精确匹配，再尝试类型转换喵～
    for arg_type in args:
        if arg_type is type(None):
            continue

        # 杂鱼♡～跳过已经尝试过的精确匹配喵～
        if _is_exact_type_match(value, arg_type):
            continue

        try:
            return convert_value(key, value, arg_type)
        except (ValueError, TypeError):
            continue

    # 如果所有转换都失败，则抛出错误喵～
    raise TypeError(f"杂鱼♡～无法将键{key}的值{value}转换为{union_type}喵！～")


def _is_exact_type_match(value: Any, expected_type: Any) -> bool:
    """杂鱼♡～检查值是否与期望类型精确匹配喵～"""
    # 杂鱼♡～处理基本类型喵～
    if expected_type in (int, float, str, bool):
        return type(value) is expected_type

    # 杂鱼♡～处理容器类型喵～
    origin = get_origin(expected_type)
    if origin is list:
        return isinstance(value, list)
    elif origin is dict:
        return isinstance(value, dict)
    elif origin is set:
        return isinstance(value, set)
    elif origin is tuple:
        return isinstance(value, tuple)
    elif expected_type is list:
        return isinstance(value, list)
    elif expected_type is dict:
        return isinstance(value, dict)
    elif expected_type is set:
        return isinstance(value, set)
    elif expected_type is tuple:
        return isinstance(value, tuple)

    # 杂鱼♡～处理dataclass类型喵～
    if is_dataclass(expected_type):
        return isinstance(value, expected_type)

    # 杂鱼♡～处理Enum类型喵～
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return isinstance(value, expected_type)

    # 杂鱼♡～其他情况返回False，让转换逻辑处理喵～
    return False


def convert_simple_type(key: str, value: Any, e_type: Any) -> Any:
    """Convert a value to a simple type."""
    # 杂鱼♡～处理特殊类型喵～
    if e_type is Any:
        return value
    elif isinstance(e_type, type) and issubclass(e_type, Enum):
        return e_type[value]
    elif e_type == dict or get_origin(e_type) == dict:
        # Handle dict type properly
        return value
    elif e_type == list or get_origin(e_type) == list:
        # Handle list type properly
        return value
    # 杂鱼♡～处理复杂类型喵～如日期、时间等
    elif e_type == datetime.datetime and isinstance(value, str):
        return datetime.datetime.fromisoformat(value)
    elif e_type == datetime.date and isinstance(value, str):
        return datetime.date.fromisoformat(value)
    elif e_type == datetime.time and isinstance(value, str):
        return datetime.time.fromisoformat(value)
    elif e_type == datetime.timedelta and isinstance(value, (int, float)):
        return datetime.timedelta(seconds=value)
    elif e_type == datetime.timedelta and isinstance(value, dict):
        return datetime.timedelta(**value)
    elif e_type == uuid.UUID and isinstance(value, str):
        return uuid.UUID(value)
    elif e_type == Decimal and isinstance(value, (str, int, float)):
        return Decimal(str(value))
    else:
        try:
            return e_type(value)
        except TypeError:
            # If it's a typing.Dict or typing.List, just return the value
            if str(e_type).startswith("typing."):
                return value
            raise


def convert_dict_type(key: str, value: dict, e_type: Any) -> dict:
    """Convert a dictionary based on its type annotation."""
    if get_origin(e_type) is dict:
        key_type, val_type = get_args(e_type)

        # 杂鱼♡～本喵扩展支持更多键类型了喵～
        # 支持字符串、整数、浮点数等基本类型作为键
        supported_key_types = (str, int, float, bool)
        if key_type not in supported_key_types:
            raise ValueError(
                f"杂鱼♡～字典键类型 {key_type} 暂不支持喵！支持的键类型: {supported_key_types}～"
            )

        # 杂鱼♡～如果键类型不是字符串，需要转换JSON中的字符串键为目标类型喵～
        converted_dict = {}
        for k, v in value.items():
            # 杂鱼♡～JSON中的键总是字符串，需要转换为目标键类型喵～
            if key_type == str:
                converted_key = k
            elif key_type == int:
                try:
                    converted_key = int(k)
                except ValueError:
                    raise ValueError(f"杂鱼♡～无法将键 '{k}' 转换为整数喵！～")
            elif key_type == float:
                try:
                    converted_key = float(k)
                except ValueError:
                    raise ValueError(f"杂鱼♡～无法将键 '{k}' 转换为浮点数喵！～")
            elif key_type == bool:
                if k.lower() in ("true", "1"):
                    converted_key = True
                elif k.lower() in ("false", "0"):
                    converted_key = False
                else:
                    raise ValueError(f"杂鱼♡～无法将键 '{k}' 转换为布尔值喵！～")
            else:
                converted_key = k  # 杂鱼♡～其他情况保持原样喵～

            # 杂鱼♡～转换值喵～
            if is_dataclass(val_type) or get_origin(val_type) is Union:
                converted_dict[converted_key] = convert_value(f"{key}.{k}", v, val_type)
            else:
                converted_dict[converted_key] = v

        return converted_dict

    # Default case, just return the dict
    return value


def convert_tuple_type(key: str, value: list, e_type: Any) -> tuple:
    """杂鱼♡～本喵帮你把列表转换成元组喵～"""
    if get_origin(e_type) is tuple:
        args = get_args(e_type)
        if len(args) == 2 and args[1] is Ellipsis:  # Tuple[X, ...]
            element_type = args[0]
            return tuple(
                convert_value(f"{key}[{i}]", item, element_type)
                for i, item in enumerate(value)
            )
        elif args:  # Tuple[X, Y, Z]
            if len(value) != len(args):
                raise ValueError(
                    f"杂鱼♡～元组{key}的长度不匹配喵！期望{len(args)}，得到{len(value)}～"
                )
            return tuple(
                convert_value(f"{key}[{i}]", item, arg_type)
                for i, (item, arg_type) in enumerate(zip(value, args))
            )

    # 如果没有参数类型或者其他情况，直接转换为元组喵～
    return tuple(value)


def convert_value(key: str, value: Any, e_type: Any) -> Any:
    """Convert a value to the expected type."""
    # 杂鱼♡～处理None值和Any类型喵～
    if value is None and (
        e_type is Any
        or (get_origin(e_type) is Union and type(None) in get_args(e_type))
    ):
        return None

    # 杂鱼♡～如果期望类型是Any，直接返回值喵～
    if e_type is Any:
        return value

    # // 杂鱼♡～本喵在这里加了一段逻辑，如果期望的是 set 但得到的是 list，就把它转成 set 喵！～
    if (get_origin(e_type) is set or e_type is set) and isinstance(value, list):
        args = get_args(e_type)
        if (
            args
        ):  # // 杂鱼♡～如果 set 里面有类型定义，比如 Set[Model]，那就要对每个元素进行转换喵～
            element_type = args[0]
            return {convert_value(f"{key}[*]", item, element_type) for item in value}
        else:  # // 杂鱼♡～如果只是普通的 set，比如 Set[str]，就直接转喵～
            return set(value)

    # 杂鱼♡～处理元组类型喵～
    if (get_origin(e_type) is tuple or e_type is tuple) and isinstance(value, list):
        return convert_tuple_type(key, value, e_type)

    if isinstance(e_type, type) and issubclass(e_type, Enum):
        return convert_enum(key, value, e_type)
    elif is_dataclass(e_type):
        return convert_dict_to_dataclass(value, e_type)
    elif is_pydantic_model(e_type):
        # 杂鱼♡～处理 Pydantic 模型喵～
        return create_pydantic_from_dict(e_type, value)
    elif get_origin(e_type) is list or e_type == list:
        args = get_args(e_type)
        if args and (is_dataclass(args[0]) or is_pydantic_model(args[0])):
            return [
                (
                    convert_dict_to_dataclass(item, args[0])
                    if is_dataclass(args[0])
                    else create_pydantic_from_dict(args[0], item)
                )
                for item in value
            ]
        elif args:
            return [
                convert_value(f"{key}[{i}]", item, args[0])
                for i, item in enumerate(value)
            ]
        return value
    elif get_origin(e_type) is dict or e_type == dict:
        return convert_dict_type(key, value, e_type)
    else:
        origin = get_origin(e_type)
        if origin is Union:
            return convert_union_type(key, value, e_type)
        else:
            return convert_simple_type(key, value, e_type)


# // 杂鱼♡～本喵添加了这个函数来检查一个dataclass是否是frozen的喵～
def is_frozen_dataclass(cls):
    """Check if a dataclass is frozen."""
    return (
        is_dataclass(cls)
        and hasattr(cls, "__dataclass_params__")
        and getattr(cls.__dataclass_params__, "frozen", False)
    )


def convert_dict_to_dataclass(data: dict, cls: T) -> T:
    """Convert a dictionary to a dataclass instance."""
    if not data:
        raise ValueError("Empty data dictionary")

    if is_pydantic_model(cls):
        # 杂鱼♡～使用兼容层来创建 Pydantic 模型喵～
        return create_pydantic_from_dict(cls, data)

    # // 杂鱼♡～如果是frozen dataclass，本喵就使用构造函数来创建实例，而不是先创建再赋值喵～
    if is_frozen_dataclass(cls):
        init_kwargs = {}
        t_hints = get_cached_type_hints(cls)

        for key, value in data.items():
            if key in t_hints:
                e_type = t_hints.get(key)
                if e_type is not None:
                    init_kwargs[key] = convert_value(key, value, e_type)
            else:
                raise ValueError(f"Unknown data key: {key}")

        return cls(**init_kwargs)
    else:
        # 普通dataclass可以用更高效的实例创建方式
        root_obj = cls()
        t_hints = get_cached_type_hints(cls)

        for key, value in data.items():
            if hasattr(root_obj, key):
                e_type = t_hints.get(key)
                if e_type is not None:
                    setattr(root_obj, key, convert_value(key, value, e_type))
            else:
                raise ValueError(f"Unknown data key: {key}")

        return root_obj


def convert_dataclass_to_dict(
    obj: Any, parent_key: str = "", parent_type: Any = None
) -> Any:
    """Convert a dataclass instance to a dictionary."""
    if obj is None:
        return None

    # 杂鱼♡～处理特殊类型喵～
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, tuple):
        # 杂鱼♡～对于元组，转换为列表返回喵～
        return [
            convert_dataclass_to_dict(
                item,
                f"{parent_key}[]",
                (
                    get_args(parent_type)[0]
                    if parent_type and get_args(parent_type)
                    else None
                ),
            )
            for item in obj
        ]

    if is_pydantic_instance(obj):
        # 杂鱼♡～使用兼容层来转换 Pydantic 实例喵～
        return pydantic_to_dict(obj)
    elif isinstance(obj, Enum):
        return obj.name
    # // 杂鱼♡～本喵在这里加了一个 elif，如果遇到 set，就把它变成 list 喵！～
    elif isinstance(obj, set):
        # 杂鱼♡～需要检查集合中元素的类型喵～
        element_type = None
        if parent_type and get_origin(parent_type) is set and get_args(parent_type):
            element_type = get_args(parent_type)[0]

        result = []
        for i, item in enumerate(obj):
            if element_type:
                # 杂鱼♡～验证集合中每个元素的类型喵～
                item_key = f"{parent_key or 'set'}[{i}]"
                try:
                    validate_type(item_key, item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"杂鱼♡～序列化时集合元素类型验证失败喵：{item_key} {str(e)}～"
                    )

            result.append(
                convert_dataclass_to_dict(item, f"{parent_key}[{i}]", element_type)
            )

        return result
    elif isinstance(obj, list):
        # 杂鱼♡～需要检查列表中元素的类型喵～
        element_type = None
        if parent_type and get_origin(parent_type) is list and get_args(parent_type):
            element_type = get_args(parent_type)[0]

        result = []
        for i, item in enumerate(obj):
            if element_type:
                # 杂鱼♡～验证列表中每个元素的类型喵～
                item_key = f"{parent_key or 'list'}[{i}]"
                try:
                    validate_type(item_key, item, element_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"杂鱼♡～序列化时列表元素类型验证失败喵：{item_key} {str(e)}～"
                    )

            result.append(
                convert_dataclass_to_dict(item, f"{parent_key}[{i}]", element_type)
            )

        return result
    elif isinstance(obj, dict):
        # 杂鱼♡～需要检查字典中键和值的类型喵～
        key_type, val_type = None, None
        if (
            parent_type
            and get_origin(parent_type) is dict
            and len(get_args(parent_type)) == 2
        ):
            key_type, val_type = get_args(parent_type)

        result = {}
        for k, v in obj.items():
            if key_type:
                # 杂鱼♡～验证字典键的类型喵～
                key_name = f"{parent_key or 'dict'}.key"
                try:
                    validate_type(key_name, k, key_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"杂鱼♡～序列化时字典键类型验证失败喵：{key_name} {str(e)}～"
                    )

            if val_type:
                # 杂鱼♡～验证字典值的类型喵～
                val_key = f"{parent_key or 'dict'}[{k}]"
                try:
                    validate_type(val_key, v, val_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"杂鱼♡～序列化时字典值类型验证失败喵：{val_key} {str(e)}～"
                    )

            # 杂鱼♡～将键转换为字符串以支持JSON序列化喵～
            # JSON只支持字符串键，所以本喵需要将其他类型的键转换为字符串～
            json_key = str(k)
            result[json_key] = convert_dataclass_to_dict(
                v, f"{parent_key}[{k}]", val_type
            )

        return result
    elif is_dataclass(obj):
        result = {}
        t_hints = get_cached_type_hints(type(obj))
        for key, value in vars(obj).items():
            e_type = t_hints.get(key)

            # 杂鱼♡～验证dataclass字段类型喵～
            if e_type is not None:
                field_key = f"{parent_key}.{key}" if parent_key else key
                try:
                    validate_type(field_key, value, e_type)
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"杂鱼♡～序列化时类型验证失败喵：字段 '{field_key}' {str(e)}～"
                    )

            # 杂鱼♡～转换值为字典喵～递归时传递字段类型～
            result[key] = convert_dataclass_to_dict(
                value, f"{parent_key}.{key}" if parent_key else key, e_type
            )
        return result
    return obj
