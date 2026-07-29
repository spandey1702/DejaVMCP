from embeddings import embed
from db import create_agent, create_task, log_decision, search_past_decisions, run_query

def reset_seed_data():
    run_query("DELETE FROM tasks WHERE task_key IN (%s, %s, %s)", ("checkout-auth", "rate-limit-api", "readme-typo"))
    run_query("DELETE FROM agents WHERE agent_key = %s", ("seed-agent",))

def seed():
    reset_seed_data()
    agent_id = create_agent("seed-agent", "Seed Agent", "demo")

    task1 = create_task("checkout-auth", "Add authentication to checkout endpoint", created_by_agent_id=agent_id)
    log_decision(
        task1, agent_id,
        decision_text="Add authentication to checkout endpoint",
        embedding=embed("Add authentication to checkout endpoint"),
        reason="Used JWT validated against Auth0 JWKS endpoint",
        state="completed",
    )

    task2 = create_task("rate-limit-api", "Add rate limiting to an API endpoint", created_by_agent_id=agent_id)
    log_decision(
        task2, agent_id,
        decision_text="Add rate limiting to an API endpoint",
        embedding=embed("Add rate limiting to an API endpoint"),
        reason="Used a token bucket algorithm, 100 requests per minute",
        state="completed",
    )

    task3 = create_task("readme-typo", "Fix a typo in the README", created_by_agent_id=agent_id)
    log_decision(
        task3, agent_id,
        decision_text="Fix a typo in the README",
        embedding=embed("Fix a typo in the README"),
        reason="Corrected 'recieve' to 'receive'",
        state="completed",
    )

    print("Seeded 3 decisions.\n")
    print("Searching for something like 'add authentication to payments endpoint':\n")
    results = search_past_decisions(embed("add authentication to payments endpoint"))
    for r in results:
        print(f"{r['similarity']:.3f}  {r['decision_text']}")

if __name__ == "__main__":
    seed()
