from dataclasses import dataclass, field
from os import listdir
from j2pipeline.types.prompt import Prompt
from typing import Callable

@dataclass(slots=True)
class Pipeline[T]:
    base_path: str
    reorder: Callable[[list[str]], list[str]] = field(default=lambda prompts: prompts)
    process: dict[str, Callable[[str], str]] = field(default_factory=dict)
    final_process: Callable[[str], T] = field(default=lambda result: result)
    extension: str = field(default='j2')
    __names: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.__names = self.reorder([name[:-len(f'.{self.extension}')]
                                     for name
                                     in listdir(path=self.base_path)])
        if '*' not in self.process.keys():
            self.process |= { '*': lambda response: response }
    
    def __call__(self, prompt: str) -> T:
        result: str = prompt
        for name in self.__names:
            func: Prompt[str] = Prompt[str](path=f'{self.base_path}\\{name}.{self.extension}',
                                            process=self.process.get(name, self.process['*']))
            result = func(prompt=result)
        return self.final_process(result)