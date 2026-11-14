# Radar História RJ — versão 2.0

**Site para o Rio de Janeiro:** https://pedro-pv28.github.io/radar-historia-rj/

Esta atualização incorpora a identidade editorial aprovada (creme, vinho e oliva), a seção **Últimas oportunidades**, pesquisa com filtros, áreas acadêmicas em separado, indicadores de apuração, páginas para indicar vagas, detalhes de salário, prazos, requisitos e vínculo, favoritos e exportação CSV.

## Instalação — sem perder os anúncios que já estão no GitHub

**Importante: este pacote de atualização NÃO contém `data/opportunities.json` de propósito.** Assim, os dados que seu GitHub já descobriu não serão substituídos por uma versão antiga. O site usa esse mesmo arquivo no endereço `data/opportunities.json` e se adapta ao formato anterior.

1. **Guarde um backup:** no repositório do GitHub, use `Code → Download ZIP` antes de atualizar.
2. Acesse https://github.com/pedro-pv28/radar-historia-rj e abra `index.html`. Para **substituir**, escolha o ícone de lápis e cole o novo conteúdo do `index.html` deste pacote (se preferir, exclua o arquivo antigo e envie o novo de mesmo nome). Faça `Commit changes`. Este `index.html` é **autossuficiente**: tem CSS, JS, arte e dados de demonstração embutidos, sem precisar enviar a pasta `assets/`.
3. Para atualizar a frequência de varredura, substitua `.github/workflows/update.yml` pelo arquivo de mesmo caminho do pacote.
4. Substitua `scripts/update_opportunities.py` pela versão do pacote.
5. Adicione `.github/ISSUE_TEMPLATE/divulgar-vaga.yml` (e habilite `Issues` no repositório se ainda estiver desativado). Para esse formulário funcionar, o visitante precisa ter conta no GitHub.
6. Mantenha **o seu `data/opportunities.json` existente**. Nunca o exclua nem o substitua pelo exemplo embutido no site.
7. Abra a guia **Actions → Atualizar e publicar Radar História RJ → Run workflow**, selecionando a branch padrão. O Pages continuará no endereço atual.

### Se preferir subir arquivos por arrastar e soltar

Arraste os arquivos de uma pasta do Windows para a página de upload **preservando seus caminhos**. O GitHub costuma achatar os caminhos ao selecionar pelo seletor de arquivos. Confira que `.github/workflows/update.yml`, `scripts/update_opportunities.py` e `.github/ISSUE_TEMPLATE/divulgar-vaga.yml` apareçam exatamente nesses caminhos.

### O que a atualização faz

- **Oportunidades**: docência básica, historiadores e cultura/patrimônio; filtros por município, região, setor, tipo, situação, favoritos.
- **Vida acadêmica**: concursos de magistério superior e seleções relacionadas a universidades.
- **Em apuração**: descobertas automáticas e anúncios de área correlata que ainda não estão comprovados para História. Não são contados como oportunidades confirmadas.
- **Divulgar uma vaga**: formulário público de indicação pelo GitHub Issues, sem publicação automática. É necessário login no GitHub.
- **Remuneração, prazo, horários e requisitos**: o site exibe o que consta nos dados e informa **Não informado** quando falta. Não cria salários nem datas.
- **Últimas oportunidades**: só anúncios cujo vínculo com História foi identificado, de acordo com a última curadoria cadastrada; prazos encerrados deixam de aparecer nos destaques.
- **Avisos na página**: opção local, só enquanto a aba estiver aberta. **Não envia e-mail nem push com o navegador fechado**. Favoritos são locais do navegador.
- **Varredura agendada**: a cada 2 horas (12 tentativas/dia), se o GitHub Actions executar normalmente. Fonte indisponível não apaga os dados. A rotina só produz possíveis anúncios **Em apuração**; não confirma editais automaticamente.

## Limitações importantes

- A API oficial de vagas da Gupy requer **token**, segundo a própria documentação. Não há acesso integral automático a Gupy, Elite ou a todas as escolas privadas; as buscas públicas são apenas complementares, e cada carreira exige integração adicional.
- O GitHub Actions pode atrasar, falhar ou ficar desativado; por isso **24h de atualização ininterrupta não é garantido**.
- Notícia de vaga não equivale a inscrição aberta. Prazo oficial, retificação e titulação devem ser conferidos na fonte antes da candidatura.
- Divulgação no GitHub Issues depende de moderação humana para virar registro confirmado.
- Não há backend de contas, e-mails ou notificações push. Isso exige solução adicional e cuidados com privacidade.

## Próximos aprimoramentos possíveis

Monitorar diretamente APIs consentidas de empregadores privados, criar moderação mais simples, cadastrar fontes dos 92 municípios e implantar alertas por e-mail com opt-in e descadastro.

---

Iniciativa independente, sem vínculo institucional com prefeituras, universidades, escolas ou bancas. O edital original sempre prevalece.
