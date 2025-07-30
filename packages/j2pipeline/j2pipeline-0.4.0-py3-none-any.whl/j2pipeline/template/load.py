def load_template(path: str) -> str:
    with open(file=path, mode='r', encoding='UTF-8') as j2_file:
        return j2_file.read()