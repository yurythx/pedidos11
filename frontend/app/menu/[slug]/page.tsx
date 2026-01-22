'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { publicMenuService, PublicEmpresa, PublicCategoria } from '@/features/menu/services/publicMenuService';
import { formatBRL } from '@/utils/currency';

export default function MenuPage() {
  const params = useParams();
  const slug = params.slug as string;
  
  const [empresa, setEmpresa] = useState<PublicEmpresa | null>(null);
  const [categorias, setCategorias] = useState<PublicCategoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('');

  useEffect(() => {
    if (slug) {
      Promise.all([
        publicMenuService.getInfo(slug),
        publicMenuService.getCatalogo(slug)
      ]).then(([info, cat]) => {
        setEmpresa(info);
        setCategorias(cat);
        if (cat.length > 0) setActiveCategory(cat[0].id);
      }).finally(() => setLoading(false));
    }
  }, [slug]);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">Carregando cardápio...</div>;
  if (!empresa) return <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">Restaurante não encontrado.</div>;

  return (
    <div className="min-h-screen bg-gray-50 pb-24 font-sans">
      {/* Header / Capa */}
      <div className="h-48 bg-gray-900 relative">
        {empresa.logo && (
            <img src={empresa.logo} className="w-full h-full object-cover opacity-60" alt={empresa.nome_fantasia} />
        )}
        <div className="absolute bottom-0 left-0 p-6 text-white w-full bg-gradient-to-t from-black/90 to-transparent">
            <h1 className="text-3xl font-bold mb-1">{empresa.nome_fantasia}</h1>
            <div className="flex items-center gap-2 text-sm opacity-90">
                <span className="bg-green-500 text-white px-2 py-0.5 rounded text-xs font-bold">ABERTO</span>
                <span>• 40-50 min • Entrega Grátis</span>
            </div>
        </div>
      </div>

      {/* Categorias Sticky */}
      <div className="sticky top-0 bg-white shadow-sm z-20 overflow-x-auto whitespace-nowrap px-4 py-3 flex gap-2 no-scrollbar border-b">
        {categorias.map(cat => (
            <button
                key={cat.id}
                onClick={() => {
                    setActiveCategory(cat.id);
                    const el = document.getElementById(`cat-${cat.id}`);
                    if (el) {
                        const y = el.getBoundingClientRect().top + window.scrollY - 80; // Offset do header
                        window.scrollTo({ top: y, behavior: 'smooth' });
                    }
                }}
                className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${
                    activeCategory === cat.id 
                    ? 'text-white shadow-md transform scale-105' 
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
                style={{ backgroundColor: activeCategory === cat.id ? (empresa.cor_primaria || '#000') : undefined }}
            >
                {cat.nome}
            </button>
        ))}
      </div>

      {/* Lista de Produtos */}
      <div className="p-4 space-y-8 max-w-2xl mx-auto">
        {categorias.map(cat => (
            <div key={cat.id} id={`cat-${cat.id}`} className="scroll-mt-24">
                <h2 className="text-xl font-bold mb-4 text-gray-800 border-l-4 pl-3" style={{ borderColor: empresa.cor_primaria }}>
                    {cat.nome}
                </h2>
                <div className="grid gap-4">
                    {cat.produtos.map(prod => (
                        <div 
                            key={prod.id} 
                            className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex gap-4 active:scale-[0.98] transition-transform cursor-pointer hover:shadow-md"
                            onClick={() => alert('Em breve: Adicionar ' + prod.nome)}
                        >
                            <div className="flex-1 flex flex-col justify-between">
                                <div>
                                    <h3 className="font-semibold text-gray-800 text-lg">{prod.nome}</h3>
                                    <p className="text-sm text-gray-500 line-clamp-2 mt-1 mb-2 leading-relaxed">{prod.descricao}</p>
                                </div>
                                <p className="font-bold text-gray-900">{formatBRL(parseFloat(prod.preco_venda))}</p>
                            </div>
                            {prod.imagem && (
                                <div className="w-28 h-28 bg-gray-100 rounded-xl overflow-hidden shrink-0 shadow-inner">
                                    <img src={prod.imagem} alt={prod.nome} className="w-full h-full object-cover" />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        ))}
      </div>

      {/* Botão Flutuante Sacola */}
      <div className="fixed bottom-6 left-4 right-4 max-w-2xl mx-auto z-30">
        <button 
            className="w-full py-4 rounded-2xl text-white font-bold shadow-xl flex justify-between px-6 items-center hover:opacity-90 transition-opacity"
            style={{ backgroundColor: empresa.cor_primaria || '#000' }}
        >
            <div className="flex items-center gap-2">
                <span className="bg-white/20 px-2 py-1 rounded text-xs">0</span>
                <span>Ver Sacola</span>
            </div>
            <span>R$ 0,00</span>
        </button>
      </div>
    </div>
  );
}
