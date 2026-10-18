"""Static submission format checks. Student source is never imported or executed."""
import ast
import difflib
import os
from pathlib import Path
import sys

# Course-specific constants are inserted here when the student package is built.
COURSE = '2026-ml-ds'
REQUIRED = {'ml02_1.py': {'divide': 2, 'pick_values': 1, 'count_at_least': 2}, 'ml02_2.py': {'to_features': 1, 'count_labels': 1, 'column_stats': 2}}
MAX_BYTES = 262144
NOTE = '内容の正しさは確認していません。締切後に教員が確認します。'


def annotate(level, filename, message, line=None):
    def escape(text):
        return str(text).replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    properties = f'file={filename}' + (f',line={line}' if line else '')
    print(f'::{level} {properties}::{escape(message)}', flush=True)


def nearby(filename):
    candidates = []
    key = filename.lower().replace('-', '_')
    for directory, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', '.github', '.venv', 'venv', '__pycache__') and not Path(directory, d).is_symlink()]
        if len(Path(directory).parts) > 8:
            dirs[:] = []
        for name in files:
            normalized = name.lower().replace('-', '_')
            if normalized == key or normalized in (key + '.py', key[:-3] + '.ipynb') or difflib.SequenceMatcher(None, normalized, key).ratio() >= .83:
                candidates.append(Path(directory, name).as_posix())
                if len(candidates) >= 8:
                    return candidates
    return candidates


def placeholder(node):
    body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
    def unfinished(n):
        if isinstance(n, ast.Pass): return True
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and n.value.value is Ellipsis: return True
        if isinstance(n, ast.Raise):
            value = n.exc.func if isinstance(n.exc, ast.Call) else n.exc
            return isinstance(value, ast.Name) and value.id == 'NotImplementedError'
        return False
    return not body or all(unfinished(n) for n in body)


def accepts(node, count):
    args = node.args
    positional = len(args.posonlyargs) + len(args.args)
    minimum = positional - len(args.defaults)
    return minimum <= count and (args.vararg is not None or count <= positional) and all(d is not None for d in args.kw_defaults)


def check(filename, functions):
    errors, warnings = [], []
    path = Path(filename)
    def error(text, line=None):
        errors.append(text); annotate('error', filename, text, line)
    def warning(text, line=None):
        warnings.append(text); annotate('warning', filename, text, line)
    # Exact spelling is checked even on a case-insensitive local filesystem.
    names = {p.name for p in Path('.').iterdir()}
    if filename not in names or not path.is_file():
        suggestions = nearby(filename)
        error(f'{filename} が最上位フォルダーにありません。' + (' 名前や保存場所が似たファイル: ' + ', '.join(suggestions) if suggestions else ' 指定の名前で作成してください。'))
        return errors, warnings
    if path.is_symlink():
        error('リンクではなく、通常のPythonファイルを提出してください。'); return errors, warnings
    if path.stat().st_size > MAX_BYTES:
        error('ファイルが256 KBを超えています。'); return errors, warnings
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_BYTES: raise ValueError('ファイルが256 KBを超えています。')
        for encoding in ('utf-8-sig', 'cp932'):
            try:
                source = raw.decode(encoding); break
            except UnicodeDecodeError: continue
        else: raise ValueError('UTF-8またはShift_JISで保存してください。')
        tree = ast.parse(source, filename=filename, feature_version=(3, 12))
        compile(tree, filename, 'exec')  # Compile for syntax validation only; never execute.
    except SyntaxError as exc:
        error(f'構文を確認してください: {exc.msg}', exc.lineno); return errors, warnings
    except (OSError, ValueError, RecursionError) as exc:
        error(str(exc)); return errors, warnings
    for name, count in functions.items():
        definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
        if len(definitions) != 1:
            error(f'{name}: ファイルの最上位に def {name}(...) を1つ定義してください。'); continue
        node = definitions[0]
        if not accepts(node, count): error(f'{name}: {count}個の位置引数で呼び出せるようにしてください。', node.lineno)
        if placeholder(node): warning(f'{name}: まだ実装していない可能性があります。', node.lineno)
        if node.decorator_list: warning(f'{name}: デコレーターで変わる動作は確認していません。', node.lineno)
    seen = set()
    for node in ast.walk(tree):
        imports = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else [node.module.split('.')[0] if node.module else '(relative import)'] if isinstance(node, ast.ImportFrom) else []
        for module in imports:
            if module not in sys.stdlib_module_names and module not in seen:
                seen.add(module); warning(f'{module}: 標準ライブラリ以外のモジュールは採点環境にありません。', node.lineno)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'input' for n in ast.walk(node)):
                warning(f'{node.name}: input()は不要です。引数で受け取り、returnで返してください。', node.lineno)
    return errors, warnings


def main():
    rows = ['## 提出ファイルの基本チェック', '', '| ファイル | 結果 | 注意 |', '|---|---|---|']
    failed = False
    for filename, functions in REQUIRED.items():
        try:
            errors, warnings = check(filename, functions)
        except OSError as exc:
            annotate('error', filename, str(exc)); errors, warnings = [str(exc)], []
        failed = failed or bool(errors)
        status = '要確認' if errors else 'OK'
        rows.append(f'| `{filename}` | {status} | {len(warnings)}件の注意 |')
        print(f'{filename}: {status}', flush=True)
    print(NOTE)
    rows += ['', NOTE, '', '緑のチェックは提出形式の確認です。正解や満点を意味しません。', '']
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as out: out.write('\n'.join(rows))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
