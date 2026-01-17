"""
Product Matcher - Sugestão inteligente de produtos para itens de NFe.

Estratégias de matching:
1. EAN/Código de Barras (100% confiança)
2. Vínculo ProdutoFornecedor existente (95%)
3. Fuzzy matching por nome (75-90%)
"""
from typing import List, Dict, Optional
from fuzzywuzzy import fuzz
from catalog.models import Produto
from nfe.models import ProdutoFornecedor


class ProductMatcher:
    """
    Matcher inteligente que sugere produtos do sistema
    para itens de NFe baseado em múltiplas estratégias.
    """
    
    # Thresholds
    MIN_FUZZY_SCORE = 75  # Score mínimo para fuzzy matching
    MAX_SUGGESTIONS = 5    # Máximo de sugestões por item
    
    @staticmethod
    def find_matches(
        empresa,
        codigo_xml: str,
        ean: Optional[str],
        descricao: str,
        cnpj_fornecedor: Optional[str] = None
    ) -> List[Dict]:
        """
        Encontra produtos que podem corresponder ao item da NFe.
        
        Args:
            empresa: Empresa do usuário
            codigo_xml: Código do produto no XML
            ean: Código de barras (EAN/GTIN)
            descricao: Descrição do produto
            cnpj_fornecedor: CNPJ do fornecedor (opcional, melhora match)
            
        Returns:
            Lista de sugestões ordenadas por score (100 = match perfeito)
            
        Exemplo:
            [
                {
                    'produto_id': 'uuid',
                    'nome': 'Coca-Cola Lata',
                    'score': 100,
                    'motivo': 'EAN exato',
                    'fator_conversao': 12  # Se encontrou vínculo
                }
            ]
        """
        sugestoes = []
        
        # Estratégia 1: Match por EAN (prioridade máxima)
        if ean and ean != 'SEM GTIN':
            match_ean = ProductMatcher._match_by_ean(empresa, ean)
            if match_ean:
                sugestoes.append(match_ean)
                return sugestoes  # Match perfeito, não precisa tentar outras estratégias
        
        # Estratégia 2: Match por vínculo existente
        if cnpj_fornecedor:
            match_vinculo = ProductMatcher._match_by_vinculo(
                empresa, cnpj_fornecedor, codigo_xml
            )
            if match_vinculo:
                sugestoes.append(match_vinculo)
                # Vínculo é quase perfeito, retorna mas permite tentar fuzzy também
                if match_vinculo['score'] >= 95:
                    return sugestoes
        
        # Estratégia 3: Match fuzzy por nome
        fuzzy_matches = ProductMatcher._match_by_fuzzy(empresa, descricao)
        sugestoes.extend(fuzzy_matches)
        
        # Remove duplicatas (caso produto apareça em múltiplas estratégias)
        seen = set()
        unique_sugestoes = []
        for sug in sugestoes:
            if sug['produto_id'] not in seen:
                seen.add(sug['produto_id'])
                unique_sugestoes.append(sug)
        
        # Ordena por score (maior primeiro)
        unique_sugestoes.sort(key=lambda x: x['score'], reverse=True)
        
        # Retorna top N
        return unique_sugestoes[:ProductMatcher.MAX_SUGGESTIONS]
    
    @staticmethod
    def _match_by_ean(empresa, ean: str) -> Optional[Dict]:
        """Match por código de barras."""
        try:
            produto = Produto.objects.filter(
                empresa=empresa,
                codigo_barras=ean,
                is_active=True
            ).first()
            
            if produto:
                return {
                    'produto_id': str(produto.id),
                    'nome': produto.nome,
                    'codigo_barras': produto.codigo_barras,
                    'score': 100,
                    'motivo': 'EAN/Código de barras exato',
                    'estrategia': 'ean'
                }
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _match_by_vinculo(
        empresa,
        cnpj_fornecedor: str,
        codigo_xml: str
    ) -> Optional[Dict]:
        """Match por vínculo ProdutoFornecedor existente."""
        try:
            vinculo = ProdutoFornecedor.objects.filter(
                empresa=empresa,
                cnpj_fornecedor=cnpj_fornecedor,
                codigo_no_fornecedor=codigo_xml
            ).select_related('produto').first()
            
            if vinculo and vinculo.produto.is_active:
                return {
                    'produto_id': str(vinculo.produto.id),
                    'nome': vinculo.produto.nome,
                    'codigo_barras': vinculo.produto.codigo_barras,
                    'score': 95,
                    'motivo': f'Vínculo existente com {vinculo.nome_fornecedor}',
                    'estrategia': 'vinculo',
                    'fator_conversao': float(vinculo.fator_conversao),
                    'ultimo_preco': float(vinculo.ultimo_preco) if vinculo.ultimo_preco else None
                }
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _match_by_fuzzy(empresa, descricao: str) -> List[Dict]:
        """Match fuzzy por similaridade de nome."""
        if not descricao or len(descricao) < 3:
            return []
        
        matches = []
        
        try:
            # Busca produtos ativos
            produtos = Produto.objects.filter(
                empresa=empresa,
                is_active=True
            ).values('id', 'nome', 'codigo_barras')[:200]  # Limita para performance
            
            descricao_clean = descricao.lower().strip()
            
            for prod in produtos:
                nome_clean = prod['nome'].lower().strip()
                
                # Calcula similaridade
                # token_sort_ratio ignora ordem das palavras
                ratio = fuzz.token_sort_ratio(descricao_clean, nome_clean)
                
                if ratio >= ProductMatcher.MIN_FUZZY_SCORE:
                    matches.append({
                        'produto_id': str(prod['id']),
                        'nome': prod['nome'],
                        'codigo_barras': prod['codigo_barras'],
                        'score': ratio,
                        'motivo': f'Similaridade de nome ({ratio}%)',
                        'estrategia': 'fuzzy'
                    })
            
            # Ordena por score
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            # Retorna top matches
            return matches[:3]  # Top 3 fuzzy matches
            
        except Exception as e:
            print(f"Erro no fuzzy matching: {e}")
            return []
    
    @staticmethod
    def get_best_match(
        empresa,
        codigo_xml: str,
        ean: Optional[str],
        descricao: str,
        cnpj_fornecedor: Optional[str] = None,
        min_confidence: int = 80
    ) -> Optional[Dict]:
        """
        Retorna apenas o melhor match se score >= min_confidence.
        
        Args:
            min_confidence: Score mínimo para considerar match (0-100)
            
        Returns:
            Dict com melhor match ou None se não houver match confiável
        """
        matches = ProductMatcher.find_matches(
            empresa, codigo_xml, ean, descricao, cnpj_fornecedor
        )
        
        if matches and matches[0]['score'] >= min_confidence:
            return matches[0]
        
        return None
    
    @staticmethod
    def suggest_conversion_factor(
        produto,
        unidade_xml: str,
        descricao_xml: str
    ) -> float:
        """
        Sugere fator de conversão baseado em padrões comuns.
        
        Exemplos:
        - "CX 12" ou "CX/12" → 12
        - "PACOTE 6" → 6
        - "DUZIA" → 12
        - "CENTENA" → 100
        
        Args:
            produto: Produto encontrado
            unidade_xml: Unidade comercial da NFe (CX, PCT, UN, etc)
            descricao_xml: Descrição completa (pode ter "CX/12" no texto)
            
        Returns:
            Float com fator sugerido (padrão 1.0)
        """
        import re
        
        # Padrões comuns
        patterns = {
            r'(?:caixa|cx|box)[\s/]*(\d+)': lambda m: float(m.group(1)),
            r'(?:pacote|pct|pack)[\s/]*(\d+)': lambda m: float(m.group(1)),
            r'(?:fardo|fd)[\s/]*(\d+)': lambda m: float(m.group(1)),
            r'duzia': lambda m: 12.0,
            r'centena': lambda m: 100.0,
            r'milheiro': lambda m: 1000.0,
        }
        
        texto = f"{unidade_xml} {descricao_xml}".lower()
        
        for pattern, converter in patterns.items():
            match = re.search(pattern, texto)
            if match:
                try:
                    return converter(match)
                except:
                    continue
        
        # Padrão: se unidade não é UN, sugere perguntar
        if unidade_xml.upper() not in ['UN', 'UND', 'UNID', 'UNIDADE']:
            return None  # Força usuário a informar
        
        return 1.0  # Padrão 1:1
