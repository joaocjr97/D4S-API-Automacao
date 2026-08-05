# language: pt

Funcionalidade: Fluxos de signatários na API D4Sign
  Como consumidor da API D4Sign
  Quero cadastrar, alterar e remover signatários
  Para validar o ciclo de assinatura via API

  Contexto:
    Dado que a API D4Sign está configurada

  @api @upload @signature @critical @signers
  Cenário: Upload com signatário por e-mail e envio para assinatura
    Quando eu faço upload de um PDF para o cofre configurado
    E eu adiciono um signatário por e-mail ao documento criado
    E eu envio o documento para assinatura
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "File sent to successfully signing"

  @api @upload @signature @regression @signers
  Cenário: Upload com signatário por WhatsApp e envio para assinatura
    Quando eu faço upload de um PDF para o cofre configurado
    E eu adiciono um signatário por WhatsApp ao documento criado
    E eu envio o documento para assinatura
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "File sent to successfully signing"

  @api @signature @regression @signers
  Cenário: Alterar e remover signatário do documento
    Quando eu faço upload de um PDF para o cofre configurado
    E eu adiciono um signatário por e-mail ao documento criado
    E eu altero o e-mail do signatário cadastrado
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "E-mail changed"
    Quando eu removo o signatário alterado do documento
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "E-mail has removed"
