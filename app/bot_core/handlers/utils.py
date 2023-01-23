def subscribes_to_text(data: dict) -> str:
    categories_list = list(
        [
            f"{key}. {value[0]}"
            for key, value in sorted(data.items(), key=lambda i: int(i[0]))
        ]
    )
    return "\n".join(categories_list)


def report_text(subscribes: dict) -> str:
    if subscribes:
        text = f"You are subscribed to categories:\n{subscribes_to_text(subscribes)}"
    else:
        text = "You are not subscribed to any category."
    return text
