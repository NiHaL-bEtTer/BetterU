from retrieve import search
from generate import ask_llm

if __name__ == "__main__":
    while True:
        query = input("\nAsk me about foods (or type 'exit'): ").strip()
        if query.lower() == "exit":
            break

        results = search(query, n_results=5)
        answer = ask_llm(query, results)
        print("\nAI answer:\n")
        print(answer)