"""
Signer para assinatura de NFe utilizando certificado A1 (PKCS#12).
"""
import base64
from lxml import etree
from signxml import XMLSigner, methods
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from django.core.exceptions import ValidationError

class NFeSigner:
    """
    Assinador de XMLs de NFe padrão ICP-Brasil.
    Utiliza signxml para gerar assinatura XMLDSig.
    """
    
    def __init__(self, certificado_pfx_bytes, senha):
        """
        Inicializa com certificado A1 (.pfx/.p12).
        
        Args:
            certificado_pfx_bytes: Conteúdo do arquivo .pfx em bytes
            senha: Senha do certificado
        """
        self.cert_bytes = certificado_pfx_bytes
        self.senha = senha
        self.private_key = None
        self.certificate = None
        
        self._load_certificate()
        
    def _load_certificate(self):
        """Carrega chave privada e certificado do PFX."""
        try:
            p12 = pkcs12.load_key_and_certificates(
                self.cert_bytes,
                self.senha.encode() if isinstance(self.senha, str) else self.senha
            )
            self.private_key = p12[0]
            self.certificate = p12[1]
            
            if not self.private_key or not self.certificate:
                raise ValidationError("Certificado inválido ou sem chave privada.")
                
        except Exception as e:
            raise ValidationError(f"Erro ao carregar certificado: {str(e)}")
            
    def sign_nfe(self, xml_content):
        """
        Assina o XML da NFe.
        
        Args:
            xml_content: String ou bytes do XML da NFe
            
        Returns:
            str: XML assinado
        """
        # Parse XML
        if isinstance(xml_content, str):
            xml_content = xml_content.encode('utf-8')
            
        try:
            root = etree.fromstring(xml_content)
        except etree.XMLSyntaxError:
            raise ValidationError("XML inválido para assinatura.")
            
        # Identificar tag a ser assinada (infNFe)
        inf_nfe = root.find(".//{http://www.portalfiscal.inf.br/nfe}infNFe")
        if inf_nfe is None:
            # Tenta sem namespace
            inf_nfe = root.find(".//infNFe")
            
        if inf_nfe is None:
            raise ValidationError("Tag infNFe não encontrada.")
            
        uri_id = inf_nfe.get("Id")
        if not uri_id:
            raise ValidationError("Atributo Id não encontrado na tag infNFe.")
            
        # Configurar Signer
        # SEFAZ exige:
        # - Reference URI apontando para o ID da infNFe
        # - Transformations: Enveloped e C14N
        # - Digest Method: SHA1
        # - Signature Method: RSA-SHA1
        
        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha1",
            digest_algorithm="sha1",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        )
        
        # Assinar
        signed_root = signer.sign(
            root,
            key=self.private_key,
            cert=self.certificate,
            reference_uri=f"#{uri_id}"
        )
        
        # Ajustar namespace da assinatura (signxml coloca ns0, mas SEFAZ prefere default ou ds)
        # O signxml já gera válido, mas às vezes precisamos limpar namespaces extras
        
        return etree.tostring(signed_root, encoding='UTF-8', xml_declaration=True).decode('utf-8')
