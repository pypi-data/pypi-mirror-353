import time
from .funny_asks import ask


def run() -> None:
    print("################################################")
    print("Seja bem-vindo(a) ao Módulo de Piadas em Python!")
    print("################################################")
    time.sleep(2)

    print("- Aí vai uma pergunta...")
    time.sleep(1)

    while True:
        an_ask, funny_response, correct_response, want_to_continue = ask()

        print(f"\n- {an_ask}")
        user_response = input()
        time.sleep(1)

        print(f"- {user_response}????? {funny_response}")
        time.sleep(1)
        print(f"- A resposta correta é: {correct_response}")
        time.sleep(1)
        print("- HaHaHaHaHaHaHaHaHaHaHa\n")

        time.sleep(2)
        print(want_to_continue)
        print("1 - Sim | 2 - Não")
        deseja_continuar = input()

        if deseja_continuar == "2":
            print("- Encerrando...")
            time.sleep(2)
            print("- Ruan Narici mandou um abraço!")
            time.sleep(1)
            print("*Processo encerrado*")
            break
