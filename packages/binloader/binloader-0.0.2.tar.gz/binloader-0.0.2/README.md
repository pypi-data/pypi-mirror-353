## Run VIM/Busybox and remote binaries accesible by http/https/ftp as a Python module in Linux/x86_64 systems

Motivation: run programs not available in restricted environments where
any package can be installed by **pip**


### Installation
```bash
pip install binloader
```

## Usage:
### Vim
```bash
python -m binloader --local vim /etc/passwd
```

### Busybox
```bash
python -m binloader --local busybox uname -a
```

### Remote binary
```bash
python -m binloader  --remote https://github.com/dtschan/vim-static/releases/download/v8.1.1045/vim --app vim /etc/passwd
```

### ToDo
1. Support for other OS/architectures
2. Add other binaries

## Author

Ulises <ulises.odysseus22@gmail.com>
