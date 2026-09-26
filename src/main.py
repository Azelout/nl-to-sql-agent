from db import sql
from lm import model, build_system_prompt
import json


RESPONSE_SYSTEM_PROMPT = """You are a precise data analyst.
    Your task is to provide a concise, direct, and factual answer to the user's initial question based solely on the provided SQL query and execution results.

    ### Guidelines:
    1. Answer the question directly without pleasantries, conversational filler, or introductory phrases (e.g., avoid "Based on the data", "Sure", "Here is your answer").
    2. Rely strictly on the query results. Do not extrapolate, hallucinate missing data, or assume values not present in the returned rows.
    3. If the query returned no records (empty set), state clearly that no matching data was found.
    4. Format numbers, currencies, and dates cleanly (e.g., format raw floats into readable figures).
    5. If the user asks in French, answer in French. If in English, answer in English.
    """

def main():
    DB = sql("data/company.db")
    Model = model()

    user_input = input("\nBonjour, comment puis-je vous aider ?\n")
    scheme_string = DB.get_scheme_string()
    SYSTEM_PROMPT = build_system_prompt(scheme_string)

    model_output = Model.call(SYSTEM_PROMPT, user_input).replace("json", "").replace("```", "")

    sql_query = json.loads(model_output)["sql"]

    db_results = DB.execute(sql_query).fetchall()
    
    user_payload = {
        "user_question": user_input,
        "executed_sql": sql_query,
        "query_results": db_results,
    }
    
    final_response = Model.call(RESPONSE_SYSTEM_PROMPT, json.dumps(user_payload, ensure_ascii=False))

    print(final_response)

    DB.close()

if __name__ == "__main__":
    while True:
        main()