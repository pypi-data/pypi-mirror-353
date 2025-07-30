import ast
import json
from pathlib import Path
from typing import cast


class ModulePropertyTransformer(ast.NodeTransformer):
    """
    Transform lib.xxx references based on JSON configuration.
    If module+name exists in config:
        - Transform properties to function calls
        - Leave variables as is
    If not in config:
        - Use callable() check
    Skip transformation inside isolate_function arguments.
    """

    def __init__(self):
        # Structure: module -> name -> {"type": "property"|"variable"}
        self.module_info: dict[str, dict[str, dict[str, any]]] = {}
        # Track if we're inside isolate_function args
        self.in_isolate_function = False

        # Load config
        try:
            with open(Path(__file__).parent / "module_properties.json") as f:
                self.module_info = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load module properties config: {e}")

    def visit(self, node: ast.AST) -> ast.AST:
        """
        Override the generic visit method to:
        1. Set .parent on each child node for chain detection
        2. Track isolate_function context
        """
        # Check if entering isolate_function call
        is_isolate_call = (isinstance(node, ast.Call) and
                           isinstance(node.func, ast.Name) and
                           node.func.id == 'isolate_function')

        # Set parent on children
        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                value.parent = node
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        item.parent = node

        # Handle isolate_function context
        if is_isolate_call:
            old_context = self.in_isolate_function
            self.in_isolate_function = True
            result = super().visit(node)
            self.in_isolate_function = old_context
            return result

        return super().visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """Process attribute access, but skip if inside isolate_function args."""
        node = cast(ast.Attribute, self.generic_visit(node))

        # Skip if inside isolate_function
        if self.in_isolate_function:
            return node

        # Retrieve the AST parent node
        parent = getattr(node, 'parent', None)

        # Intermediate module - if the parent is also an Attribute, this is not the topmost attribute
        if isinstance(parent, ast.Attribute):
            return node

        # Function call - if the parent is a Call, and this is being called
        if isinstance(parent, ast.Call) and parent.func == node:
            return node

        # If this node has already been processed, or the chain does not start with lib..., skip
        if hasattr(node, '_processed') or not self._is_lib_reference(node):
            return node

        # Now it's the topmost attribute (e.g., ...data_window)
        # Check the full module path and the final attribute
        module_path, name = self._get_module_info(node)
        if not module_path or not name:
            return node

        # Check the config for this attribute
        module_attrs = self.module_info.get(module_path, {})
        attr_info = module_attrs.get(name)

        # If the attribute is in the config: property -> () call, or variable -> leave as is
        if attr_info:
            if attr_info["type"] == "property":
                result = ast.Call(
                    func=self._copy_node(node),
                    args=[],
                    keywords=[]
                )
            else:
                result = node

        # Fall back to __module_property__ check
        elif f"{module_path}.{name}" not in self.module_info:  # Skip if it is a module
            # Check for __module_property__ attribute
            result = ast.IfExp(
                test=ast.Call(
                    func=ast.Name(id='hasattr', ctx=ast.Load()),
                    args=[
                        self._copy_node(node),
                        ast.Constant(value='__module_property__')
                    ],
                    keywords=[]
                ),
                body=ast.Call(
                    func=self._copy_node(node),
                    args=[],
                    keywords=[]
                ),
                orelse=self._copy_node(node)
            )
        # Leave module attributes as is
        else:
            result = node

        result._processed = True
        return result

    @staticmethod
    def _is_lib_reference(node: ast.Attribute) -> bool:
        """Check if the attribute chain starts with 'lib'."""
        current = node
        while isinstance(current, ast.Attribute):
            current = current.value
        return isinstance(current, ast.Name) and current.id == 'lib'

    @staticmethod
    def _get_module_info(node: ast.Attribute) -> tuple[str | None, str | None]:
        """
        Gather the full chain of attributes until we reach 'lib',
        then split into (module_path, final_attribute).
        Example: lib.display.data_window -> (lib.display, data_window)
        """
        attrs = []
        current = node
        while isinstance(current, ast.Attribute):
            attrs.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name) and current.id == 'lib':
            attrs.append('lib')
            attrs.reverse()
            # Example: ['lib', 'display', 'data_window']
            if len(attrs) < 2:
                return None, None
            module_path = '.'.join(attrs[:-1])  # 'lib.display'
            final_attr = attrs[-1]  # 'data_window'
            return module_path, final_attr
        return None, None

    @staticmethod
    def _copy_node(node: ast.AST) -> ast.expr:
        """Create a shallow copy of an AST node (Attribute or Name)."""
        if isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=node.ctx)
        elif isinstance(node, ast.Attribute):
            value = cast(ast.expr, ModulePropertyTransformer._copy_node(node.value))
            return ast.Attribute(value=value, attr=node.attr, ctx=node.ctx)
        return cast(ast.expr, node)
