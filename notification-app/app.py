import json

TYPE_WEIGHT = {
    "Placement": 100,
    "Result": 60,
    "Event": 30
}


def calculate_priority(notification):
    return TYPE_WEIGHT.get(notification["type"], 0)


with open("notifications.json", "r") as file:
    data = json.load(file)

notifications = data["notifications"]

for notification in notifications:
    notification["priority"] = calculate_priority(notification)

notifications.sort(
    key=lambda x: x["priority"],
    reverse=True
)

print("\nTOP PRIORITY NOTIFICATIONS\n")

for index, notification in enumerate(notifications[:10], start=1):
    print(
        f"{index}. "
        f"{notification['type']} | "
        f"Priority={notification['priority']} | "
        f"{notification['message']}"
    )
