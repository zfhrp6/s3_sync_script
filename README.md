# s3 sync directories

WIP

## why

`aws s3 sync` checks files to be uploaded/deleted itself automatically, but it's slow.

## install

* rename **.env.template** into **.env**, and fill **.env**
* rename **target_dirs.py.template** into **target_dirs.py**, and fill **target_dirs.py**
* `poetry install`

## usage

```sh
poetry run python main.py
```

