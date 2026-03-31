import openai

# Set your OpenAI API Key (Replace with your actual key)
openai_client = openai.OpenAI(api_key="your_openai_api_key")  

def generate_interview_question(job_description):
    prompt = f"""
    You are an AI interviewer for technical roles. Given a job description, generate a LeetCode-style coding question.

    Job Description:
    {job_description}

    Format the output as:
    - **Problem Statement**: Clear and concise
    - **Input Format**
    - **Output Format**
    - **Constraints**
    - **Example Test Case**
    """

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI that generates coding interview questions."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Test different job descriptions
job_desc_1 = "Backend Engineer, Java, Spring Boot, AWS, PostgreSQL"
job_desc_2 = "Frontend Developer, React, TypeScript, Next.js"
job_desc_3 = "Data Engineer, Python, SQL, Airflow, Spark"

print("\n🔹 Generated Question for Backend Engineer:\n")
print(generate_interview_question(job_desc_1))

print("\n🔹 Generated Question for Frontend Developer:\n")
print(generate_interview_question(job_desc_2))

print("\n🔹 Generated Question for Data Engineer:\n")
print(generate_interview_question(job_desc_3))
