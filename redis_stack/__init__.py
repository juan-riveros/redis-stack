from __future__ import annotations
from pathlib import Path
import os, sys, json

from redis import Redis

class StackManager:
    def __init__(self):

        BASE_DIR = Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')).expanduser()
        conf_dir = BASE_DIR/"redis-todo"
        conf_dir.mkdir(mode=711, parents=True,exist_ok=True)
        conf_file = conf_dir/'config.json'
        if not conf_file.exists():
            print("Missing Configuration File",str(conf_file.resolve()))
            print("Generating with defaults values then exiting")
            with open(conf_file,'w') as f:
                f.write(json.dumps({"REDIS_HOST":"localhost", "REDIS_PORT":6379, "REDIS_DB":0}))
            sys.exit(0)
        with open(conf_file) as f:
            self.CONFIG = json.loads(f.read())

        self.redis = Redis(
            host=self.CONFIG.get('REDIS_HOST'),
            port=self.CONFIG.get('REDIS_PORT'),
            db=self.CONFIG.get("REDIS_DB", 0)
        )

    def add_to_stack(self,stack:str, items:list[str]):
        self.redis.lpush(stack, *items)
    
    def pop_from_stack(self, stack:str) -> str:
        return self.redis.lpop(stack)
    
    def cycle_stack_head(self, stack:str):
        return self.redis.rpush(stack,self.redis.lpop(stack))
    
    def reverse_stack(self,stack:str):
        items = self.redis.lrange(stack,0,-1)[::-1]
        self.redis.delete(stack)
        self.redis.rpush(stack, *items)
    
    def list_stack(self, stack:str):
        return list(s.decode() for s in self.redis.lrange(stack, 0, -1))
    
    def transfer(self, source:str, target:str):
        item = self.redis.lpop(source)
        self.redis.lpush(target, item)

    def flush(self, stack:str):
        self.redis.delete(stack)

    def sink_item(self, stack:str, depth:int):
        items = [self.redis.lpop(stack) for _ in range(depth+1)]
        items.append(items.pop(0))
        self.redis.lpush(stack,*items[::-1])


    def command(self, *args, **kwargs):
        
        match args:
            case ["head", name]:
                items = self.list_stack(name)
                print(json.dumps(items[0].decode()))
            case ["do"|"add"|"create"|"push", name, *items]:
                self.add_to_stack(name, items)
                print(json.dumps(self.list_stack(name)))
            case ["done"|"complete"|"pop", name]:
                self.transfer(name, f"{name}:complete")
                print(f"{name}:complete",json.dumps(self.list_stack(f"{name}:complete")))
            case ["sink"|"shift", name, depth]:
                if isinstance(depth, str):
                    depth = int(depth)
                self.sink_item(name,depth)
                print(json.dumps(self.list_stack(name)))
            case ["cycle", name]:
                self.cycle_stack_head(name)
                print(json.dumps(self.list_stack(name)))
            case ["reverse"|"rev", name]:
                self.reverse_stack(name)
                print(json.dumps(self.list_stack(name)))
            case ["list"|"ls"|"show", name]:
                print(json.dumps(self.list_stack(name)))
            case ['transfer', source, target]:
                self.transfer(source, target)
                print(target,json.dumps(self.list_stack(target)))
            case ['flush', name]:
                self.flush(name)
                print(name, "flushed")
            case _:
                print()
                print(sys.argv[0], '<command>')
                print()
                print('  <command> :=', "<create expr>|<complete expr>|<cycle expr>|<reverse expr>|<list expr>")
                print(
                    "",
                    '    <create expr>   := do|add|create <stack name:str> <items:list[str]|str>',
                    '    <complete expr> := complete|done <stack name:str>',
                    '    <cycle expr>    := cycle         <stack name:str>',
                    "    <reverse expr>  := reverse|rev   <stack name:str>",
                    "    <list expr>     := ls|list|show  <stack name:str>",
                    "    <head expr>     := head          <stack name:str>",
                    sep='\n'
                )
                return

def main():
    app = StackManager()
    args = sys.argv[1:]
    
    app.command(*args)

if __name__ == "__main__":
    main()
