# SPEC — AI Management System
Versão: v1.3 (Documento Mestre consolidado)

---

## 1. Conceitos base

### Cliente
Entidade comercial/logística associada a uma ou mais moradas.

### Contacto
Pessoa que interage via WhatsApp.
- Identificada por telefone (único).
- Tem preferências próprias (ex.: sugestões).

### Morada
Local de entrega associado a um cliente.
- Identificada por um alias semântico (Casa, Avó, Trabalho, etc.).

### Encomenda
Pedido de produtos com:
- cliente,
- contacto,
- morada específica,
- data/hora,
- linhas de produto.

---

## 2. Regras de negócio críticas

### 2.1 Consentimento para sugestões (OBRIGATÓRIO)

Campo: `contacts.accepts_suggestions`

Estados:
- `null` → ainda não perguntado
- `true` → aceita sugestões
- `false` → não aceita sugestões

Regras:
- Sem consentimento explícito → **não sugerir nada**
- Perguntar apenas uma vez (retry máximo 1)
- Ambiguidade → assumir **false**
- Preferência é por contacto, não por cliente
- Pode ser alterada a qualquer momento

Pergunta padrão:
> “Quer receber sugestões baseadas em histórico de compras ou para conhecer produtos novos?”

---

### 2.2 Moradas com alias

- Alias é obrigatório
- Alias é único por cliente (case-insensitive)
- Alias é usado apenas para interação
- Nunca usar alias como chave técnica

Recomendação técnica:
- guardar `alias_normalized = lower(trim(alias))`
- constraint: unique(customer_id, alias_normalized)

---

### 2.3 LLM-first (governação)

O LLM:
- interpreta mensagens,
- identifica intenção,
- extrai entidades,
- sugere perguntas de clarificação.

O LLM **não**:
- cria registos,
- altera dados,
- aplica regras de negócio.

---

## 3. Estados

### Encomendas
- draft
- confirmed
- planned
- in_production
- ready
- delivered
- cancelled

### Produção
- planned
- in_progress
- completed
- cancelled

---

## 4. Scoring de produtos habituais

### Janela temporal
- Últimos **14 dias**
- Apenas encomendas confirmadas/entregues

### Componentes

F — Frequência  
- 1 compra: 15  
- 2–3: 35  
- 4–6: 55  
- >6: 70  

R — Recência  
- ≤3 dias: 40  
- 4–7: 25  
- 8–14: 10  

C — Consistência  
- ≥75%: 30  
- 50–74%: 20  
- 25–49%: 10  

Q — Estabilidade quantidade  
- <20%: 20  
- 20–40%: 10  

K — Compatibilidade  
- comprado junto: 20  
- mesma categoria: 10  

Score máximo: 180

### Patamares
- ≥110 → habitual forte
- 80–109 → recorrente
- 50–79 → ocasional
- <50 → irrelevante

### Exclusões
- produto já no pedido
- recusado nas últimas 2 encomendas
- ignorado na encomenda anterior
- indisponível
- contexto temporal incompatível

---

## 5. Rastreabilidade

### Backward trace
Produto → lote produção → lotes MP → fornecedor

### Forward trace
Lote MP → produções → encomendas → clientes/moradas

---

## 6. Auditoria

- Chat histórico integral
- Registo de input/output do LLM
- Decisão final do backend
- Alterações manuais auditadas
