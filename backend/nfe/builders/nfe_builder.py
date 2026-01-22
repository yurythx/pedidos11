"""
Builder para construção do XML da NFe 4.00.
"""
import random
from datetime import datetime
from decimal import Decimal
from lxml import etree
from django.utils import timezone

from nfe.models import NotaFiscal, ItemNotaFiscal, TipoEmissao


class NFeBuilder:
    """
    Constrói o XML da NFe versão 4.00.
    """
    
    NSMAP = {
        None: "http://www.portalfiscal.inf.br/nfe"
    }
    
    def __init__(self, nota: NotaFiscal):
        self.nota = nota
        self.root = None
        self.inf_nfe = None
    
    def build(self) -> str:
        """
        Gera o XML completo da NFe.
        
        Returns:
            str: XML assinado (ou apenas gerado se não houver certificado)
        """
        # 1. Gerar Chave de Acesso se não existir
        if not self.nota.chave_acesso:
            self._gerar_chave_acesso()
            self.nota.save(update_fields=['chave_acesso'])
            
        # 2. Estrutura Básica
        self.root = etree.Element("NFe", nsmap=self.NSMAP)
        self.inf_nfe = etree.SubElement(self.root, "infNFe", Id=f"NFe{self.nota.chave_acesso}", versao="4.00")
        
        # 3. Construir grupos
        self._build_ide()
        self._build_emit()
        self._build_dest()
        self._build_det()
        self._build_total()
        self._build_transp()
        self._build_pag()
        self._build_inf_adic()
        
        # 4. Retornar string
        return etree.tostring(self.root, encoding='UTF-8', xml_declaration=True).decode('utf-8')

    def _gerar_chave_acesso(self):
        """Gera chave de acesso da NFe."""
        # Componentes
        uf = self.nota.empresa.endereco_uf_ibge_code or '35' # Default SP se não tiver
        data = self.nota.data_emissao
        aamm = f"{data.year % 100:02d}{data.month:02d}"
        cnpj = self.nota.empresa.cnpj_limpo
        mod = self.nota.modelo
        serie = f"{self.nota.serie:03d}"
        ncnf = f"{self.nota.numero:09d}"
        tp_emis = self.nota.tipo_emissao
        
        # Código Numérico Aleatório (cNF) - 8 dígitos
        # Para simplificar e manter reprodutibilidade, usaremos o número da nota com padding diferente ou random
        # O manual diz que cNF é aleatório.
        cnf = f"{random.randint(0, 99999999):08d}"
        
        # Montar chave sem DV
        chave_base = f"{uf}{aamm}{cnpj}{mod}{serie}{ncnf}{tp_emis}{cnf}"
        
        # Calcular DV (Módulo 11)
        dv = self._calcular_dv_modulo11(chave_base)
        
        self.nota.chave_acesso = f"{chave_base}{dv}"

    def _calcular_dv_modulo11(self, chave: str) -> str:
        """Calcula dígito verificador módulo 11."""
        pesos = [2, 3, 4, 5, 6, 7, 8, 9]
        soma = 0
        for i, char in enumerate(reversed(chave)):
            peso = pesos[i % len(pesos)]
            soma += int(char) * peso
            
        resto = soma % 11
        if resto == 0 or resto == 1:
            return '0'
        return str(11 - resto)

    def _build_ide(self):
        """Grupo B. Identificação da NFe."""
        ide = etree.SubElement(self.inf_nfe, "ide")
        
        self._tag(ide, "cUF", self.nota.empresa.endereco_uf_ibge_code or '35')
        self._tag(ide, "cNF", self.nota.chave_acesso[35:43]) # Código Numérico da chave
        self._tag(ide, "natOp", self.nota.natureza_operacao)
        self._tag(ide, "mod", self.nota.modelo)
        self._tag(ide, "serie", str(self.nota.serie))
        self._tag(ide, "nNF", str(self.nota.numero))
        self._tag(ide, "dhEmi", self.nota.data_emissao.isoformat())
        self._tag(ide, "tpNF", "1") # 1=Saída
        self._tag(ide, "idDest", "1") # 1=Operação interna (por enquanto fixo)
        self._tag(ide, "cMunFG", self.nota.empresa.endereco_municipio_ibge or '3550308') # Default SP
        self._tag(ide, "tpImp", "1") # 1=Retrato
        self._tag(ide, "tpEmis", self.nota.tipo_emissao)
        self._tag(ide, "cDV", self.nota.chave_acesso[-1])
        self._tag(ide, "tpAmb", self.nota.ambiente)
        self._tag(ide, "finNFe", self.nota.finalidade)
        self._tag(ide, "indFinal", "1") # 1=Consumidor final
        self._tag(ide, "indPres", "1") # 1=Operação presencial
        self._tag(ide, "procEmi", "0") # 0=Emissão com aplicativo do contribuinte
        self._tag(ide, "verProc", "NixPDV 1.0")

    def _build_emit(self):
        """Grupo C. Emitente."""
        emit = etree.SubElement(self.inf_nfe, "emit")
        
        self._tag(emit, "CNPJ", self.nota.empresa.cnpj_limpo)
        self._tag(emit, "xNome", self.nota.empresa.razao_social[:60])
        self._tag(emit, "xFant", (self.nota.empresa.nome_fantasia or self.nota.empresa.razao_social)[:60])
        
        ender = etree.SubElement(emit, "enderEmit")
        # TODO: Pegar endereço real da empresa. Usando dados da venda por enquanto se faltar na empresa
        # Assumindo que empresa tem campos de endereço (precisamos garantir isso no models)
        self._tag(ender, "xLgr", self.nota.empresa.logradouro or "Rua Teste")
        self._tag(ender, "nro", self.nota.empresa.numero or "123")
        self._tag(ender, "xBairro", self.nota.empresa.bairro or "Centro")
        self._tag(ender, "cMun", self.nota.empresa.endereco_municipio_ibge or "3550308")
        self._tag(ender, "xMun", self.nota.empresa.cidade or "Sao Paulo")
        self._tag(ender, "UF", self.nota.empresa.uf or "SP")
        self._tag(ender, "CEP", (self.nota.empresa.cep or "01001000").replace('-', ''))
        self._tag(ender, "cPais", "1058") # Brasil
        self._tag(ender, "xPais", "BRASIL")
        
        self._tag(emit, "IE", self.nota.empresa.inscricao_estadual.replace('.', '').replace('-', ''))
        self._tag(emit, "CRT", "1") # 1=Simples Nacional

    def _build_dest(self):
        """Grupo E. Destinatário."""
        dest = etree.SubElement(self.inf_nfe, "dest")
        
        cliente = self.nota.cliente
        cpf_cnpj = cliente.cpf_cnpj_limpo
        
        if len(cpf_cnpj) == 14:
            self._tag(dest, "CNPJ", cpf_cnpj)
        else:
            self._tag(dest, "CPF", cpf_cnpj)
            
        self._tag(dest, "xNome", cliente.nome[:60])
        
        # Endereço
        endereco = cliente.enderecos.first() # Já validado no service
        if endereco:
            ender = etree.SubElement(dest, "enderDest")
            self._tag(ender, "xLgr", endereco.logradouro[:60])
            self._tag(ender, "nro", endereco.numero[:60])
            self._tag(ender, "xBairro", endereco.bairro[:60])
            self._tag(ender, "cMun", endereco.codigo_municipio_ibge)
            self._tag(ender, "xMun", endereco.cidade[:60])
            self._tag(ender, "UF", endereco.uf)
            self._tag(ender, "CEP", endereco.cep.replace('-', ''))
            self._tag(ender, "cPais", "1058")
            self._tag(ender, "xPais", "BRASIL")
            
        self._tag(dest, "indIEDest", "9") # 9=Não Contribuinte (simplificado para MVP)

    def _build_det(self):
        """Grupo H. Detalhamento de Produtos e Serviços."""
        for i, item in enumerate(self.nota.itens.all(), start=1):
            det = etree.SubElement(self.inf_nfe, "det", nItem=str(i))
            
            # Produto
            prod = etree.SubElement(det, "prod")
            self._tag(prod, "cProd", item.codigo_produto[:60])
            self._tag(prod, "cEAN", "SEM GTIN")
            self._tag(prod, "xProd", item.descricao_produto[:120])
            self._tag(prod, "NCM", item.ncm)
            if item.cest:
                self._tag(prod, "CEST", item.cest)
            self._tag(prod, "CFOP", item.cfop)
            self._tag(prod, "uCom", item.unidade_comercial)
            self._tag(prod, "qCom", self._fmt_qtd(item.quantidade))
            self._tag(prod, "vUnCom", self._fmt_dec(item.valor_unitario, 10))
            self._tag(prod, "vProd", self._fmt_dec(item.valor_total))
            self._tag(prod, "cEANTrib", "SEM GTIN")
            self._tag(prod, "uTrib", item.unidade_comercial)
            self._tag(prod, "qTrib", self._fmt_qtd(item.quantidade))
            self._tag(prod, "vUnTrib", self._fmt_dec(item.valor_unitario, 10))
            self._tag(prod, "indTot", "1") # 1=Compõe valor total da NF
            
            # Impostos
            imposto = etree.SubElement(det, "imposto")
            
            # ICMS (Simples Nacional)
            icms = etree.SubElement(imposto, "ICMS")
            icms_sn = etree.SubElement(icms, "ICMSSN102") # Simplificado 102
            self._tag(icms_sn, "orig", item.origem)
            self._tag(icms_sn, "CSOSN", item.csosn)
            
            # PIS
            pis = etree.SubElement(imposto, "PIS")
            pis_nt = etree.SubElement(pis, "PISNT") # Não tributado
            self._tag(pis_nt, "CST", "07") # 07=Isento
            
            # COFINS
            cofins = etree.SubElement(imposto, "COFINS")
            cofins_nt = etree.SubElement(cofins, "COFINSNT") # Não tributado
            self._tag(cofins_nt, "CST", "07")

    def _build_total(self):
        """Grupo W. Total da NFe."""
        total = etree.SubElement(self.inf_nfe, "total")
        icms_tot = etree.SubElement(total, "ICMSTot")
        
        self._tag(icms_tot, "vBC", "0.00")
        self._tag(icms_tot, "vICMS", "0.00")
        self._tag(icms_tot, "vICMSDeson", "0.00")
        self._tag(icms_tot, "vFCP", "0.00")
        self._tag(icms_tot, "vBCST", "0.00")
        self._tag(icms_tot, "vST", "0.00")
        self._tag(icms_tot, "vFCPST", "0.00")
        self._tag(icms_tot, "vFCPSTRet", "0.00")
        self._tag(icms_tot, "vProd", self._fmt_dec(self.nota.valor_total_produtos))
        self._tag(icms_tot, "vFrete", self._fmt_dec(self.nota.valor_frete))
        self._tag(icms_tot, "vSeg", self._fmt_dec(self.nota.valor_seguro))
        self._tag(icms_tot, "vDesc", self._fmt_dec(self.nota.valor_desconto))
        self._tag(icms_tot, "vII", "0.00")
        self._tag(icms_tot, "vIPI", "0.00")
        self._tag(icms_tot, "vIPIDevol", "0.00")
        self._tag(icms_tot, "vPIS", "0.00")
        self._tag(icms_tot, "vCOFINS", "0.00")
        self._tag(icms_tot, "vOutro", self._fmt_dec(self.nota.valor_outras_despesas))
        self._tag(icms_tot, "vNF", self._fmt_dec(self.nota.valor_total_nota))

    def _build_transp(self):
        """Grupo X. Transporte."""
        transp = etree.SubElement(self.inf_nfe, "transp")
        self._tag(transp, "modFrete", "9") # 9=Sem Ocorrência de Transporte

    def _build_pag(self):
        """Grupo YA. Pagamento."""
        pag = etree.SubElement(self.inf_nfe, "pag")
        det_pag = etree.SubElement(pag, "detPag")
        
        # Simplificado: Dinheiro
        self._tag(det_pag, "tPag", "01") # 01=Dinheiro
        self._tag(det_pag, "vPag", self._fmt_dec(self.nota.valor_total_nota))

    def _build_inf_adic(self):
        """Grupo Z. Informações Adicionais."""
        if self.nota.observacoes:
            inf_adic = etree.SubElement(self.inf_nfe, "infAdic")
            self._tag(inf_adic, "infCpl", self.nota.observacoes[:5000])

    def _tag(self, parent, name, value):
        """Cria uma tag com valor se não for None."""
        if value is not None:
            elem = etree.SubElement(parent, name)
            elem.text = str(value)
            return elem
        return None

    def _fmt_dec(self, value, places=2):
        """Formata decimal."""
        if value is None:
            return "0.00"
        return f"{value:.{places}f}"

    def _fmt_qtd(self, value):
        """Formata quantidade (4 casas)."""
        if value is None:
            return "0.0000"
        return f"{value:.4f}"
