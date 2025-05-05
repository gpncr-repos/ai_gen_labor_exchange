import abc
import ast
import inspect
import json
import re
from dataclasses import fields, is_dataclass
from typing import Any, Dict, List, Optional, Type, get_type_hints

from pydantic import BaseModel


class ClassAnalyzer:
    """
    Анализатор классов для извлечения структуры в машиночитаемом формате.
    Учитывает переопределенные методы, свойства и переменные, а также их видимость.
    """

    def __init__(self):
        """Инициализация анализатора с базовыми настройками."""
        self._seen_classes = set()
        self._base_model_attrs = set(dir(BaseModel))
        self._abc_attrs = set(dir(abc.ABC))
        self._magic_methods = self._init_magic_methods()

    def _init_magic_methods(self) -> set:
        """Инициализирует список магических методов."""
        return {
            '__abs__', '__add__', '__and__', '__bool__', '__call__',
            '__enter__', '__exit__', '__next__', '__iter__',
            '__contains__', '__delattr__', '__delitem__', '__dir__',
            '__divmod__', '__eq__', '__float__', '__floordiv__',
            '__ge__', '__getattr__', '__getattribute__', '__getitem__',
            '__gt__', '__hash__', '__iadd__', '__iand__', '__ifloordiv__',
            '__ilshift__', '__imatmul__', '__imod__', '__imul__', '__index__',
            '__init__', '__init_subclass__', '__int__', '__invert__',
            '__ior__', '__ipow__', '__irshift__', '__isub__', '__iter__',
            '__itruediv__', '__ixor__', '__le__', '__len__', '__lshift__',
            '__lt__', '__matmul__', '__mod__', '__mul__', '__ne__',
            '__neg__', '__new__', '__or__', '__pos__', '__pow__',
            '__radd__', '__rand__', '__rdivmod__', '__reduce__',
            '__reduce_ex__', '__repr__', '__reversed__', '__rfloordiv__',
            '__rlshift__', '__rmatmul__', '__rmod__', '__rmul__', '__ror__',
            '__round__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
            '__rtruediv__', '__rxor__', '__setattr__', '__setitem__',
            '__sizeof__', '__str__', '__sub__', '__subclasshook__',
            '__truediv__', '__xor__',
            '__aenter__', '__aexit__', '__anext__', '__aiter__'
        }

    def analyze(self, *classes: Type) -> Dict[str, Any]:
        """
        Анализирует переданные классы.
        Args:
            *classes: Произвольное количество классов для анализа
        Returns:
            Словарь с информацией о классах в формате:
            {
                "classes": [
                    {информация о классе 1},
                    {информация о классе 2},
                    ...
                ]
            }
        """
        return {"classes": [self._analyze_class(cls) for cls in classes]}

    def to_json(self, *classes: Type) -> str:
        """
        Конвертирует анализ классов в JSON строку.
        Args:
            *classes: Классы для анализа
        Returns:
            JSON строка с результатами анализа
        """
        return json.dumps(self.analyze(*classes), indent=2, ensure_ascii=False)

    def _analyze_class(self, cls: Type) -> Dict[str, Any]:
        """Анализирует отдельный класс."""
        if cls in self._seen_classes:
            return {"name": cls.__name__, "description": "Already processed"}

        self._seen_classes.add(cls)
        return self._build_class_info(cls)

    def _build_class_info(self, cls: Type) -> Dict[str, Any]:
        """Строит полную информацию о классе."""
        return {
            **self._get_basic_class_info(cls),
            "methods": self._get_class_methods(cls),
            "properties": self._get_class_properties(cls),
            "fields": self._get_class_fields(cls),
            "class_variables": self._get_class_variables(cls)
        }

    def _get_basic_class_info(self, cls: Type) -> Dict[str, Any]:
        """Возвращает базовую информацию о классе."""
        return {
            "name": cls.__name__,
            "description": inspect.getdoc(cls) or "",
            "is_abstract": inspect.isabstract(cls) or self._has_abc_base(cls),
            "is_dataclass": is_dataclass(cls),
            "is_pydantic": issubclass(cls, BaseModel),
            "parent_classes": [base.__name__ for base in cls.__bases__ if base != object]
        }

    def _has_abc_base(self, cls: Type) -> bool:
        """Проверяет, наследуется ли класс от ABC."""
        return any(
            base.__module__ == 'abc' and base.__name__ == 'ABC'
            for base in cls.__bases__
        )

    def _get_class_methods(self, cls: Type) -> List[Dict[str, Any]]:
        """Извлекает методы класса с учетом переопределений."""
        methods = []

        for name, member in inspect.getmembers(cls):
            if self._should_skip_member(name, member, cls):
                continue

            if isinstance(member, (classmethod, staticmethod)):
                method_info = self._process_method(cls, name, member.__func__)
                method_info["type"] = "classmethod" if isinstance(member, classmethod) else "staticmethod"
                methods.append(method_info)
            elif inspect.isfunction(member) or inspect.ismethod(member):
                methods.append(self._process_method(cls, name, member))

        return methods

    def _process_method(self, cls: Type, name: str, method: Any) -> Dict[str, Any]:
        """Обрабатывает информацию о методе."""
        is_redefined = self._is_method_redefined(cls, name, method)
        method_name = method.__name__ if method.__name__ else name

        return {
            "name": method_name,
            "type": "method",
            "description": inspect.getdoc(method) or "",
            "is_abstract": getattr(method, "__isabstractmethod__", False),
            "is_async": inspect.iscoroutinefunction(method),
            "is_protected": method_name.startswith('_') and not method_name.startswith('__'),
            "is_private": method_name.startswith('__') and method_name not in self._magic_methods,
            "is_magic": method_name in self._magic_methods,
            "signature": self._get_method_signature(method),
            "parameters": self._get_method_parameters(method),
            "raises": self._parse_raises_from_docstring(inspect.getdoc(method)),
            "source": self._get_method_source(method) if is_redefined else None,
            "is_redefined": is_redefined,
            "decorators": self._get_method_decorators(cls, name)
        }

    def _get_method_signature(self, method: Any) -> str:
        """Генерирует строку с сигнатурой метода."""
        try:
            return str(inspect.signature(method))
        except (ValueError, TypeError):
            return "()"

    def _get_method_parameters(self, method: Any) -> Dict[str, Any]:
        """Извлекает параметры метода."""
        parameters = {}

        try:
            sig = inspect.signature(method)
            for param_name, param in sig.parameters.items():
                if param_name in ('self', 'cls'):
                    continue

                parameters[param_name] = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                    "description": ""
                }
        except (ValueError, TypeError):
            pass

        return parameters

    def _parse_raises_from_docstring(self, docstring: Optional[str]) -> List[str]:
        """Извлекает исключения из docstring."""
        if not docstring:
            return []

        matches = re.search(
            r"Raises:\s*\n\s*(.*?)(?:\n\n|\n\s*Args:|\n\s*Returns:|\Z)",
            docstring,
            re.DOTALL | re.IGNORECASE
        )

        if not matches:
            return []

        return list(set(re.findall(r"(\w+Error|\w+Exception)", matches.group(1))))

    def _get_method_source(self, method: Any) -> Optional[str]:
        """Получает исходный код метода."""
        try:
            return inspect.getsource(method)
        except (TypeError, OSError):
            return None

    def _get_method_decorators(self, cls: Type, method_name: str) -> List[str]:
        """Получает декораторы метода."""
        try:
            source = inspect.getsource(cls)
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    return [self._get_decorator_name(decorator) for decorator in node.decorator_list]
        except (TypeError, OSError, SyntaxError):
            pass
        return []

    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Получает имя декоратора из AST узла."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return "unknown_decorator"

    def _get_class_properties(self, cls: Type) -> List[Dict[str, Any]]:
        """Извлекает свойства класса с учетом переопределений."""
        return [
            self._extract_property_info(cls, name, prop)
            for name, prop in inspect.getmembers(cls, lambda x: isinstance(x, property))
            if not self._is_inherited_from_base_model(cls, name, prop)
        ]

    def _extract_property_info(self, cls: Type, name: str, prop: property) -> Dict[str, Any]:
        """Извлекает информацию о свойстве."""
        is_redefined = self._is_property_redefined(cls, name, prop)
        prop_name = prop.fget.__name__ if prop.fget else name
        info = {
            "name": prop_name,
            "description": inspect.getdoc(prop) or "",
            "type": "property",
            "is_abstract": getattr(prop.fget, "__isabstractmethod__", False),
            "is_protected": prop_name.startswith('_') and not prop_name.startswith('__'),
            "is_private": prop_name.startswith('__'),
            "signature": self._get_property_signature(prop),
            "source_getter": self._get_property_source(prop) if is_redefined else None,
            "source_setter": self._get_property_source(prop, is_getter=False) if is_redefined else None,
            "is_redefined": is_redefined
        }

        if prop.fget:
            info["getter"] = self._extract_accessor_info(prop.fget)
        if prop.fset:
            info["setter"] = self._extract_accessor_info(prop.fset)
        if prop.fdel:
            info["deleter"] = self._extract_accessor_info(prop.fdel)

        return info

    def _get_property_signature(self, prop: property) -> str:
        """Генерирует сигнатуру свойства."""
        parts = []
        if prop.fget:
            parts.append(f"getter{self._get_method_signature(prop.fget)}")
        if prop.fset:
            parts.append(f"setter{self._get_method_signature(prop.fset)}")
        if prop.fdel:
            parts.append(f"deleter{self._get_method_signature(prop.fdel)}")
        return "property(" + ", ".join(parts) + ")"

    def _extract_accessor_info(self, accessor: Any) -> Dict[str, Any]:
        """Извлекает информацию о геттере/сеттере свойства."""
        return {
            "description": inspect.getdoc(accessor) or "",
            "is_async": inspect.iscoroutinefunction(accessor),
            "raises": self._parse_raises_from_docstring(inspect.getdoc(accessor)),
            "signature": self._get_method_signature(accessor)
        }

    def _get_property_source(self, prop: property, is_getter=True) -> Optional[str]:
        """Получает исходный код свойства."""
        try:
            if is_getter and prop.fget:
                return inspect.getsource(prop.fget)
            if not is_getter and prop.fset:
                return inspect.getsource(prop.fset)
            return None
        except (TypeError, OSError):
            return None

    def _is_method_redefined(self, cls: Type, name: str, method: Any) -> bool:
        """Проверяет, был ли метод переопределен в классе."""
        if name in cls.__dict__:
            return True

        for base in cls.__bases__:
            if hasattr(base, name):
                base_method = getattr(base, name)

                if inspect.isfunction(base_method):
                    return method.__code__.co_code != base_method.__code__.co_code
        return False

    def _is_property_redefined(self, cls: Type, name: str, prop: property) -> bool:
        """Проверяет, было ли свойство переопределено в классе."""
        if name in cls.__dict__:
            return True

        for base in cls.__bases__:
            if hasattr(base, name):
                base_prop = getattr(base, name)
                if isinstance(base_prop, property) and prop.fget and base_prop.fget:
                    return prop.fget.__code__.co_code != base_prop.fget.__code__.co_code
        return False

    def _get_class_variables(self, cls: Type) -> List[Dict[str, Any]]:
        """Извлекает переменные класса с учетом переопределений."""
        variables = []
        type_hints = get_type_hints(cls)
        base_attrs = self._get_base_attributes(cls)

        for name, value in vars(cls).items():
            if self._should_skip_variable(name, value, base_attrs):
                continue

            is_redefined = name not in base_attrs
            variables.append({
                "name": name,
                "type": str(type_hints.get(name, type(value))),
                "value": str(value) if not callable(value) else None,
                "description": "",
                "is_protected": name.startswith('_') and not name.startswith('__'),
                "is_private": name.startswith('__'),
                "is_redefined": is_redefined
            })

        return variables

    def _get_base_attributes(self, cls: Type) -> set:
        """Получает атрибуты базовых классов."""
        base_attrs = set()
        for base in cls.__bases__:
            base_attrs.update(dir(base))
        return base_attrs

    def _should_skip_variable(self, name: str, value: Any, base_attrs: set) -> bool:
        """Определяет, нужно ли пропускать переменную класса."""
        return (
                (name.startswith('__') and name.endswith('__')) or
                inspect.isfunction(value) or
                isinstance(value, (property, classmethod, staticmethod)) or
                name in self._abc_attrs or
                name in self._base_model_attrs
        )

    def _get_class_fields(self, cls: Type) -> List[Dict[str, Any]]:
        """Извлекает поля класса в зависимости от его типа."""
        if issubclass(cls, BaseModel):
            return self._extract_pydantic_fields(cls)
        elif is_dataclass(cls):
            return self._extract_dataclass_fields(cls)
        return []

    def _extract_pydantic_fields(self, cls: Type[BaseModel]) -> List[Dict[str, Any]]:
        """Извлекает поля Pydantic модели."""
        if not issubclass(cls, BaseModel):
            return []

        return [
            {
                "name": name,
                "type": str(field.annotation),
                "default": str(field.default) if field.default is not None else None,
                "default_factory": str(field.default_factory) if field.default_factory else None,
                "description": field.description or "",
                "required": field.is_required()
            }
            for name, field in cls.model_fields.items()
        ]

    def _extract_dataclass_fields(self, cls: Type) -> List[Dict[str, Any]]:
        """Извлекает поля dataclass."""
        if not is_dataclass(cls):
            return []

        return [
            {
                "name": field.name,
                "type": str(field.type),
                "default": str(field.default) if field.default is not inspect.Parameter.empty else None,
                "default_factory": str(
                    field.default_factory) if field.default_factory is not inspect.Parameter.empty else None,
                "description": ""
            }
            for field in fields(cls)
        ]

    def _should_skip_member(self, name: str, member: Any, cls: Type) -> bool:
        """Определяет, нужно ли пропускать член класса при анализе."""
        if name in ('__init__', '__replace__') and is_dataclass(cls):
            return True

        if not self._is_method_redefined(cls, name, member) or not self._is_property_redefined(cls, name, member):
            return True
        return False

    def _is_inherited_from_base_model(self, cls: Type, name: str, member: Any) -> bool:
        """Проверяет, унаследован ли член от BaseModel."""
        if not issubclass(cls, BaseModel) or not hasattr(BaseModel, name):
            return False

        base_member = getattr(BaseModel, name)

        if inspect.isfunction(member):
            return (
                inspect.isfunction(base_member) and
                member.__module__ == base_member.__module__ and
                member.__qualname__ == base_member.__qualname__
            )

        if isinstance(member, property):
            return (
                isinstance(base_member, property) and
                member.fget and base_member.fget and
                member.fget.__module__ == base_member.fget.__module__ and
                member.fget.__qualname__ == base_member.fget.__qualname__
            )

        return False
