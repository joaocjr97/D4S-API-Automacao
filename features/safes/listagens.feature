# language: pt

Funcionalidade: Listagens de cofres na API D4Sign
  Como consumidor da API D4Sign
  Quero consultar os cofres da conta
  Para validar o endpoint GET /safes

  Contexto:
    Dado que a API D4Sign está configurada

  @api @smoke @safes
  Cenário: Listar todos os cofres da conta
    Quando eu consulto todos os cofres da conta
    Então a resposta deve ter status 200
    E o tempo de resposta deve ser menor que 30 segundos
