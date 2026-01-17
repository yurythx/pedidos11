import argparse
import sys
import json
from pathlib import Path
from nfe.parsers.nfe_parser import NFeParser, NFeParseError


def main():
    parser = argparse.ArgumentParser(prog="nfe-cli", add_help=True)
    parser.add_argument("xml_path", type=str)
    args = parser.parse_args()

    p = Path(args.xml_path)
    if not p.exists() or not p.is_file():
        print("Arquivo não encontrado", file=sys.stderr)
        sys.exit(1)

    xml_bytes = p.read_bytes()
    valid = NFeParser.validar_xml(xml_bytes)
    if not valid["valid"]:
        print(json.dumps({"valid": False, "errors": valid["errors"]}, ensure_ascii=False), file=sys.stdout)
        sys.exit(2)

    try:
        dados = NFeParser.parse_file(xml_bytes)
    except NFeParseError as e:
        print(json.dumps({"valid": False, "errors": [str(e)]}, ensure_ascii=False), file=sys.stdout)
        sys.exit(3)

    print(json.dumps({"valid": True, "dados": dados}, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()

