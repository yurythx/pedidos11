"""
Cliente SOAP para comunicação com a SEFAZ.
"""
import requests
from requests_pkcs12 import Pkcs12Adapter
from lxml import etree
from django.core.exceptions import ValidationError
from tenant.models import AmbienteNFe

class SefazClient:
    """
    Cliente para consumo dos Web Services da SEFAZ.
    Suporta NFe 4.00.
    """
    
    # URLs dos Web Services (Exemplo SP)
    # TODO: Mover para arquivo de configuração ou banco de dados por UF
    URLS = {
        'SP': {
            AmbienteNFe.HOMOLOGACAO: {
                'NfeAutorizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx',
                'NfeRetAutorizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nferetautorizacao4.asmx',
            },
            AmbienteNFe.PRODUCAO: {
                'NfeAutorizacao': 'https://nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx',
                'NfeRetAutorizacao': 'https://nfe.fazenda.sp.gov.br/ws/nferetautorizacao4.asmx',
            }
        }
    }
    
    def __init__(self, empresa):
        """
        Inicializa cliente com certificado da empresa.
        
        Args:
            empresa: Instância do model Empresa com certificado configurado.
        """
        self.empresa = empresa
        self.uf = empresa.uf or 'SP'
        self.ambiente = empresa.ambiente_nfe
        
        if not self.empresa.certificado_digital:
            raise ValidationError("Empresa sem certificado digital configurado.")
            
        self.session = self._create_session()
        
    def _create_session(self):
        """Cria sessão requests configurada com certificado PFX."""
        session = requests.Session()
        
        # Carregar bytes do certificado
        try:
            with self.empresa.certificado_digital.open('rb') as f:
                pfx_bytes = f.read()
        except Exception as e:
            raise ValidationError(f"Erro ao ler certificado: {e}")
            
        # Configurar adaptador PKCS12
        # requests-pkcs12 permite passar o conteúdo do PFX e a senha
        adapter = Pkcs12Adapter(
            pkcs12_data=pfx_bytes,
            pkcs12_password=self.empresa.senha_certificado
        )
        
        # Montar adaptador para https
        session.mount('https://', adapter)
        
        return session
        
    def autorizar_nfe(self, xml_assinado, id_lote='1'):
        """
        Envia lote de NFe para autorização (Síncrono ou Assíncrono).
        Para NFe 4.00, o método padrão é NfeAutorizacao.
        
        Args:
            xml_assinado: String do XML da NFe assinada (apenas o conteúdo da NFe)
            id_lote: Identificador do lote (pode ser sequencial)
            
        Returns:
            Dict com resposta (status, motivo, recibo, etc)
        """
        url = self._get_url('NfeAutorizacao')
        
        # Montar Envelope SOAP
        xml_content = xml_assinado.replace("<?xml version='1.0' encoding='UTF-8'?>", "")
        envelope = self._build_soap_envelope(
            method='nfeAutorizacaoLote',
            content=f"""
            <nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4">
                <enviNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
                    <idLote>{id_lote}</idLote>
                    <indSinc>1</indSinc>
                    {xml_content}
                </enviNFe>
            </nfeDadosMsg>
            """
        )
        
        # Enviar requisição
        response = self._post(url, envelope)
        
        # Parse resposta
        return self._parse_retorno_autorizacao(response)
        
    def consultar_recibo(self, numero_recibo):
        """
        Consulta o status de processamento de um lote (Recibo).
        Método: NfeRetAutorizacao.
        
        Args:
            numero_recibo: Número do recibo retornado pela autorização assíncrona.
            
        Returns:
            Dict com o resultado do processamento.
        """
        url = self._get_url('NfeRetAutorizacao')
        
        # Montar Envelope SOAP
        envelope = self._build_soap_envelope(
            method='nfeRetAutorizacaoLote',
            content=f"""
            <nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeRetAutorizacao4">
                <consReciNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
                    <tpAmb>{self.ambiente}</tpAmb>
                    <nRec>{numero_recibo}</nRec>
                </consReciNFe>
            </nfeDadosMsg>
            """
        )
        
        # Enviar requisição
        response = self._post(url, envelope)
        
        # Parse resposta (similar ao retorno de autorização, mas structure retConsReciNFe)
        return self._parse_retorno_recibo(response)

    def _parse_retorno_recibo(self, xml_response):
        """Parse do retorno da consulta de recibo."""
        root = etree.fromstring(xml_response)
        
        ns_soap = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
        body = root.find('.//soap:Body', ns_soap)
        
        ret_cons = body.find('.//{http://www.portalfiscal.inf.br/nfe}retConsReciNFe')
        if ret_cons is None:
            ret_cons = body.find('.//retConsReciNFe')
            
        if ret_cons is None:
            raise ValidationError("Resposta inválida da SEFAZ: retConsReciNFe não encontrado.")
            
        c_stat = ret_cons.findtext('.//{http://www.portalfiscal.inf.br/nfe}cStat') or ret_cons.findtext('.//cStat')
        x_motivo = ret_cons.findtext('.//{http://www.portalfiscal.inf.br/nfe}xMotivo') or ret_cons.findtext('.//xMotivo')
        
        resultado = {
            'cStat': c_stat,
            'xMotivo': x_motivo,
            'xml_raw': etree.tostring(ret_cons, encoding='unicode')
        }
        
        # Extrair protocolos
        prot_nfe = ret_cons.find('.//{http://www.portalfiscal.inf.br/nfe}protNFe')
        if prot_nfe is not None:
            inf_prot = prot_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}infProt')
            if inf_prot is not None:
                resultado['protocolo'] = {
                    'nProt': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}nProt'),
                    'cStat': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}cStat'),
                    'xMotivo': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}xMotivo'),
                    'dhRecbto': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}dhRecbto'),
                    'chNFe': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}chNFe'),
                    'xml_prot': etree.tostring(prot_nfe, encoding='unicode')
                }
                
        return resultado

    def _get_url(self, servico):
        """Retorna URL do serviço para UF e Ambiente configurados."""
        urls_uf = self.URLS.get(self.uf, self.URLS['SP']) # Fallback SP
        return urls_uf[self.ambiente][servico]
        
    def _build_soap_envelope(self, method, content):
        """Monta envelope SOAP 1.2."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
            <soap12:Body>
                {content}
            </soap12:Body>
        </soap12:Envelope>
        """
        
    def _post(self, url, data):
        """Realiza POST SOAP."""
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8'
        }
        
        try:
            response = self.session.post(url, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Erro na comunicação com SEFAZ: {str(e)}")
            
    def _parse_retorno_autorizacao(self, xml_response):
        """
        Faz parse do retorno da autorização.
        
        Pode retornar:
        - Recibo (infRec) se foi assíncrono ou lote processado
        - ProtNFe se foi síncrono e processado direto
        """
        root = etree.fromstring(xml_response)
        
        # Namespace SOAP body
        ns_soap = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}
        body = root.find('.//soap:Body', ns_soap)
        
        # Extrair nfeResultMsg
        # Como o namespace pode variar ou ser default, vamos buscar por tag name local
        ret_envi = body.find('.//{http://www.portalfiscal.inf.br/nfe}retEnviNFe')
        if ret_envi is None:
             # Tenta sem namespace
            ret_envi = body.find('.//retEnviNFe')
            
        if ret_envi is None:
            raise ValidationError("Resposta inválida da SEFAZ: retEnviNFe não encontrado.")
            
        c_stat = ret_envi.findtext('.//{http://www.portalfiscal.inf.br/nfe}cStat') or ret_envi.findtext('.//cStat')
        x_motivo = ret_envi.findtext('.//{http://www.portalfiscal.inf.br/nfe}xMotivo') or ret_envi.findtext('.//xMotivo')
        
        resultado = {
            'cStat': c_stat,
            'xMotivo': x_motivo,
            'xml_raw': etree.tostring(ret_envi, encoding='unicode')
        }
        
        # Se síncrono, pode vir protNFe direto
        prot_nfe = ret_envi.find('.//{http://www.portalfiscal.inf.br/nfe}protNFe')
        if prot_nfe is not None:
            inf_prot = prot_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}infProt')
            if inf_prot is not None:
                resultado['protocolo'] = {
                    'nProt': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}nProt'),
                    'cStat': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}cStat'),
                    'xMotivo': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}xMotivo'),
                    'dhRecbto': inf_prot.findtext('.//{http://www.portalfiscal.inf.br/nfe}dhRecbto'),
                    'xml_prot': etree.tostring(prot_nfe, encoding='unicode')
                }
        
        return resultado
