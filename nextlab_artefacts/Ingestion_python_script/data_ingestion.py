import requests
import concurrent.futures
from faker import Faker
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
fake = Faker()

ENDPOINTS = {
    "/api/config": lambda _: {
        "name": fake.word(),
        "appType": fake.random_element(elements=("AppTypeA", "AppTypeB", "AppTypeC")),
        "description": fake.text(max_nb_chars=50)
    }
}


def send_request(host, endpoint, payload, method="POST"):
    url = f"{host}{endpoint}"
    try:
        response = requests.post(url, json=payload) if method.upper() == "POST" else None
        if response and response.status_code in (200, 201):
            return f"Success: {response.status_code}, Payload: {payload}"
        else:
            logging.error(
                f"Failed: {response.status_code if response else 'No Response'}, Payload: {payload}, Response: {response.text if response else 'No Response'}")
            return f"Failed: {response.status_code if response else 'No Response'}, Payload: {payload}, Response: {response.text if response else 'No Response'}"
    except Exception as e:
        logging.error(f"Error: {e}, Payload: {payload}")
        return f"Error: {e}, Payload: {payload}"


def perform_ingestion(host, endpoint, iterations, method="POST", max_workers=5):
    if endpoint not in ENDPOINTS:
        raise ValueError(f"Endpoint '{endpoint}' is not configured.")

    payloads = [ENDPOINTS[endpoint](None) for _ in range(iterations)]
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_payload = {
            executor.submit(send_request, host, endpoint, payload, method): payload
            for payload in payloads
        }
        for future in concurrent.futures.as_completed(future_to_payload):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")

    for result in results:
        print(result)


if __name__ == "__main__":
    host = "http://3.88.29.2:30080/demo"
    perform_ingestion(host, "/api/config", iterations=1000, method="POST", max_workers=5)
