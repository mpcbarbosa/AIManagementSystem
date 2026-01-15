# AI Management System (LLM-First)

## Objetivo
Sistema LLM-first para gestão de:
- encomendas via WhatsApp,
- clientes, contactos e moradas com alias,
- produção por lotes,
- custos reais de produção,
- rastreabilidade alimentar completa,
- sugestões inteligentes de produtos (com consentimento explícito).

O sistema é desenvolvido para:
- produção alimentar artesanal,
- consumo frequente (diário),
- WhatsApp como canal principal,
- backend robusto e auditável.

---

## Princípios fundamentais

1. **LLM interpreta, backend decide**
   - O LLM apenas interpreta mensagens e devolve dados estruturados.
   - O backend valida regras de negócio e persiste dados.

2. **WhatsApp-first**
   - Linguagem natural, sem formulários rígidos.
   - Experiência simples para o cliente.

3. **Consentimento explícito para sugestões**
   - Cada contacto decide se quer ou não receber sugestões.
   - Sem consentimento → zero sugestões (habituais ou novos produtos).

4. **Rastreabilidade total**
   - Fornecedor → lote MP → produção → encomenda → cliente/morada.

5. **Auditabilidade**
   - Chat histórico completo.
   - Registo de todas as decisões do LLM.

---

## Estrutura do repositório

