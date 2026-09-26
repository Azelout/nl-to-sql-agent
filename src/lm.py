from openai import OpenAI

def build_system_prompt(schema_ddl: str) -> str:
    return f"""You are an expert SQLite data analyst and query generation engine.
    Your sole purpose is to convert user questions into syntactically valid SQLite queries based on the provided schema.

    ### Output Contract:
    You MUST respond with a single, valid JSON object matching the schema below.
    Do NOT output markdown codeblocks (no ```json or ```), commentary, or explanations outside the JSON payload.

    ### Database Schema:
    {schema_ddl}

    ### Operational Rules:
    1. Strict Read-Only: Generate only SELECT or WITH statements. Any DDL or DML (INSERT, UPDATE, DELETE, DROP) is strictly prohibited.
    2. Dialect Constraints: Adhere strictly to SQLite 3 syntax:
    - Use standard SQLite functions (e.g. strftime, date, printf, round).
    - Case-insensitive string matching must use LOWER(column) = LOWER('value') or the LIKE operator.
    - Do NOT assume non-existent foreign keys; join tables solely on primary/foreign key relationships defined in the schema.
    3. Schema Adherence: Use exact table and column names as written in the schema. Check column types and enum-like CHECK constraints before filtering.
    4. Robustness:
    - When calculating averages or divisions, guard against division by zero using NULLIF.
    - Handle possible NULL values appropriately with COALESCE or IS NULL / IS NOT NULL clauses.



    {{
        "thought": "Concise step-by-step logic detailing target tables, joins, filters, and aggregations.",
        "sql": "SELECT ...;"
    }}"""



class model():
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="token-vllm"  # vLLM n'exige pas de vraie clé en local
        )

    def call(self, SYSTEM_PROMPT: str, USER_PROMPT: str):
        response = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-1.5B-Instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT},
            ],
            temperature=0.0
        )

        generated_text = response.choices[0].message.content

        return generated_text

if __name__ == "__main__":
    qwen = model()
    SYSTEM_PROMPT = build_system_prompt("")
    print(qwen.call(SYSTEM_PROMPT, "Get the number of users"))


