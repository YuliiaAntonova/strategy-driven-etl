# Chunking

Чанки задаются только числовыми полями в `runtime` (код не читает флаги вида `use_chunks`):

```yaml
runtime:
  extract_chunk_size: 1000   # опционально; сколько строк за один проход extract
  write_chunk_size: 500       # опционально; размер чанка при записи в БД
```

- при заданном `extract_chunk_size` экстрактор с `extract_in_chunks` отдаёт несколько батчей за один `run()`;
- `write_chunk_size` пробрасывается в writer при записи.
