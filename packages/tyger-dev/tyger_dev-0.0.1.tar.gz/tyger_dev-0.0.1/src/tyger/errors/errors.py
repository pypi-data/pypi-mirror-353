from typing import Optional, Any, Union
import ast


class TygerError(Exception):
    """Base class for all Tyger type checking errors."""

    msg: str = "TYG000: Generic Tyger error"

    def __init__(self, node: ast.AST, filename: Optional[str] = None) -> None:
        """Initialize base Tyger error with location information.

        Args:
            node: AST node where the error occurred
            filename: Optional name of the file where the error occurred
        """
        self.node = node
        self.filename = filename
        self.lineno = node.lineno if hasattr(node, "lineno") else None
        self.end_lineno = node.end_lineno if hasattr(node, "end_lineno") else None
        self.col_offset = node.col_offset if hasattr(node, "col_offset") else None
        self.end_col_offset = (
            node.end_col_offset if hasattr(node, "end_col_offset") else None
        )

    def get_location(self) -> str:
        """Get formatted location string for error reporting.

        Returns:
            String representation of error location (file:line:col)
        """
        return (
            f"{self.filename}:{self.node.lineno}:{self.node.col_offset}"
            if self.filename
            else f"{self.node.lineno}:{self.node.col_offset}"
        )

    def __str__(self) -> str:
        """String representation of the error with location and message.

        Returns:
            Formatted error message with location information
        """
        return f"{self.msg} at {self.get_location()}"


class TypeMismatchError(TygerError):
    """Error raised when there is a type mismatch."""

    msg = "TYG100: Type mismatch error"

    def __init__(
        self,
        node: ast.AST,
        actual_type: Any,
        expected_type: Any,
        filename: Optional[str] = None,
    ) -> None:
        """Initialize type mismatch error.

        Args:
            node: AST node where the error occurred
            actual_type: The type that was provided
            expected_type: The type that was expected
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.expected_type = expected_type
        self.actual_type = actual_type

    def __str__(self) -> str:
        """Format detailed error message with expected and actual types.

        Returns:
            Formatted error message with type mismatch details
        """
        return f"{self.msg} at {self.get_location()} - Expected {self.expected_type}, got {self.actual_type}"


class RedefineVariableError(TygerError):
    """Error raised when a variable is redefined."""

    msg = "TYG101: Redefine variable error"

    def __init__(
        self, node: ast.AST, name: str, filename: Optional[str] = None
    ) -> None:
        """Initialize variable redefinition error.

        Args:
            node: AST node where the error occurred
            name: The name of the variable being redefined
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.name = name

    def __str__(self) -> str:
        """Format detailed error message with variable name.

        Returns:
            Formatted error message with variable redefinition details
        """
        return f"{self.msg} at {self.get_location()} - Variable {self.name} already defined"


class NotFoundTypeError(TygerError):
    """Error raised when no result type is found for an operation between two types."""

    msg = "TYG102: Not found type error"

    def __init__(
        self,
        node: ast.AST,
        lty: Union[str, Any],
        rty: Union[str, Any],
        str_op: str,
        filename: Optional[str] = None,
    ) -> None:
        """Initialize type operation error.

        Args:
            node: AST node where the error occurred
            lty: The left operand type
            rty: The right operand type
            str_op: The operation string representation
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.lty = lty
        self.rty = rty
        self.str_op = str_op

    def __str__(self) -> str:
        """Format detailed error message with operation and operand types.

        Returns:
            Formatted error message with operation type information
        """
        return (
            f"{self.msg} at {self.get_location()} - "
            f"Not found type for operand {self.str_op} and arguments of type {self.lty} and {self.rty}"
        )


class AttributeNotFoundError(TygerError):
    """Error raised when an attribute is not found in a type."""

    msg = "TYG103: Attribute not found error"

    def __init__(
        self, node: ast.AST, attr: str, filename: Optional[str] = None
    ) -> None:
        """Initialize attribute not found error.

        Args:
            node: AST node where the error occurred
            attr: The name of the attribute that was not found
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.attr = attr

    def __str__(self) -> str:
        """Format detailed error message with attribute name.

        Returns:
            Formatted error message with missing attribute details
        """
        return f"{self.msg} at {self.get_location()} - Object has no attribute '{self.attr}'"
