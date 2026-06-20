<div align="center">

<pre>
 _______  _______  ______    _______  ___      ___      _______  ___            ___   _______  _______ 
|       ||   _   ||    _ |  |   _   ||   |    |   |    |       ||   |          |   | |       ||       |
|    _  ||  |_|  ||   | ||  |  |_|  ||   |    |   |    |    ___||   |          |   | |   _   ||  _____|
|   |_| ||       ||   |_||_ |       ||   |    |   |    |   |___ |   |          |   | |  | |  || |_____ 
|    ___||       ||    __  ||       ||   |___ |   |___ |    ___||   |___  ___  |   | |  |_|  ||_____  |
|   |    |   _   ||   |  | ||   _   ||       ||       ||   |___ |       ||   | |   | |       | _____| |
|___|    |__| |__||___|  |_||__| |__||_______||_______||_______||_______||___| |___| |_______||_______|

Fast, parallelized, and automated file deployment for remote devices.
tftp > [=======>file>--------] > devices
</pre>

</div>

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Parallel.IOS

### [Read this in english](README.en.md)

Uma ferramenta Python com interface gráfica (GUI) desenvolvida para automatizar a cópia e verificação de imagens IOS (ou outros arquivos) a partir de um servidor TFTP para a memória flash de múltiplos dispositivos Cisco. Este script otimiza o tempo e diminui o trabalho manual realizando as cópias de forma simultânea para diversos equipamentos.

---

## Cenário Típico:

**Chefe:**<br><br> Precisamos atualizar a versão de firmware de todos os dispositivos de rede da empresa devido a uma vulnerabilidade crítica que foi descoberta ontem a noite!<br>
**🔴E PRECISO DISSO PRONTO ATÉ AS 17H!!🔴**
<br><br><br>
**Time de Infra/Redes(você, no caso!):<br><br>**<img src="/assets/CJ.jpg" alt="Screenshot 1" width="60%"> <br>*Ah shit! Here we go again!*

## O Problema:
Você tem 90 switches, um servidor TFTP e a paciência de um monge. O que você vai fazer? 😭 *<--esse é você*<br>
Copiar os arquivos um por um manualmente não é "trabalho de infra", é castigo divino. É aquele momento onde você se pergunta se deveria ter estudado botânica ou se deveria ter entrado pro teatro.

## A Solução? (Ou quase isso):
Esta ferramenta é um script Python com uma interface gráfica que fiz para que você não precise digitar `copy tftp flash:` até os seus dedos sangrarem.<br>
Ele automatiza o tédio e faz o upload simultâneo para múltiplos dispositivos Cisco e depois(*sim, tem mais!*) da cópia ainda verifica se o arquivo foi copiado corretamente utilizando o hash MD5 dele. (porque a vida é curta demais para ficar acompanhando barras de progresso.)

## O que ele faz? (além de salvar seu tempo):

1.	**Multitarefa Real:** Ele ataca vários dispositivos ao mesmo tempo. Enquanto o TFTP sofre fazendo todas as cópias, você finge que está lendo a documentação (na verdade você está vendo reels no Instagram).
2.	**Verificação de espaço disponível:** Cabe ou não cabe? Tem espaço livre ou não? Não importa! Você informa o tamanho do arquivo, o script verifica pra você, se não tiver ele te avisa e não copia o arquivo para o dispositivo sem espaço.
3.	**Verificação de Integridade(hash MD5):** Ele checa se o arquivo chegou inteiro ou se virou um amontoado de bits inúteis no meio do caminho.
4.	**Interface Gráfica:** Porque as vezes a gente só quer clicar em um botãozinho bonito ao invés de brigar com o terminal.

## Compatibilidade

Este script é compatível com dispositivos Cisco **IOS/IOS-XE** e **NX-OS** (Nexus). Basta selecionar o módulo correspondente (**Cisco IOS** ou **Cisco NX-OS**) no campo **Module** da seção "Advanced Config" da interface antes de iniciar a transferência.

**Importante!** Não é possível misturar dispositivos IOS e NX-OS na mesma execução — todos os IPs informados devem ser do mesmo tipo selecionado no módulo. Caso um dispositivo do tipo errado seja detectado, a transferência para ele falhará com um erro indicando para trocar o módulo, e o processo seguirá normalmente para os demais. Outros sistemas operacionais de rede (como Junos, Arista EOS, etc.) ainda **NÃO** são suportados.

## Screenshots

<img src="/assets/screenshot-00.png" alt="Screenshot 1" width="85%">

<img src="/assets/screenshot-01.png" alt="Screenshot 1" width="85%"><br>

*Gostou das cores? Retrô está na moda de novo!*

## Pré-requisitos

Para utilizar este script, você precisará:

1.  **Servidor TFTP:** Um servidor **TFTP** configurado e operacional na sua rede, acessível pelos dispositivos, e com a imagem IOS(ou arquivo) que deseja copiar hospedada nele. Recomendado: [Tftpd64](https://pjo2.github.io/tftpd64/)
2.  **Acesso aos Dispositivos:** Credenciais (usuário e senha) para acesso SSH aos dispositivos.
3.  **Café☕ e fé nos bits🙏**

## Como Usar

### Pré-requisitos
  ```bash
  Python 3.x
  ```
### Execução

1.  **Baixe o Repositório:**
    ```bash
    git clone https://github.com/solopx/parallelios.git
    cd parallelios
    ```
2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```    
3.  **Execute o Script:**
    ```bash
    python src/main.py
    ```

4.  **Preencha as Informações na GUI:**
    * **TFTP Server IP Address:** Endereço IP de seu servidor TFTP.
    * **Filename:** Nome completo da imagem/arquivo no servidor TFTP (ex: `c2960s-universalk9-mz.152-7.E2.bin`).
    * **Hash MD5:** O valor de hash MD5 esperado para o arquivo (verifique o hash MD5 do arquivo utilizando os comandos: certutil, md5sum ou através de fontes oficiais).
    * **Size(MB):** Tamanho estimado do arquivo em `Megabytes(MB)`. O tamanho informado neste campo será utilizado para verificar se há espaço disponível nos dispositivos de destino antes de efetuar a cópia. `Obs.: Se informado como 0 ou não informado esta verificação não será realizada.`
    * **Username:** Seu nome de usuário para autenticação nos dispositivos.
    * **Password:** Sua senha de autenticação nos dispositivos.
    * **Enable Pass:** Marque esta checkbox caso os dispositivos necessitem de senha de enable e informe a mesma. `Obs.: Esta opção é desabilitada automaticamente ao selecionar o módulo "Cisco NX-OS", já que o NX-OS não utiliza enable mode.`
    * **Module:** Selecione o tipo de dispositivo de destino: **Cisco IOS** (padrão) ou **Cisco NX-OS**.
    * **Devices:** Uma lista de endereços IP dos dispositivos de destino, separados por vírgula (ex: `192.168.1.1, 192.168.1.2, 192.168.1.3`).


5.  **Iniciar Cópia(s):** Clique no botãozinho bonito "**Start Transfer**".
6.  **Output Log:** O log de saída na parte inferior da janela mostrará o status de cada dispositivo em tempo real.
7.  **Tome seu café** e aprecie a bela paisagem de seu escritório enquanto aguarda o fim de todo o processo.

## Notas: ##

#### MD5: ####

Você pode obter o hash MD5 do arquivo a ser copiado a partir de fontes confiáveis como: sites oficiais ou utilizando a linha de comando.

Para checar o hash MD5 de um arquivo em sistemas `windows` utilize o seguinte comando no prompt:
```bash
certutil -hashfile "C:\Caminho\Do\Arquivo Desejado.bin" MD5
```
Para sistemas `linux\unix` utilize:
```bash
md5sum  "C:\Caminho\Do\Arquivo Desejado.bin"
```

#### Tamanho dos pacotes TFTP: ####

Em algumas versões de IOS, o tamanho do pacote TFTP pode ser personalizado para otimizar o tempo de cópia, você pode verificar se seus dispositivos possuem esta funcionalidade com o comando:

```bash
Switch(config)# ip tftp blocksize <valor>
```

Os valores válidos são entre 512(padrão) a 8192.


## Troubleshooting e Logs de Debug

O script gera um arquivo de log chamado `copy-tftp-flash.log` no mesmo diretório de execução. Este arquivo contém detalhes de baixo nível das interações com os dispositivos e é extremamente útil para depuração.

## Observações sobre `MAX_WORKERS` e `TIMEOUT_MAX`

O campo `MAX_WORKERS` define o número máximo de operações de cópia simultâneas. O valor padrão é `5`. Se você estiver processando um grande número de dispositivos e tiver uma infraestrutura de rede robusta e um servidor TFTP capaz, você pode ajustar este valor para aumentar o número de transferências simultâneas e o desempenho. Tenha em mente que, no entanto, um valor muito alto pode sobrecarregar seus recursos.

Já o campo `TRANSFER TIMEOUT` define o tempo máximo(em minutos) que o script irá aguardar para trasnferir o arquivo selecionado para cada dispositivo.

## Estrutura de Arquivos

Esta aplicação atualmente está dividida nos seguintes arquivos principais:

* `main.py` - Ponto de entrada da aplicação. Conecta a interface gráfica à lógica de rede, gerencia validações de input e roteia a execução para o motor de transferência correto (IOS ou NX-OS) conforme o módulo selecionado.

* `gui.py` - Interface gráfica em Tkinter. Define o layout, estilos visuais e expõe os widgets para o main orquestrar.

* `engine_core.py` - Funções e estado compartilhados entre os motores de transferência: validação de IPs, verificação de espaço em disco, logging e orquestração das transferências paralelas (`ThreadPoolExecutor`).

* `ios_engine.py` - Motor de transferência específico para dispositivos Cisco IOS/IOS-XE (filesystem `flash:`, comando `verify /md5`, enable mode).

* `nxos_engine.py` - Motor de transferência específico para dispositivos Cisco NX-OS (filesystem `bootflash:`, comando `show file ... md5sum`, sem enable mode).

## Futuro

Em futuros updates pretendo colocar uma música suave de elevador enquanto as cópias são realizadas e um barulho de buzina de caminhão quando elas forem concluídas. Também pretendo inserir suporte a outros fabricantes e ao protocolo SCP/SFTP como alternativa ao TFTP.

## Contribuições

Contribuições são bem-vindas! Se você tiver ideias para melhorias, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido por solopx
GitHub: [https://github.com/solopx/](https://github.com/solopx/)
