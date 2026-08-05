# language: pt

Funcionalidade: Templates na API D4Sign
  Como consumidor da API D4Sign
  Quero gerar documentos a partir de templates Word e HTML
  Para validar os endpoints de template

  Contexto:
    Dado que a API D4Sign está configurada

  @api @template @regression @templates
  Cenário: Gerar documento via template Word e replicar pin
    Quando eu gero um documento via template Word no cofre configurado
    Então a resposta deve ter status 200
    E o upload deve ter sido concluído com sucesso
    Quando eu adiciono um signatário por e-mail ao documento criado
    E eu replico um pin em todas as páginas do documento
    Então a resposta deve ter status 200

  @api @template @regression @templates
  Cenário: Criar documento via template HTML
    Quando eu gero um documento via template HTML no cofre configurado
    Então a resposta deve ter status 200
    E a mensagem da resposta deve ser "success"
