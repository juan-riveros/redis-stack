# redis-stack

A very shoddy task tracker using redis as the backing store.

# quickstart

## building

```bash
make package
./dist/redis-stack-$(poetry version -s)-bin
```


## installing

```bash
$SOME_PATH_DIR=$HOME/.local/bin
make package
cp ./dist/redis-stack-$(poetry version -s)-bin $SOME_PATH_DIR/redis-stack
redis-stack
```


## configuration 

Uses a configuration file located in `$XDG_CONFIG_HOME/redis-stack/config.json`. Example Config:

```json
{
  "REDIS_HOST": "localhost",
  "REDIS_PORT": "6379",
  "REDIS_DB": 0
}
```

## usage

### eBNF

```bash
redis-stack := <create expr>|<complete expr>|<cycle expr>|<reverse expr>|<list expr>
    <create   expr> := do|add|create <stack name:str> <items:list[str]|str>
    <complete expr> := complete|done <stack name:str>
    <cycle    expr> := cycle         <stack name:str>
    <reverse  expr> := reverse|rev   <stack name:str>
    <list     expr> := list|ls|show  <stack name:str>
    <head     expr> := head          <stack name:str>
```

### Examples

```bash
redis-stack ls todo:work
> []
redis-stack add todo:work "meeting" "format code" "refactor lib"
> ["refactor lib", "format code", "meeting"]
redis-stack ls todo:work 
> ["refactor lib", "format code", "meeting"]
```
