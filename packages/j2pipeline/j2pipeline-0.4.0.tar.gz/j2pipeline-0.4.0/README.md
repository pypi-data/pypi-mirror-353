# J2pipeline

## Installation

Create Python 3.12 virtual environment, activate it and run

```sh
pip install j2pipeline
```

## Setup

J2pipeline requires an active TCP server listening on port 50027

**Server:**

-   Receives a prompt
-   Sends back AI response

**Protocol:**

1. 16 bytes header (message length)
2. Message (in UTF-8)

**For example:**

```python
data: bytes = message.encode(encoding='UTF-8')
size: bytes = f'{len(data):16}'.encode(encoding='UTF-8')
server.send(size)
server.send(data)
```

### Server

-   For personal use, you might consider installing a Telegram GPT server available at `https://github.com/yaz008/TG-GPT-API`

-   You can write your own server following the described protocol

## Usage

### Prompt

Prompt creates a function based on a single template file

#### Params

-   **path:** path to a template file
-   **process:** function that modifies LLM output
-   **auto_upper:** makes sure all arguments passed in the template are in upper case

#### Example

Suppose we have a `translate.j2` file

```j2
Translate the following text into {% LANGUAGE %}:

{% TEXT %}
```

From this template we can than create `translate` function

```python
from j2pipeline import Prompt

translate: Prompt[str] = Prompt[str](path='translate.j2')

text: str = 'Quelle heure est-il?'
translation: str = translate(language='English', text=text)
print(translation)
```

In the output we shall see

```
What time is it?
```

### Pipeline

Pipeline creates a function based on a sequence of templates

#### Params

-   **base_path:** path to a folder with templates
-   **reorder:** function that takes a list of files and returns reordered one
-   **process:** a dict where keys are template names and values are respective modifiers
-   **final_process:** function that processes the final result
-   **extension:** common extension of the template files

#### Example

Suppose we have two template files in `yoderize` folder

-   `yoda.j2`:

```j2
You are Yoda from Star Wars, so you must speak like him
Rewrite this text in style of Yoda

{% PROMPT %}
```

-   `translate.j2`:

```j2
Translate the following text into German preserving the style of Yoda:

{% PROMPT %}

Your response must only contain the translation
```

From this template we can than create `yoderize` function

```python
from j2pipeline import Pipeline

yoderize: Pipeline[str] = Pipeline[str](base_path='yoderize',
                                        reorder=lambda _: ['yoda', 'translate'],
                                        final_process=lambda text: f'German Yoda:\n{text}')
yoderized: str = yoderize(prompt='I give you an advice: you should be wise')
print(yoderized)
```

In the end we shall see

```
German Yoda:
Weise, sein solltest du. Rat, gebe ich dir.
```

## License

J2pipeline is a free, open-source software distributed under the [MIT License](LICENSE.txt)
