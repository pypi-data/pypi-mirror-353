import ast

def explain_code(code, emoji=True):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "⚠️ Invalid Python syntax." if emoji else "Invalid Python syntax."

    explanations = []
    function_defs = {}

    # Collect function names
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_defs[node.name] = node

    # Helper: extract docstring if present
    def get_docstring(node):
        return ast.get_docstring(node)

    def e(text):
        # Helper to optionally add emojis based on the flag
        return text if emoji else text.replace("📦", "").replace("📥", "").replace("📤", "").replace("🧮", "").replace("🖨️", "")\
            .replace("📖", "").replace("📚", "").replace("📂", "").replace("🛠️", "").replace("🔁", "").replace("❓", "")\
            .replace("🔢", "").replace("🧩", "").replace("🏛️", "").replace("📝", "").replace("🔥", "").replace("🚀", "")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            params = [arg.arg for arg in node.args.args]
            is_recursive = any(
                isinstance(inner, ast.Call) and getattr(inner.func, 'id', None) == node.name
                for inner in ast.walk(node)
            )
            rec_note = e(" 🔁 This function is recursive.") if is_recursive else ""
            decorators = [ast.unparse(d) for d in node.decorator_list]
            decorator_note = e(f" 🔥 Decorators: {', '.join(decorators)}") if decorators else ""
            doc = get_docstring(node)
            doc_note = e(f" 📝 Docstring: \"{doc}\"") if doc else ""
            explanations.append(
                e(f"📌 Line {node.lineno}: Defines function `{node.name}` with parameter(s): {', '.join(params)}.{rec_note}{decorator_note}{doc_note}")
            )

        elif isinstance(node, ast.ClassDef):
            doc = get_docstring(node)
            doc_note = e(f" 📝 Docstring: \"{doc}\"") if doc else ""
            explanations.append(e(f"🏛️ Line {node.lineno}: Declares a class named `{node.name}`.{doc_note}"))

        elif isinstance(node, ast.Import):
            modules = ", ".join([alias.name for alias in node.names])
            explanations.append(e(f"📦 Line {node.lineno}: Imports module(s): {modules}."))

        elif isinstance(node, ast.ImportFrom):
            modules = ", ".join([alias.name for alias in node.names])
            explanations.append(e(f"📦 Line {node.lineno}: From `{node.module}` import(s): {modules}."))

        elif isinstance(node, ast.Assign):
            targets = ", ".join([ast.unparse(t) for t in node.targets])
            explanations.append(e(f"🧮 Line {node.lineno}: Assigns value to variable(s): {targets}."))

        elif isinstance(node, ast.AnnAssign):
            target = ast.unparse(node.target)
            hint = ast.unparse(node.annotation)
            explanations.append(e(f"📝 Line {node.lineno}: Assigns variable `{target}` with type hint `{hint}`."))

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if getattr(node.value.func, 'id', '') == 'print':
                explanations.append(e(f"🖨️ Line {node.lineno}: Prints output to the console."))

        elif isinstance(node, ast.If):
            test_code = ast.unparse(node.test)
            explanations.append(e(f"❓ Line {node.lineno}: Conditional `if` statement checking: `{test_code}`."))

            # Special __main__ detection
            if hasattr(node.test, 'left') and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                explanations.append(e(f"🚀 Line {node.lineno}: Entry point check for `__main__`."))

        elif isinstance(node, ast.For):
            target = ast.unparse(node.target)
            iter_ = ast.unparse(node.iter)
            explanations.append(e(f"🔁 Line {node.lineno}: For-loop iterating `{target}` over `{iter_}`."))

        elif isinstance(node, ast.While):
            test = ast.unparse(node.test)
            explanations.append(e(f"🔁 Line {node.lineno}: While-loop running while `{test}` is True."))

        elif isinstance(node, ast.With):
            context_exprs = ", ".join([ast.unparse(item.context_expr) for item in node.items])
            explanations.append(e(f"📂 Line {node.lineno}: `with` block (context manager): {context_exprs}."))

        elif isinstance(node, ast.Try):
            explanations.append(e(f"🛠️ Line {node.lineno}: Try-except block for handling exceptions."))
            if node.handlers:
                for handler in node.handlers:
                    if handler.type:
                        htype = ast.unparse(handler.type)
                        explanations.append(e(f"🛠️ Line {handler.lineno}: Handles exception of type `{htype}`."))

        elif isinstance(node, ast.Return):
            val = ast.unparse(node.value)
            explanations.append(e(f"📤 Line {node.lineno}: Returns `{val}` from the function."))

        elif isinstance(node, ast.Lambda):
            explanations.append(e(f"🧩 Line {node.lineno}: Lambda (anonymous) function defined, often used for small inline functions."))

        elif isinstance(node, ast.ListComp):
            explanations.append(e(f"📝 Line {node.lineno}: List comprehension used to create a new list concisely."))

        elif isinstance(node, ast.SetComp):
            explanations.append(e(f"📝 Line {node.lineno}: Set comprehension used to create a new set concisely."))

        elif isinstance(node, ast.DictComp):
            explanations.append(e(f"📝 Line {node.lineno}: Dictionary comprehension used to create a new dict concisely."))

        elif isinstance(node, ast.Dict):
            explanations.append(e(f"📖 Line {node.lineno}: Dictionary literal defined."))

        elif isinstance(node, ast.List):
            explanations.append(e(f"📚 Line {node.lineno}: List literal defined."))

        elif isinstance(node, ast.Tuple):
            explanations.append(e(f"📦 Line {node.lineno}: Tuple literal defined."))

        elif isinstance(node, ast.Set):
            explanations.append(e(f"🔢 Line {node.lineno}: Set literal defined."))

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "read":
                explanations.append(e(f"📘 Line {node.lineno}: File read using `.read()`."))
            elif node.func.attr == "write":
                explanations.append(e(f"📗 Line {node.lineno}: File write using `.write()`."))

    if not explanations:
        return e("🤔 Couldn’t find anything explainable in that snippet.")

    # Sort by line number extracted from explanation string safely
    def extract_line(line):
        parts = line.split()
        for part in parts:
            if part.rstrip(":").isdigit():
                return int(part.rstrip(":"))
        return 0

    explanations.sort(key=extract_line)
    return "\n".join(explanations)
