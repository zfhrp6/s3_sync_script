# s3 sync directories

WIP: only listing the files to be uploaded/deleted.

## why

AWS CLI `aws s3 sync` checks files to be uploaded/deleted itself automatically, but it's slow.

## install, install dependencies

* rename **.env.template** into **.env**, and fill **.env**
* rename **target_dirs.py.template** into **target_dirs.py**, and fill **target_dirs.py**
* `poetry install`

## usage

```sh
poetry run python main.py
```

## performance comparison

AWS CLI vs. my script

### conditions

* number of files: about 32,000

### raw AWS CLI

takes about 15 minutes (900s)

```console
$ \time aws s3 sync --storage-class GLACIER --size-only ./ s3://BUCKET/ --delete --dryrun
15.87user 22.97system 15:07.63elapsed 4%CPU (0avgtext+0avgdata 76032maxresident)k
76112inputs+0outputs (291major+17376minor)pagefaults 0swaps
```

### my script

takes about 65s

```console
$ \time poetry run python main.py
to be uploaded:
to be deleted :
5.57user 3.52system 1:03.64elapsed 14%CPU (0avgtext+0avgdata 77424maxresident)k
78112inputs+0outputs (295major+40131minor)pagefaults 0swaps
```
