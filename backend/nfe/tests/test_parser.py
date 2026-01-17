from pathlib import Path
from decimal import Decimal
import unittest

from nfe.parsers.nfe_parser import NFeParser


class TestNFeParser(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).parent / "fixtures" / "nfe_teste.xml"
        self.xml_bytes = base.read_bytes()

    def test_validar_xml(self):
        result = NFeParser.validar_xml(self.xml_bytes)
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_parse_file_dados_basicos(self):
        dados = NFeParser.parse_file(self.xml_bytes)
        self.assertIn("fornecedor", dados)
        self.assertIn("identificacao", dados)
        self.assertIn("itens", dados)

        fornecedor = dados["fornecedor"]
        self.assertEqual(fornecedor["cnpj"], "12345678000199")
        self.assertEqual(fornecedor["nome"], "Fornecedor Teste LTDA")

        ide = dados["identificacao"]
        self.assertEqual(ide["numero_nfe"], "12345")
        self.assertEqual(ide["serie_nfe"], "1")

    def test_parse_file_item_unico(self):
        dados = NFeParser.parse_file(self.xml_bytes)
        itens = dados["itens"]
        self.assertEqual(len(itens), 1)
        item = itens[0]
        self.assertEqual(item["codigo_xml"], "TEST001")
        self.assertEqual(item["ean"], "7891000100045")
        self.assertEqual(item["descricao_xml"], "Produto Teste CX/12")
        self.assertEqual(item["unidade_xml"], "CX")
        self.assertEqual(item["qtd_xml"], Decimal("5"))
        self.assertEqual(item["preco_xml"], Decimal("48.00"))
        self.assertIsNotNone(item["lote"])
        self.assertEqual(item["lote"]["codigo"], "LOTE2026")
        self.assertEqual(item["lote"]["validade"], "2026-12-31")


if __name__ == "__main__":
    unittest.main()

