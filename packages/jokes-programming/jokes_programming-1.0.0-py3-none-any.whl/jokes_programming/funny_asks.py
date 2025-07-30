import numpy as np


def ask() -> dict[str, str]:
    full_asks = [
        {
            "an_ask": "Por que o Java foi ao terapeuta?",
            "funny_response": "Hmm... essa foi tão ruim que até o NullPointerException chorou.",
            "correct_response": "Porque ele tinha muitos problemas de classe.",
            "want_to_continue": "Mais uma pra conta?",
        },
        {
            "an_ask": "Qual é o algoritmo favorito dos stalkers?",
            "funny_response": "Ok, essa foi mais perdida que um ponteiro sem referência.",
            "correct_response": "Depth First Search.",
            "want_to_continue": "Bora pra próxima?",
        },
        {
            "an_ask": "Como um programador confunde Halloween com Natal?",
            "funny_response": "Sua resposta tem menos sentido que código mal indentado.",
            "correct_response": "Porque OCT 31 == DEC 25.",
            "want_to_continue": "Quer sentir vergonha alheia de novo?",
        },
        {
            "an_ask": "Por que os cientistas de dados são péssimos em esconder segredos?",
            "funny_response": "Essa resposta teve menos privacidade que dataset público.",
            "correct_response": "Porque eles sempre expõem os dados!",
            "want_to_continue": "Continua comigo nessa?",
        },
        {
            "an_ask": "O que o Python disse para o código bagunçado?",
            "funny_response": "Rapaz... essa resposta tá pior que identação errada.",
            "correct_response": "Indentifique-se!",
            "want_to_continue": "A próxima tá melhor, quer ouvir?",
        },
        {
            "an_ask": "Por que o SELECT foi ao psicólogo?",
            "funny_response": "Tá traumatizado de tanto fazer join errado? Igual essa resposta aí...",
            "correct_response": "Porque ele tinha problemas para se relacionar (JOIN).",
            "want_to_continue": "Quer outra piada de programador?",
        },
        {
            "an_ask": "Qual é o animal favorito do SQL?",
            "funny_response": "Com essa resposta, até o INNER JOIN ficou OUTER. 😅",
            "correct_response": "O JOINt-venture!",
            "want_to_continue": "Se quiser mais, é só falar!",
        },
        {
            "an_ask": "Por que o programador levou o computador pra academia?",
            "funny_response": "Porque até o PC queria ficar 'fit' pra rodar código pesado!",
            "correct_response": "Pra melhorar a performance e o processamento.",
            "want_to_continue": "Quer mais piada pra dar push nessa branch?",
        },
        {
            "an_ask": "O que um algoritmo disse pra outro que estava lento?",
            "funny_response": "Calma, tô só rodando no modo 'soneca'... Zzz",
            "correct_response": "Você precisa otimizar seu tempo de execução!",
            "want_to_continue": "Quer outra otimizada na zoeira?",
        },
        {
            "an_ask": "Por que o frontend se dá mal no mundo real?",
            "funny_response": "Porque ele só sabe lidar com interfaces, mas não com problemas reais!",
            "correct_response": "Porque frontend cuida só da interface visual, não do backend ou lógica complexa.",
            "want_to_continue": "Quer mais um bug de humor?",
        },
        {
            "an_ask": "Qual é o medo do programador em um relacionamento?",
            "funny_response": "Ficar preso no 'loop infinito' de discussões!",
            "correct_response": "Medo de ficar preso em discussões que nunca acabam.",
            "want_to_continue": "Quer dar commit nessa próxima piada?",
        },
        {
            "an_ask": "Por que os dados ficaram bravos com o cientista de dados?",
            "funny_response": "Porque ele ficava demais tentando extrair segredos íntimos!",
            "correct_response": "Porque o cientista fazia muitas análises exploratórias revelando tudo.",
            "want_to_continue": "Mais uma análise de humor?",
        },
        {
            "an_ask": "Por que o código Python terminou com o código JavaScript?",
            "funny_response": "Porque ele não aguentava mais tanta callback!",
            "correct_response": "Porque JavaScript usa callbacks, que podem ser confusos e difíceis de gerenciar.",
            "want_to_continue": "Quer mais drama de linguagens?",
        },
        {
            "an_ask": "O que o DevOps falou pro programador desleixado?",
            "funny_response": "Aqui não é lugar pra código largado, meu irmão!",
            "correct_response": "Porque a cultura DevOps preza por automação, qualidade e organização.",
            "want_to_continue": "Quer mais integração contínua de piadas?",
        },
    ]

    random_ask = np.random.randint(low=0, high=(len(full_asks) - 1))

    return full_asks[random_ask].values()  # type: ignore
