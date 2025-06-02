```bash
python -m venv .venv
.venv/Script/activate
pip install -r ./requirements.txt
python main.py
```

Il Faut allumer le bluetouth sur son ordinateur

Lister tous les appareils Muses
```python
python -m muselsl list
```

Streamer le premier appareil Muse
```python
python -m muselsl stream
```

Visualiser la data, le stream doit rester actif
```python
python -m muselsl view
```

Récuperer que le gyro
```python
python -m muselsl record --type GYRO
```
