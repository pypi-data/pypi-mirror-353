import os
from typing import Any, Dict

import antlr4
from antlr4 import ParserRuleContext
from antlr4.Token import CommonToken

from sdoc.antlr.sdoc1Lexer import sdoc1Lexer
from sdoc.antlr.sdoc1Parser import sdoc1Parser
from sdoc.antlr.sdoc1ParserVisitor import sdoc1ParserVisitor
from sdoc.Exception.SDocException import SDocException
from sdoc.helper.PathResolver import PathResolver
from sdoc.helper.SDoc import SDoc
from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc.SDocVisitor import SDocVisitor
from sdoc.sdoc1.data_type.ArrayDataType import ArrayDataType
from sdoc.sdoc1.data_type.DataType import DataType
from sdoc.sdoc1.data_type.IdentifierDataType import IdentifierDataType
from sdoc.sdoc1.data_type.IntegerDataType import IntegerDataType
from sdoc.sdoc1.data_type.StringDataType import StringDataType
from sdoc.sdoc1.error import DataTypeError


class SDoc1Visitor(sdoc1ParserVisitor, SDocVisitor):
    """
    Visitor for SDoc level 1.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: SDocIO, path: str):
        """
        Object constructor.

        :param path: The relative path from the CWD to the SDoc1 document.
        """
        SDocVisitor.__init__(self, io)

        self._io: SDocIO = io
        """
        Styled output formatter.
        """

        self._output: Any = None
        """
        Object for streaming the generated output. This object MUST implement the write method.
        """

        self._global_scope: ArrayDataType = ArrayDataType()
        """
        All defined variables at global scope.
        """

        self._include_level: int = 0
        """
        The level of including other SDoc documents.
        """

        self._options: Dict[str, int] = {'max_include_level': 100}
        """
        The options.
        """

        self._path: str = path
        """
        The relative path from the CWD to the SDoc1 document.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def output(self) -> Any:
        """
        Getter for output.
        """
        return self._output

    # ------------------------------------------------------------------------------------------------------------------
    @output.setter
    def output(self, output: Any) -> None:
        """
        Setter for output.

        :param output: This object MUST implement the write method.
        """
        self._output = output

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def include_level(self) -> int:
        """
        Getter for include_level.
        """
        return self._include_level

    # ------------------------------------------------------------------------------------------------------------------
    @include_level.setter
    def include_level(self, include_level: int) -> None:
        """
        Setter for include_level.

        :param int include_level: The include level.
        """
        self._include_level = include_level

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def global_scope(self) -> ArrayDataType:
        """
        Getter for global_scope.
        """
        return self._global_scope

    # ------------------------------------------------------------------------------------------------------------------
    @global_scope.setter
    def global_scope(self, scope: ArrayDataType) -> None:
        """
        Setter for global_scope.

        :param scope: The global scope.
        """
        self._global_scope = scope

    # ------------------------------------------------------------------------------------------------------------------
    def stream(self, snippet: str) -> None:
        """
        Puts an output snippet on the output stream.

        :param snippet: The snippet to be appended to the output stream of this parser.
        """
        if snippet is not None:
            self._output.write(snippet)

    # ------------------------------------------------------------------------------------------------------------------
    def put_position(self, ctx: ParserRuleContext, position: str) -> None:
        """
        Puts a position SDoc2 command on the output stream.

        :param ctx: The context tree.
        :param position: Either start or stop.
        """
        if position == 'start':
            token = ctx.start
        else:
            token = ctx.stop

        stream = token.getInputStream()
        if hasattr(stream, 'fileName'):
            # antlr4.FileStream.FileStream
            filename = stream.fileName  # Replace fileName with get_source_name() when implemented in ANTLR.
        else:
            # Input stream is a antlr4.InputStream.InputStream.
            filename = ''

        line_number = token.line
        column = token.column

        if position == 'stop':
            column += len(token.text)

        self.stream(f'\\position{{{SDoc.escape(filename)}:{line_number}.{column}}}')

    # ------------------------------------------------------------------------------------------------------------------
    def _data_is_true(self, data: DataType, token: CommonToken | None = None) -> bool | None:
        """
        Returns True if a data type evaluates to True, False if a data type evaluates to False, and None if an error
        occurs.

        :param data: The data.
        :param CommonToken token: The token where data type is being used.
        """
        try:
            return data.is_true()

        except DataTypeError as e:
            self._error(str(e), token)
            return None

    # ------------------------------------------------------------------------------------------------------------------
    def visit(self, tree: ParserRuleContext) -> Any:
        """
        Visits a parse tree produced by sdoc1

        :param tree: The context tree.
        """
        self.put_position(tree, 'start')

        return super().visit(tree)

    # ------------------------------------------------------------------------------------------------------------------
    def visitAssignmentExpressionAssignment(self, ctx: sdoc1Parser.AssignmentExpressionAssignmentContext) -> Any:
        """
        Visit a parse tree for expression like a = b.

        :param ctx: The context tree.
        """
        right_hand_side = ctx.assignmentExpression().accept(self)
        left_hand_side = ctx.postfixExpression().accept(self)

        # Left hand side must be an identifier.
        # @todo implement array element.
        if not isinstance(left_hand_side, IdentifierDataType):
            message = f"Left hand side '{str(left_hand_side)!s}' is not an identifier."
            self._error(message, ctx.postfixExpression().start)
            return None

        try:
            value = left_hand_side.set_value(right_hand_side)
        except DataTypeError as e:
            self._error(str(e), ctx.assignmentExpression().start)
            return None

        return value

    # ------------------------------------------------------------------------------------------------------------------
    def visitLogicalAndExpressionAnd(self, ctx: sdoc1Parser.LogicalAndExpressionAndContext) -> IntegerDataType:
        """
        Visits a parse tree for expressions like 'a && b'.

        :param ctx: The context tree.
        """
        a_ctx = ctx.logicalAndExpression()
        b_ctx = ctx.equalityExpression()

        a = a_ctx.accept(self)
        b = b_ctx.accept(self)

        a_is_true = self._data_is_true(a, a_ctx.start)
        b_is_true = self._data_is_true(b, b_ctx.start)

        return IntegerDataType(1 if a_is_true and b_is_true else 0)

    # ------------------------------------------------------------------------------------------------------------------
    def visitLogicalOrExpressionLogicalOr(self,
                                          ctx: sdoc1Parser.LogicalOrExpressionLogicalOrContext) -> IntegerDataType:
        """
        Visits a parse tree for expressions like 'a || b'.

        :param ctx: The context tree.
        """
        a_ctx = ctx.logicalOrExpression()
        b_ctx = ctx.logicalAndExpression()

        a = a_ctx.accept(self)
        b = b_ctx.accept(self)

        a_is_true = self._data_is_true(a, a_ctx.start)
        b_is_true = self._data_is_true(b, b_ctx.start)

        return IntegerDataType(1 if a_is_true or b_is_true else 0)

    # ------------------------------------------------------------------------------------------------------------------
    def visitPostfixExpressionExpression(self, ctx: sdoc1Parser.PostfixExpressionExpressionContext) \
            -> DataType | None:
        """
        Visits a parse tree for expressions like 'a[1]'.

        :param ctx: The context tree.
        """
        # First, get the value of key.
        expression = ctx.expression().accept(self)
        if not expression.is_defined():
            message = f'{ctx.expression().getSymbol()!s} is not defined.'
            self._error(message, ctx.expression().start)
            return None

        postfix_expression = ctx.postfixExpression().accept(self)
        if not isinstance(postfix_expression, IdentifierDataType):
            message = f"'{ctx.postfixExpression().getSymbol()!s}' is not an identifier."
            self._error(message, ctx.postfixExpression().start)
            return None

        return postfix_expression.get_array_element(expression)

    # ------------------------------------------------------------------------------------------------------------------
    def visitPrimaryExpressionIdentifier(self, ctx: sdoc1Parser.PrimaryExpressionIdentifierContext) \
            -> IdentifierDataType:
        """
        Visits a parse tree produced by sdoc1Parser#primaryExpressionIdentifier.
        """
        return IdentifierDataType(self._global_scope, ctx.EXPR_IDENTIFIER().getText())

    # ------------------------------------------------------------------------------------------------------------------
    def visitPrimaryExpressionIntegerConstant(self, ctx: sdoc1Parser.PrimaryExpressionIntegerConstantContext) \
            -> IntegerDataType:
        """
        Visits a parse tree produced by sdoc1Parser#PrimaryExpressionIntegerConstantContext.

        :param ctx: The context tree.
        """
        return IntegerDataType(ctx.EXPR_INTEGER_CONSTANT().getText())

    # ------------------------------------------------------------------------------------------------------------------
    def visitPrimaryExpressionStringConstant(self, ctx: sdoc1Parser.PrimaryExpressionStringConstantContext) \
            -> StringDataType:
        """
        Visits a parse tree produced by sdoc1Parser#PrimaryExpressionStringConstantContext.

        :param ctx: The context tree.
        """
        return StringDataType(ctx.EXPR_STRING_CONSTANT().getText()[1:-1].replace('\\\\', '\\').replace('\\\'', '\''))

    # ------------------------------------------------------------------------------------------------------------------
    def visitPrimaryExpressionSubExpression(self, ctx: sdoc1Parser.PrimaryExpressionSubExpressionContext) -> Any:
        """
        Visits a parse tree for sub-expressions like (a && b).

        :param ctx: The context tree.
        """
        return ctx.expression().accept(self)

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_comment(self, ctx: sdoc1Parser.Cmd_commentContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#cmd_comment.

        :param ctx: The context tree.
        """
        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_debug(self, ctx: sdoc1Parser.Cmd_debugContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#cmd_debug.

        :param ctx: The context tree.
        """
        expression = ctx.expression()

        if expression is not None:
            self._io.write_line(expression.accept(self).debug())
        else:
            self._io.write_line(self._global_scope.debug())

        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_expression(self, ctx: sdoc1Parser.Cmd_expressionContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#cmd_expression.

        :param ctx: The context tree.
        """
        self.visitExpression(ctx.expression())

        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_error(self, ctx: sdoc1Parser.Cmd_errorContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#cmd_error.

        :param ctx: The parse tree.
        """
        token = ctx.ERROR().getSymbol()
        message = SDoc.unescape(ctx.SIMPLE_ARG().getText())

        self._error(message, token)

        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_if(self, ctx: sdoc1Parser.Cmd_ifContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#cmd_if.

        :param ctx: The parse tree.
        """
        n = ctx.getChildCount()
        fired = False
        i = 0
        while i < n and not fired:
            child = ctx.getChild(i)
            token_text = child.getText()
            i += 1
            if token_text in ['\\if', '\\elif']:
                # Skip {
                i += 1

                # Child is the expression to be evaluated.
                child = ctx.getChild(i)
                i += 1
                data = child.accept(self)

                # Skip }
                i += 1

                if self._data_is_true(data, child.start):
                    # Child is the code inside the if or elif clause.
                    child = ctx.getChild(i)
                    self.put_position(child, 'start')
                    i += 1
                    child.accept(self)
                    fired = True

                else:
                    # Skip the code inside the if or elif clause.
                    i += 1

            elif token_text == '\\else':
                # Child is the code inside the else clause.
                child = ctx.getChild(i)
                i += 1

                child.accept(self)
                fired = True

            elif token_text == '\\endif':
                pass

        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_include(self, ctx: sdoc1Parser.Cmd_includeContext) -> None:
        """
        Includes another SDoc in this SDoc.

        :param ctx: The parse tree.
        """
        # Test the maximum include level.
        if self._include_level >= self._options['max_include_level']:
            message = 'Maximum include level exceeded'
            self._error(message, ctx.INCLUDE().getSymbol())
            return

        # Open a stream for the sub-document.
        filename = SDoc.unescape(ctx.SIMPLE_ARG().getText())
        try:
            path = PathResolver.resolve_path(self._path, filename)
            self._io.write_line(f'Including <fso>{path}</fso>')
            try:
                stream = antlr4.FileStream(path, 'utf-8')

                # root_dir

                # Create a new lexer and parser for the sub-document.
                lexer = sdoc1Lexer(stream)
                tokens = antlr4.CommonTokenStream(lexer)
                parser = sdoc1Parser(tokens)
                tree = parser.sdoc()

                # Create a visitor.
                visitor = SDoc1Visitor(self._io, path=path)

                # Set or inherit properties from the parser of the parent document.
                visitor.include_level = self._include_level + 1
                visitor.output = self._output
                visitor.global_scope = self._global_scope

                # Run the visitor on the parse tree.
                visitor.visit(tree)

                # Copy properties from the child document.
                self._errors += visitor.errors

                self.put_position(ctx, 'stop')
            except FileNotFoundError as e:
                self._error(f'Unable to open file {path}.\nCause: {e.strerror}', ctx.INCLUDE().getSymbol())
        except SDocException as e:
            self._error(f'Unable to process file {filename}.\nCause: {str(e)}', ctx.INCLUDE().getSymbol())

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_notice(self, ctx: sdoc1Parser.Cmd_noticeContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#cmd_notice.

        :param ctx: The parse tree.
        """
        token = ctx.NOTICE().getSymbol()
        filename = token.getInputStream().fileName  # Replace fileName with get_source_name() when implemented in ANTLR.
        line_number = token.line
        message = SDoc.unescape(ctx.SIMPLE_ARG().getText())

        self._io.write_line(f'<notice>Notice: {message} at {os.path.relpath(filename)}:{line_number}</notice>')

        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_substitute(self, ctx: sdoc1Parser.Cmd_substituteContext) -> None:
        """
        Visit a parse tree produced by sdoc1Parser#cmd_substitute.

        :param ctx:  The parse tree.
        """
        expression = ctx.expression()
        self.stream(expression.accept(self).get_value())

        self.put_position(ctx, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    def visitCmd_sdoc2(self, ctx: sdoc1Parser.Cmd_sdoc2Context) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#sdoc2_cmd.

        :param ctx: The parse tree.
        """
        self.stream(ctx.SDOC2_COMMAND().getText())

    # ------------------------------------------------------------------------------------------------------------------
    def visitText(self, ctx: sdoc1Parser.TextContext) -> None:
        """
        Visits a parse tree produced by sdoc1Parser#text.

        :param ctx: The parse tree.
        """
        self.stream(ctx.TEXT().getText())

# ----------------------------------------------------------------------------------------------------------------------
