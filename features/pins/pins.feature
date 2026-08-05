# language: pt

Funcionalidade: Pins de assinatura na API D4Sign
  Como consumidor da API D4Sign
  Quero posicionar pins de assinatura, rubrica e selo
  Para validar o endpoint de pins

  Contexto:
    Dado que a API D4Sign está configurada

  @api @upload @signature @critical @pins
  Cenário: Upload com signatário e pins de assinatura, rubrica e selo
    Quando eu faço upload de um PDF para o cofre configurado
    E eu adiciono um signatário por e-mail ao documento criado
    E eu adiciono pins de assinatura, rubrica e selo ao documento
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "success"
