"""
Parser de XML de NFe (Nota Fiscal Eletrônica) - Projeto Nix.

Suporta NFe versões 3.10 e 4.00 do padrão brasileiro.
"""
from lxml import etree
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional


class NFeParseError(Exception):
    """Exceção customizada para erros de parsing."""
    pass


class NFeParser:
    """
    Parser para arquivos XML de NFe.
    
    Extrai informações de:
    - Fornecedor (emitente)
    - Número e série da NF
    - Itens (produtos)
    - Lotes e rastreabilidade
    """
    
    # Namespaces NFe
    NS = {
        'nfe': 'http://www.portalfiscal.inf.br/nfe'
    }
    
    @staticmethod
    def parse_file(xml_content: bytes) -> Dict:
        """
        Parse completo do XML da NFe.
        
        Args:
            xml_content: Conteúdo do arquivo XML em bytes
            
        Returns:
            Dict com todos os dados extraídos
            
        Raises:
            NFeParseError: Se XML inválido ou dados faltantes
        """
        try:
            tree = etree.fromstring(xml_content)
        except etree.XMLSyntaxError as e:
            raise NFeParseError(f"XML inválido: {str(e)}")
        
        # Tenta encontrar a tag NFe
        nfe = tree.find('.//nfe:NFe', NFeParser.NS)
        if nfe is None:
            # Tenta sem namespace (alguns XMLs não têm)
            nfe = tree.find('.//NFe')
            if nfe is None:
                raise NFeParseError("Tag <NFe> não encontrada no XML")
        
        # Extrai infNFe
        inf_nfe = nfe.find('.//nfe:infNFe', NFeParser.NS)
        if inf_nfe is None:
            inf_nfe = nfe.find('.//infNFe')
            if inf_nfe is None:
                raise NFeParseError("Tag <infNFe> não encontrada")
        
        # Parse dados
        return {
            'fornecedor': NFeParser._parse_fornecedor(inf_nfe),
            'identificacao': NFeParser._parse_identificacao(inf_nfe),
            'itens': NFeParser._parse_itens(inf_nfe)
        }
    
    @staticmethod
    def _parse_fornecedor(inf_nfe) -> Dict:
        """Extrai dados do fornecedor (emitente)."""
        emit = inf_nfe.find('.//nfe:emit', NFeParser.NS)
        if emit is None:
            emit = inf_nfe.find('.//emit')
            if emit is None:
                raise NFeParseError("Dados do fornecedor não encontrados")
        
        cnpj = NFeParser._get_text(emit, './/nfe:CNPJ') or NFeParser._get_text(emit, './/CNPJ')
        nome = NFeParser._get_text(emit, './/nfe:xNome') or NFeParser._get_text(emit, './/xNome')
        
        if not cnpj:
            raise NFeParseError("CNPJ do fornecedor não encontrado")
        
        return {
            'cnpj': cnpj.replace('.', '').replace('/', '').replace('-', ''),
            'nome': nome or 'Não informado'
        }
    
    @staticmethod
    def _parse_identificacao(inf_nfe) -> Dict:
        """Extrai número e série da NFe."""
        ide = inf_nfe.find('.//nfe:ide', NFeParser.NS)
        if ide is None:
            ide = inf_nfe.find('.//ide')
            if ide is None:
                raise NFeParseError("Dados de identificação não encontrados")
        
        numero = NFeParser._get_text(ide, './/nfe:nNF') or NFeParser._get_text(ide, './/nNF')
        serie = NFeParser._get_text(ide, './/nfe:serie') or NFeParser._get_text(ide, './/serie')
        
        if not numero:
            raise NFeParseError("Número da NFe não encontrado")
        
        return {
            'numero_nfe': numero,
            'serie_nfe': serie or '1'
        }
    
    @staticmethod
    def _parse_itens(inf_nfe) -> List[Dict]:
        """Extrai lista de itens da NFe."""
        dets = inf_nfe.findall('.//nfe:det', NFeParser.NS)
        if not dets:
            dets = inf_nfe.findall('.//det')
            if not dets:
                raise NFeParseError("Nenhum item encontrado na NFe")
        
        itens = []
        for det in dets:
            try:
                item = NFeParser._parse_item(det)
                itens.append(item)
            except Exception as e:
                # Ignora item com erro mas continua processando outros
                print(f"Aviso: Erro ao processar item: {e}")
                continue
        
        if not itens:
            raise NFeParseError("Nenhum item válido encontrado")
        
        return itens
    
    @staticmethod
    def _parse_item(det) -> Dict:
        """Parse de um item individual."""
        prod = det.find('.//nfe:prod', NFeParser.NS)
        if prod is None:
            prod = det.find('.//prod')
            if prod is None:
                raise ValueError("Tag <prod> não encontrada no item")
        
        # Dados básicos
        codigo = (
            NFeParser._get_text(prod, './/nfe:cProd') or 
            NFeParser._get_text(prod, './/cProd')
        )
        ean = (
            NFeParser._get_text(prod, './/nfe:cEAN') or 
            NFeParser._get_text(prod, './/cEAN')
        )
        descricao = (
            NFeParser._get_text(prod, './/nfe:xProd') or 
            NFeParser._get_text(prod, './/xProd')
        )
        unidade = (
            NFeParser._get_text(prod, './/nfe:uCom') or 
            NFeParser._get_text(prod, './/uCom')
        )
        quantidade = (
            NFeParser._get_text(prod, './/nfe:qCom') or 
            NFeParser._get_text(prod, './/qCom')
        )
        preco = (
            NFeParser._get_text(prod, './/nfe:vUnCom') or 
            NFeParser._get_text(prod, './/vUnCom')
        )
        
        if not codigo or not quantidade or not preco:
            raise ValueError("Dados obrigatórios do item faltando")
        
        # Dados de rastreabilidade (lote)
        lote_data = NFeParser._parse_rastreabilidade(det)
        
        return {
            'codigo_xml': codigo,
            'ean': ean if ean and ean != 'SEM GTIN' else None,
            'descricao_xml': descricao or 'Sem descrição',
            'unidade_xml': unidade or 'UN',
            'qtd_xml': Decimal(quantidade.replace(',', '.')),
            'preco_xml': Decimal(preco.replace(',', '.')),
            'lote': lote_data
        }
    
    @staticmethod
    def _parse_rastreabilidade(det) -> Optional[Dict]:
        """Parse de dados de rastreabilidade (lote, validade)."""
        rastro = det.find('.//nfe:rastro', NFeParser.NS)
        if rastro is None:
            rastro = det.find('.//rastro')
            if rastro is None:
                return None
        
        codigo_lote = (
            NFeParser._get_text(rastro, './/nfe:nLote') or 
            NFeParser._get_text(rastro, './/nLote')
        )
        data_fab = (
            NFeParser._get_text(rastro, './/nfe:dFab') or 
            NFeParser._get_text(rastro, './/dFab')
        )
        data_val = (
            NFeParser._get_text(rastro, './/nfe:dVal') or 
            NFeParser._get_text(rastro, './/dVal')
        )
        
        if not codigo_lote:
            return None
        
        return {
            'codigo': codigo_lote,
            'fabricacao': NFeParser._parse_date(data_fab),
            'validade': NFeParser._parse_date(data_val)
        }
    
    @staticmethod
    def _get_text(element, xpath: str) -> Optional[str]:
        """Helper para pegar texto de um elemento."""
        node = element.find(xpath, NFeParser.NS)
        if node is None:
            # Tenta sem namespace
            node = element.find(xpath.replace('nfe:', ''))
        
        if node is not None and node.text:
            return node.text.strip()
        return None
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[str]:
        """
        Converte data do formato NFe para ISO.
        
        NFe usa formato: YYYY-MM-DD
        """
        if not date_str:
            return None
        
        try:
            # Já está no formato correto
            return date_str
        except:
            return None
    
    @staticmethod
    def validar_xml(xml_content: bytes) -> Dict:
        """
        Valida se XML é uma NFe válida.
        
        Returns:
            Dict com {'valid': bool, 'errors': list}
        """
        errors = []
        
        # Tenta parsear
        try:
            tree = etree.fromstring(xml_content)
        except etree.XMLSyntaxError as e:
            return {'valid': False, 'errors': [f"XML mal formado: {str(e)}"]}
        
        # Verifica root tag
        root_tag = tree.tag.split('}')[-1]  # Remove namespace
        if root_tag not in ['nfeProc', 'NFe']:
            errors.append(f"Root tag inválida: {root_tag}. Esperado: nfeProc ou NFe")
        
        # Verifica se tem NFe
        nfe = tree.find('.//nfe:NFe', NFeParser.NS)
        if nfe is None:
            nfe = tree.find('.//NFe')
            if nfe is None:
                errors.append("Tag <NFe> não encontrada")
        
        # Verifica fornecedor
        if nfe is not None:
            emit = nfe.find('.//nfe:emit', NFeParser.NS)
            if emit is None:
                emit = nfe.find('.//emit')
                if emit is None:
                    errors.append("Dados do fornecedor (<emit>) não encontrados")
        
        # Verifica itens
        if nfe is not None:
            dets = nfe.findall('.//nfe:det', NFeParser.NS)
            if not dets:
                dets = nfe.findall('.//det')
                if not dets:
                    errors.append("Nenhum item (<det>) encontrado")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
