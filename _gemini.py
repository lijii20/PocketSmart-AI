from google import genai
client = genai.Client(api_key="AQ.Ab8RN6JZ-cFl93PDwP-KtwBPqlbAxD_-grPJSqz0ZfDwzst-CQ")
response = client.models.generate_content(
  model="gemini-3.5-flash-lite",
  contents="Hello, are you working?"
)
print(response.text)