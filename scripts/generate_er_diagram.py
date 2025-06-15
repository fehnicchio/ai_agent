import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import matplotlib.lines as lines

def create_er_diagram():
    # Configurações do gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title('Diagrama Entidade-Relacionamento\nSistema de Clientes e Pedidos', fontsize=16, pad=20)
    
    # Estilos
    entity_style = {'facecolor': 'lightblue', 'edgecolor': 'black', 'boxstyle': 'round,pad=0.5'}
    relationship_style = {'facecolor': 'pink', 'edgecolor': 'black', 'boxstyle': 'round,pad=0.5'}
    
    # Entidade CLIENTES
    clientes_text = "CLIENTES\n\n" \
                    "id: SERIAL (PK)\n" \
                    "nome: VARCHAR(100)\n" \
                    "email: VARCHAR(100)\n" \
                    "estado: CHAR(2)\n" \
                    "data_cadastro: DATE"
    
    ax.text(2, 4, clientes_text, 
            bbox=entity_style, 
            ha='center', va='center', 
            fontsize=10, 
            fontfamily='monospace')
    
    # Entidade PEDIDOS
    pedidos_text = "PEDIDOS\n\n" \
                   "id: SERIAL (PK)\n" \
                   "cliente_id: INTEGER (FK)\n" \
                   "produto: VARCHAR(50)\n" \
                   "quantidade: INTEGER\n" \
                   "valor: NUMERIC(10,2)\n" \
                   "data_pedido: DATE"
    
    ax.text(8, 4, pedidos_text, 
            bbox=entity_style, 
            ha='center', va='center', 
            fontsize=10, 
            fontfamily='monospace')
    
    # Relacionamento FAZ
    ax.text(5, 4, "FAZ\n(1:N)", 
            bbox=relationship_style, 
            ha='center', va='center', 
            fontsize=12)
    
    # Conexões
    ax.annotate("", xy=(3.5, 4), xytext=(2.5, 4),
                arrowprops=dict(arrowstyle="->", lw=2, color='black'))
    
    ax.annotate("", xy=(6.5, 4), xytext=(5.5, 4),
                arrowprops=dict(arrowstyle="->", lw=2, color='black'))
    
    # Legenda da cardinalidade
    ax.text(3, 3.5, "1", fontsize=12, ha='center')
    ax.text(7, 3.5, "N", fontsize=12, ha='center')
    
    # Salva como PNG
    plt.savefig('docs/ER_diagram.png', dpi=300, bbox_inches='tight')
    print("Diagrama ER gerado com sucesso em 'docs/ER_diagram.png'")

if __name__ == "__main__":
    create_er_diagram()