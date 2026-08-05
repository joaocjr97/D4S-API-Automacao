# language: pt

Funcionalidade: Uploads de documentos na API D4Sign
  Como consumidor da API D4Sign
  Quero enviar documentos por PDF, base64, hash e anexo
  Para validar os endpoints de upload

  Contexto:
    Dado que a API D4Sign está configurada

  @api @upload @critical @documents
  Cenário: Upload de documento PDF
    Quando eu faço upload de um PDF para o cofre configurado
    Então a resposta deve ter status 200
    E o upload deve ter sido concluído com sucesso

  @api @upload @regression @documents
  Cenário: Upload de documento binário em base64
    Quando eu faço upload binário em base64 para o cofre configurado
    Então a resposta deve ter status 200
    E o upload deve ter sido concluído com sucesso

  @api @upload @regression @documents
  Cenário: Upload de documento por HASH
    Quando eu faço upload por hash SHA256 e SHA512 para o cofre configurado
    Então a resposta deve ter status 200
    E o upload deve ter sido concluído com sucesso

  @api @upload @critical @documents
  Cenário: Upload de documento com anexo
    Quando eu faço upload de um PDF para o cofre configurado
    E eu adiciono um anexo PDF ao documento criado
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "File created"
