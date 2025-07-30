
# smartchunks

`smartchunks` is a flexible, powerful chunking utility for Python that provides more than just slicing — it allows pattern-based, overlapping, and conditional chunking.

---

## ✨ Features

- ✅ Standard fixed-size chunking
- ✅ `nth_position`: Take every nth item before or after chunking
- ✅ `chunk_position`: Pick every nth *chunk*
- ✅ `stride`: Create overlapping chunks (sliding window)
- ✅ `fillvalue`: Pad final incomplete chunks
- ✅ `filter_fn`: Apply a custom condition to keep or discard chunks
- ✅ `materialize`: Toggle between generator and list output

---

## 📦 Installation

```bash
pip install smartchunks
```

---

## 🧪 Usage Examples

```python
from smartchunks import chunked

data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### 🔹 Standard Chunking
```python
print(list(chunked(data, size=3)))
# → [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
```

### 🔹 nth_position (Before Chunking)
```python
print(list(chunked(data, size=2, nth_position=2)))
# → [[1, 3], [5, 7], [9]]
```

### 🔹 chunk_position (Every nth Chunk)
```python
print(list(chunked(data, size=2, chunk_position=2)))
# → [[3, 4], [7, 8]]
```

### 🔹 nth_position After Chunking
```python
print(list(chunked(data, size=3, nth_position=2, apply_nth_before_chunk=False)))
# → [[2], [5], [8]]
```

### 🔹 Overlapping chunks (stride)
```python
print(list(chunked(data, size=3, stride=1)))
# → [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8], [7, 8, 9]]
```

### 🔹 Padding incomplete chunks
```python
print(list(chunked([1, 2, 3, 4, 5], size=3, fillvalue=0)))
# → [[1, 2, 3], [4, 5, 0]]
```

### 🔹 Filtering chunks (keep those whose sum > 15)
```python
print(list(chunked(data, size=3, stride=1, filter_fn=lambda x: sum(x) > 15)))
# → [[5, 6, 7], [6, 7, 8], [7, 8, 9], [8, 9]]
```

### 🔹 Materialized output
```python
chunks = chunked(data, size=2)
print(next(chunks))  # Lazy generator by default

chunks = chunked(data, size=2, materialize=True)
print(chunks)  # Fully materialized list of chunks
```

---

## 🧠 Advanced Combinations

```python
print(list(chunked(data, size=2, stride=2, chunk_position=2, nth_position=2, apply_nth_before_chunk=False)))
# Apply chunking with stride, select every 2nd chunk, then take the 2nd element from each
```

---

## 📜 License
MIT License © 2024 Maurya Allimuthu

---

## 🧩 Special Examples

### 🔹 stride with overlap
```python
data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
print(list(chunked(data, size=3, stride=1)))
# → [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7], [6, 7, 8], [7, 8, 9]]
```

---

### 🔹 nth_position then chunk_position
```python
# Pick every 2nd element first, then every 2nd chunk
print(list(chunked(data, size=2, nth_position=2, chunk_position=2, apply_nth_before_chunk=True)))
# → [[5, 7]]
```

---

### 🔹 chunk_position then nth_position
```python
# Chunk normally, keep every 2nd chunk, then take 2nd element from each
print(list(chunked(data, size=2, chunk_position=2, nth_position=2, apply_nth_before_chunk=False)))
# → [[4], [8]]
```
