from dotenv import load_dotenv

import lambda_function


load_dotenv()

response = lambda_function.lambda_handler({}, None)

print(response)