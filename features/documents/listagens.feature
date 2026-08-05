# language: pt

Funcionalidade: Listagens de documentos na API D4Sign
  Como consumidor da API D4Sign
  Quero consultar documentos, webhooks e pins
  Para validar os endpoints de listagem (GET)

  Contexto:
    Dado que a API D4Sign está configurada

  @api @smoke @critical @documents
  Cenário: Listar todos os documentos da conta
    Quando eu consulto todos os documentos da conta
    Então a resposta deve ter status 200
    E o tempo de resposta deve ser menor que 30 segundos

  @api @critical @documents
  Cenário: Listar documento específico
    Quando eu consulto o documento específico configurado
    Então a resposta deve ter status 200
    E o corpo da resposta não deve estar vazio

  @api @regression @documents
  Cenário: Listar documentos por fase
    Quando eu consulto os documentos pela fase configurada
    Então a resposta deve ter status 200

  @api @critical @documents
  Cenário: Listar documentos de um cofre específico
    Quando eu consulto os documentos do cofre configurado
    Então a resposta deve ter status 200

  @api @regression @documents @webhooks
  Cenário: Listar webhooks de um documento específico
    Quando eu consulto os webhooks do documento configurado
    Então a resposta deve ter status 200

  @api @signature @critical @documents @pins
  Cenário: Listar pins do documento
    Quando eu consulto os pins do documento configurado
    Então a resposta deve ter status 200
    E o corpo da resposta não deve estar vazio
    E o primeiro pin deve refletir os dados esperados do ambiente
