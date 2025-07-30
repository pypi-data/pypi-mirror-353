from dataclasses import dataclass, field
from j2pipeline.template import load_template, render
from j2pipeline.tcp import client
from typing import Callable, Generator, cast
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from uuid import uuid4

@dataclass(slots=True)
class Prompt[T]:
    path: str
    process: Callable[[str], T] = field(default=lambda response: response)
    auto_upper: bool = field(default=True)

    def __call__(self, **subs: str) -> T:
        if self.auto_upper:
            subs = { key.upper(): value for key, value in subs.items() }
        template: str = load_template(path=self.path)
        prompt: str = render(template=template, subs=subs)
        with client() as clt:
            result: str = clt.send(prompt)
        return self.process(result)

@contextmanager
def inline_prompt[T](
    prompt: str,
    process: Callable[[str], T] | None = None,
    auto_upper: bool = True,
) -> Generator[Prompt[T], None, None]:
    with TemporaryDirectory() as temp_dir:
        temp_file_path: str = f'{temp_dir}/{uuid4().hex}.j2'
        with open(file=temp_file_path, mode='w') as temp_file:
            temp_file.write(prompt)
        yield Prompt(
            path=temp_file_path,
            process=(
                process
                if process is not None
                else lambda response: cast(T, response)
            ),
            auto_upper=auto_upper,
        )
