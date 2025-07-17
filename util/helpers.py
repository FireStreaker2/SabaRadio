def bar(current: int, total: int):
    ratio = current / total
    position = int(ratio * 10)

    bar = ""
    for i in range(10):
        bar += "❍" if i == position else "-"

    mins, secs = divmod(int(current), 60)
    totalm, totals = divmod(int(total), 60)

    return f"{mins}:{secs:02} {bar} {totalm}:{totals:02}"
